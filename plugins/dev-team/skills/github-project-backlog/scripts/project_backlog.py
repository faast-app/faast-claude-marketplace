#!/usr/bin/env python3
"""Backlog profesional en un GitHub Project v2 desde UN spec JSON (dev-team).

Lo usa el agente product-owner (comando /dev-team:project, skill github-project-backlog).
Solo Python 3 (biblioteca estandar) + GitHub CLI (`gh`) autenticado con scope `project`.

SUBCOMANDOS
  aplicar SPEC     Crea o REUTILIZA todo lo que el spec describe: Project, campos
                   single-select y sus opciones (incluidas las de Status), etiquetas,
                   milestones por fase, epicas por categoria, issues reales, sub-issues,
                   items del Project con sus campos, cierre de lo ya hecho, vistas,
                   espejo local y registro en .coordination/config.json. Idempotente:
                   volver a correrlo NO duplica nada (sirve para "crear" y "agregar").
  verificar SPEC   Revisa el Project real: borradores, items sin campos (el caso
                   "Content already exists"), issues del proyecto fuera del Project,
                   sub-issues faltantes. Con --corregir los arregla. Reporta conteos por
                   Fase / Categoria / Status / Tipo.
  espejo SPEC      Regenera la seccion del Project en .coordination/backlog.md (al
                   principio, sin borrar lo demas; reemplaza solo su propia seccion).

MODO PRUEBA
  --dry-run        Imprime el plan (que crearia / reutilizaria / actualizaria) SIN
                   ninguna escritura: ni en GitHub ni en disco. Solo hace lecturas con gh.
  --offline        Junto con --dry-run: no llama a gh en absoluto (asume que nada existe).

FORMATO DEL SPEC (JSON, UTF-8)
  {
    "org": "mi-org",                       # owner del Project (organizacion o usuario)
    "repo": "mi-org/repo-de-issues",       # o solo "repo-de-issues" (se antepone org)
    "project": "Nombre exacto del Project",
    "project_label": "MiProyecto",         # opcional; por defecto el nombre del Project
    "generar_salidas": true,               # opcional; crea "Salida de la Fase N" si falta
    "categoria_salidas": "Documentacion y gobierno",   # opcional
    "vistas": true,                        # opcional
    "fases": [
      {"nombre": "Fase 0", "titulo": "Entorno de pruebas listo",
       "objetivo": "...", "condicion_salida": "...",
       "milestone": "titulo opcional", "cat_salida": "categoria opcional"}
    ],
    "categorias": [ {"nombre": "Entorno de pruebas", "descripcion": "..."} ],
    "items": [
      {"titulo": "...", "body": "markdown en lenguaje de negocio",
       "fase": "Fase 0", "cat": "Entorno de pruebas",
       "prio": "Alta|Media|Baja",
       "tipo": "Historia|Decision|Riesgo|Tarea de negocio",
       "estado": "Backlog|Sprint actual|En progreso|En QA|Bloqueado|Hecho",
       "etiquetas": ["opcional"], "comentario_hecho": "opcional"}
    ]
  }
  "categorias" y "fases" aceptan tambien la forma de diccionario {nombre: descripcion}
  / {nombre: {...}}. Acentos: se conservan en titulos y cuerpos; los NOMBRES de
  opciones de campos y de etiquetas se guardan sin acentos.

ARCHIVO DE ESTADO (para reanudar y como resultado)
  Nunca en el directorio actual ni dentro de un repo git. Se busca subiendo desde el
  cwd una carpeta `.coordination/` con config.json cuya carpeta padre NO este dentro de
  un repo git (git -C <padre> rev-parse --is-inside-work-tree) y se usa
  `.coordination/project-state/<nombre>.json`; si no hay, `~/.dev-team/project-state/`.
  `--estado RUTA` lo fija a mano (tambien se rechaza si cae dentro de un repo git).

GARANTIAS
  - GraphQL siempre con VARIABLES (cuerpo JSON por --input); jamas se interpolan
    titulos ni cuerpos en el texto de la consulta.
  - Reintentos con espera creciente ante errores transitorios / rate limit.
  - Mutaciones en lotes chicos (maximo 5 alias por llamada).
  - Nunca crea borradores: cada item es un issue real.
  - Sub-issues por REST con el id NUMERICO del issue (no el numero ni el node_id).
  - En re-ejecuciones solo LLENA campos vacios: no pisa el Status que el equipo movio.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# Catalogos fijos
# ---------------------------------------------------------------------------

STATUS_OPCIONES = [
    ("Backlog", "GRAY", "Pendiente, aun no planificado"),
    ("Sprint actual", "BLUE", "Comprometido para el sprint en curso"),
    ("En progreso", "YELLOW", "Alguien lo esta trabajando"),
    ("En QA", "PURPLE", "En validacion de calidad"),
    ("Bloqueado", "RED", "Detenido por una dependencia o decision"),
    ("Hecho", "GREEN", "Terminado y aceptado"),
]
# Opciones por defecto de GitHub que se RENOMBRAN (conservando el id y los valores).
STATUS_RENOMBRES = {"todo": "Backlog", "in progress": "En progreso", "done": "Hecho"}

PRIORIDADES = [
    ("Alta", "RED", "Impacta la salida de la fase"),
    ("Media", "YELLOW", "Importante, no bloquea"),
    ("Baja", "GRAY", "Deseable"),
]
# (opcion del campo Tipo, color, etiqueta)
TIPOS = [
    ("Historia", "BLUE", "historia"),
    ("Decision", "PURPLE", "decision"),
    ("Riesgo", "ORANGE", "riesgo"),
    ("Tarea de negocio", "GRAY", "tarea de negocio"),
    ("Epica", "GREEN", "epica"),
]
COLORES = ["BLUE", "GREEN", "YELLOW", "ORANGE", "RED", "PINK", "PURPLE", "GRAY"]

COLOR_LABEL = {
    "proyecto": "5319E7", "fase": "1D76DB", "cat": "C5DEF5", "historia": "0E8A16",
    "decision": "8250DF", "riesgo": "D93F0B", "tarea de negocio": "BFBFBF", "epica": "006B75",
}

VISTAS = [
    ("Tablero por Estado", "BOARD_LAYOUT"),
    ("Tabla por Fase", "TABLE_LAYOUT"),
    ("Tabla por Categoria", "TABLE_LAYOUT"),
    ("Roadmap por Fase", "ROADMAP_LAYOUT"),
]
CAMPOS_VISIBLES = ["Title", "Status", "Fase", "Categoria", "Prioridad", "Tipo"]

LOTE_MAX = 5
COMENTARIO_HECHO = "Ya realizado; se registra como Hecho."
MARCA_EPICA_INI = "<!-- historias:inicio -->"
MARCA_EPICA_FIN = "<!-- historias:fin -->"

# Palabras que delatan redaccion tecnica (solo advertencia, no bloquea).
JERGA = re.compile(
    r"\b(endpoint|api|sql|json|https?|backend|frontend|deploy\w*|commit\w*|merge\w*|"
    r"branch|nullable|null|refactor\w*|docker\w*|kubernetes|stack ?trace|microservicio\w*|"
    r"query|payload|token)\b",
    re.IGNORECASE,
)

TRANSITORIO = re.compile(
    r"(rate limit|secondary rate|abuse|submitted too quickly|timed? ?out|timeout|"
    r"\b50[234]\b|500 internal|bad gateway|service unavailable|something went wrong|"
    r"resource limits|econnreset|connection reset|unexpected eof|\beof\b|tls handshake|"
    r"temporarily|try again)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def sin_acentos(texto: str) -> str:
    """Quita tildes y dieresis (para nombres de etiquetas y opciones de campos)."""
    norm = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in norm if not unicodedata.combining(c))


def clave(texto: str) -> str:
    """Clave de comparacion: sin acentos, sin espacios extremos, en minusculas."""
    return re.sub(r"\s+", " ", sin_acentos(texto or "")).strip().lower()


def slug(texto: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", clave(texto)).strip("-")
    return s or "project"


def lotes(lista, n=LOTE_MAX):
    for i in range(0, len(lista), n):
        yield lista[i:i + n]


def ahora() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


def info(msg: str = "") -> None:
    print(msg, flush=True)


class ErrorSpec(Exception):
    pass


class GhError(Exception):
    def __init__(self, mensaje: str, transitorio: bool = False):
        super().__init__(mensaje)
        self.transitorio = transitorio


# ---------------------------------------------------------------------------
# Ubicacion del estado y de .coordination
# ---------------------------------------------------------------------------

def dentro_de_git(directorio: Path) -> bool:
    """True si `directorio` esta dentro de un work tree git."""
    d = directorio
    while not d.exists() and d != d.parent:
        d = d.parent
    if shutil.which("git"):
        try:
            r = subprocess.run(["git", "-C", str(d), "rev-parse", "--is-inside-work-tree"],
                               capture_output=True, text=True, timeout=15)
            return r.returncode == 0 and r.stdout.strip() == "true"
        except (OSError, subprocess.TimeoutExpired):
            pass
    # Sin git disponible: buscar un .git subiendo.
    for p in [d, *d.parents]:
        if (p / ".git").exists():
            return True
    return False


def _coord_root_plugin(inicio: Path) -> Path | None:
    """Usa el resolvedor del plugin (hooks/coord_root.py: registro ~/.claude/dev-team.config.json,
    puntero legado, carpeta del proyecto). Devuelve la coordinacion canonica FUERA de repos."""
    try:
        hooks = Path(__file__).resolve().parents[3] / "hooks"
        if (hooks / "coord_root.py").is_file():
            sys.path.insert(0, str(hooks))
            from coord_root import resolve  # type: ignore
            r = resolve(str(inicio))
            if r.get("path") and not r.get("en_repo") and (Path(r["path"]) / "config.json").is_file():
                return Path(r["path"])
    except Exception:
        pass
    return None


def buscar_coordination(inicio: Path, canonica: bool) -> Path | None:
    """Coordinacion del proyecto. Regla del equipo: NUNCA se escribe dentro de un repo git, asi
    que siempre se exige una coordinacion fuera de repos (canonica). El parametro se conserva
    por compatibilidad."""
    c = _coord_root_plugin(inicio)
    if c:
        return c
    for d in [inicio, *inicio.parents]:
        c = d / ".coordination"
        if (c / "config.json").is_file():
            if not dentro_de_git(d):
                return c
    return None


def resolver_estado(nombre_project: str, explicita: str | None) -> Path:
    if explicita:
        p = Path(explicita).expanduser().resolve()
        if dentro_de_git(p.parent):
            raise ErrorSpec(f"--estado {p} cae dentro de un repo git; el estado nunca se guarda en un repo.")
        return p
    canon = buscar_coordination(Path.cwd().resolve(), canonica=True)
    base = canon / "project-state" if canon else Path.home() / ".dev-team" / "project-state"
    return base / f"{slug(nombre_project)}.json"


class Estado:
    """Archivo de estado/resultado (cache para reanudar + registro de lo hecho)."""

    def __init__(self, ruta: Path, escribir: bool):
        self.ruta = ruta
        self.escribir = escribir
        self.datos: dict = {}
        if ruta.is_file():
            try:
                self.datos = json.loads(ruta.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                self.datos = {}
        self.datos.setdefault("epicas", {})
        self.datos.setdefault("items", {})

    def guardar(self) -> None:
        if not self.escribir:
            return
        self.datos["actualizado"] = ahora()
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.ruta.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.datos, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(self.ruta)


# ---------------------------------------------------------------------------
# Cliente gh (lecturas, escrituras, reintentos)
# ---------------------------------------------------------------------------

class Gh:
    def __init__(self, dry_run: bool, offline: bool, intentos: int = 5, espera: float = 3.0):
        self.dry_run = dry_run
        self.offline = offline
        self.intentos = intentos
        self.espera = espera
        self.escrituras = 0

    def _run(self, args: list[str], stdin: str | None, escritura: bool, reintentar: bool = True) -> str:
        if self.offline:
            raise RuntimeError("BUG: llamada a gh en modo --offline")
        if escritura and self.dry_run:
            raise RuntimeError("BUG: intento de escritura en modo --dry-run (bloqueado)")
        espera = self.espera
        ultimo = ""
        for intento in range(1, (self.intentos if reintentar else 1) + 1):
            try:
                r = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True, timeout=180)
            except subprocess.TimeoutExpired:
                r = None
                ultimo = "timeout ejecutando gh"
            if r is not None:
                if r.returncode == 0:
                    if escritura:
                        self.escrituras += 1
                    return r.stdout
                ultimo = (r.stderr or "").strip() or (r.stdout or "").strip()
                # GraphQL: errores con datos parciales vienen en stdout con rc=1.
                if args[:2] == ["api", "graphql"] and r.stdout.strip().startswith("{"):
                    try:
                        cuerpo = json.loads(r.stdout)
                    except json.JSONDecodeError:
                        cuerpo = None
                    if cuerpo is not None:
                        msgs = " | ".join(e.get("message", "") for e in cuerpo.get("errors", []))
                        if not TRANSITORIO.search(msgs) and not TRANSITORIO.search(ultimo):
                            return r.stdout  # error definitivo: lo interpreta gql()
                        ultimo = msgs or ultimo
            if not TRANSITORIO.search(ultimo) or intento == self.intentos or not reintentar:
                raise GhError(ultimo[:600], transitorio=bool(TRANSITORIO.search(ultimo)))
            pausa = max(espera, 60.0) if re.search(r"secondary|abuse|too quickly", ultimo, re.I) else espera
            info(f"   ... error transitorio ({ultimo[:90]}); reintento {intento}/{self.intentos - 1} en {pausa:.0f}s")
            time.sleep(pausa)
            espera *= 2
        raise GhError(ultimo[:600])

    # --- REST -------------------------------------------------------------
    def get(self, path: str, params: dict | None = None, paginar: bool = False):
        args = ["api", "-X", "GET", path]
        for k, v in (params or {}).items():
            args += ["-f", f"{k}={v}"]
        if paginar:
            args += ["--paginate", "--slurp"]
        out = self._run(args, None, escritura=False)
        datos = json.loads(out) if out.strip() else None
        if paginar and isinstance(datos, list):
            plano = []
            for pagina in datos:
                plano.extend(pagina if isinstance(pagina, list) else [pagina])
            return plano
        return datos

    def write(self, metodo: str, path: str, payload: dict, reintentar: bool = True):
        out = self._run(["api", "-X", metodo, path, "--input", "-"], json.dumps(payload, ensure_ascii=False),
                        escritura=True, reintentar=reintentar)
        return json.loads(out) if out.strip() else {}

    # --- GraphQL (siempre con variables) ------------------------------------
    def gql(self, query: str, variables: dict | None = None, escritura: bool = False) -> dict:
        cuerpo = json.dumps({"query": query, "variables": variables or {}}, ensure_ascii=False)
        out = self._run(["api", "graphql", "--input", "-"], cuerpo, escritura=escritura)
        resp = json.loads(out)
        errores = resp.get("errors") or []
        if errores:
            msg = " | ".join(e.get("message", "?") for e in errores)
            if not resp.get("data") or all(v is None for v in (resp.get("data") or {}).values()):
                raise GhError(msg)
            resp.setdefault("data", {})["_errores"] = msg
        return resp.get("data") or {}


# ---------------------------------------------------------------------------
# Spec
# ---------------------------------------------------------------------------

def _como_lista(valor, campo_desc: str) -> list[dict]:
    if isinstance(valor, dict):
        salida = []
        for nombre, v in valor.items():
            d = dict(v) if isinstance(v, dict) else {campo_desc: v}
            d["nombre"] = nombre
            salida.append(d)
        return salida
    return [dict(x) for x in (valor or [])]


def _buscar(opciones: list[str], valor: str) -> str | None:
    for o in opciones:
        if clave(o) == clave(valor):
            return o
    return None


def cargar_spec(ruta: str) -> tuple[dict, list[str]]:
    """Lee y normaliza el spec. Devuelve (spec, advertencias). Lanza ErrorSpec."""
    try:
        spec = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ErrorSpec(f"No pude leer el spec {ruta}: {e}")
    errores, avisos = [], []
    for k in ("org", "repo", "project"):
        if not str(spec.get(k, "")).strip():
            errores.append(f"falta '{k}'")
    if errores:
        raise ErrorSpec("Spec invalido: " + "; ".join(errores))
    org = spec["org"].strip()
    repo = spec["repo"].strip()
    if "/" not in repo:
        repo = f"{org}/{repo}"
    spec["org"], spec["repo"], spec["project"] = org, repo, spec["project"].strip()
    spec["project_label"] = sin_acentos(str(spec.get("project_label") or spec["project"]).strip())
    spec.setdefault("generar_salidas", True)
    spec.setdefault("vistas", True)

    fases = _como_lista(spec.get("fases"), "condicion_salida")
    if not fases:
        errores.append("'fases' esta vacio")
    for i, f in enumerate(fases):
        if not f.get("nombre"):
            errores.append(f"fase #{i + 1} sin 'nombre'")
            continue
        f["opcion"] = sin_acentos(f["nombre"]).strip()
        num = f["opcion"].split()[-1]
        f["etiqueta"] = "fase-" + (num if num.isdigit() else slug(f["opcion"]))
        if not str(f.get("condicion_salida", "")).strip():
            errores.append(f"{f['nombre']}: falta 'condicion_salida'")
        titulo = str(f.get("titulo", "")).strip()
        f["titulo"] = titulo
        f["nombre_largo"] = f"{f['nombre']}: {titulo}" if titulo else f["nombre"]
        f["milestone"] = f.get("milestone") or f"{spec['project_label']} · {f['nombre_largo']}"
    spec["fases"] = fases

    cats = _como_lista(spec.get("categorias"), "descripcion")
    if not cats:
        errores.append("'categorias' esta vacio")
    for c in cats:
        c["opcion"] = sin_acentos(c["nombre"]).strip()
        c["etiqueta"] = "cat: " + c["opcion"]
        c.setdefault("descripcion", "")
    spec["categorias"] = cats

    nombres_fase = [f["nombre"] for f in fases if f.get("nombre")]
    nombres_cat = [c["nombre"] for c in cats]
    tipos = [t[0] for t in TIPOS if t[0] != "Epica"]
    prios = [p[0] for p in PRIORIDADES]
    estados = [s[0] for s in STATUS_OPCIONES]

    items = [dict(x) for x in spec.get("items") or []]
    titulos = set()
    for n, it in enumerate(items, 1):
        ref = f"item #{n} ({str(it.get('titulo', ''))[:40]!r})"
        it["titulo"] = str(it.get("titulo", "")).strip()
        if not it["titulo"]:
            errores.append(f"{ref}: sin titulo")
        if clave(it["titulo"]) in titulos:
            errores.append(f"{ref}: titulo duplicado")
        titulos.add(clave(it["titulo"]))
        for campo, opciones, defecto in (("fase", nombres_fase, None), ("cat", nombres_cat, None),
                                         ("tipo", tipos, "Historia"), ("prio", prios, "Media"),
                                         ("estado", estados, "Backlog")):
            valor = it.get(campo) or defecto
            if not valor:
                errores.append(f"{ref}: falta '{campo}'")
                continue
            ok = _buscar(opciones, valor)
            if not ok:
                errores.append(f"{ref}: {campo}={valor!r} no es valido (opciones: {', '.join(opciones)})")
            it[campo] = ok or valor
        it["body"] = str(it.get("body") or "").strip()
        if not it["body"]:
            avisos.append(f"{ref}: cuerpo vacio (el PO debe redactarlo)")
        if JERGA.search(it["titulo"]):
            avisos.append(f"{ref}: el TITULO suena tecnico ({JERGA.search(it['titulo']).group(0)!r}); reescribir en negocio")
        elif JERGA.search(it["body"]):
            avisos.append(f"{ref}: el cuerpo menciona {JERGA.search(it['body']).group(0)!r}; revisar lenguaje de negocio")
        if it.get("tipo") == "Historia" and not (re.search(r"\bdado\b", it["body"], re.I)
                                                  and re.search(r"\bentonces\b", it["body"], re.I)):
            avisos.append(f"{ref}: historia sin criterios Gherkin (Dado/Cuando/Entonces)")
        it.setdefault("generado", False)

    # Item "Salida de la Fase N" por fase (si falta y se pide).
    if spec["generar_salidas"] and not errores:
        cat_def = spec.get("categoria_salidas") or nombres_cat[0]
        for f in fases:
            prefijo = clave(f"Salida de la {f['nombre']}")
            if any(clave(i["titulo"]).startswith(prefijo) for i in items):
                continue
            cat = _buscar(nombres_cat, f.get("cat_salida") or cat_def) or nombres_cat[0]
            items.append({
                "titulo": f"Salida de la {f['nombre_largo']}",
                "body": cuerpo_salida(f),
                "fase": f["nombre"], "cat": cat, "tipo": "Tarea de negocio",
                "prio": "Alta", "estado": "Backlog", "generado": True,
            })
    if errores:
        raise ErrorSpec("Spec invalido:\n  - " + "\n  - ".join(errores))
    # Orden de creacion: por fase, respetando el orden del spec; la salida al final.
    orden = {f["nombre"]: i for i, f in enumerate(fases)}
    items.sort(key=lambda i: (orden.get(i["fase"], 99), 1 if i["generado"] else 0))
    spec["items"] = items
    return spec, avisos


def cuerpo_salida(f: dict) -> str:
    obj = str(f.get("objetivo") or "").strip()
    return (
        f"## Contexto\nCierre formal de la {f['nombre_largo']}."
        + (f" Objetivo de la fase: {obj}" if obj else "") + "\n\n"
        f"## Condición de salida\n{f['condicion_salida']}\n\n"
        "## Criterios de aceptación\n```gherkin\n"
        f"Escenario: Cierre de la {f['nombre']}\n"
        f"  Dado que las historias de la {f['nombre']} están en Hecho\n"
        "  Cuando el usuario revisa la condición de salida con el equipo\n"
        "  Entonces la fase se da por cerrada y puede comenzar la siguiente\n"
        "```\n\n"
        f"## Clasificación\n- Fase: {f['nombre']}\n- Tipo: Tarea de negocio\n"
    )


def opciones_deseadas(spec: dict) -> dict[str, list[tuple[str, str, str]]]:
    return {
        "Status": STATUS_OPCIONES,
        "Fase": [(f["opcion"], COLORES[i % len(COLORES)], sin_acentos(f["titulo"])[:100])
                 for i, f in enumerate(spec["fases"])],
        "Categoria": [(c["opcion"], COLORES[i % len(COLORES)], sin_acentos(c["descripcion"])[:100])
                      for i, c in enumerate(spec["categorias"])],
        "Prioridad": PRIORIDADES,
        "Tipo": [(t[0], t[1], "") for t in TIPOS],
    }


def etiquetas_deseadas(spec: dict) -> list[tuple[str, str, str]]:
    salida = [(spec["project_label"], COLOR_LABEL["proyecto"], f"Backlog del Project {sin_acentos(spec['project'])}")]
    for f in spec["fases"]:
        salida.append((f["etiqueta"], COLOR_LABEL["fase"], sin_acentos(f["nombre_largo"])[:100]))
    for c in spec["categorias"]:
        salida.append((c["etiqueta"], COLOR_LABEL["cat"], sin_acentos(c["descripcion"])[:100]))
    for _, _, et in TIPOS:
        salida.append((et, COLOR_LABEL[et], ""))
    for it in spec["items"]:
        for extra in it.get("etiquetas") or []:
            salida.append((sin_acentos(extra), "EDEDED", ""))
    vistos, unicos = set(), []
    for e in salida:
        if clave(e[0]) not in vistos:
            vistos.add(clave(e[0]))
            unicos.append(e)
    return unicos


def etiqueta_tipo(tipo: str) -> str:
    return next(t[2] for t in TIPOS if t[0] == tipo)


def fase_de(spec: dict, nombre: str) -> dict:
    return next(f for f in spec["fases"] if f["nombre"] == nombre)


def cat_de(spec: dict, nombre: str) -> dict:
    return next(c for c in spec["categorias"] if c["nombre"] == nombre)


def titulo_epica(cat: dict) -> str:
    return f"Épica: {cat['nombre']}"


def etiquetas_item(spec: dict, it: dict) -> list[str]:
    return [spec["project_label"], fase_de(spec, it["fase"])["etiqueta"], cat_de(spec, it["cat"])["etiqueta"],
            etiqueta_tipo(it["tipo"]), *[sin_acentos(e) for e in it.get("etiquetas") or []]]


# ---------------------------------------------------------------------------
# Lecturas de GitHub
# ---------------------------------------------------------------------------

Q_OWNER = """query($login:String!){ repositoryOwner(login:$login){ __typename id login } }"""

Q_PROJECTS = """
query($login:String!,$q:String!,$after:String){
  repositoryOwner(login:$login){
    ... on Organization { projectsV2(first:50, query:$q, after:$after){
        pageInfo{ hasNextPage endCursor } nodes{ id number title url closed } } }
    ... on User { projectsV2(first:50, query:$q, after:$after){
        pageInfo{ hasNextPage endCursor } nodes{ id number title url closed } } }
  }
}"""

Q_PROJECT = """
query($id:ID!){ node(id:$id){ ... on ProjectV2 {
  id number title url
  repositories(first:50){ nodes{ nameWithOwner } }
  fields(first:50){ nodes{
    ... on ProjectV2Field { id name dataType }
    ... on ProjectV2IterationField { id name dataType }
    ... on ProjectV2SingleSelectField { id name dataType options{ id name color description } } } }
  views(first:50){ nodes{ id name number layout } }
} } }"""

Q_ITEMS = """
query($id:ID!,$after:String){ node(id:$id){ ... on ProjectV2 {
  items(first:100, after:$after){
    pageInfo{ hasNextPage endCursor }
    nodes{ id type isArchived
      content{ __typename
        ... on Issue { id databaseId number title state url repository{ nameWithOwner } labels(first:40){ nodes{ name } } }
        ... on DraftIssue { id title }
        ... on PullRequest { id number title url } }
      fieldValues(first:30){ nodes{
        ... on ProjectV2ItemFieldSingleSelectValue { name optionId field{ ... on ProjectV2SingleSelectField { id name } } } } }
    } } } } }"""


class Actual:
    """Lo que ya existe en GitHub (vacio en modo --offline)."""

    def __init__(self):
        self.owner_id: str | None = None
        self.repo_id: str | None = None
        self.project: dict | None = None
        self.repos_enlazados: set[str] = set()
        self.campos: dict[str, dict] = {}       # nombre -> {id, dataType, options[]}
        self.vistas: list[dict] = []
        self.items: dict[str, dict] = {}        # node_id del issue -> {item_id, valores{campo: opcion}, ...}
        self.borradores: list[dict] = []
        self.etiquetas: dict[str, str] = {}     # clave -> nombre real
        self.milestones: dict[str, dict] = {}   # titulo -> {number, description}
        self.issues: dict[str, dict] = {}       # clave(titulo) -> issue REST
        self.sub_issues: dict[int, set[int]] = {}  # numero epica -> ids numericos hijos
        self.duplicados: list[str] = []


def leer_project_por_titulo(gh: Gh, org: str, titulo: str) -> dict | None:
    encontrados, after = [], None
    while True:
        d = gh.gql(Q_PROJECTS, {"login": org, "q": titulo, "after": after})
        owner = d.get("repositoryOwner") or {}
        conn = owner.get("projectsV2") or {"nodes": [], "pageInfo": {}}
        encontrados += [p for p in conn["nodes"] if p and p["title"].strip() == titulo]
        if not conn["pageInfo"].get("hasNextPage"):
            break
        after = conn["pageInfo"]["endCursor"]
    abiertos = [p for p in encontrados if not p["closed"]] or encontrados
    if len(abiertos) > 1:
        nums = ", ".join(f"#{p['number']}" for p in abiertos)
        raise ErrorSpec(f"Hay {len(abiertos)} Projects llamados {titulo!r} ({nums}); el usuario debe elegir uno.")
    return abiertos[0] if abiertos else None


def leer_detalle_project(gh: Gh, act: Actual) -> None:
    d = gh.gql(Q_PROJECT, {"id": act.project["id"]})["node"]
    act.repos_enlazados = {r["nameWithOwner"].lower() for r in d["repositories"]["nodes"]}
    act.campos = {f["name"]: f for f in d["fields"]["nodes"] if f}
    act.vistas = d["views"]["nodes"]


def leer_items(gh: Gh, act: Actual) -> None:
    act.items, act.borradores, after = {}, [], None
    while True:
        d = gh.gql(Q_ITEMS, {"id": act.project["id"], "after": after})["node"]["items"]
        for n in d["nodes"]:
            if not n or n.get("isArchived"):
                continue
            valores = {}
            for v in n["fieldValues"]["nodes"]:
                if v and v.get("field") and v["field"].get("name"):
                    valores[v["field"]["name"]] = v["name"]
            c = n.get("content") or {}
            if n["type"] == "DRAFT_ISSUE":
                act.borradores.append({"item_id": n["id"], "titulo": c.get("title", ""), "valores": valores})
            elif c.get("__typename") == "Issue":
                act.items[c["id"]] = {
                    "item_id": n["id"], "valores": valores, "numero": c["number"], "titulo": c["title"],
                    "estado": c["state"], "url": c["url"], "repo": c["repository"]["nameWithOwner"],
                    "db_id": c.get("databaseId"), "etiquetas": [x["name"] for x in c["labels"]["nodes"]],
                }
        if not d["pageInfo"]["hasNextPage"]:
            break
        after = d["pageInfo"]["endCursor"]


def leer_issues(gh: Gh, spec: dict, act: Actual) -> None:
    lista = gh.get(f"repos/{spec['repo']}/issues",
                   {"labels": spec["project_label"], "state": "all", "per_page": "100"}, paginar=True) or []
    act.issues = {}
    for i in sorted((x for x in lista if "pull_request" not in x), key=lambda x: x["number"]):
        k = clave(i["title"])
        if k in act.issues:
            act.duplicados.append(f"#{i['number']} repite el titulo de #{act.issues[k]['number']}: {i['title']}")
            continue
        act.issues[k] = i


def leer_sub_issues(gh: Gh, spec: dict, numero: int) -> set[int]:
    hijos = gh.get(f"repos/{spec['repo']}/issues/{numero}/sub_issues", {"per_page": "100"}, paginar=True) or []
    return {h["id"] for h in hijos}


def descubrir(gh: Gh, spec: dict) -> tuple[Actual, list[str]]:
    act, avisos = Actual(), []
    if gh.offline:
        return act, ["modo --offline: no se consulto GitHub; el plan asume que NADA existe todavia"]
    auth = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    salida_auth = auth.stdout + auth.stderr
    if auth.returncode != 0:
        raise ErrorSpec("gh no esta autenticado (gh auth status). Ejecutar /dev-team:setup; no se hace auth interactivo.")
    if not re.search(r"['\s,]project['\s,]", salida_auth):
        msg = "el token de gh no tiene scope 'project' (gh auth refresh -s project lo agrega; lo hace el usuario)"
        if not gh.dry_run:
            raise ErrorSpec(msg)
        avisos.append(msg)
    owner = gh.gql(Q_OWNER, {"login": spec["org"]}).get("repositoryOwner")
    if not owner:
        raise ErrorSpec(f"No existe la organizacion/usuario {spec['org']!r} o no hay acceso.")
    act.owner_id = owner["id"]
    try:
        act.repo_id = gh.get(f"repos/{spec['repo']}")["node_id"]
    except GhError as e:
        raise ErrorSpec(f"No existe el repo {spec['repo']} o no hay acceso ({e}). Nunca se crean repos sin autorizacion.")
    act.project = leer_project_por_titulo(gh, spec["org"], spec["project"])
    if act.project:
        leer_detalle_project(gh, act)
        leer_items(gh, act)
    act.etiquetas = {clave(e["name"]): e["name"] for e in
                     json.loads(gh._run(["label", "list", "--repo", spec["repo"], "--limit", "1000",
                                         "--json", "name"], None, escritura=False) or "[]")}
    for m in gh.get(f"repos/{spec['repo']}/milestones", {"state": "all", "per_page": "100"}, paginar=True) or []:
        act.milestones[m["title"]] = {"number": m["number"], "description": m.get("description") or ""}
    leer_issues(gh, spec, act)
    for c in spec["categorias"]:
        epica = act.issues.get(clave(titulo_epica(c)))
        if epica:
            act.sub_issues[epica["number"]] = leer_sub_issues(gh, spec, epica["number"])
    avisos += act.duplicados
    reconciliar_salidas(spec, act)
    return act, avisos


def reconciliar_salidas(spec: dict, act: Actual) -> None:
    """Si ya existe un issue "Salida de la Fase N..." con otro titulo, el item generado lo reutiliza."""
    for it in spec["items"]:
        if not it["generado"] or clave(it["titulo"]) in act.issues:
            continue
        prefijo = clave(f"Salida de la {it['fase']}")
        for k, issue in act.issues.items():
            resto = k[len(prefijo):]
            if k.startswith(prefijo) and not (resto[:1].isdigit()):
                it["titulo"] = issue["title"]
                etqs = {clave(e["name"]) for e in issue.get("labels", [])}
                for c in spec["categorias"]:
                    if clave(c["etiqueta"]) in etqs:
                        it["cat"] = c["nombre"]  # respeta la categoria que ya tiene
                break


# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------

def fusionar_opciones(campo: str, existentes: list[dict], deseadas):
    """Devuelve (lista_para_mutacion, descripcion) o (None, None) si no hay cambios.

    Conserva el id de las opciones existentes (no se pierden valores de items) y las
    opciones extra que el equipo haya agregado. En Status renombra Todo/In Progress/Done."""
    ex = {clave(o["name"]): o for o in existentes}
    faltan = [d for d in deseadas if clave(d[0]) not in ex]
    if not faltan:
        return None, None
    renombres = {}
    if campo == "Status":
        for viejo, nuevo in STATUS_RENOMBRES.items():
            if viejo in ex and clave(nuevo) not in ex:
                renombres[clave(nuevo)] = ex[viejo]
    usados, salida, desc = set(), [], []
    for nombre, color, descripcion in deseadas:
        k = clave(nombre)
        if k in ex:
            o = ex[k]
            salida.append({"id": o["id"], "name": o["name"], "color": o["color"], "description": o.get("description") or ""})
            usados.add(o["id"])
        elif k in renombres:
            o = renombres[k]
            salida.append({"id": o["id"], "name": nombre, "color": color, "description": descripcion})
            usados.add(o["id"])
            desc.append(f"renombrar {o['name']} -> {nombre}")
        else:
            salida.append({"name": nombre, "color": color, "description": descripcion})
            desc.append(f"agregar {nombre}")
    for o in existentes:
        if o["id"] not in usados:
            salida.append({"id": o["id"], "name": o["name"], "color": o["color"], "description": o.get("description") or ""})
    return salida, ", ".join(desc)


def campos_existentes_supuestos(act: Actual) -> dict[str, dict]:
    """Campos del Project; si el Project aun no existe, asume el Status por defecto de GitHub."""
    if act.project:
        return act.campos
    return {"Status": {"id": None, "dataType": "SINGLE_SELECT",
                       "options": [{"id": f"(def-{n})", "name": n, "color": "GRAY", "description": ""}
                                   for n in ("Todo", "In Progress", "Done")]}}


def imprimir_plan(spec: dict, act: Actual, ruta_estado: Path, avisos: list[str], backlog: Path | None) -> None:
    info("=" * 72)
    info("PLAN (modo prueba: no se escribe nada en GitHub ni en disco)")
    info("=" * 72)
    if act.project:
        info(f"[REUTILIZAR] Project #{act.project['number']} {spec['project']!r}  {act.project['url']}")
    else:
        info(f"[CREAR]      Project {spec['project']!r} en {spec['org']} (y enlazarlo al repo {spec['repo']})")
    info(f"             Repo de issues: {spec['repo']} · etiqueta del proyecto: {spec['project_label']!r}")
    info(f"             Estado/resultado: {ruta_estado}")
    info(f"             Espejo local: {backlog or '(no se encontro .coordination/; usar --backlog)'}")

    info("\nCampos del Project:")
    existentes = campos_existentes_supuestos(act)
    for campo, deseadas in opciones_deseadas(spec).items():
        actual = existentes.get(campo)
        nombres = ", ".join(d[0] for d in deseadas)
        if not actual:
            info(f"  [CREAR]      {campo}: {nombres}")
            continue
        _, desc = fusionar_opciones(campo, actual.get("options") or [], deseadas)
        etiqueta = "Status (integrado)" if campo == "Status" else campo
        info(f"  [ACTUALIZAR] {etiqueta}: {desc}" if desc else f"  [OK]         {etiqueta}: {nombres}")

    info("\nEtiquetas:")
    nuevas = [e[0] for e in etiquetas_deseadas(spec) if clave(e[0]) not in act.etiquetas]
    reuso = [e[0] for e in etiquetas_deseadas(spec) if clave(e[0]) in act.etiquetas]
    if nuevas:
        info(f"  [CREAR]      {len(nuevas)}: " + ", ".join(nuevas))
    if reuso:
        info(f"  [REUTILIZAR] {len(reuso)}: " + ", ".join(reuso))

    info("\nMilestones por fase (con condicion de salida):")
    for f in spec["fases"]:
        m = act.milestones.get(f["milestone"])
        marca = f"[REUTILIZAR] #{m['number']}" if m else "[CREAR]     "
        info(f"  {marca} {f['milestone']}  ->  salida: {f['condicion_salida'][:70]}")

    info("\nEpicas por categoria:")
    for c in spec["categorias"]:
        e = act.issues.get(clave(titulo_epica(c)))
        marca = f"[REUTILIZAR] #{e['number']}" if e else "[CREAR]     "
        info(f"  {marca} {titulo_epica(c)}")

    info("\nItems (issues reales, nunca borradores):")
    sub_nuevos = 0
    for f in spec["fases"]:
        info(f"  {f['nombre_largo']}")
        for it in (i for i in spec["items"] if i["fase"] == f["nombre"]):
            e = act.issues.get(clave(it["titulo"]))
            marca = f"[REUTILIZAR] #{e['number']}" if e else "[CREAR]     "
            extra = " (se comenta y cierra)" if it["estado"] == "Hecho" and (not e or e["state"] == "open") else ""
            gen = " [generado]" if it["generado"] else ""
            info(f"    {marca} {it['titulo']}{gen}")
            info(f"                 {it['cat']} · {it['tipo']} · {it['prio']} · {it['estado']}{extra}")
            epica = act.issues.get(clave(titulo_epica(cat_de(spec, it["cat"]))))
            if not e or not epica or e["id"] not in act.sub_issues.get(epica["number"], set()):
                sub_nuevos += 1
    info(f"\nSub-issues a enlazar con su epica: {sub_nuevos}")

    if spec["vistas"]:
        info("\nVistas:")
        nombres = {v["name"] for v in act.vistas}
        for nombre, layout in VISTAS:
            info(f"  {'[OK]        ' if nombre in nombres else '[CREAR]     '} {nombre} ({layout})")
        info("  (el agrupamiento/orden de cada vista se marca A MANO en la interfaz: la API no lo permite)")

    info("\nConteo planificado:")
    imprimir_conteos([{"Fase": sin_acentos(i["fase"]), "Categoria": sin_acentos(i["cat"]),
                       "Status": i["estado"], "Tipo": i["tipo"]} for i in spec["items"]])
    if avisos:
        info("\nAdvertencias:")
        for a in avisos:
            info(f"  ! {a}")
    info("\nNo se escribio nada. Para ejecutar: mismo comando sin --dry-run (requiere OK del usuario).")


def imprimir_conteos(filas: list[dict]) -> dict:
    conteos = {}
    for campo in ("Fase", "Categoria", "Status", "Tipo"):
        c: dict[str, int] = {}
        for f in filas:
            c[f.get(campo) or "(vacio)"] = c.get(f.get(campo) or "(vacio)", 0) + 1
        conteos[campo] = c
        info(f"  {campo:<10} " + " | ".join(f"{k}: {v}" for k, v in c.items()))
    info(f"  Total      {len(filas)}")
    return conteos


# ---------------------------------------------------------------------------
# Escrituras
# ---------------------------------------------------------------------------

M_CREAR_PROJECT = """mutation($o:ID!,$t:String!){ createProjectV2(input:{ownerId:$o,title:$t}){ projectV2{ id number title url } } }"""
M_ENLAZAR = """mutation($p:ID!,$r:ID!){ linkProjectV2ToRepository(input:{projectId:$p,repositoryId:$r}){ clientMutationId } }"""
M_CREAR_CAMPO = """mutation($p:ID!,$n:String!,$o:[ProjectV2SingleSelectFieldOptionInput!]!){
  createProjectV2Field(input:{projectId:$p,dataType:SINGLE_SELECT,name:$n,singleSelectOptions:$o}){
    projectV2Field{ ... on ProjectV2SingleSelectField{ id name dataType options{ id name color description } } } } }"""
M_ACT_CAMPO = """mutation($f:ID!,$o:[ProjectV2SingleSelectFieldOptionInput!]!){
  updateProjectV2Field(input:{fieldId:$f,singleSelectOptions:$o}){
    projectV2Field{ ... on ProjectV2SingleSelectField{ id name dataType options{ id name color description } } } } }"""
M_AGREGAR_ITEM = """mutation($p:ID!,$c:ID!){ addProjectV2ItemById(input:{projectId:$p,contentId:$c}){ item{ id } } }"""
M_CREAR_VISTA = """mutation($p:ID!,$n:String!,$l:ProjectV2ViewLayout!){
  createProjectV2View(input:{projectId:$p,name:$n,layout:$l}){ projectV2View{ id name layout } } }"""
M_CREAR_VISTA_CFG = """mutation($p:ID!,$n:String!,$l:ProjectV2ViewLayout!,$v:[ID!]){
  createProjectV2View(input:{projectId:$p,name:$n,layout:$l,configuration:{visibleFieldIds:$v}}){ projectV2View{ id name layout } } }"""
M_ACT_VISTA = """mutation($v:ID!,$n:String!,$l:ProjectV2ViewLayout!){
  updateProjectV2View(input:{viewId:$v,name:$n,layout:$l}){ projectV2View{ id name layout } } }"""
M_CONVERTIR = """mutation($i:ID!,$r:ID!){ convertProjectV2DraftIssueItemToIssue(input:{itemId:$i,repositoryId:$r}){
  item{ id content{ ... on Issue{ id number title url } } } } }"""


class Ejecutor:
    def __init__(self, gh: Gh, spec: dict, act: Actual, estado: Estado, pausa: float):
        self.gh, self.spec, self.act, self.estado, self.pausa = gh, spec, act, estado, pausa
        self.repo = spec["repo"]
        self.avisos: list[str] = []
        self.campos: dict[str, dict] = {}   # nombre -> {id, opciones{clave: id}}
        self.creados = {"issues": 0, "reutilizados": 0, "sub_issues": 0, "cerrados": 0, "campos": 0}

    # --- Project, campos, etiquetas, milestones ----------------------------
    def project(self) -> None:
        if not self.act.project:
            d = self.gh.gql(M_CREAR_PROJECT, {"o": self.act.owner_id, "t": self.spec["project"]}, escritura=True)
            self.act.project = d["createProjectV2"]["projectV2"]
            info(f"Project creado #{self.act.project['number']}: {self.act.project['url']}")
            leer_detalle_project(self.gh, self.act)
        else:
            info(f"Project reutilizado #{self.act.project['number']}: {self.act.project['url']}")
        if self.repo.lower() not in self.act.repos_enlazados:
            try:
                self.gh.gql(M_ENLAZAR, {"p": self.act.project["id"], "r": self.act.repo_id}, escritura=True)
            except GhError as e:
                self.avisos.append(f"no pude enlazar el Project al repo {self.repo}: {e}")
        p = self.act.project
        self.estado.datos["project"] = {"id": p["id"], "number": p["number"], "url": p["url"], "title": self.spec["project"],
                                        "org": self.spec["org"], "repo": self.repo, "label": self.spec["project_label"]}
        self.estado.guardar()

    def campos_project(self) -> None:
        for campo, deseadas in opciones_deseadas(self.spec).items():
            actual = self.act.campos.get(campo)
            if actual and actual.get("dataType") != "SINGLE_SELECT":
                raise ErrorSpec(f"El campo {campo!r} existe pero no es de seleccion simple; renombrarlo o borrarlo a mano.")
            if not actual:
                opts = [{"name": n, "color": c, "description": d} for n, c, d in deseadas]
                f = self.gh.gql(M_CREAR_CAMPO, {"p": self.act.project["id"], "n": campo, "o": opts},
                                escritura=True)["createProjectV2Field"]["projectV2Field"]
                info(f"Campo creado: {campo}")
            else:
                lista, desc = fusionar_opciones(campo, actual.get("options") or [], deseadas)
                f = actual
                if lista:
                    f = self.gh.gql(M_ACT_CAMPO, {"f": actual["id"], "o": lista},
                                    escritura=True)["updateProjectV2Field"]["projectV2Field"]
                    info(f"Campo actualizado: {campo} ({desc})")
            self.act.campos[campo] = f
            self.campos[campo] = {"id": f["id"], "opciones": {clave(o["name"]): o["id"] for o in f["options"]}}
        self.estado.datos["campos"] = self.campos
        self.estado.guardar()

    def etiquetas(self) -> None:
        for nombre, color, desc in etiquetas_deseadas(self.spec):
            if clave(nombre) in self.act.etiquetas:
                continue
            try:
                self.gh.write("POST", f"repos/{self.repo}/labels", {"name": nombre, "color": color, "description": desc})
            except GhError as e:
                if "already_exists" not in str(e) and "already exists" not in str(e):
                    raise
            self.act.etiquetas[clave(nombre)] = nombre
            info(f"Etiqueta creada: {nombre}")

    def milestones(self) -> None:
        self.estado.datos["milestones"] = {}
        for f in self.spec["fases"]:
            desc = (f"Proyecto: {self.spec['project']}\n\n"
                    + (f"Objetivo: {f['objetivo']}\n\n" if f.get("objetivo") else "")
                    + f"CONDICIÓN DE SALIDA: {f['condicion_salida']}")
            m = self.act.milestones.get(f["milestone"])
            if not m:
                r = self.gh.write("POST", f"repos/{self.repo}/milestones", {"title": f["milestone"], "description": desc})
                m = {"number": r["number"], "description": desc}
                self.act.milestones[f["milestone"]] = m
                info(f"Milestone creado: {f['milestone']}")
            elif m["description"].strip() != desc.strip():
                self.gh.write("PATCH", f"repos/{self.repo}/milestones/{m['number']}", {"description": desc})
                m["description"] = desc
            self.estado.datos["milestones"][f["nombre"]] = m["number"]
        self.estado.guardar()

    # --- Issues ------------------------------------------------------------
    def _buscar_issue(self, titulo: str) -> dict | None:
        lista = self.gh.get(f"repos/{self.repo}/issues",
                            {"labels": self.spec["project_label"], "state": "all", "per_page": "100"}, paginar=True) or []
        for i in lista:
            if "pull_request" not in i and clave(i["title"]) == clave(titulo):
                return i
        return None

    def asegurar_issue(self, titulo: str, body: str, etiquetas: list[str], milestone: int | None) -> tuple[dict, bool]:
        """Reutiliza el issue (titulo exacto + etiqueta del proyecto) o lo crea. (issue, creado)."""
        existente = self.act.issues.get(clave(titulo))
        if existente:
            self.creados["reutilizados"] += 1
            actuales = {clave(e["name"]) for e in existente.get("labels", [])}
            faltan = [e for e in etiquetas if clave(e) not in actuales]
            if faltan:
                self.gh.write("POST", f"repos/{self.repo}/issues/{existente['number']}/labels", {"labels": faltan})
            if milestone and not existente.get("milestone"):
                self.gh.write("PATCH", f"repos/{self.repo}/issues/{existente['number']}", {"milestone": milestone})
            return existente, False
        payload = {"title": titulo, "body": body, "labels": etiquetas}
        if milestone:
            payload["milestone"] = milestone
        # Crear NO se reintenta a ciegas: si fallo por algo transitorio, puede haberse creado igual.
        espera = 5.0
        for intento in range(1, 4):
            try:
                issue = self.gh.write("POST", f"repos/{self.repo}/issues", payload, reintentar=False)
                break
            except GhError as e:
                if not e.transitorio or intento == 3:
                    raise
                time.sleep(espera)
                espera *= 3
                issue = self._buscar_issue(titulo)
                if issue:
                    break
        self.act.issues[clave(titulo)] = issue
        self.creados["issues"] += 1
        time.sleep(self.pausa)
        return issue, True

    def item_del_project(self, issue: dict) -> str | None:
        ya = self.act.items.get(issue["node_id"])
        if ya:
            return ya["item_id"]
        try:
            d = self.gh.gql(M_AGREGAR_ITEM, {"p": self.act.project["id"], "c": issue["node_id"]}, escritura=True)
        except GhError as e:
            self.avisos.append(f"#{issue['number']}: no se pudo agregar al Project ({str(e)[:80]}); se revisa en la verificacion")
            return None
        item = (d.get("addProjectV2ItemById") or {}).get("item")
        if not item:
            return None  # "Content already exists" sin id: la verificacion final lo recupera
        self.act.items[issue["node_id"]] = {"item_id": item["id"], "valores": {}, "numero": issue["number"]}
        return item["id"]

    def valores_pendientes(self, item_id: str, valores_actuales: dict, deseados: dict) -> list[tuple]:
        """Solo los campos VACIOS (no pisa lo que el equipo ya movio)."""
        pendientes = []
        for campo, opcion in deseados.items():
            if valores_actuales.get(campo):
                continue
            c = self.campos[campo]
            oid = c["opciones"].get(clave(opcion))
            if oid:
                pendientes.append((item_id, c["id"], oid))
        return pendientes

    def aplicar_valores(self, pendientes: list[tuple]) -> None:
        for lote in lotes(pendientes):
            decl, partes, var = ["$p:ID!"], [], {"p": self.act.project["id"]}
            for n, (item, campo, opcion) in enumerate(lote):
                decl += [f"$i{n}:ID!", f"$f{n}:ID!", f"$o{n}:String!"]
                partes.append(f"u{n}: updateProjectV2ItemFieldValue(input:{{projectId:$p,itemId:$i{n},"
                              f"fieldId:$f{n},value:{{singleSelectOptionId:$o{n}}}}}){{ clientMutationId }}")
                var.update({f"i{n}": item, f"f{n}": campo, f"o{n}": opcion})
            try:
                d = self.gh.gql(f"mutation({','.join(decl)}){{ {' '.join(partes)} }}", var, escritura=True)
            except GhError as e:
                self.avisos.append(f"lote de campos rechazado ({str(e)[:100]}); se reintenta en la verificacion")
                continue
            if d.get("_errores"):
                self.avisos.append(f"algunos campos no se fijaron ({d['_errores'][:100]}); se revisa en la verificacion")
            self.creados["campos"] += len(lote)

    def enlazar_sub_issue(self, epica: dict, issue: dict) -> None:
        hijos = self.act.sub_issues.setdefault(epica["number"], set())
        if issue["id"] in hijos:
            return
        try:
            # REST con el id NUMERICO del issue (ni el numero ni el node_id).
            self.gh.write("POST", f"repos/{self.repo}/issues/{epica['number']}/sub_issues", {"sub_issue_id": issue["id"]})
            hijos.add(issue["id"])
            self.creados["sub_issues"] += 1
        except GhError as e:
            self.avisos.append(f"#{issue['number']} no quedo como sub-issue de #{epica['number']}: {str(e)[:100]}")

    def cerrar_hecho(self, issue: dict, comentario: str) -> None:
        if issue.get("state") == "closed":
            return
        self.gh.write("POST", f"repos/{self.repo}/issues/{issue['number']}/comments", {"body": comentario})
        self.gh.write("PATCH", f"repos/{self.repo}/issues/{issue['number']}", {"state": "closed", "state_reason": "completed"})
        issue["state"] = "closed"
        self.creados["cerrados"] += 1

    def epicas(self) -> dict[str, dict]:
        epicas = {}
        for c in self.spec["categorias"]:
            cuerpo = f"## Qué agrupa\n{c['descripcion']}\n\n{MARCA_EPICA_INI}\n_(se completa al cargar las historias)_\n{MARCA_EPICA_FIN}\n"
            e, creado = self.asegurar_issue(titulo_epica(c), cuerpo, [self.spec["project_label"], "epica", c["etiqueta"]], None)
            if creado:
                self.act.sub_issues[e["number"]] = set()
            elif e["number"] not in self.act.sub_issues:
                self.act.sub_issues[e["number"]] = leer_sub_issues(self.gh, self.spec, e["number"])
            item = self.item_del_project(e)
            if item:
                vals = self.act.items.get(e["node_id"], {}).get("valores", {})
                self.aplicar_valores(self.valores_pendientes(item, vals, {
                    "Categoria": c["opcion"], "Tipo": "Epica", "Prioridad": "Alta", "Status": "Backlog"}))
            epicas[c["nombre"]] = e
            self.estado.datos["epicas"][c["nombre"]] = {"number": e["number"], "id": e["id"], "node_id": e["node_id"],
                                                        "url": e["html_url"], "item_id": item}
            info(f"{'Epica creada' if creado else 'Epica reutilizada'} #{e['number']}: {titulo_epica(c)}")
            self.estado.guardar()
        return epicas

    def items(self, epicas: dict[str, dict]) -> None:
        for it in self.spec["items"]:
            fase = fase_de(self.spec, it["fase"])
            issue, creado = self.asegurar_issue(it["titulo"], it["body"], etiquetas_item(self.spec, it),
                                                self.act.milestones[fase["milestone"]]["number"])
            self.enlazar_sub_issue(epicas[it["cat"]], issue)
            item = self.item_del_project(issue)
            if item:
                vals = self.act.items.get(issue["node_id"], {}).get("valores", {})
                self.aplicar_valores(self.valores_pendientes(item, vals, deseados_item(it)))
            if it["estado"] == "Hecho":
                self.cerrar_hecho(issue, it.get("comentario_hecho") or COMENTARIO_HECHO)
            self.estado.datos["items"][it["titulo"]] = {
                "number": issue["number"], "id": issue["id"], "node_id": issue["node_id"], "url": issue["html_url"],
                "item_id": item, "fase": it["fase"], "cat": it["cat"], "tipo": it["tipo"], "prio": it["prio"],
                "estado": it["estado"]}
            self.estado.guardar()
            info(f"  {'+' if creado else '='} #{issue['number']} {it['titulo'][:70]}")

    def cuerpos_epicas(self, epicas: dict[str, dict]) -> None:
        """Reescribe SOLO la seccion marcada de cada epica con sus historias por fase."""
        for c in self.spec["categorias"]:
            e = epicas[c["nombre"]]
            hijos =[i for i in self.act.issues.values() if i["number"] != e["number"] and self._de_categoria(i, c)]
            lineas = ["## Historias por fase"]
            for f in self.spec["fases"]:
                de_fase = sorted((i for i in hijos if self._de_fase(i, f)), key=lambda i: i["number"])
                if de_fase:
                    lineas.append(f"### {f['nombre_largo']}")
                    lineas += [f"- [{'x' if i.get('state') == 'closed' else ' '}] #{i['number']} {i['title']}" for i in de_fase]
            seccion = f"{MARCA_EPICA_INI}\n" + "\n".join(lineas) + f"\n{MARCA_EPICA_FIN}"
            cuerpo = e.get("body") or ""
            if MARCA_EPICA_INI in cuerpo and MARCA_EPICA_FIN in cuerpo:
                nuevo = re.sub(re.escape(MARCA_EPICA_INI) + r".*?" + re.escape(MARCA_EPICA_FIN),
                               lambda _m: seccion, cuerpo, flags=re.S)
            else:
                nuevo = cuerpo.rstrip() + "\n\n" + seccion + "\n"
            if nuevo.strip() != cuerpo.strip():
                self.gh.write("PATCH", f"repos/{self.repo}/issues/{e['number']}", {"body": nuevo})
                e["body"] = nuevo

    def _de_categoria(self, issue: dict, c: dict) -> bool:
        """Manda la etiqueta `cat: X`; el titulo del spec solo si el issue no tiene ninguna."""
        etqs = {clave(x["name"]) for x in issue.get("labels", [])}
        if any(e.startswith("cat: ") for e in etqs):
            return clave(c["etiqueta"]) in etqs
        return clave(issue["title"]) in {clave(i["titulo"]) for i in self.spec["items"] if i["cat"] == c["nombre"]}

    def _de_fase(self, issue: dict, f: dict) -> bool:
        etqs = {clave(x["name"]) for x in issue.get("labels", [])}
        if any(e.startswith("fase-") for e in etqs):
            return clave(f["etiqueta"]) in etqs
        return clave(issue["title"]) in {clave(i["titulo"]) for i in self.spec["items"] if i["fase"] == f["nombre"]}

    # --- Vistas --------------------------------------------------------------
    def vistas(self) -> None:
        if not self.spec["vistas"]:
            return
        try:
            leer_detalle_project(self.gh, self.act)
            por_nombre = {v["name"]: v for v in self.act.vistas}
            visibles = [self.act.campos[n]["id"] for n in CAMPOS_VISIBLES if n in self.act.campos]
            nuestras = {n for n, _ in VISTAS}
            for nombre, layout in VISTAS:
                if nombre in por_nombre:
                    continue
                defecto = [v for v in self.act.vistas if v["name"] not in nuestras and re.match(r"^(View|Vista) \d+$", v["name"])]
                if layout == "BOARD_LAYOUT" and len(self.act.vistas) == 1 and defecto:
                    self.gh.gql(M_ACT_VISTA, {"v": defecto[0]["id"], "n": nombre, "l": layout}, escritura=True)
                    info(f"Vista por defecto renombrada: {nombre}")
                    continue
                try:
                    if layout == "TABLE_LAYOUT" and visibles:
                        self.gh.gql(M_CREAR_VISTA_CFG, {"p": self.act.project["id"], "n": nombre, "l": layout, "v": visibles},
                                    escritura=True)
                    else:
                        raise GhError("sin configuracion")
                except GhError:
                    self.gh.gql(M_CREAR_VISTA, {"p": self.act.project["id"], "n": nombre, "l": layout}, escritura=True)
                info(f"Vista creada: {nombre}")
        except (GhError, KeyError, TypeError) as e:
            self.avisos.append(f"vistas: la API no permitio crearlas/renombrarlas ({str(e)[:100]}); crearlas a mano")


def deseados_item(it: dict) -> dict:
    return {"Fase": sin_acentos(it["fase"]), "Categoria": sin_acentos(it["cat"]), "Prioridad": it["prio"],
            "Tipo": it["tipo"], "Status": it["estado"]}


# ---------------------------------------------------------------------------
# Verificacion
# ---------------------------------------------------------------------------

def deseados_por_etiquetas(spec: dict | None, it: dict, campos: dict) -> dict:
    """Valores esperados de un item del Project: del spec si el titulo coincide, si no de sus etiquetas."""
    if spec:
        for s in spec["items"]:
            if clave(s["titulo"]) == clave(it["titulo"]):
                return deseados_item(s)
    etqs = {clave(e) for e in it.get("etiquetas", [])}
    d = {}
    for o in (campos.get("Fase") or {}).get("options", []):
        num = o["name"].split()[-1]
        if clave("fase-" + (num if num.isdigit() else slug(o["name"]))) in etqs:
            d["Fase"] = o["name"]
    for o in (campos.get("Categoria") or {}).get("options", []):
        if clave("cat: " + o["name"]) in etqs:
            d["Categoria"] = o["name"]
    for opcion, _, et in TIPOS:
        if clave(et) in etqs:
            d["Tipo"] = opcion
    if clave(it.get("titulo", "")).startswith("epica:"):
        d["Tipo"] = "Epica"
    d["Status"] = "Hecho" if it.get("estado") == "CLOSED" else "Backlog"
    return d


def verificar(gh: Gh, spec: dict, act: Actual, corregir: bool, ej: Ejecutor | None = None) -> dict:
    """Revisa el Project y (si corregir) re-llena campos vacios, agrega issues faltantes,
    convierte borradores y enlaza sub-issues. Devuelve los conteos."""
    if not act.project:
        raise ErrorSpec(f"No existe el Project {spec['project']!r} en {spec['org']}; usar 'aplicar'.")
    leer_detalle_project(gh, act)
    leer_items(gh, act)
    ej = ej or Ejecutor(gh, spec, act, Estado(Path("/dev/null"), False), 0)
    ej.campos = {n: {"id": f["id"], "opciones": {clave(o["name"]): o["id"] for o in f.get("options") or []}}
                 for n, f in act.campos.items() if f.get("dataType") == "SINGLE_SELECT"}
    hallazgos: list[str] = []

    # 1) Borradores
    for b in act.borradores:
        hallazgos.append(f"BORRADOR (debe ser issue real): {b['titulo']}")
        if corregir:
            d = gh.gql(M_CONVERTIR, {"i": b["item_id"], "r": act.repo_id}, escritura=True)
            nuevo = d["convertProjectV2DraftIssueItemToIssue"]["item"]["content"]
            gh.write("POST", f"repos/{spec['repo']}/issues/{nuevo['number']}/labels", {"labels": [spec["project_label"]]})
            info(f"  convertido en issue #{nuevo['number']}")

    # 2) Issues del proyecto fuera del Project
    for i in act.issues.values():
        if i["node_id"] not in act.items:
            hallazgos.append(f"FUERA DEL PROJECT: #{i['number']} {i['title']}")
            if corregir:
                ej.item_del_project(i)
    if corregir:
        leer_items(gh, act)

    # 3) Items sin campos (incluye el caso "Content already exists")
    obligatorios = ["Status", "Tipo", "Categoria", "Prioridad", "Fase"]
    pendientes = []
    for node, it in act.items.items():
        es_epica = clave(it["titulo"]).startswith("epica:")
        faltan = [c for c in obligatorios if not it["valores"].get(c) and not (es_epica and c == "Fase")]
        if not faltan:
            continue
        deseado = deseados_por_etiquetas(spec, it, act.campos)
        if es_epica:
            deseado.setdefault("Prioridad", "Alta")
        hallazgos.append(f"SIN CAMPOS {', '.join(faltan)}: #{it['numero']} {it['titulo']}")
        sin_dato = [c for c in faltan if c not in deseado]
        if sin_dato:
            hallazgos.append(f"   -> sin dato para {', '.join(sin_dato)}: lo define el PO")
        pendientes += ej.valores_pendientes(it["item_id"], it["valores"], {c: deseado[c] for c in faltan if c in deseado})
    if corregir and pendientes:
        ej.aplicar_valores(pendientes)
        leer_items(gh, act)

    # 4) Sub-issues faltantes
    for c in spec["categorias"]:
        epica = act.issues.get(clave(titulo_epica(c)))
        if not epica:
            hallazgos.append(f"FALTA LA EPICA: {titulo_epica(c)}")
            continue
        hijos = leer_sub_issues(gh, spec, epica["number"])
        act.sub_issues[epica["number"]] = hijos
        for i in act.issues.values():
            if i["number"] == epica["number"] or not ej._de_categoria(i, c) or i["id"] in hijos:
                continue
            if clave(i["title"]).startswith("epica:"):
                continue
            hallazgos.append(f"SUB-ISSUE FALTANTE: #{i['number']} no cuelga de #{epica['number']} ({c['nombre']})")
            if corregir:
                ej.enlazar_sub_issue(epica, i)

    # 5) Cerrados que no estan en Hecho (solo se reporta)
    for it in act.items.values():
        if it.get("estado") == "CLOSED" and it["valores"].get("Status") not in (None, "Hecho"):
            hallazgos.append(f"CERRADO PERO EN {it['valores'].get('Status')!r}: #{it['numero']} {it['titulo']}")

    info("\nVERIFICACION del Project " + act.project["url"])
    if hallazgos:
        for h in hallazgos:
            info(f"  - {h}")
        info("  (corregido)" if corregir else "  -> ejecutar 'verificar --corregir' para arreglar lo corregible")
    else:
        info("  Sin hallazgos: todos los items son issues reales, con campos completos y colgados de su epica.")
    info("\nConteos por campo:")
    filas = [{k: v.get("valores", {}).get(k) for k in ("Fase", "Categoria", "Status", "Tipo")}
             for v in act.items.values()]
    conteos = imprimir_conteos(filas)
    return {"hallazgos": hallazgos, "conteos": conteos}


# ---------------------------------------------------------------------------
# Espejo local
# ---------------------------------------------------------------------------

def generar_espejo(spec: dict, act: Actual, planificado: bool) -> str:
    label = spec["project_label"]
    url = act.project["url"] if act.project else "(Project aun no creado)"
    filas = []
    if planificado or not act.project:
        for it in spec["items"]:
            e = act.issues.get(clave(it["titulo"]))
            filas.append({"num": e["number"] if e else None, "url": e["html_url"] if e else None, "titulo": it["titulo"],
                          "Fase": sin_acentos(it["fase"]), "Categoria": sin_acentos(it["cat"]), "Tipo": it["tipo"],
                          "Prioridad": it["prio"], "Status": it["estado"]})
    else:
        for it in act.items.values():
            if clave(it["titulo"]).startswith("epica:"):
                continue
            filas.append({"num": it["numero"], "url": it.get("url"), "titulo": it["titulo"], **it["valores"]})
    lineas = [f"<!-- project-backlog:inicio {label} -->", f"## Project: {spec['project']}", "",
              f"- Project: {url}", f"- Repo de issues: `{spec['repo']}` · etiqueta `{label}`",
              f"- Actualizado: {ahora()} (generado; se regenera con `/dev-team:project espejo`)", "",
              "| Fase | Items | Hecho |", "|---|---|---|"]
    for f in spec["fases"]:
        de_f = [x for x in filas if clave(x.get("Fase") or "") == clave(f["opcion"])]
        lineas.append(f"| {f['nombre_largo']} | {len(de_f)} | {sum(1 for x in de_f if x.get('Status') == 'Hecho')} |")
    lineas += ["", "| Categoria | Items |", "|---|---|"]
    for c in spec["categorias"]:
        lineas.append(f"| {c['nombre']} | {sum(1 for x in filas if clave(x.get('Categoria') or '') == clave(c['opcion']))} |")
    lineas += ["", "### Condición de salida por fase"]
    lineas += [f"- **{f['nombre_largo']}**: {f['condicion_salida']}" for f in spec["fases"]]
    for f in spec["fases"]:
        lineas += ["", f"### {f['nombre_largo']}"]
        for x in sorted((x for x in filas if clave(x.get("Fase") or "") == clave(f["opcion"])),
                        key=lambda x: x["num"] or 10 ** 9):
            ref = f"[#{x['num']}]({x['url']})" if x["num"] else "(nuevo)"
            marca = "x" if x.get("Status") == "Hecho" else " "
            lineas.append(f"- [{marca}] {ref} {x['titulo']} — {x.get('Categoria') or '?'} · {x.get('Tipo') or '?'} · "
                          f"{x.get('Prioridad') or '?'} · {x.get('Status') or '?'}")
    sin_fase = [x for x in filas if not x.get("Fase")]
    if sin_fase:
        lineas += ["", "### Sin fase asignada (revisar con `verificar`)"]
        lineas += [f"- #{x['num']} {x['titulo']}" for x in sin_fase]
    lineas.append(f"<!-- project-backlog:fin {label} -->")
    return "\n".join(lineas) + "\n"


def escribir_espejo(ruta: Path, seccion: str, label: str) -> None:
    previo = ruta.read_text(encoding="utf-8") if ruta.is_file() else ""
    patron = re.compile(r"<!-- project-backlog:inicio " + re.escape(label) + r" -->.*?<!-- project-backlog:fin "
                        + re.escape(label) + r" -->\n?", re.S)
    if patron.search(previo):
        nuevo = patron.sub(lambda _m: seccion, previo, count=1)
    else:
        lineas = previo.splitlines(keepends=True)
        if lineas and lineas[0].startswith("# "):
            nuevo = lineas[0] + "\n" + seccion + "\n" + "".join(lineas[1:])
        else:
            nuevo = seccion + ("\n" + previo if previo else "")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(nuevo, encoding="utf-8")


def resolver_backlog(explicita: str | None) -> Path | None:
    if explicita:
        p = Path(explicita).expanduser().resolve()
        if dentro_de_git(p.parent):
            raise ErrorSpec(f"--backlog {p} cae dentro de un repo git; la coordinacion nunca se escribe en un repo.")
        return p
    c = buscar_coordination(Path.cwd().resolve(), canonica=True)
    return c / "backlog.md" if c else None


def registrar_config(backlog: Path | None, spec: dict, act: Actual, avisos: list[str]) -> None:
    """Registra el Project en .coordination/config.json -> tracker (merge, sin pisar lo demas)."""
    if not backlog:
        return
    cfg_path = backlog.parent / "config.json"
    if not cfg_path.is_file():
        return
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        avisos.append(f"no pude leer {cfg_path}: {e}")
        return
    tracker = cfg.setdefault("tracker", {})
    if tracker.get("provider") not in (None, "", "github"):
        avisos.append(f"tracker.provider es {tracker.get('provider')!r}; no se registro el Project en config.json")
        return
    tracker["provider"] = "github"
    gh_cfg = tracker.setdefault("github", {})
    gh_cfg.update({"org": spec["org"], "repo": spec["repo"], "project": spec["project"],
                   "projectNumber": act.project["number"], "projectUrl": act.project["url"],
                   "projectLabel": spec["project_label"]})
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Subcomandos
# ---------------------------------------------------------------------------

def cmd_aplicar(args) -> int:
    spec, avisos = cargar_spec(args.spec)
    gh = Gh(dry_run=args.dry_run, offline=args.offline)
    ruta = resolver_estado(spec["project"], args.estado)
    backlog = None if args.sin_espejo else resolver_backlog(args.backlog)
    act, avisos_gh = descubrir(gh, spec)
    avisos += avisos_gh
    if args.dry_run:
        imprimir_plan(spec, act, ruta, avisos, backlog)
        return 0
    estado = Estado(ruta, escribir=True)
    estado.datos["spec"] = {k: v for k, v in json.loads(Path(args.spec).read_text(encoding="utf-8")).items()}
    ej = Ejecutor(gh, spec, act, estado, args.pausa)
    info(f"Estado/resultado: {ruta}")
    ej.project()
    ej.campos_project()
    ej.etiquetas()
    ej.milestones()
    epicas = ej.epicas()
    ej.items(epicas)
    ej.cuerpos_epicas(epicas)
    ej.vistas()
    resultado = verificar(gh, spec, act, corregir=True, ej=ej)
    estado.datos["verificacion"] = resultado
    estado.guardar()
    if backlog:
        escribir_espejo(backlog, generar_espejo(spec, act, planificado=False), spec["project_label"])
        registrar_config(backlog, spec, act, ej.avisos)
    info("\n" + "=" * 72)
    info(f"LISTO  {act.project['url']}")
    info(f"  issues creados: {ej.creados['issues']} · reutilizados: {ej.creados['reutilizados']} · "
         f"sub-issues enlazados: {ej.creados['sub_issues']} · cerrados como Hecho: {ej.creados['cerrados']} · "
         f"valores de campo fijados: {ej.creados['campos']}")
    ejemplos = [i["titulo"] for i in spec["items"]][:5]
    info("  Ejemplos: " + " | ".join(ejemplos))
    info(f"  Estado: {ruta}" + (f" · Espejo: {backlog}" if backlog else ""))
    info("  PENDIENTE MANUAL: en cada vista marcar el agrupamiento en la interfaz (Group by Status / Fase / "
         "Categoria; el roadmap por Fase). La API no lo permite.")
    for a in avisos + ej.avisos:
        info(f"  ! {a}")
    return 0


def cmd_verificar(args) -> int:
    spec, avisos = cargar_spec(args.spec)
    gh = Gh(dry_run=not args.corregir, offline=False)
    act, avisos_gh = descubrir(gh, spec)
    ej = None
    if args.corregir:
        estado = Estado(resolver_estado(spec["project"], args.estado), escribir=True)
        ej = Ejecutor(gh, spec, act, estado, 0.5)
    r = verificar(gh, spec, act, corregir=args.corregir, ej=ej)
    for a in avisos_gh + (ej.avisos if ej else []):
        info(f"  ! {a}")
    return 1 if r["hallazgos"] and not args.corregir else 0


def cmd_espejo(args) -> int:
    spec, _ = cargar_spec(args.spec)
    gh = Gh(dry_run=True, offline=args.offline)
    act, _ = descubrir(gh, spec)
    seccion = generar_espejo(spec, act, planificado=args.offline or not act.project)
    backlog = resolver_backlog(args.backlog)
    if args.dry_run or args.offline or not backlog:
        info(seccion)
        if not backlog:
            info("(no se encontro .coordination/; indicar --backlog RUTA para escribirlo)")
        return 0
    escribir_espejo(backlog, seccion, spec["project_label"])
    info(f"Espejo actualizado: {backlog}")
    return 0


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="project_backlog.py",
        description="Crea, completa, verifica y refleja un backlog profesional en un GitHub Project v2 "
                    "a partir de UN spec JSON. Idempotente: re-ejecutarlo no duplica nada.",
        epilog=(
            "Ejemplos:\n"
            "  project_backlog.py aplicar spec.json --dry-run            # plan con lecturas de GitHub\n"
            "  project_backlog.py aplicar spec.json --dry-run --offline  # plan sin llamar a gh\n"
            "  project_backlog.py aplicar spec.json                      # ejecutar (con OK del usuario)\n"
            "  project_backlog.py verificar spec.json [--corregir]\n"
            "  project_backlog.py espejo spec.json [--dry-run]\n\n"
            "El formato del spec y las reglas estan en el docstring del script y en la skill\n"
            "github-project-backlog (SKILL.md). Ejemplo: assets/spec-ejemplo.json."),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True, metavar="{aplicar,verificar,espejo}")

    a = sub.add_parser("aplicar", help="crear o completar el Project desde el spec (crear / agregar)")
    a.add_argument("spec", help="ruta al spec JSON")
    a.add_argument("--dry-run", action="store_true", help="solo imprimir el plan; ninguna escritura")
    a.add_argument("--offline", action="store_true", help="con --dry-run: no llamar a gh (asume que nada existe)")
    a.add_argument("--estado", metavar="RUTA", help="archivo de estado/resultado (nunca dentro de un repo git)")
    a.add_argument("--backlog", metavar="RUTA", help="backlog.md del espejo local (por defecto .coordination/backlog.md)")
    a.add_argument("--sin-espejo", action="store_true", help="no tocar el backlog.md local ni config.json")
    a.add_argument("--pausa", type=float, default=1.0, help="segundos entre creaciones de issues (default 1.0)")
    a.set_defaults(func=cmd_aplicar)

    v = sub.add_parser("verificar", help="detectar (y con --corregir arreglar) problemas del Project")
    v.add_argument("spec", help="ruta al spec JSON (org, repo, project, fases, categorias; items opcional)")
    v.add_argument("--corregir", action="store_true", help="arreglar lo corregible (escribe en GitHub)")
    v.add_argument("--estado", metavar="RUTA", help="archivo de estado (nunca dentro de un repo git)")
    v.set_defaults(func=cmd_verificar)

    e = sub.add_parser("espejo", help="regenerar la seccion del Project en .coordination/backlog.md")
    e.add_argument("spec", help="ruta al spec JSON")
    e.add_argument("--dry-run", action="store_true", help="imprimir la seccion sin escribirla")
    e.add_argument("--offline", action="store_true", help="armar la seccion solo desde el spec, sin gh")
    e.add_argument("--backlog", metavar="RUTA", help="ruta del backlog.md")
    e.set_defaults(func=cmd_espejo)
    return p


def main(argv=None) -> int:
    args = construir_parser().parse_args(argv)
    if getattr(args, "offline", False) and args.cmd == "aplicar" and not args.dry_run:
        info("ERROR: --offline solo tiene sentido junto con --dry-run.")
        return 2
    if not getattr(args, "offline", False) and not shutil.which("gh"):
        info("ERROR: falta GitHub CLI (gh). Ejecutar /dev-team:setup.")
        return 2
    try:
        return args.func(args)
    except ErrorSpec as e:
        info(f"ERROR: {e}")
        return 2
    except GhError as e:
        info(f"ERROR de GitHub (se puede re-ejecutar: es idempotente y reanuda): {e}")
        return 3
    except KeyboardInterrupt:
        info("Interrumpido. Re-ejecutar el mismo comando reanuda sin duplicar.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
