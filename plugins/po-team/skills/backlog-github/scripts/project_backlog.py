#!/usr/bin/env python3
"""Backlog del Product Owner en un GitHub Project v2 con el ciclo FaaST (po-team).

Lo usa el comando /po-team:tablero crear-backlog (skill backlog-github). Autosuficiente:
solo Python 3 (biblioteca estandar) + GitHub CLI (`gh`) autenticado con scope `project`.
No depende de dev-team.

SUBCOMANDOS
  crear SPEC       Crea el Project (o, con --reutilizar, usa el que ya existe con el mismo
                   nombre exacto) y lo deja listo: Status con las opciones del ciclo FaaST
                   (FUSIONADAS conservando los ids existentes: nunca se pierde el estado de
                   un item), campos Prioridad, Puntos (numero), Sprint (iteracion; si la API
                   lo rechaza, seleccion simple Sprint 1..N), Fecha Demo, Fecha Preprod y
                   Fecha VB cliente (fecha), repos vinculados, vistas, epicas e items
                   opcionales, espejo local y registro en .po-team/config.json.
  agregar SPEC     Lo mismo sobre un Project que YA existe (falla si no existe): suma items,
                   epicas, opciones o campos que falten. Idempotente.
  verificar SPEC   Revisa el Project real: opciones del ciclo y campos faltantes, borradores,
                   items sin Status, issues del backlog fuera del Project, sub-issues
                   faltantes, items con un Status fuera del ciclo. Con --corregir arregla lo
                   corregible (sin borrar ni pisar nada).
  espejo SPEC      Regenera la seccion del Project en .po-team/backlog.md.
  (aplicar = alias de crear, por compatibilidad con dev-team)

MODO PRUEBA
  --dry-run        Imprime el plan (crear / reutilizar / actualizar) SIN ninguna escritura:
                   ni en GitHub ni en disco. Solo hace lecturas con gh.
  --offline        Junto con --dry-run: no llama a gh en absoluto (asume que nada existe y
                   que el Project nuevo trae el Status por defecto Todo / In Progress / Done).

FORMATO DEL SPEC (JSON, UTF-8) — todo opcional salvo "project"; lo que falta sale del config
  {
    "org": "mi-org",                     # defecto: tracker.github.org
    "repo": "repo-de-hus",               # repo de issues; defecto tracker.github.repoDefault
    "repos": ["repo-a", "repo-b"],       # repos a vincular; defecto tracker.github.repos
    "project": "Backlog Equipo X",       # nombre EXACTO del Project
    "alias": "backlog",                  # alias en config (tracker.github.projects[].alias)
    "project_label": "BacklogEquipoX",   # etiqueta de los issues que crea este script
    "status_opciones": ["No iniciado", {"nombre": "En QA", "color": "PURPLE",
                        "descripcion": "..."}],   # defecto: ciclo del config o el FaaST
    "etapas": {"desarrollo": ["No iniciado", "..."], "...": []},  # solo con status_opciones propias
    "campos": {"puntos": "Puntos", "sprint": "Sprint", "prioridad": "Prioridad",
               "fechaDemo": "Fecha Demo", "fechaPreprod": "Fecha Preprod",
               "fechaVB": "Fecha VB cliente"},       # "" desactiva ese campo
    "prioridades": ["Alta", "Media", "Baja"],
    "sprint": {"via": "iteration|select|milestone", "inicio": "2026-11-02",
               "duracion_dias": 14, "cantidad": 4},
    "vistas": true,
    "agregar_abiertos": false,           # agrega los issues abiertos de los repos vinculados
    "epicas": [ {"nombre": "Autogestion del cliente", "descripcion": "..."} ],
    "items": [
      {"titulo": "...", "body": "markdown de negocio", "tipo": "Historia|Bug|Tarea",
       "epica": "nombre de epica", "estado": "No iniciado", "prio": "Alta",
       "puntos": 3, "sprint": 1, "fechaDemo": "2026-11-20", "fechaPreprod": "",
       "fechaVB": "", "etiquetas": ["cliente:ACME"]}
    ]
  }

UBICACION (nunca dentro de un repo git)
  Carpeta canonica `.po-team/` resuelta con plugins/po-team/hooks/coord_root.py (registro
  ~/.claude/po-team.config.json, puntero, subida de directorios) o, si no esta, subiendo desde
  el cwd hasta una `.po-team/config.json` fuera de repos. Estado: `.po-team/project-state/
  <nombre>.json`; sin `.po-team/`, `~/.po-team/project-state/`. `--po-team DIR` y `--estado RUTA`
  la fijan a mano y se rechazan si caen dentro de un repo git.

GARANTIAS
  - GraphQL siempre con VARIABLES (cuerpo JSON por --input); nunca se interpolan textos.
  - Reintentos con espera creciente ante errores transitorios / rate limit; la creacion de
    issues no se reintenta a ciegas (antes de repetir busca si se creo).
  - Mutaciones en lotes chicos (maximo 5 alias por llamada).
  - Opciones de seleccion simple SIEMPRE fusionadas pasando el id de las existentes (si no, GitHub
    borra el valor de todos los items). Ninguna opcion existente se elimina.
  - Nunca modifica la configuracion de un campo de iteracion existente.
  - Nunca crea borradores, nunca borra ni renombra un Project, nunca crea repos.
  - En re-ejecuciones solo LLENA valores vacios: no pisa el Status que el equipo movio.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# Catalogos
# ---------------------------------------------------------------------------

# Ciclo FaaST por defecto: (nombre, color, descripcion de negocio)
STATUS_DEFECTO = [
    ("No iniciado", "GRAY", "Listo para tomar; aun no empieza el desarrollo"),
    ("En desarrollo", "YELLOW", "El equipo de desarrollo lo esta construyendo"),
    ("Desarrollo terminado", "ORANGE", "Desarrollo lo dio por resuelto; espera QA"),
    ("En QA", "PURPLE", "QA lo esta validando"),
    ("Validado por QA", "BLUE", "QA lo aprobo con evidencia (lo mueve solo QA)"),
    ("Pase a Demo", "BLUE", "Listo o en curso el pase al ambiente Demo"),
    ("En validacion", "PURPLE", "El PO lo valida en Demo o Preprod del cliente"),
    ("Observado", "RED", "Devuelto con observaciones; vuelve a desarrollo"),
    ("Bloqueado", "RED", "Detenido por una dependencia o una decision"),
    ("VB cliente", "GREEN", "El cliente dio su visto bueno"),
]
# Mapeo del ciclo por defecto a las etapas del config.
ETAPAS_DEFECTO = [
    {"clave": "desarrollo", "nombre": "Desarrollo", "estados": ["No iniciado", "En desarrollo", "Desarrollo terminado"], "etiquetas": []},
    {"clave": "qa", "nombre": "Validacion QA", "estados": ["En QA", "Validado por QA"], "etiquetas": []},
    {"clave": "demo", "nombre": "Pase a Demo", "estados": ["Pase a Demo"], "etiquetas": ["ambiente:demo"]},
    {"clave": "validacion", "nombre": "Validacion Demo / Preprod", "estados": ["En validacion"], "etiquetas": ["vb-po"]},
    {"clave": "vb", "nombre": "VB cliente", "estados": ["VB cliente"], "etiquetas": ["vb-cliente"]},
]
OBSERVADO_DEFECTO = ["Observado"]
BLOQUEADO_DEFECTO = ["Bloqueado"]
REGLAS_DEFECTO = {"estadosSoloQA": ["Validado por QA"], "estadoAlResolver": "Desarrollo terminado"}

PRIORIDADES_DEFECTO = ["Alta", "Media", "Baja"]
COLOR_PRIO = {"alta": "RED", "media": "YELLOW", "baja": "GRAY"}
COLORES = ["BLUE", "GREEN", "YELLOW", "ORANGE", "RED", "PINK", "PURPLE", "GRAY"]

# Nombres de campos del config po-team (tracker.github.projects[].campos) -> nombre por defecto
CAMPOS_DEFECTO = {
    "estado": "Status", "puntos": "Puntos", "sprint": "Sprint", "prioridad": "Prioridad",
    "fechaDemo": "Fecha Demo", "fechaPreprod": "Fecha Preprod", "fechaVB": "Fecha VB cliente",
}
CAMPOS_FECHA = ("fechaDemo", "fechaPreprod", "fechaVB")

TIPOS = ["Historia", "Bug", "Tarea"]

LOTE_MAX = 5
LIMITE_ABIERTOS = 200
MARCA_EPICA_INI = "<!-- historias:inicio -->"
MARCA_EPICA_FIN = "<!-- historias:fin -->"

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
    norm = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in norm if not unicodedata.combining(c))


def clave(texto) -> str:
    return re.sub(r"\s+", " ", sin_acentos(str(texto or ""))).strip().lower()


def slug(texto: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", clave(texto)).strip("-")
    return s or "project"


def es_placeholder(v) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip() or "{{" in v
    if isinstance(v, (list, tuple)):
        return not v or any(es_placeholder(x) for x in v)
    return False


def lotes(lista, n=LOTE_MAX):
    for i in range(0, len(lista), n):
        yield lista[i:i + n]


def ahora() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


def info(msg: str = "") -> None:
    print(msg, flush=True)


def fecha(valor: str, ref: str) -> str:
    try:
        return _dt.date.fromisoformat(str(valor).strip()).isoformat()
    except ValueError:
        raise ErrorSpec(f"{ref}: fecha {valor!r} invalida (formato AAAA-MM-DD)")


def proximo_lunes(hoy: _dt.date | None = None) -> str:
    hoy = hoy or _dt.date.today()
    return (hoy + _dt.timedelta(days=(7 - hoy.weekday()) % 7 or 7)).isoformat()


def corto(repo: str, org: str) -> str:
    return repo.split("/", 1)[1] if repo.lower().startswith(org.lower() + "/") else repo


class ErrorSpec(Exception):
    pass


class GhError(Exception):
    def __init__(self, mensaje: str, transitorio: bool = False):
        super().__init__(mensaje)
        self.transitorio = transitorio


# ---------------------------------------------------------------------------
# Ubicacion de .po-team y del estado (nunca dentro de un repo git)
# ---------------------------------------------------------------------------

def dentro_de_git(directorio: Path) -> bool:
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
    for p in [d, *d.parents]:
        if (p / ".git").exists():
            return True
    return False


def _po_team_plugin(inicio: Path) -> Path | None:
    """Resolvedor del plugin (hooks/coord_root.py). Devuelve la .po-team canonica FUERA de repos."""
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


def resolver_po_team(explicita: str | None) -> Path | None:
    if explicita:
        p = Path(explicita).expanduser().resolve()
        if p.name != ".po-team" and (p / ".po-team").is_dir():
            p = p / ".po-team"
        if dentro_de_git(p.parent):
            raise ErrorSpec(f"--po-team {p} cae dentro de un repo git; .po-team nunca vive en un repo.")
        return p
    inicio = Path.cwd().resolve()
    c = _po_team_plugin(inicio)
    if c:
        return c
    for d in [inicio, *inicio.parents]:
        c = d / ".po-team"
        if (c / "config.json").is_file() and not dentro_de_git(d):
            return c
    return None


def cargar_config(po_dir: Path | None) -> dict:
    if not po_dir or not (po_dir / "config.json").is_file():
        return {}
    try:
        return json.loads((po_dir / "config.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ErrorSpec(f"No pude leer {po_dir / 'config.json'}: {e}")


def resolver_estado(nombre_project: str, explicita: str | None, po_dir: Path | None) -> Path:
    if explicita:
        p = Path(explicita).expanduser().resolve()
        if dentro_de_git(p.parent):
            raise ErrorSpec(f"--estado {p} cae dentro de un repo git; el estado nunca se guarda en un repo.")
        return p
    base = po_dir / "project-state" if po_dir else Path.home() / ".po-team" / "project-state"
    return base / f"{slug(nombre_project)}.json"


def escribir_atomico(ruta: Path, texto: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_name(ruta.name + ".tmp")
    tmp.write_text(texto, encoding="utf-8")
    os.replace(tmp, ruta)


class Estado:
    def __init__(self, ruta: Path, escribir: bool):
        self.ruta, self.escribir, self.datos = ruta, escribir, {}
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
        escribir_atomico(self.ruta, json.dumps(self.datos, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------------------
# Cliente gh (lecturas, escrituras, reintentos)
# ---------------------------------------------------------------------------

class Gh:
    def __init__(self, dry_run: bool, offline: bool, intentos: int = 5, espera: float = 3.0):
        self.dry_run, self.offline, self.intentos, self.espera = dry_run, offline, intentos, espera
        self.escrituras = 0

    def _run(self, args: list[str], stdin: str | None, escritura: bool, reintentar: bool = True) -> str:
        if self.offline:
            raise RuntimeError("BUG: llamada a gh en modo --offline")
        if escritura and self.dry_run:
            raise RuntimeError("BUG: intento de escritura en modo --dry-run (bloqueado)")
        espera, ultimo = self.espera, ""
        for intento in range(1, (self.intentos if reintentar else 1) + 1):
            try:
                r = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True, timeout=180)
            except subprocess.TimeoutExpired:
                r, ultimo = None, "timeout ejecutando gh"
            if r is not None:
                if r.returncode == 0:
                    if escritura:
                        self.escrituras += 1
                    return r.stdout
                ultimo = (r.stderr or "").strip() or (r.stdout or "").strip()
                if args[:2] == ["api", "graphql"] and r.stdout.strip().startswith("{"):
                    try:
                        cuerpo = json.loads(r.stdout)
                    except json.JSONDecodeError:
                        cuerpo = None
                    if cuerpo is not None:
                        msgs = " | ".join(e.get("message", "") for e in cuerpo.get("errors", []))
                        if not TRANSITORIO.search(msgs) and not TRANSITORIO.search(ultimo):
                            return r.stdout
                        ultimo = msgs or ultimo
            if not TRANSITORIO.search(ultimo) or intento == self.intentos or not reintentar:
                raise GhError(ultimo[:600], transitorio=bool(TRANSITORIO.search(ultimo)))
            pausa = max(espera, 60.0) if re.search(r"secondary|abuse|too quickly", ultimo, re.I) else espera
            info(f"   ... error transitorio ({ultimo[:90]}); reintento {intento}/{self.intentos - 1} en {pausa:.0f}s")
            time.sleep(pausa)
            espera *= 2
        raise GhError(ultimo[:600])

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
# Spec (+ valores por defecto desde .po-team/config.json)
# ---------------------------------------------------------------------------

def _como_lista(valor, campo_desc: str) -> list[dict]:
    if isinstance(valor, dict):
        salida = []
        for nombre, v in valor.items():
            d = dict(v) if isinstance(v, dict) else {campo_desc: v}
            d["nombre"] = nombre
            salida.append(d)
        return salida
    return [dict(x) if isinstance(x, dict) else {"nombre": str(x)} for x in (valor or [])]


def _buscar(opciones: list[str], valor) -> str | None:
    for o in opciones:
        if clave(o) == clave(valor):
            return o
    return None


def status_desde_config(cfg: dict) -> list[str] | None:
    """Estados del ciclo en orden: etapas (salvo la ultima), Observado, Bloqueado, ultima etapa.
    None si el config no tiene ciclo o aun tiene valores de ejemplo {{...}}."""
    ciclo = cfg.get("ciclo") or {}
    etapas = ciclo.get("etapas") or []
    if not etapas:
        return None
    grupos = [list(e.get("estados") or []) for e in etapas]
    obs, blq = list(ciclo.get("estadosObservado") or []), list(ciclo.get("estadosBloqueado") or [])
    todos = [s for g in grupos for s in g] + obs + blq
    if not todos or any(es_placeholder(s) for s in todos):
        return None
    orden = [s for g in grupos[:-1] for s in g] + obs + blq + grupos[-1]
    vistos, salida = set(), []
    for s in orden:
        if clave(s) not in vistos:
            vistos.add(clave(s))
            salida.append(s.strip())
    return salida


def _opcion_status(nombre: str, i: int) -> tuple[str, str, str]:
    for n, c, d in STATUS_DEFECTO:
        if clave(n) == clave(nombre):
            return (nombre, c, d)
    return (nombre, COLORES[i % len(COLORES)], "")


def cargar_spec(ruta: str, cfg: dict) -> tuple[dict, list[str]]:
    try:
        spec = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ErrorSpec(f"No pude leer el spec {ruta}: {e}")
    errores, avisos = [], []
    gcfg = ((cfg.get("tracker") or {}).get("github") or {})
    proveedor = (cfg.get("tracker") or {}).get("provider")
    if proveedor and not es_placeholder(proveedor) and proveedor != "github":
        raise ErrorSpec(f"tracker.provider es {proveedor!r}: este backlog es para GitHub Projects; "
                        "en Azure DevOps el backlog se crea en Boards (/po-team:setup tracker).")

    def defecto(k_spec, k_cfg):
        v = spec.get(k_spec)
        if es_placeholder(v):
            v = gcfg.get(k_cfg)
        return None if es_placeholder(v) else v

    org = defecto("org", "org")
    repo = defecto("repo", "repoDefault")
    if not org:
        errores.append("falta 'org' (ni en el spec ni en tracker.github.org)")
    if not repo:
        errores.append("falta 'repo' (repo de issues; ni en el spec ni en tracker.github.repoDefault)")
    if es_placeholder(spec.get("project")):
        errores.append("falta 'project' (nombre exacto del Project)")
    if errores:
        raise ErrorSpec("Spec invalido: " + "; ".join(errores))
    org = str(org).strip()
    repo = str(repo).strip()
    repo = repo if "/" in repo else f"{org}/{repo}"
    repos_src = spec.get("repos")
    if es_placeholder(repos_src):
        repos_src = [r for r in (gcfg.get("repos") or []) if not es_placeholder(r)]
    repos = []
    for r in [repo, *(repos_src or [])]:
        r = str(r).strip()
        r = r if "/" in r else f"{org}/{r}"
        if r.lower() not in [x.lower() for x in repos]:
            repos.append(r)
    spec.update(org=org, repo=repo, repos=repos, project=str(spec["project"]).strip())
    spec["project_label"] = sin_acentos(str(spec.get("project_label") or spec["project"]).strip())
    spec["alias"] = str(spec.get("alias") or "").strip() or ("backlog" if not any(
        not es_placeholder(p.get("titulo")) for p in gcfg.get("projects") or []) else slug(spec["project"]))
    spec.setdefault("vistas", True)
    spec["agregar_abiertos"] = bool(spec.get("agregar_abiertos", False))

    # --- Campos (nombres configurables; "" desactiva) ---
    campos = dict(CAMPOS_DEFECTO)
    for k, v in (spec.get("campos") or {}).items():
        if k in campos:
            campos[k] = sin_acentos(str(v or "")).strip() if k != "estado" else "Status"
    campos["estado"] = "Status"
    spec["campos"] = campos

    # --- Status del ciclo ---
    propias = spec.get("status_opciones")
    if propias:
        lista = []
        for i, o in enumerate(propias):
            if isinstance(o, dict):
                n = str(o.get("nombre") or o.get("name") or "").strip()
                base = _opcion_status(n, i)
                lista.append((n, str(o.get("color") or base[1]).upper(), str(o.get("descripcion") or base[2])))
            else:
                lista.append(_opcion_status(str(o).strip(), i))
        origen = "spec"
    else:
        desde_cfg = status_desde_config(cfg)
        if desde_cfg:
            lista, origen = [_opcion_status(s, i) for i, s in enumerate(desde_cfg)], "config"
        else:
            lista, origen = list(STATUS_DEFECTO), "defecto"
            if cfg.get("ciclo"):
                avisos.append("el config aun tiene el ciclo de ejemplo ({{...}}): se usa el ciclo FaaST por defecto")
    lista = [(n, c if c in COLORES else "GRAY", d[:100]) for n, c, d in lista if n]
    if not lista:
        raise ErrorSpec("status_opciones quedo vacio")
    spec["status"] = lista
    spec["status_origen"] = origen
    nombres_status = [s[0] for s in lista]

    # --- Prioridades ---
    prios = [str(p).strip() for p in (spec.get("prioridades") or PRIORIDADES_DEFECTO) if str(p).strip()]
    spec["prioridades"] = prios

    # --- Sprint ---
    sp = dict(spec.get("sprint") or {})
    via = str(sp.get("via") or "iteration").strip().lower()
    if via not in ("iteration", "select", "milestone"):
        raise ErrorSpec(f"sprint.via {via!r} invalido (iteration | select | milestone)")
    if not campos["sprint"] and via != "milestone":
        via = "ninguno"
    habiles = (cfg.get("capacidad") or {}).get("duracionSprintDias")
    dur_def = round(habiles * 7 / 5) if isinstance(habiles, (int, float)) and habiles > 0 else 14
    sp["via"] = via
    sp["duracion_dias"] = int(sp.get("duracion_dias") or dur_def)
    sp["cantidad"] = int(sp.get("cantidad") or 4)
    sp["inicio"] = fecha(sp["inicio"], "sprint.inicio") if sp.get("inicio") else proximo_lunes()
    if sp["duracion_dias"] < 1 or sp["cantidad"] < 1:
        raise ErrorSpec("sprint.duracion_dias y sprint.cantidad deben ser >= 1")
    if _dt.date.fromisoformat(sp["inicio"]).weekday() != 0:
        avisos.append(f"sprint.inicio {sp['inicio']} no es lunes")
    ini = _dt.date.fromisoformat(sp["inicio"])
    sp["iteraciones"] = [{"title": f"Sprint {n + 1}",
                          "startDate": (ini + _dt.timedelta(days=n * sp["duracion_dias"])).isoformat(),
                          "duration": sp["duracion_dias"]} for n in range(sp["cantidad"])]
    spec["sprint"] = sp
    nombres_sprint = [x["title"] for x in sp["iteraciones"]]

    # --- Epicas ---
    epicas = _como_lista(spec.get("epicas"), "descripcion")
    for e in epicas:
        e["nombre"] = str(e.get("nombre") or "").strip()
        e.setdefault("descripcion", "")
        if not e["nombre"]:
            errores.append("epica sin 'nombre'")
    spec["epicas"] = epicas
    nombres_epica = [e["nombre"] for e in epicas]

    # --- Items ---
    est = cfg.get("estimacion") or {}
    escala = [x for x in (est.get("escala") or [1, 2, 3, 5, 8, 13]) if isinstance(x, (int, float))]
    maximo = est.get("maximoEnSprint") if isinstance(est.get("maximoEnSprint"), (int, float)) else None
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
        it["tipo"] = _buscar(TIPOS, it.get("tipo") or "Historia") or errores.append(
            f"{ref}: tipo {it.get('tipo')!r} invalido ({', '.join(TIPOS)})") or "Historia"
        valor = it.get("estado") or nombres_status[0]
        it["estado"] = _buscar(nombres_status, valor) or errores.append(
            f"{ref}: estado {valor!r} no esta en el ciclo ({', '.join(nombres_status)})") or valor
        if it.get("prio"):
            it["prio"] = _buscar(prios, it["prio"]) or errores.append(
                f"{ref}: prio {it['prio']!r} invalida ({', '.join(prios)})") or it["prio"]
            if not campos["prioridad"]:
                avisos.append(f"{ref}: trae prio pero el campo Prioridad esta desactivado")
        if it.get("epica"):
            it["epica"] = _buscar(nombres_epica, it["epica"]) or errores.append(
                f"{ref}: epica {it['epica']!r} no esta en 'epicas'") or it["epica"]
        if it.get("puntos") not in (None, ""):
            try:
                it["puntos"] = float(it["puntos"])
            except (TypeError, ValueError):
                errores.append(f"{ref}: puntos {it['puntos']!r} no es un numero")
                it["puntos"] = None
            if it["puntos"] is not None:
                if escala and it["puntos"] not in escala:
                    avisos.append(f"{ref}: {it['puntos']:g} puntos fuera de la escala {escala}")
                if maximo and it.get("sprint") and it["puntos"] > maximo:
                    avisos.append(f"{ref}: {it['puntos']:g} puntos supera el maximo por sprint ({maximo}); dividir la HU")
        else:
            it["puntos"] = None
        if it.get("sprint") not in (None, ""):
            s = it["sprint"]
            nombre = f"Sprint {s}" if isinstance(s, int) or str(s).strip().isdigit() else str(s).strip()
            it["sprint"] = _buscar(nombres_sprint, nombre) or errores.append(
                f"{ref}: sprint {s!r} fuera de los {len(nombres_sprint)} sprints del spec") or nombre
            if via == "ninguno":
                avisos.append(f"{ref}: trae sprint pero el campo Sprint esta desactivado")
        else:
            it["sprint"] = None
        for k in CAMPOS_FECHA:
            if it.get(k):
                try:
                    it[k] = fecha(it[k], ref)
                except ErrorSpec as e:
                    errores.append(str(e))
            else:
                it[k] = None
        it["body"] = str(it.get("body") or "").strip()
        if not it["body"]:
            avisos.append(f"{ref}: cuerpo vacio (el PO debe redactarlo)")
        if JERGA.search(it["titulo"]):
            avisos.append(f"{ref}: el TITULO suena tecnico ({JERGA.search(it['titulo']).group(0)!r}); reescribir en lenguaje de negocio")
        elif JERGA.search(it["body"]):
            avisos.append(f"{ref}: el cuerpo menciona {JERGA.search(it['body']).group(0)!r}; revisar lenguaje de negocio")
        if it["tipo"] == "Historia" and not (re.search(r"\bdado\b", it["body"], re.I)
                                             and re.search(r"\bentonces\b", it["body"], re.I)):
            avisos.append(f"{ref}: historia sin criterios Dado / Cuando / Entonces")
    spec["items"] = items
    if errores:
        raise ErrorSpec("Spec invalido:\n  - " + "\n  - ".join(errores))
    return spec, avisos


def etiquetas_tipo(cfg: dict) -> dict[str, str]:
    e = ((cfg.get("tracker") or {}).get("etiquetas") or {})
    hu = e.get("hu") if not es_placeholder(e.get("hu")) else "historia-usuario"
    bug = e.get("bug") if not es_placeholder(e.get("bug")) else "bug"
    return {"Historia": hu, "Bug": bug, "Tarea": "tarea", "Epica": "epica"}


def usa_issues(spec: dict) -> bool:
    return bool(spec["items"] or spec["epicas"])


def titulo_epica(e: dict) -> str:
    return f"Épica: {e['nombre']}"


def opciones_select(spec: dict, via_sprint: str | None = None) -> dict[str, list[tuple[str, str, str]]]:
    """Campos de seleccion simple deseados: nombre real -> [(opcion, color, descripcion)]."""
    c = spec["campos"]
    salida = {"Status": spec["status"]}
    if c["prioridad"]:
        salida[c["prioridad"]] = [(p, COLOR_PRIO.get(clave(p), COLORES[i % len(COLORES)]), "")
                                  for i, p in enumerate(spec["prioridades"])]
    if (via_sprint or spec["sprint"]["via"]) == "select":
        salida[c["sprint"]] = [(x["title"], "BLUE", f"Desde {x['startDate']} ({x['duration']} dias)")
                               for x in spec["sprint"]["iteraciones"]]
    return salida


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
    ... on ProjectV2IterationField { id name dataType configuration{ duration startDay
        iterations{ id title startDate duration } completedIterations{ id title startDate duration } } }
    ... on ProjectV2SingleSelectField { id name dataType options{ id name color description } } } }
  views(first:50){ nodes{ id name number layout filter } }
} } }"""

Q_ITEMS = """
query($id:ID!,$after:String){ node(id:$id){ ... on ProjectV2 {
  items(first:100, after:$after){
    pageInfo{ hasNextPage endCursor }
    nodes{ id type isArchived
      content{ __typename
        ... on Issue { id databaseId number title state url repository{ nameWithOwner }
                       milestone{ title } labels(first:40){ nodes{ name } } }
        ... on DraftIssue { id title }
        ... on PullRequest { id number title url } }
      fieldValues(first:40){ nodes{
        ... on ProjectV2ItemFieldSingleSelectValue { name field{ ... on ProjectV2SingleSelectField { name } } }
        ... on ProjectV2ItemFieldNumberValue { number field{ ... on ProjectV2Field { name } } }
        ... on ProjectV2ItemFieldDateValue { date field{ ... on ProjectV2Field { name } } }
        ... on ProjectV2ItemFieldIterationValue { title field{ ... on ProjectV2IterationField { name } } } } }
    } } } } }"""


class Actual:
    """Lo que ya existe en GitHub (vacio en modo --offline)."""

    def __init__(self):
        self.owner_id: str | None = None
        self.repo_ids: dict[str, str] = {}       # org/repo (minusculas) -> node_id
        self.project: dict | None = None
        self.project_previo = False
        self.repos_enlazados: set[str] = set()
        self.campos: dict[str, dict] = {}         # nombre -> {id, dataType, options[] | configuration}
        self.vistas: list[dict] = []
        self.items: dict[str, dict] = {}          # node_id del contenido -> {...}
        self.borradores: list[dict] = []
        self.etiquetas: dict[str, str] = {}
        self.milestones: dict[str, dict] = {}
        self.issues: dict[str, dict] = {}         # clave(titulo) -> issue REST (con la etiqueta del backlog)
        self.sub_issues: dict[int, set[int]] = {}
        self.abiertos: list[dict] = []            # issues abiertos de los repos que no estan en el Project
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
    act.campos = {f["name"]: f for f in d["fields"]["nodes"] if f and f.get("name")}
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
                    for k in ("name", "number", "date", "title"):
                        if k in v:
                            valores[v["field"]["name"]] = v[k]
                            break
            c = n.get("content") or {}
            if n["type"] == "DRAFT_ISSUE":
                act.borradores.append({"item_id": n["id"], "titulo": c.get("title", ""), "valores": valores})
            elif c.get("__typename") == "Issue":
                act.items[c["id"]] = {
                    "item_id": n["id"], "valores": valores, "numero": c["number"], "titulo": c["title"],
                    "estado": c["state"], "url": c["url"], "repo": c["repository"]["nameWithOwner"],
                    "db_id": c.get("databaseId"), "etiquetas": [x["name"] for x in c["labels"]["nodes"]],
                    "milestone": (c.get("milestone") or {}).get("title"),
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


def leer_abiertos(gh: Gh, spec: dict, act: Actual) -> None:
    act.abiertos = []
    for r in spec["repos"]:
        for i in gh.get(f"repos/{r}/issues", {"state": "open", "per_page": "100"}, paginar=True) or []:
            if "pull_request" not in i and i["node_id"] not in act.items:
                act.abiertos.append({"node_id": i["node_id"], "number": i["number"], "title": i["title"], "repo": r})


def descubrir(gh: Gh, spec: dict) -> tuple[Actual, list[str]]:
    act, avisos = Actual(), []
    if gh.offline:
        return act, ["modo --offline: no se consulto GitHub; el plan asume que NADA existe todavia"]
    auth = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    salida_auth = auth.stdout + auth.stderr
    if auth.returncode != 0:
        raise ErrorSpec("gh no esta autenticado (gh auth status). Correr /po-team:setup tracker; no se hace auth interactivo.")
    if not re.search(r"['\s,]project['\s,]", salida_auth):
        msg = "el token de gh no tiene scope 'project' (gh auth refresh -s project lo agrega; lo corre el usuario)"
        if not gh.dry_run:
            raise ErrorSpec(msg)
        avisos.append(msg)
    owner = gh.gql(Q_OWNER, {"login": spec["org"]}).get("repositoryOwner")
    if not owner:
        raise ErrorSpec(f"No existe la organizacion/usuario {spec['org']!r} o no hay acceso.")
    act.owner_id = owner["id"]
    for r in spec["repos"]:
        try:
            act.repo_ids[r.lower()] = gh.get(f"repos/{r}")["node_id"]
        except GhError as e:
            raise ErrorSpec(f"No existe el repo {r} o no hay acceso ({e}). Nunca se crean repos.")
    act.project = leer_project_por_titulo(gh, spec["org"], spec["project"])
    act.project_previo = bool(act.project)
    if act.project:
        leer_detalle_project(gh, act)
        leer_items(gh, act)
    if usa_issues(spec) or spec["sprint"]["via"] == "milestone":
        act.etiquetas = {clave(e["name"]): e["name"] for e in
                         json.loads(gh._run(["label", "list", "--repo", spec["repo"], "--limit", "1000",
                                             "--json", "name"], None, escritura=False) or "[]")}
        for m in gh.get(f"repos/{spec['repo']}/milestones", {"state": "all", "per_page": "100"}, paginar=True) or []:
            act.milestones[m["title"]] = {"number": m["number"], "description": m.get("description") or ""}
        leer_issues(gh, spec, act)
        for e in spec["epicas"]:
            ep = act.issues.get(clave(titulo_epica(e)))
            if ep:
                act.sub_issues[ep["number"]] = leer_sub_issues(gh, spec, ep["number"])
    if spec["agregar_abiertos"]:
        leer_abiertos(gh, spec, act)
    avisos += act.duplicados
    return act, avisos


# ---------------------------------------------------------------------------
# Fusion de opciones (la correccion clave: nunca perder valores)
# ---------------------------------------------------------------------------

def renombres_status(existentes: list[dict], deseadas) -> dict[str, dict]:
    """Opciones por defecto de GitHub que se RENOMBRAN conservando su id (y los valores de los
    items): Todo -> primer estado del ciclo, In Progress -> segundo, Done -> ultimo."""
    ex = {clave(o["name"]): o for o in existentes}
    nombres = [d[0] for d in deseadas]
    mapa = {"todo": nombres[0], "in progress": nombres[1] if len(nombres) > 1 else None, "done": nombres[-1]}
    salida, usados = {}, set()
    for viejo, nuevo in mapa.items():
        if not nuevo or viejo not in ex or clave(nuevo) in ex or clave(nuevo) in usados:
            continue
        if any(clave(n) == viejo for n in nombres):   # la opcion vieja ya es parte del ciclo
            continue
        salida[clave(nuevo)] = ex[viejo]
        usados.add(clave(nuevo))
    return salida


def fusionar_opciones(campo: str, existentes: list[dict], deseadas):
    """Devuelve (lista_para_mutacion, descripcion) o (None, None) si no hay cambios.

    - Cada opcion existente viaja CON SU id (sin id GitHub la recrea y borra el valor de
      todos los items que la tenian).
    - Ninguna opcion existente se elimina: las que el ciclo no usa se conservan al final.
    - En Status, las opciones por defecto de GitHub se renombran conservando el id."""
    ex = {clave(o["name"]): o for o in existentes}
    renombres = renombres_status(existentes, deseadas) if campo == "Status" else {}
    faltan = [d for d in deseadas if clave(d[0]) not in ex]
    if not faltan:
        return None, None
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
            desc.append(f"renombrar {o['name']} -> {nombre} (mismo id)")
        else:
            salida.append({"name": nombre, "color": color, "description": descripcion})
            desc.append(f"agregar {nombre}")
    extra = [o for o in existentes if o["id"] not in usados]
    for o in extra:
        salida.append({"id": o["id"], "name": o["name"], "color": o["color"], "description": o.get("description") or ""})
    if extra:
        desc.append("conservar " + ", ".join(o["name"] for o in extra))
    return salida, ", ".join(desc)


def campos_supuestos(act: Actual) -> dict[str, dict]:
    if act.project:
        return act.campos
    return {"Status": {"id": None, "dataType": "SINGLE_SELECT",
                       "options": [{"id": f"(def-{n})", "name": n, "color": "GRAY", "description": ""}
                                   for n in ("Todo", "In Progress", "Done")]}}


# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------

def imprimir_plan(spec: dict, cfg: dict, act: Actual, ruta_estado: Path, avisos: list[str], po_dir: Path | None,
                  modo: str) -> None:
    info("=" * 72)
    info("PLAN (modo prueba: no se escribe nada en GitHub ni en disco)")
    info("=" * 72)
    if act.project:
        info(f"[REUTILIZAR] Project #{act.project['number']} {spec['project']!r}  {act.project['url']}")
        if modo == "crear":
            info("             ! YA EXISTE un Project con ese nombre: CONFIRMAR con el usuario que se reutiliza")
            info("               (ejecutar con --reutilizar) o elegir otro nombre. Nunca se borra ni renombra.")
    else:
        info(f"[CREAR]      Project {spec['project']!r} en {spec['org']}")
    for r in spec["repos"]:
        ok = r.lower() in act.repos_enlazados
        info(f"  {'[OK]        ' if ok else '[VINCULAR]  '} repo {r}")
    info(f"             Repo de issues: {spec['repo']} · etiqueta del backlog: {spec['project_label']!r} · alias {spec['alias']!r}")
    info(f"             Estado/resultado: {ruta_estado}")
    info(f"             .po-team: {po_dir or '(no encontrada: no se escribira espejo ni config; usar --po-team)'}")

    info(f"\nCampos de seleccion (Status integrado: ciclo desde {spec['status_origen']}):")
    existentes = campos_supuestos(act)
    for campo, deseadas in opciones_select(spec, "iteration").items():
        actual = existentes.get(campo)
        nombres = " · ".join(d[0] for d in deseadas)
        etiqueta = "Status" if campo == "Status" else campo
        if not actual:
            info(f"  [CREAR]      {etiqueta} (seleccion): {nombres}")
            continue
        if actual.get("dataType") != "SINGLE_SELECT":
            info(f"  [CONFLICTO]  {etiqueta} existe como {actual.get('dataType')}; no se toca")
            continue
        _, desc = fusionar_opciones(campo, actual.get("options") or [], deseadas)
        info(f"  [ACTUALIZAR] {etiqueta}: {desc}" if desc else f"  [OK]         {etiqueta}: {nombres}")
        if campo == "Status" and desc:
            info("               (mutacion con el id de cada opcion existente: ningun item pierde su estado)")

    info("\nCampos del PO:")
    c = spec["campos"]
    for k, tipo in (("puntos", "NUMBER"), *((f, "DATE") for f in CAMPOS_FECHA)):
        if not c[k]:
            info(f"  [OMITIR]     {k} (desactivado en el spec)")
            continue
        actual = existentes.get(c[k])
        if not actual:
            info(f"  [CREAR]      {c[k]} ({tipo})")
        elif actual.get("dataType") == tipo:
            info(f"  [REUTILIZAR] {c[k]} ({tipo})")
        else:
            info(f"  [CONFLICTO]  {c[k]} existe como {actual.get('dataType')} (se esperaba {tipo}); no se llena")
    sp = spec["sprint"]
    rango = f"{len(sp['iteraciones'])} sprints de {sp['duracion_dias']} dias corridos desde {sp['inicio']}"
    if sp["via"] == "ninguno":
        info("  [OMITIR]     Sprint (desactivado)")
    elif sp["via"] == "milestone":
        for x in sp["iteraciones"]:
            m = act.milestones.get(x["title"])
            info(f"  {'[REUTILIZAR]' if m else '[CREAR]     '} milestone {x['title']} (desde {x['startDate']})")
    else:
        actual = existentes.get(c["sprint"])
        if actual and actual.get("dataType") == "ITERATION":
            its = [i["title"] for i in (actual.get("configuration") or {}).get("iterations") or []]
            info(f"  [REUTILIZAR] {c['sprint']} (ITERATION; iteraciones actuales: {', '.join(its) or 'ninguna'}; "
                 "no se modifica su configuracion)")
        elif actual and actual.get("dataType") == "SINGLE_SELECT":
            info(f"  [REUTILIZAR] {c['sprint']} como SELECCION (sprintVia=select)")
        elif actual:
            info(f"  [CONFLICTO]  {c['sprint']} existe como {actual.get('dataType')}; no se toca")
        elif sp["via"] == "iteration":
            info(f"  [CREAR]      {c['sprint']} (ITERATION): {rango}")
            info("               si la API rechaza la iteracion: seleccion simple Sprint 1..N y se avisa")
        else:
            info(f"  [CREAR]      {c['sprint']} (SELECCION): {rango}")
        for x in sp["iteraciones"]:
            info(f"                 {x['title']}: {x['startDate']} ({x['duration']} dias)")

    if usa_issues(spec):
        info("\nEtiquetas:")
        nuevas = [e for e in etiquetas_deseadas(spec, cfg) if clave(e[0]) not in act.etiquetas]
        info(f"  [CREAR]      {', '.join(e[0] for e in nuevas)}" if nuevas else "  [OK]         todas existen")
    if spec["epicas"]:
        info("\nEpicas:")
        for e in spec["epicas"]:
            ep = act.issues.get(clave(titulo_epica(e)))
            info(f"  {'[REUTILIZAR] #' + str(ep['number']) if ep else '[CREAR]     '} {titulo_epica(e)}")
    if spec["items"]:
        info("\nItems (issues reales, nunca borradores):")
        for it in spec["items"]:
            e = act.issues.get(clave(it["titulo"]))
            info(f"  {'[REUTILIZAR] #' + str(e['number']) if e else '[CREAR]     '} {it['titulo']}")
            det = [it["tipo"], it["estado"]]
            if it["puntos"] is not None:
                det.append(f"{it['puntos']:g} pts")
            det += [x for x in (it.get("sprint"), it.get("prio") and f"prio {it['prio']}",
                                it.get("epica") and f"epica {it['epica']}") if x]
            det += [f"{k} {it[k]}" for k in CAMPOS_FECHA if it.get(k)]
            info("                 " + " · ".join(det))
    if spec["agregar_abiertos"]:
        info("\nIssues abiertos de los repos vinculados:")
        if gh_offline_marker(act):
            info("  [AGREGAR]    (se cuentan al ejecutar con red; el plan offline no los ve)")
        else:
            n = len(act.abiertos)
            info(f"  [AGREGAR]    {n} issues abiertos que no estan en el Project (Status vacio -> {spec['status'][0][0]!r})")
            if n > LIMITE_ABIERTOS:
                info(f"               ! mas de {LIMITE_ABIERTOS}: pedir confirmacion aparte y ejecutar con --masivo")

    if spec["vistas"]:
        info("\nVistas (la API permite crearlas, nombrarlas, elegir layout, campos visibles y filtro):")
        nombres = {v["name"] for v in act.vistas}
        for nombre, layout, filtro in vistas_deseadas(spec, spec["sprint"]["via"]):
            f = f" filtro {filtro!r}" if filtro else ""
            info(f"  {'[OK]        ' if nombre in nombres else '[CREAR]     '} {nombre} ({layout}{f})")
        info("  MANUAL: el agrupamiento y el orden de cada vista NO se fijan por API (Group by / Sort by en la interfaz).")

    if spec["items"]:
        info("\nConteo planificado:")
        imprimir_conteos([{"Status": i["estado"], "Sprint": i.get("sprint"), "Tipo": i["tipo"], "puntos": i["puntos"]}
                          for i in spec["items"]])
    if avisos:
        info("\nAdvertencias:")
        for a in avisos:
            info(f"  ! {a}")
    info("\nNo se escribio nada. Para ejecutar: mismo comando sin --dry-run (requiere OK del usuario).")


def gh_offline_marker(act: Actual) -> bool:
    return act.owner_id is None


def imprimir_conteos(filas: list[dict]) -> dict:
    conteos = {}
    for campo in ("Status", "Sprint", "Tipo"):
        c: dict[str, int] = {}
        for f in filas:
            k = f.get(campo) or "(vacio)"
            c[k] = c.get(k, 0) + 1
        conteos[campo] = c
        info(f"  {campo:<8} " + " | ".join(f"{k}: {v}" for k, v in c.items()))
    pts = sum(f.get("puntos") or 0 for f in filas)
    sin = sum(1 for f in filas if f.get("puntos") in (None, ""))
    info(f"  Puntos   {pts:g} (sin estimar: {sin}) · Total items {len(filas)}")
    conteos["puntos"] = pts
    return conteos


def etiquetas_deseadas(spec: dict, cfg: dict) -> list[tuple[str, str, str]]:
    et = etiquetas_tipo(cfg)
    salida = [(spec["project_label"], "5319E7", f"Backlog del Project {sin_acentos(spec['project'])}"[:100])]
    tipos = {i["tipo"] for i in spec["items"]} | ({"Epica"} if spec["epicas"] else set())
    salida += [(et[t], {"Historia": "0E8A16", "Bug": "D73A4A", "Tarea": "BFBFBF", "Epica": "006B75"}[t], "") for t in sorted(tipos)]
    for it in spec["items"]:
        salida += [(sin_acentos(x), "EDEDED", "") for x in it.get("etiquetas") or []]
    vistos, unicos = set(), []
    for e in salida:
        if clave(e[0]) not in vistos:
            vistos.add(clave(e[0]))
            unicos.append(e)
    return unicos


def vistas_deseadas(spec: dict, via: str) -> list[tuple[str, str, str | None]]:
    s = spec["campos"]["sprint"]
    actual = f"{slug(s)}:@current" if via == "iteration" else None
    backlog = "no:milestone" if via == "milestone" else (f"no:{slug(s)}" if via in ("iteration", "select") else None)
    return [("Tablero", "BOARD_LAYOUT", None), ("Sprint actual", "TABLE_LAYOUT", actual),
            ("Backlog", "TABLE_LAYOUT", backlog)]


# ---------------------------------------------------------------------------
# Escrituras
# ---------------------------------------------------------------------------

M_CREAR_PROJECT = """mutation($o:ID!,$t:String!){ createProjectV2(input:{ownerId:$o,title:$t}){ projectV2{ id number title url } } }"""
M_ENLAZAR = """mutation($p:ID!,$r:ID!){ linkProjectV2ToRepository(input:{projectId:$p,repositoryId:$r}){ clientMutationId } }"""
M_CREAR_SELECT = """mutation($p:ID!,$n:String!,$o:[ProjectV2SingleSelectFieldOptionInput!]!){
  createProjectV2Field(input:{projectId:$p,dataType:SINGLE_SELECT,name:$n,singleSelectOptions:$o}){
    projectV2Field{ ... on ProjectV2SingleSelectField{ id name dataType options{ id name color description } } } } }"""
M_CREAR_SIMPLE = """mutation($p:ID!,$n:String!,$t:ProjectV2CustomFieldType!){
  createProjectV2Field(input:{projectId:$p,dataType:$t,name:$n}){
    projectV2Field{ ... on ProjectV2Field{ id name dataType } } } }"""
M_CREAR_ITERACION = """mutation($p:ID!,$n:String!,$c:ProjectV2IterationFieldConfigurationInput!){
  createProjectV2Field(input:{projectId:$p,dataType:ITERATION,name:$n,iterationConfiguration:$c}){
    projectV2Field{ ... on ProjectV2IterationField{ id name dataType configuration{ duration startDay
      iterations{ id title startDate duration } completedIterations{ id title startDate duration } } } } } }"""
M_ACT_SELECT = """mutation($f:ID!,$o:[ProjectV2SingleSelectFieldOptionInput!]!){
  updateProjectV2Field(input:{fieldId:$f,singleSelectOptions:$o}){
    projectV2Field{ ... on ProjectV2SingleSelectField{ id name dataType options{ id name color description } } } } }"""
M_AGREGAR_ITEM = """mutation($p:ID!,$c:ID!){ addProjectV2ItemById(input:{projectId:$p,contentId:$c}){ item{ id } } }"""
M_CREAR_VISTA = """mutation($p:ID!,$n:String!,$l:ProjectV2ViewLayout!){
  createProjectV2View(input:{projectId:$p,name:$n,layout:$l}){ projectV2View{ id name layout } } }"""
M_CREAR_VISTA_CFG = """mutation($p:ID!,$n:String!,$l:ProjectV2ViewLayout!,$v:[ID!]){
  createProjectV2View(input:{projectId:$p,name:$n,layout:$l,configuration:{visibleFieldIds:$v}}){ projectV2View{ id name layout } } }"""
M_ACT_VISTA = """mutation($v:ID!,$n:String!,$l:ProjectV2ViewLayout!){
  updateProjectV2View(input:{viewId:$v,name:$n,layout:$l}){ projectV2View{ id name layout } } }"""
M_FILTRO_VISTA = """mutation($v:ID!,$f:String!){ updateProjectV2View(input:{viewId:$v,filter:$f}){ projectV2View{ id filter } } }"""
M_CONVERTIR = """mutation($i:ID!,$r:ID!){ convertProjectV2DraftIssueItemToIssue(input:{itemId:$i,repositoryId:$r}){
  item{ id content{ ... on Issue{ id number title url } } } } }"""


def mapa_campo(f: dict) -> dict:
    """{id, tipo, opciones{clave: id}} de un campo leido de GitHub."""
    tipo = f.get("dataType")
    opciones = {}
    if tipo == "SINGLE_SELECT":
        opciones = {clave(o["name"]): o["id"] for o in f.get("options") or []}
    elif tipo == "ITERATION":
        cfg = f.get("configuration") or {}
        for i in (cfg.get("iterations") or []) + (cfg.get("completedIterations") or []):
            opciones[clave(i["title"])] = i["id"]
    return {"id": f["id"], "tipo": tipo, "opciones": opciones}


class Ejecutor:
    def __init__(self, gh: Gh, spec: dict, cfg: dict, act: Actual, estado: Estado, pausa: float):
        self.gh, self.spec, self.cfg, self.act, self.estado, self.pausa = gh, spec, cfg, act, estado, pausa
        self.repo = spec["repo"]
        self.avisos: list[str] = []
        self.campos: dict[str, dict] = {}          # nombre real -> mapa_campo
        self.via = spec["sprint"]["via"]           # via efectiva tras crear/reutilizar
        self.creados = {"issues": 0, "reutilizados": 0, "sub_issues": 0, "valores": 0, "agregados": 0}

    # --- Project y campos ---------------------------------------------------
    def project(self) -> None:
        if not self.act.project:
            d = self.gh.gql(M_CREAR_PROJECT, {"o": self.act.owner_id, "t": self.spec["project"]}, escritura=True)
            self.act.project = d["createProjectV2"]["projectV2"]
            info(f"Project creado #{self.act.project['number']}: {self.act.project['url']}")
            leer_detalle_project(self.gh, self.act)
        else:
            info(f"Project reutilizado #{self.act.project['number']}: {self.act.project['url']}")
        for r in self.spec["repos"]:
            if r.lower() in self.act.repos_enlazados:
                continue
            try:
                self.gh.gql(M_ENLAZAR, {"p": self.act.project["id"], "r": self.act.repo_ids[r.lower()]}, escritura=True)
                self.act.repos_enlazados.add(r.lower())
                info(f"Repo vinculado: {r}")
            except GhError as e:
                self.avisos.append(f"no pude vincular el repo {r}: {e}")
        p = self.act.project
        self.estado.datos["project"] = {"id": p["id"], "number": p["number"], "url": p["url"], "title": self.spec["project"],
                                        "org": self.spec["org"], "repo": self.repo, "label": self.spec["project_label"]}
        self.estado.guardar()

    def _select(self, nombre: str, deseadas) -> None:
        actual = self.act.campos.get(nombre)
        if actual and actual.get("dataType") != "SINGLE_SELECT":
            self.avisos.append(f"el campo {nombre!r} existe como {actual.get('dataType')}; no se toca ni se llena")
            return
        if not actual:
            opts = [{"name": n, "color": c, "description": d} for n, c, d in deseadas]
            f = self.gh.gql(M_CREAR_SELECT, {"p": self.act.project["id"], "n": nombre, "o": opts},
                            escritura=True)["createProjectV2Field"]["projectV2Field"]
            info(f"Campo creado: {nombre}")
        else:
            lista, desc = fusionar_opciones(nombre, actual.get("options") or [], deseadas)
            f = actual
            if lista:
                f = self.gh.gql(M_ACT_SELECT, {"f": actual["id"], "o": lista},
                                escritura=True)["updateProjectV2Field"]["projectV2Field"]
                info(f"Campo actualizado: {nombre} ({desc})")
        self.act.campos[nombre] = f
        self.campos[nombre] = mapa_campo(f)

    def _simple(self, nombre: str, tipo: str) -> None:
        actual = self.act.campos.get(nombre)
        if actual:
            if actual.get("dataType") != tipo:
                self.avisos.append(f"el campo {nombre!r} existe como {actual.get('dataType')} (se esperaba {tipo}); no se llena")
                return
            f = actual
        else:
            f = self.gh.gql(M_CREAR_SIMPLE, {"p": self.act.project["id"], "n": nombre, "t": tipo},
                            escritura=True)["createProjectV2Field"]["projectV2Field"]
            info(f"Campo creado: {nombre} ({tipo})")
            self.act.campos[nombre] = f
        self.campos[nombre] = mapa_campo(f)

    def _sprint(self) -> None:
        sp, nombre = self.spec["sprint"], self.spec["campos"]["sprint"]
        if self.via == "ninguno":
            return
        if self.via == "milestone":
            self.milestones_sprint()
            return
        actual = self.act.campos.get(nombre)
        if actual and actual.get("dataType") == "ITERATION":
            self.via = "iteration"
            self.campos[nombre] = mapa_campo(actual)
            faltan = [x["title"] for x in sp["iteraciones"] if clave(x["title"]) not in self.campos[nombre]["opciones"]]
            if faltan and self.spec["items"]:
                self.avisos.append(f"la iteracion {nombre!r} ya existe y no tiene {', '.join(faltan)}; no se modifica "
                                   "su configuracion (agregarlas en la interfaz)")
            return
        if actual and actual.get("dataType") == "SINGLE_SELECT":
            self.via = "select"
            self._select(nombre, opciones_select(self.spec, "select")[nombre])
            return
        if actual:
            self.avisos.append(f"el campo {nombre!r} existe como {actual.get('dataType')}; no se usa como Sprint")
            self.via = "ninguno"
            return
        if self.via == "iteration":
            conf = {"startDate": sp["inicio"], "duration": sp["duracion_dias"], "iterations": sp["iteraciones"]}
            try:
                f = self.gh.gql(M_CREAR_ITERACION, {"p": self.act.project["id"], "n": nombre, "c": conf},
                                escritura=True)["createProjectV2Field"]["projectV2Field"]
                self.act.campos[nombre] = f
                self.campos[nombre] = mapa_campo(f)
                info(f"Campo creado: {nombre} (ITERATION, {len(sp['iteraciones'])} sprints)")
                return
            except GhError as e:
                self.avisos.append(f"GitHub rechazo crear la iteracion {nombre!r} ({str(e)[:120]}); se creo como "
                                   "seleccion simple Sprint 1..N (sprintVia=select)")
                self.via = "select"
        self._select(nombre, opciones_select(self.spec, "select")[nombre])

    def milestones_sprint(self) -> None:
        for x in self.spec["sprint"]["iteraciones"]:
            if x["title"] in self.act.milestones:
                continue
            fin = _dt.date.fromisoformat(x["startDate"]) + _dt.timedelta(days=x["duration"] - 1)
            r = self.gh.write("POST", f"repos/{self.repo}/milestones",
                              {"title": x["title"], "description": f"{x['title']}: del {x['startDate']} al {fin.isoformat()}",
                               "due_on": f"{fin.isoformat()}T23:59:59Z"})
            self.act.milestones[x["title"]] = {"number": r["number"], "description": ""}
            info(f"Milestone creado: {x['title']}")

    def campos_project(self) -> None:
        c = self.spec["campos"]
        if "Status" not in self.act.campos:
            raise ErrorSpec("El Project no tiene el campo integrado Status (inesperado); revisar en la interfaz.")
        for nombre, deseadas in opciones_select(self.spec, "iteration").items():
            self._select(nombre, deseadas)
        if c["puntos"]:
            self._simple(c["puntos"], "NUMBER")
        for k in CAMPOS_FECHA:
            if c[k]:
                self._simple(c[k], "DATE")
        self._sprint()
        self.estado.datos["campos"] = self.campos
        self.estado.datos["sprintVia"] = self.via
        self.estado.guardar()

    # --- Etiquetas e issues ---------------------------------------------------
    def etiquetas(self) -> None:
        for nombre, color, desc in etiquetas_deseadas(self.spec, self.cfg):
            if clave(nombre) in self.act.etiquetas:
                continue
            try:
                self.gh.write("POST", f"repos/{self.repo}/labels", {"name": nombre, "color": color, "description": desc})
            except GhError as e:
                if "already_exists" not in str(e) and "already exists" not in str(e):
                    raise
            self.act.etiquetas[clave(nombre)] = nombre
            info(f"Etiqueta creada: {nombre}")

    def _buscar_issue(self, titulo: str) -> dict | None:
        lista = self.gh.get(f"repos/{self.repo}/issues",
                            {"labels": self.spec["project_label"], "state": "all", "per_page": "100"}, paginar=True) or []
        for i in lista:
            if "pull_request" not in i and clave(i["title"]) == clave(titulo):
                return i
        return None

    def asegurar_issue(self, titulo: str, body: str, etiquetas: list[str], milestone: int | None) -> tuple[dict, bool]:
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
        espera, issue = 5.0, None
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

    def item_del_project(self, node_id: str, numero) -> str | None:
        ya = self.act.items.get(node_id)
        if ya:
            return ya["item_id"]
        try:
            d = self.gh.gql(M_AGREGAR_ITEM, {"p": self.act.project["id"], "c": node_id}, escritura=True)
        except GhError as e:
            self.avisos.append(f"#{numero}: no se pudo agregar al Project ({str(e)[:80]}); se revisa en la verificacion")
            return None
        item = (d.get("addProjectV2ItemById") or {}).get("item")
        if not item:
            return None
        self.act.items[node_id] = {"item_id": item["id"], "valores": {}, "numero": numero}
        return item["id"]

    def valores_pendientes(self, item_id: str, actuales: dict, deseados: dict) -> list[tuple]:
        """Solo campos VACIOS. deseados: {nombre_campo: valor legible}."""
        pend = []
        for nombre, valor in deseados.items():
            if valor in (None, "") or actuales.get(nombre) not in (None, ""):
                continue
            c = self.campos.get(nombre)
            if not c:
                continue
            if c["tipo"] == "SINGLE_SELECT":
                oid = c["opciones"].get(clave(valor))
                v = {"singleSelectOptionId": oid} if oid else None
            elif c["tipo"] == "ITERATION":
                oid = c["opciones"].get(clave(valor))
                v = {"iterationId": oid} if oid else None
            elif c["tipo"] == "NUMBER":
                v = {"number": float(valor)}
            elif c["tipo"] == "DATE":
                v = {"date": str(valor)}
            else:
                v = None
            if v:
                pend.append((item_id, c["id"], v))
            else:
                self.avisos.append(f"valor {valor!r} no existe en el campo {nombre!r}; quedo vacio")
        return pend

    def aplicar_valores(self, pendientes: list[tuple]) -> None:
        for lote in lotes(pendientes):
            decl, partes, var = ["$p:ID!"], [], {"p": self.act.project["id"]}
            for n, (item, campo, valor) in enumerate(lote):
                decl += [f"$i{n}:ID!", f"$f{n}:ID!", f"$v{n}:ProjectV2FieldValue!"]
                partes.append(f"u{n}: updateProjectV2ItemFieldValue(input:{{projectId:$p,itemId:$i{n},"
                              f"fieldId:$f{n},value:$v{n}}}){{ clientMutationId }}")
                var.update({f"i{n}": item, f"f{n}": campo, f"v{n}": valor})
            try:
                d = self.gh.gql(f"mutation({','.join(decl)}){{ {' '.join(partes)} }}", var, escritura=True)
            except GhError as e:
                self.avisos.append(f"lote de valores rechazado ({str(e)[:100]}); se reintenta en la verificacion")
                continue
            if d.get("_errores"):
                self.avisos.append(f"algunos valores no se fijaron ({d['_errores'][:100]}); se revisa en la verificacion")
            self.creados["valores"] += len(lote)

    def enlazar_sub_issue(self, epica: dict, issue: dict) -> None:
        hijos = self.act.sub_issues.setdefault(epica["number"], set())
        if issue["id"] in hijos:
            return
        try:
            self.gh.write("POST", f"repos/{self.repo}/issues/{epica['number']}/sub_issues", {"sub_issue_id": issue["id"]})
            hijos.add(issue["id"])
            self.creados["sub_issues"] += 1
        except GhError as e:
            self.avisos.append(f"#{issue['number']} no quedo como sub-issue de #{epica['number']}: {str(e)[:100]}")

    def epicas(self) -> dict[str, dict]:
        epicas, et = {}, etiquetas_tipo(self.cfg)
        for e in self.spec["epicas"]:
            cuerpo = f"## Que agrupa\n{e['descripcion']}\n\n{MARCA_EPICA_INI}\n_(se completa al cargar las historias)_\n{MARCA_EPICA_FIN}\n"
            ep, creado = self.asegurar_issue(titulo_epica(e), cuerpo, [self.spec["project_label"], et["Epica"]], None)
            if creado:
                self.act.sub_issues[ep["number"]] = set()
            elif ep["number"] not in self.act.sub_issues:
                self.act.sub_issues[ep["number"]] = leer_sub_issues(self.gh, self.spec, ep["number"])
            item = self.item_del_project(ep["node_id"], ep["number"])
            if item:
                vals = self.act.items.get(ep["node_id"], {}).get("valores", {})
                self.aplicar_valores(self.valores_pendientes(item, vals, {"Status": self.spec["status"][0][0]}))
            epicas[e["nombre"]] = ep
            self.estado.datos["epicas"][e["nombre"]] = {"number": ep["number"], "url": ep["html_url"], "item_id": item}
            info(f"{'Epica creada' if creado else 'Epica reutilizada'} #{ep['number']}: {titulo_epica(e)}")
            self.estado.guardar()
        return epicas

    def deseados(self, it: dict) -> dict:
        c = self.spec["campos"]
        d = {"Status": it["estado"]}
        if c["prioridad"]:
            d[c["prioridad"]] = it.get("prio")
        if c["puntos"]:
            d[c["puntos"]] = it.get("puntos")
        if self.via in ("iteration", "select"):
            d[c["sprint"]] = it.get("sprint")
        for k in CAMPOS_FECHA:
            if c[k]:
                d[c[k]] = it.get(k)
        return d

    def items(self, epicas: dict[str, dict]) -> None:
        et = etiquetas_tipo(self.cfg)
        for it in self.spec["items"]:
            etqs = [self.spec["project_label"], et[it["tipo"]], *[sin_acentos(x) for x in it.get("etiquetas") or []]]
            ms = None
            if self.via == "milestone" and it.get("sprint"):
                ms = self.act.milestones[it["sprint"]]["number"]
            issue, creado = self.asegurar_issue(it["titulo"], it["body"], etqs, ms)
            if it.get("epica"):
                self.enlazar_sub_issue(epicas[it["epica"]], issue)
            item = self.item_del_project(issue["node_id"], issue["number"])
            if item:
                vals = self.act.items.get(issue["node_id"], {}).get("valores", {})
                self.aplicar_valores(self.valores_pendientes(item, vals, self.deseados(it)))
            self.estado.datos["items"][it["titulo"]] = {"number": issue["number"], "url": issue["html_url"], "item_id": item,
                                                        "estado": it["estado"], "puntos": it["puntos"], "sprint": it.get("sprint")}
            self.estado.guardar()
            info(f"  {'+' if creado else '='} #{issue['number']} {it['titulo'][:70]}")

    def cuerpos_epicas(self, epicas: dict[str, dict]) -> None:
        for e in self.spec["epicas"]:
            ep = epicas[e["nombre"]]
            hijos = [self.act.issues.get(clave(i["titulo"])) for i in self.spec["items"] if i.get("epica") == e["nombre"]]
            lineas = ["## Historias"] + [f"- [{'x' if h.get('state') == 'closed' else ' '}] #{h['number']} {h['title']}"
                                         for h in sorted((h for h in hijos if h), key=lambda h: h["number"])]
            seccion = f"{MARCA_EPICA_INI}\n" + "\n".join(lineas) + f"\n{MARCA_EPICA_FIN}"
            cuerpo = ep.get("body") or ""
            if MARCA_EPICA_INI in cuerpo and MARCA_EPICA_FIN in cuerpo:
                nuevo = re.sub(re.escape(MARCA_EPICA_INI) + r".*?" + re.escape(MARCA_EPICA_FIN),
                               lambda _m: seccion, cuerpo, flags=re.S)
            else:
                nuevo = cuerpo.rstrip() + "\n\n" + seccion + "\n"
            if nuevo.strip() != cuerpo.strip():
                self.gh.write("PATCH", f"repos/{self.repo}/issues/{ep['number']}", {"body": nuevo})
                ep["body"] = nuevo

    def agregar_abiertos(self, masivo: bool) -> None:
        if not self.spec["agregar_abiertos"]:
            return
        leer_abiertos(self.gh, self.spec, self.act)
        if len(self.act.abiertos) > LIMITE_ABIERTOS and not masivo:
            self.avisos.append(f"{len(self.act.abiertos)} issues abiertos (> {LIMITE_ABIERTOS}): no se agregaron; "
                               "confirmar con el usuario y re-ejecutar con --masivo")
            return
        primero, pend = self.spec["status"][0][0], []
        for i in self.act.abiertos:
            item = self.item_del_project(i["node_id"], i["number"])
            if item:
                self.creados["agregados"] += 1
                pend += self.valores_pendientes(item, {}, {"Status": primero})
            time.sleep(min(self.pausa, 0.3))
        self.aplicar_valores(pend)
        info(f"Issues abiertos agregados: {self.creados['agregados']}")

    # --- Vistas -------------------------------------------------------------
    def vistas(self) -> None:
        if not self.spec["vistas"]:
            return
        try:
            leer_detalle_project(self.gh, self.act)
            por_nombre = {v["name"]: v for v in self.act.vistas}
            c = self.spec["campos"]
            visibles_n = ["Title", "Status", c["puntos"], c["sprint"] if self.via in ("iteration", "select") else "Milestone",
                          c["prioridad"], *[c[k] for k in CAMPOS_FECHA]]
            visibles = [self.act.campos[n]["id"] for n in visibles_n if n and n in self.act.campos]
            nuestras = {n for n, _, _ in vistas_deseadas(self.spec, self.via)}
            for nombre, layout, filtro in vistas_deseadas(self.spec, self.via):
                vista = por_nombre.get(nombre)
                if not vista:
                    defecto = [v for v in self.act.vistas if v["name"] not in nuestras and re.match(r"^(View|Vista) \d+$", v["name"])]
                    if layout == "BOARD_LAYOUT" and len(self.act.vistas) == 1 and defecto:
                        vista = self.gh.gql(M_ACT_VISTA, {"v": defecto[0]["id"], "n": nombre, "l": layout},
                                            escritura=True)["updateProjectV2View"]["projectV2View"]
                        info(f"Vista por defecto renombrada: {nombre}")
                    else:
                        try:
                            if layout == "TABLE_LAYOUT" and visibles:
                                d = self.gh.gql(M_CREAR_VISTA_CFG, {"p": self.act.project["id"], "n": nombre, "l": layout,
                                                                    "v": visibles}, escritura=True)
                            else:
                                raise GhError("sin configuracion")
                        except GhError:
                            d = self.gh.gql(M_CREAR_VISTA, {"p": self.act.project["id"], "n": nombre, "l": layout},
                                            escritura=True)
                        vista = d["createProjectV2View"]["projectV2View"]
                        info(f"Vista creada: {nombre}")
                if filtro and not (vista.get("filter") or "").strip():
                    try:
                        self.gh.gql(M_FILTRO_VISTA, {"v": vista["id"], "f": filtro}, escritura=True)
                    except GhError as e:
                        self.avisos.append(f"vista {nombre!r}: no se pudo fijar el filtro {filtro!r} ({str(e)[:80]}); ponerlo a mano")
            if self.via == "select":
                self.avisos.append("vista 'Sprint actual': con Sprint de seleccion no hay @current; filtrar a mano por el sprint en curso")
        except (GhError, KeyError, TypeError) as e:
            self.avisos.append(f"vistas: la API no permitio crearlas ({str(e)[:100]}); crearlas a mano")


# ---------------------------------------------------------------------------
# Verificacion
# ---------------------------------------------------------------------------

def verificar(gh: Gh, spec: dict, cfg: dict, act: Actual, corregir: bool, ej: Ejecutor | None = None) -> dict:
    if not act.project:
        raise ErrorSpec(f"No existe el Project {spec['project']!r} en {spec['org']}; usar 'crear'.")
    leer_detalle_project(gh, act)
    leer_items(gh, act)
    ej = ej or Ejecutor(gh, spec, cfg, act, Estado(Path(os.devnull), False), 0)
    hallazgos: list[str] = []
    c = spec["campos"]

    # 0) Opciones del ciclo y campos del PO
    st = act.campos.get("Status") or {}
    faltan_st = [d[0] for d in spec["status"] if clave(d[0]) not in {clave(o["name"]) for o in st.get("options") or []}]
    if faltan_st:
        hallazgos.append(f"STATUS SIN OPCIONES DEL CICLO: {', '.join(faltan_st)}")
    faltan_campos = [c[k] for k in ("puntos", "prioridad", *CAMPOS_FECHA) if c[k] and c[k] not in act.campos]
    if spec["sprint"]["via"] in ("iteration", "select") and c["sprint"] not in act.campos:
        faltan_campos.append(c["sprint"])
    if faltan_campos:
        hallazgos.append(f"CAMPOS FALTANTES: {', '.join(faltan_campos)}")
    if corregir and (faltan_st or faltan_campos):
        ej.campos_project()
        leer_detalle_project(gh, act)
    ej.campos = {n: mapa_campo(f) for n, f in act.campos.items() if f.get("id")}
    sp_campo = act.campos.get(c["sprint"]) or {}
    tipo_sp = sp_campo.get("dataType")
    if spec["sprint"]["via"] in ("milestone", "ninguno"):
        ej.via = spec["sprint"]["via"]
    else:
        ej.via = {"ITERATION": "iteration", "SINGLE_SELECT": "select"}.get(tipo_sp, "ninguno")

    # 1) Borradores
    for b in act.borradores:
        hallazgos.append(f"BORRADOR (debe ser issue real): {b['titulo']}")
        if corregir:
            repo_id = act.repo_ids.get(spec["repo"].lower())
            d = gh.gql(M_CONVERTIR, {"i": b["item_id"], "r": repo_id}, escritura=True)
            nuevo = d["convertProjectV2DraftIssueItemToIssue"]["item"]["content"]
            gh.write("POST", f"repos/{spec['repo']}/issues/{nuevo['number']}/labels", {"labels": [spec["project_label"]]})
            info(f"  convertido en issue #{nuevo['number']}")

    # 2) Issues del backlog fuera del Project
    for i in act.issues.values():
        if i["node_id"] not in act.items:
            hallazgos.append(f"FUERA DEL PROJECT: #{i['number']} {i['title']}")
            if corregir:
                ej.item_del_project(i["node_id"], i["number"])
    if corregir:
        leer_items(gh, act)

    # 3) Valores vacios (Status siempre; el resto solo si el spec trae el dato)
    por_titulo = {clave(s["titulo"]): s for s in spec["items"]}
    estados = {clave(d[0]) for d in spec["status"]}
    pendientes = []
    for it in act.items.values():
        s = por_titulo.get(clave(it["titulo"]))
        actual_st = it["valores"].get("Status")
        if actual_st and clave(actual_st) not in estados:
            hallazgos.append(f"SIN ETAPA (Status {actual_st!r} fuera del ciclo): #{it['numero']} {it['titulo']}")
        deseado = ej.deseados(s) if s else {}
        if not actual_st and not s:
            if it.get("estado") == "OPEN":
                deseado = {"Status": spec["status"][0][0]}
            else:
                hallazgos.append(f"SIN STATUS y cerrado: #{it['numero']} {it['titulo']} -> lo define el PO")
        p = ej.valores_pendientes(it["item_id"], it["valores"], deseado)
        if p:
            nombres = [n for n, v in deseado.items() if v not in (None, "") and it["valores"].get(n) in (None, "")]
            hallazgos.append(f"SIN {', '.join(nombres)}: #{it['numero']} {it['titulo']}")
            pendientes += p
    if corregir and pendientes:
        ej.aplicar_valores(pendientes)
        leer_items(gh, act)

    # 4) Sub-issues faltantes
    for e in spec["epicas"]:
        ep = act.issues.get(clave(titulo_epica(e)))
        if not ep:
            hallazgos.append(f"FALTA LA EPICA: {titulo_epica(e)}")
            continue
        hijos = leer_sub_issues(gh, spec, ep["number"])
        act.sub_issues[ep["number"]] = hijos
        for s in spec["items"]:
            i = act.issues.get(clave(s["titulo"]))
            if s.get("epica") == e["nombre"] and i and i["id"] not in hijos:
                hallazgos.append(f"SUB-ISSUE FALTANTE: #{i['number']} no cuelga de #{ep['number']} ({e['nombre']})")
                if corregir:
                    ej.enlazar_sub_issue(ep, i)

    info("\nVERIFICACION del Project " + act.project["url"])
    if hallazgos:
        for h in hallazgos:
            info(f"  - {h}")
        info("  (corregido lo corregible)" if corregir else "  -> 'verificar --corregir' arregla lo corregible (sin borrar ni pisar)")
    else:
        info("  Sin hallazgos: ciclo completo, campos presentes, items reales con Status.")
    info("\nConteos:")
    por_etiqueta = {clave(et): tipo for tipo, et in etiquetas_tipo(cfg).items()}
    filas = [{"Status": v["valores"].get("Status"),
              "Sprint": v["valores"].get(c["sprint"]) if ej.via != "milestone" else v.get("milestone"),
              "Tipo": next((por_etiqueta[clave(e)] for e in v.get("etiquetas") or [] if clave(e) in por_etiqueta), None),
              "puntos": v["valores"].get(c["puntos"]) if c["puntos"] else None}
             for v in act.items.values()]
    conteos = imprimir_conteos(filas)
    return {"hallazgos": hallazgos, "conteos": conteos}


# ---------------------------------------------------------------------------
# Espejo local (.po-team/backlog.md)
# ---------------------------------------------------------------------------

def generar_espejo(spec: dict, act: Actual, planificado: bool, via: str) -> str:
    label, c = spec["project_label"], spec["campos"]
    url = act.project["url"] if act.project else "(Project aun no creado)"
    filas = []
    if planificado or not act.project:
        for it in spec["items"]:
            e = act.issues.get(clave(it["titulo"]))
            filas.append({"num": e["number"] if e else None, "url": e["html_url"] if e else None, "titulo": it["titulo"],
                          "Status": it["estado"], "Sprint": it.get("sprint"), "puntos": it["puntos"],
                          "epica": it.get("epica")})
    else:
        for it in act.items.values():
            if clave(it["titulo"]).startswith("epica:"):
                continue
            v = it["valores"]
            filas.append({"num": it["numero"], "url": it.get("url"), "titulo": it["titulo"], "Status": v.get("Status"),
                          "Sprint": it.get("milestone") if via == "milestone" else v.get(c["sprint"]),
                          "puntos": v.get(c["puntos"]) if c["puntos"] else None, "epica": None})
    lineas = [f"<!-- backlog-github:inicio {label} -->", f"## Backlog: {spec['project']}", "",
              f"- Project: {url}", f"- Repos: " + ", ".join(f"`{r}`" for r in spec["repos"]) + f" · etiqueta `{label}`",
              f"- Actualizado: {ahora()} (generado; se regenera con `/po-team:tablero crear-backlog espejo`)", "",
              "| Estado | Items | Puntos |", "|---|---|---|"]
    for n, _, _ in spec["status"]:
        de = [x for x in filas if clave(x.get("Status")) == clave(n)]
        lineas.append(f"| {n} | {len(de)} | {sum(float(x['puntos'] or 0) for x in de):g} |")
    otros = [x for x in filas if clave(x.get("Status")) not in {clave(s[0]) for s in spec["status"]}]
    if otros:
        lineas.append(f"| (sin etapa) | {len(otros)} | {sum(float(x['puntos'] or 0) for x in otros):g} |")
    grupos = []
    for s in [x["title"] for x in spec["sprint"]["iteraciones"]]:
        grupos.append((s, [x for x in filas if clave(x.get("Sprint")) == clave(s)]))
    conocidos = {clave(g[0]) for g in grupos}
    extra = sorted({x["Sprint"] for x in filas if x.get("Sprint") and clave(x["Sprint"]) not in conocidos})
    grupos += [(s, [x for x in filas if x.get("Sprint") == s]) for s in extra]
    grupos.append(("Sin sprint (backlog)", [x for x in filas if not x.get("Sprint")]))
    for nombre, de in grupos:
        if not de:
            continue
        pts = sum(float(x["puntos"] or 0) for x in de)
        lineas += ["", f"### {nombre} — {len(de)} items · {pts:g} puntos"]
        for x in sorted(de, key=lambda x: x["num"] or 10 ** 9):
            ref = f"[#{x['num']}]({x['url']})" if x["num"] else "(nuevo)"
            p = f"{float(x['puntos']):g} pts" if x.get("puntos") not in (None, "") else "sin estimar"
            ep = f" · {x['epica']}" if x.get("epica") else ""
            lineas.append(f"- {ref} {x['titulo']} — {x.get('Status') or '?'} · {p}{ep}")
    lineas.append(f"<!-- backlog-github:fin {label} -->")
    return "\n".join(lineas) + "\n"


def escribir_espejo(ruta: Path, seccion: str, label: str) -> None:
    previo = ruta.read_text(encoding="utf-8") if ruta.is_file() else ""
    patron = re.compile(r"<!-- backlog-github:inicio " + re.escape(label) + r" -->.*?<!-- backlog-github:fin "
                        + re.escape(label) + r" -->\n?", re.S)
    if patron.search(previo):
        nuevo = patron.sub(lambda _m: seccion, previo, count=1)
    else:
        lineas = previo.splitlines(keepends=True)
        if lineas and lineas[0].startswith("# "):
            nuevo = lineas[0] + "\n" + seccion + "\n" + "".join(lineas[1:])
        else:
            nuevo = "# Backlog del PO\n\n" + seccion + ("\n" + previo if previo else "")
    escribir_atomico(ruta, nuevo)


# ---------------------------------------------------------------------------
# Registro en .po-team/config.json (esquema po-team; conserva el resto)
# ---------------------------------------------------------------------------

def registrar_config(cfg_path: Path, spec: dict, project: dict, nombres_status: list[str], via: str,
                     campos_ok: dict[str, str], avisos: list[str]) -> bool:
    """Registra el Project en tracker.github.projects[] y el mapeo del ciclo. Escritura atomica.

    project: {number, title, url}; nombres_status: nombres REALES de las opciones del Status;
    via: iteration | select | milestone | ninguno; campos_ok: {clave_config: nombre real o ""}."""
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.is_file() else {}
    except (OSError, json.JSONDecodeError) as e:
        avisos.append(f"no pude leer {cfg_path}: {e}; no se registro el Project")
        return False
    tracker = cfg.setdefault("tracker", {})
    if tracker.get("provider") not in (None, "", "github") and not es_placeholder(tracker.get("provider")):
        avisos.append(f"tracker.provider es {tracker.get('provider')!r}; no se registro el Project en config.json")
        return False
    tracker["provider"] = "github"
    g = tracker.setdefault("github", {})
    org = spec["org"]
    if es_placeholder(g.get("org")):
        g["org"] = org
    if es_placeholder(g.get("repoDefault")):
        g["repoDefault"] = corto(spec["repo"], org)
    repos = [r for r in (g.get("repos") or []) if not es_placeholder(r)]
    for r in spec["repos"]:
        rc = corto(r, org)
        if clave(rc) not in {clave(x) for x in repos} and clave(r) not in {clave(x) for x in repos}:
            repos.append(rc)
    g["repos"] = repos

    entrada = {"alias": spec["alias"], "numero": project["number"], "titulo": project.get("title") or spec["project"],
               "url": project.get("url", ""), "campos": {"estado": "Status", **{k: campos_ok.get(k, "") for k in CAMPOS_DEFECTO if k != "estado"}}}
    projects = [p for p in (g.get("projects") or []) if isinstance(p, dict)]
    idx = next((i for i, p in enumerate(projects) if p.get("numero") == project["number"]), None)
    if idx is None:
        idx = next((i for i, p in enumerate(projects) if clave(p.get("titulo")) == clave(entrada["titulo"])), None)
    if idx is None:
        idx = next((i for i, p in enumerate(projects) if not p.get("numero") or es_placeholder(p.get("titulo"))), None)
    if idx is None:
        projects.append(entrada)
    else:
        previo = projects[idx]
        alias_previo = previo.get("alias")
        merged = {**previo, **entrada}
        if alias_previo and not es_placeholder(alias_previo) and not spec.get("_alias_explicito"):
            merged["alias"] = alias_previo
        merged["campos"] = {**{k: v for k, v in (previo.get("campos") or {}).items() if not es_placeholder(v)},
                            **entrada["campos"]}
        projects[idx] = merged
        entrada = merged
    g["projects"] = projects
    aliases = {p.get("alias") for p in projects}
    if es_placeholder(g.get("projectDefault")) or g.get("projectDefault") not in aliases:
        g["projectDefault"] = entrada["alias"]
    if via in ("iteration", "select", "milestone"):
        g["sprintVia"] = via

    # Ciclo: nombres REALES de las opciones (por clave) en cada etapa.
    real = {clave(n): n for n in nombres_status}
    ciclo = cfg.setdefault("ciclo", {})
    origen = spec.get("status_origen")

    def mapear(lista):
        return [real.get(clave(s), s) for s in lista if clave(s) in real]

    if origen == "config":
        for e in ciclo.get("etapas") or []:
            e["estados"] = mapear(e.get("estados") or []) or e.get("estados") or []
        ciclo["estadosObservado"] = mapear(ciclo.get("estadosObservado") or [])
        ciclo["estadosBloqueado"] = mapear(ciclo.get("estadosBloqueado") or [])
    elif origen == "defecto":
        previas = {e.get("clave"): e for e in ciclo.get("etapas") or [] if isinstance(e, dict)}
        etapas = []
        for d in ETAPAS_DEFECTO:
            e = dict(previas.get(d["clave"]) or d)
            e["clave"], e["estados"] = d["clave"], mapear(d["estados"])
            if es_placeholder(e.get("nombre")):
                e["nombre"] = d["nombre"]
            if not isinstance(e.get("etiquetas"), list):
                e["etiquetas"] = d["etiquetas"]
            etapas.append(e)
        ciclo["etapas"] = etapas
        ciclo["estadosObservado"] = mapear(OBSERVADO_DEFECTO)
        ciclo["estadosBloqueado"] = mapear(BLOQUEADO_DEFECTO)
        reglas = tracker.setdefault("reglas", {})
        if es_placeholder(reglas.get("estadosSoloQA")):
            reglas["estadosSoloQA"] = mapear(REGLAS_DEFECTO["estadosSoloQA"])
        if es_placeholder(reglas.get("estadoAlResolver")):
            reglas["estadoAlResolver"] = real.get(clave(REGLAS_DEFECTO["estadoAlResolver"]), REGLAS_DEFECTO["estadoAlResolver"])
    else:  # status_opciones propias del spec
        etapas_spec = spec.get("etapas") or {}
        if etapas_spec:
            previas = {e.get("clave"): e for e in ciclo.get("etapas") or [] if isinstance(e, dict)}
            for k, lista in etapas_spec.items():
                if k in ("observado", "bloqueado"):
                    ciclo["estadosObservado" if k == "observado" else "estadosBloqueado"] = mapear(lista)
                    continue
                e = previas.get(k)
                if e is None:
                    e = {"clave": k, "nombre": k.capitalize(), "estados": [], "etiquetas": []}
                    ciclo.setdefault("etapas", []).append(e)
                e["estados"] = mapear(lista)
        else:
            avisos.append("status_opciones propias sin 'etapas': mapear ciclo.etapas[].estados con /po-team:setup tracker")
    escribir_atomico(cfg_path, json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
    return True


# ---------------------------------------------------------------------------
# Subcomandos
# ---------------------------------------------------------------------------

def preparar(args):
    po_dir = resolver_po_team(getattr(args, "po_team", None))
    cfg = cargar_config(po_dir)
    spec, avisos = cargar_spec(args.spec, cfg)
    spec["_alias_explicito"] = bool(json.loads(Path(args.spec).read_text(encoding="utf-8")).get("alias"))
    return po_dir, cfg, spec, avisos


def cmd_crear(args, modo: str = "crear") -> int:
    po_dir, cfg, spec, avisos = preparar(args)
    gh = Gh(dry_run=args.dry_run, offline=args.offline)
    ruta = resolver_estado(spec["project"], args.estado, po_dir)
    act, avisos_gh = descubrir(gh, spec)
    avisos += avisos_gh
    if modo == "agregar" and not act.project and not args.offline:
        raise ErrorSpec(f"No existe el Project {spec['project']!r} en {spec['org']}: 'agregar' solo completa uno existente; usar 'crear'.")
    if modo == "agregar" and args.offline:
        avisos.append("'agregar' offline: no se pudo comprobar que el Project exista")
    if args.dry_run:
        imprimir_plan(spec, cfg, act, ruta, avisos, None if args.sin_espejo else po_dir, modo)
        return 0
    if modo == "crear" and act.project_previo and not args.reutilizar:
        raise ErrorSpec(f"Ya existe el Project #{act.project['number']} {spec['project']!r} ({act.project['url']}). "
                        "Preguntar al usuario: reutilizarlo (re-ejecutar con --reutilizar) o usar otro nombre. "
                        "Nunca se borra ni se renombra.")
    estado = Estado(ruta, escribir=True)
    estado.datos["spec"] = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    ej = Ejecutor(gh, spec, cfg, act, estado, args.pausa)
    info(f"Estado/resultado: {ruta}")
    ej.project()
    ej.campos_project()
    epicas = {}
    if usa_issues(spec):
        ej.etiquetas()
    if usa_issues(spec):
        epicas = ej.epicas()
        ej.items(epicas)
        ej.cuerpos_epicas(epicas)
    ej.agregar_abiertos(args.masivo)
    ej.vistas()
    resultado = verificar(gh, spec, cfg, act, corregir=True, ej=ej)
    estado.datos["verificacion"] = resultado
    estado.guardar()
    st = act.campos.get("Status") or {}
    nombres_status = [o["name"] for o in st.get("options") or []]
    c = spec["campos"]
    campos_ok = {k: (c[k] if c[k] and k in ("puntos", "prioridad", *CAMPOS_FECHA) and c[k] in ej.campos else "")
                 for k in CAMPOS_DEFECTO if k != "estado"}
    campos_ok["sprint"] = c["sprint"] if ej.via in ("iteration", "select") and c["sprint"] in ej.campos else ""
    if po_dir and not args.sin_espejo:
        escribir_espejo(po_dir / "backlog.md", generar_espejo(spec, act, False, ej.via), spec["project_label"])
        registrar_config(po_dir / "config.json", spec, act.project, nombres_status, ej.via, campos_ok, ej.avisos)
    elif not po_dir:
        ej.avisos.append("no se encontro .po-team/ fuera de repos: no se escribio el espejo ni el config (usar --po-team)")
    info("\n" + "=" * 72)
    info(f"LISTO  {act.project['url']}")
    info(f"  issues creados: {ej.creados['issues']} · reutilizados: {ej.creados['reutilizados']} · sub-issues: "
         f"{ej.creados['sub_issues']} · abiertos agregados: {ej.creados['agregados']} · valores fijados: {ej.creados['valores']}")
    info(f"  sprintVia: {ej.via} · Estado: {ruta}" + (f" · .po-team: {po_dir}" if po_dir else ""))
    info("  PENDIENTE MANUAL: en cada vista fijar el agrupamiento/orden en la interfaz (la API no lo permite);"
         " el Tablero usa Status como columnas por defecto: confirmarlo.")
    for a in avisos + ej.avisos:
        info(f"  ! {a}")
    return 0


def cmd_agregar(args) -> int:
    args.reutilizar = True
    return cmd_crear(args, modo="agregar")


def cmd_verificar(args) -> int:
    po_dir, cfg, spec, _ = preparar(args)
    gh = Gh(dry_run=not args.corregir, offline=False)
    act, avisos_gh = descubrir(gh, spec)
    ej = None
    if args.corregir:
        ej = Ejecutor(gh, spec, cfg, act, Estado(resolver_estado(spec["project"], args.estado, po_dir), True), 0.5)
    r = verificar(gh, spec, cfg, act, corregir=args.corregir, ej=ej)
    for a in avisos_gh + (ej.avisos if ej else []):
        info(f"  ! {a}")
    return 1 if r["hallazgos"] and not args.corregir else 0


def cmd_espejo(args) -> int:
    po_dir, cfg, spec, _ = preparar(args)
    gh = Gh(dry_run=True, offline=args.offline)
    act, _ = descubrir(gh, spec)
    via = spec["sprint"]["via"]
    if act.project and act.campos.get(spec["campos"]["sprint"], {}).get("dataType") == "SINGLE_SELECT":
        via = "select"
    seccion = generar_espejo(spec, act, args.offline or not act.project, via)
    if args.dry_run or args.offline or not po_dir:
        info(seccion)
        if not po_dir:
            info("(no se encontro .po-team/ fuera de repos; indicar --po-team DIR para escribirlo)")
        return 0
    escribir_espejo(po_dir / "backlog.md", seccion, spec["project_label"])
    info(f"Espejo actualizado: {po_dir / 'backlog.md'}")
    return 0


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="project_backlog.py",
        description="Crea, completa, verifica y refleja el backlog del PO en un GitHub Project v2 con el "
                    "ciclo FaaST, a partir de UN spec JSON. Idempotente: re-ejecutarlo no duplica nada.",
        epilog=(
            "Ejemplos:\n"
            "  project_backlog.py crear spec.json --dry-run            # plan con lecturas de GitHub\n"
            "  project_backlog.py crear spec.json --dry-run --offline  # plan sin llamar a gh\n"
            "  project_backlog.py crear spec.json                      # ejecutar (con OK del usuario)\n"
            "  project_backlog.py crear spec.json --reutilizar         # el Project ya existe y el usuario dijo usarlo\n"
            "  project_backlog.py agregar spec.json [--dry-run]\n"
            "  project_backlog.py verificar spec.json [--corregir]\n"
            "  project_backlog.py espejo spec.json [--dry-run]\n\n"
            "Formato del spec: docstring del script y skill backlog-github (assets/spec-ejemplo.json)."),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True, metavar="{crear,agregar,verificar,espejo}")

    def comunes(sp, escritura=True):
        sp.add_argument("spec", help="ruta al spec JSON")
        sp.add_argument("--po-team", metavar="DIR", help="carpeta .po-team (o la que la contiene); nunca dentro de un repo")
        sp.add_argument("--estado", metavar="RUTA", help="archivo de estado/resultado (nunca dentro de un repo git)")

    for nombre, fn, ayuda in (("crear", cmd_crear, "crear el Project y dejarlo listo"),
                              ("aplicar", cmd_crear, "alias de crear"),
                              ("agregar", cmd_agregar, "completar un Project existente (items, epicas, campos)")):
        a = sub.add_parser(nombre, help=ayuda)
        comunes(a)
        a.add_argument("--dry-run", action="store_true", help="solo imprimir el plan; ninguna escritura")
        a.add_argument("--offline", action="store_true", help="con --dry-run: no llamar a gh")
        a.add_argument("--sin-espejo", action="store_true", help="no tocar .po-team/backlog.md ni config.json")
        a.add_argument("--reutilizar", action="store_true", help="crear: usar el Project existente con el mismo nombre")
        a.add_argument("--masivo", action="store_true", help=f"permitir agregar mas de {LIMITE_ABIERTOS} issues abiertos")
        a.add_argument("--pausa", type=float, default=1.0, help="segundos entre creaciones de issues (default 1.0)")
        a.set_defaults(func=fn)

    v = sub.add_parser("verificar", help="detectar (y con --corregir arreglar) problemas del Project")
    comunes(v)
    v.add_argument("--corregir", action="store_true", help="arreglar lo corregible (escribe en GitHub)")
    v.set_defaults(func=cmd_verificar)

    e = sub.add_parser("espejo", help="regenerar la seccion del Project en .po-team/backlog.md")
    comunes(e)
    e.add_argument("--dry-run", action="store_true", help="imprimir la seccion sin escribirla")
    e.add_argument("--offline", action="store_true", help="armar la seccion solo desde el spec, sin gh")
    e.set_defaults(func=cmd_espejo)
    return p


def main(argv=None) -> int:
    args = construir_parser().parse_args(argv)
    if getattr(args, "offline", False) and args.cmd in ("crear", "aplicar", "agregar") and not args.dry_run:
        info("ERROR: --offline solo tiene sentido junto con --dry-run.")
        return 2
    if not getattr(args, "offline", False) and not shutil.which("gh"):
        info("ERROR: falta GitHub CLI (gh). Correr /po-team:setup tracker.")
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
