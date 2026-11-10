#!/usr/bin/env python3
"""memoria.py — memoria del equipo: recuperacion (RAG) + retroalimentacion + mejora continua.

Tres piezas, sin dependencias (solo Python 3) y sin servicios externos:

1. RECUPERAR. Indice BM25 local sobre lo que el proyecto ya sabe — lecciones, wiki, handoffs,
   decisiones de diseño, retros y fuentes extra del config (p. ej. faast-brain) — para que un
   agente traiga los 3-5 fragmentos que le sirven en vez de releer todo.
2. RETROALIMENTAR. Cada leccion acumula senales: quien la origino (usuario > QA > retro >
   agente), cuantas veces se confirmo, y si a quien la uso le sirvio (`feedback util|no-util`).
   Esas senales reordenan la recuperacion; lo que no sirve se retira solo.
3. MEJORA CONTINUA. `consolidar` destila las lecciones validadas en un manual por agente que se
   inyecta al iniciar cada agente, propone cuales ya merecen ser regla permanente del plugin,
   y `evaluar` mide la recuperacion contra los casos que el propio uso fue confirmando.

No se reentrena ningun modelo: lo que mejora es lo que el equipo lee antes de actuar.

Comandos (todos aceptan --coord RUTA; por defecto la coordinacion canonica del proyecto):
  indexar                                   reconstruye el indice (incremental por fecha de archivo)
  buscar "consulta" [--tipo T] [--agente A] [--k 5] [--solo lecciones|docs] [--json]
  aprender --tipo T --texto "..." [--agente A] [--ref ID] [--tags a,b] [--fuente usuario|qa|retro|agente]
  feedback ID util|no-util [--nota "..."] [--consulta "..."]
  para-agente AGENTE [--tarea "..."] [--k 4]        (lo usa el hook de inicio de agente)
  pendientes                                correcciones del usuario aun sin convertir en leccion
  consolidar                                manual por agente + candidatas a regla permanente
  metricas                                  salud de la memoria
  evaluar [--k 5]                           recall@k y MRR sobre los casos confirmados
  listar [--tipo T] [--agente A] [--estado activa|retirada]

Tipos: diseno, qa, codigo, bd, infra, proceso, negocio, seguridad, permisos.
"""
import datetime
import hashlib
import json
import math
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "..", "hooks"))
try:
    from coord_root import resolve  # noqa: E402
except Exception:  # el script tambien funciona copiado fuera del plugin, con --coord
    resolve = None

TIPOS = ("diseno", "qa", "codigo", "bd", "infra", "proceso", "negocio", "seguridad", "permisos")
PESO_FUENTE = {"usuario": 1.6, "qa": 1.3, "retro": 1.2, "agente": 1.0}
# que tipos de leccion le sirven a cada agente aunque no lleven su nombre
DOMINIO = {
    "ui-designer": ("diseno",), "ux-researcher": ("diseno",), "visual-designer": ("diseno",),
    "motion-designer": ("diseno",), "artist-3d": ("diseno",), "design-engineer": ("diseno", "codigo"),
    "frontend": ("codigo", "diseno", "qa"), "backend": ("codigo", "qa", "bd"),
    "dba": ("bd", "proceso"), "infra": ("infra", "permisos"), "release-manager": ("proceso", "bd"),
    "qa": ("qa",), "qa-frontend": ("qa", "diseno"), "qa-backend": ("qa",),
    "lead": ("proceso", "permisos", "qa"), "product-owner": ("negocio", "proceso"),
    "architect": ("codigo", "infra"), "cybersec": ("seguridad",), "pentester": ("seguridad",),
    "appsec": ("seguridad", "codigo"), "cloudsec": ("seguridad", "infra"),
    "tech-writer": ("proceso",), "setup": ("permisos", "infra"),
}
VACIAS = set("""a al algo ante antes asi aun aunque bajo cada como con contra cual cuando de del desde donde
dos el ella ellas ellos en entre era es esa ese eso esta este esto estos fue ha hace hacia hasta hay la las le
les lo los mas me mi muy no nos o os otra otro para pero por porque que se sea segun ser si sin sobre son su sus
tambien te tiene todo tras tu un una uno unos y ya the of and to in for is on with""".split())
K1, B = 1.5, 0.75
MAX_TROZO = 1400
DIAS_VIDA_MEDIA = 240
CORRECCION = re.compile(
    r"(?i)(^|[\s,.;:¡!¿?])(no asi|asi no|no era|no es asi|te dije|ya te dije|otra vez|de nuevo lo mismo|"
    r"no me gusta|no quiero|no vuelvas|deja de|nunca (mas )?|siempre (que|debes|hay que)|prefiero|"
    r"esta mal|estuvo mal|mal hecho|eso no|error tuyo|te equivocaste|corrige|no debiste|"
    r"de ahora en adelante|a partir de ahora|recuerda que|la proxima vez|tienes que|debes )")


# ------------------------------------------------------------------ utilidades

def ahora():
    return datetime.datetime.now(datetime.timezone.utc)


def iso(dt=None):
    return (dt or ahora()).strftime("%Y-%m-%dT%H:%M:%SZ")


def arg(nombre, defecto=None):
    if nombre in sys.argv:
        i = sys.argv.index(nombre)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return defecto


def fallar(msg, codigo=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(codigo)


def coord_dir(obligatoria=True):
    dado = arg("--coord")
    if dado:
        return os.path.abspath(os.path.expanduser(dado))
    if resolve:
        r = resolve(os.getcwd())
        if r.get("path") and not r.get("en_repo"):
            return r["path"]
    if obligatoria:
        fallar("no encuentro la coordinacion del proyecto fuera de un repo. Pasa --coord RUTA.")
    return None


def tokens(texto):
    t = unicodedata.normalize("NFD", texto.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    out = []
    for w in re.findall(r"[a-z0-9ñ][a-z0-9ñ_#.-]*[a-z0-9ñ]|[a-z0-9ñ]", t):
        if w in VACIAS or len(w) < 2:
            continue
        # raiz minima: plural y genero, suficiente para emparejar "tablas"/"tabla", "aprobada"/"aprobado"
        if len(w) > 4 and not re.search(r"\d", w):
            w = re.sub(r"(es|s)$", "", w) if not w.endswith("ss") else w
            w = re.sub(r"(a|o)$", "", w) if len(w) > 4 else w
        out.append(w)
    return out


def leer_jsonl(ruta):
    out = []
    try:
        for l in open(ruta, encoding="utf-8"):
            l = l.strip()
            if l:
                try:
                    out.append(json.loads(l))
                except Exception:
                    continue
    except FileNotFoundError:
        pass
    return out


def escribir_jsonl(ruta, filas):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for x in filas:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    os.replace(tmp, ruta)


def anexar_jsonl(ruta, fila):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")


class Mem:
    def __init__(self, coord):
        self.coord = coord
        self.dir = os.path.join(coord, "memoria")
        self.lecciones = os.path.join(self.dir, "lecciones.jsonl")
        self.indice = os.path.join(self.dir, "indice.json")
        self.consultas = os.path.join(self.dir, "consultas.jsonl")
        self.casos = os.path.join(self.dir, "evaluacion.jsonl")
        self.estado = os.path.join(self.dir, "estado.json")
        self.manuales = os.path.join(self.dir, "aprendizajes")

    def cargar_lecciones(self):
        return leer_jsonl(self.lecciones)


# ------------------------------------------------------------------ lecciones

def senal(l):
    """Multiplicador por retroalimentacion: origen, confirmaciones, utilidad y frescura."""
    util, no_util = l.get("util", 0), l.get("no_util", 0)
    m = PESO_FUENTE.get(l.get("fuente", "agente"), 1.0)
    m *= 1 + 0.15 * min(l.get("peso", 1) - 1, 4)             # confirmada varias veces
    m *= max(0.3, min(2.5, 1 + 0.25 * util - 0.4 * no_util))  # le sirvio / no le sirvio a quien la uso
    try:
        ref = l.get("ultima_util") or l.get("ts")
        dias = (ahora() - datetime.datetime.strptime(ref, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc)).days
        if util == 0 and l.get("fuente") != "usuario":        # lo que dijo el usuario no caduca solo
            m *= max(0.5, 0.5 ** (dias / DIAS_VIDA_MEDIA))
    except Exception:
        pass
    return m


def texto_leccion(l):
    return " ".join(filter(None, [l.get("texto", ""), " ".join(l.get("tags", [])), l.get("ref", ""),
                                  l.get("tipo", ""), l.get("agente", "")]))


def similitud(a, b):
    sa, sb = set(tokens(a)), set(tokens(b))
    return len(sa & sb) / len(sa | sb) if sa and sb else 0.0


def cmd_aprender(m):
    tipo, texto = arg("--tipo"), arg("--texto")
    if tipo not in TIPOS or not texto or len(texto.strip()) < 15:
        fallar(f"uso: aprender --tipo {{{'|'.join(TIPOS)}}} --texto \"que paso y que hacer la proxima vez\" "
               "[--agente A] [--ref ID] [--tags a,b] [--fuente usuario|qa|retro|agente]")
    fuente = arg("--fuente", "agente")
    if fuente not in PESO_FUENTE:
        fallar(f"--fuente debe ser una de: {', '.join(PESO_FUENTE)}")
    texto = " ".join(texto.split())
    lecciones = m.cargar_lecciones()
    for l in lecciones:
        if l.get("estado") != "retirada" and l.get("tipo") == tipo and similitud(l["texto"], texto) >= 0.75:
            l["peso"] = l.get("peso", 1) + 1
            l["ultima_confirmacion"] = iso()
            if PESO_FUENTE[fuente] > PESO_FUENTE.get(l.get("fuente", "agente"), 1):
                l["fuente"] = fuente
            escribir_jsonl(m.lecciones, lecciones)
            print(f"REFORZADA {l['id']} (ya existia; confirmaciones: {l['peso']}): {l['texto'][:140]}")
            return
    lid = "L-" + hashlib.sha1((iso() + texto).encode()).hexdigest()[:8]
    nueva = {"id": lid, "ts": iso(), "tipo": tipo, "agente": arg("--agente", ""), "ref": arg("--ref", ""),
             "texto": texto, "tags": [t.strip() for t in (arg("--tags", "") or "").split(",") if t.strip()],
             "fuente": fuente, "peso": 1, "usos": 0, "util": 0, "no_util": 0, "estado": "activa"}
    anexar_jsonl(m.lecciones, nueva)
    print(f"APRENDIDA {lid} [{tipo}/{fuente}]: {texto[:160]}")


def cmd_feedback(m):
    if len(sys.argv) < 4 or sys.argv[3] not in ("util", "no-util"):
        fallar("uso: feedback ID util|no-util [--nota \"...\"] [--consulta \"...\"]")
    lid, voto = sys.argv[2], sys.argv[3]
    lecciones = m.cargar_lecciones()
    for l in lecciones:
        if l["id"] == lid:
            if voto == "util":
                l["util"] = l.get("util", 0) + 1
                l["ultima_util"] = iso()
                consulta = arg("--consulta") or _ultima_consulta_con(m, lid)
                if consulta:  # caso confirmado: alimenta la evaluacion de la recuperacion
                    casos = leer_jsonl(m.casos)
                    if not any(c["consulta"] == consulta and lid in c["esperado"] for c in casos):
                        anexar_jsonl(m.casos, {"ts": iso(), "consulta": consulta, "esperado": [lid]})
            else:
                l["no_util"] = l.get("no_util", 0) + 1
                if l["no_util"] >= 3 and l["no_util"] > l.get("util", 0) and l.get("fuente") != "usuario":
                    l["estado"] = "retirada"
                    l["retirada"] = iso()
            if arg("--nota"):
                l.setdefault("notas", []).append({"ts": iso(), "voto": voto, "nota": arg("--nota")[:300]})
            escribir_jsonl(m.lecciones, lecciones)
            print(f"{lid}: util={l.get('util', 0)} no_util={l.get('no_util', 0)} estado={l.get('estado')}")
            return
    fallar(f"no existe la leccion {lid}", 1)


def _ultima_consulta_con(m, lid):
    for c in reversed(leer_jsonl(m.consultas)[-200:]):
        if lid in c.get("ids", []):
            return c.get("consulta")
    return None


# ------------------------------------------------------------------ indice de documentos

def fuentes_docs(m):
    """(ruta, clase) de los documentos a indexar. Crudos inmutables: solo se leen."""
    rutas = []
    for sub, clase, limite in (("wiki", "wiki", 2000), ("retros", "retro", 200),
                               ("handoffs", "handoff", 400), ("design", "diseno", 400)):
        base = os.path.join(m.coord, sub)
        encontrados = []
        for raiz, dirs, archivos in os.walk(base):
            dirs[:] = [d for d in dirs if not d.startswith((".", "_")) and d not in ("faast-kit", "node_modules")]
            for a in archivos:
                if a.endswith(".md") and not a.startswith(".") and a != "CLAUDE.md":
                    if clase == "diseno" and a not in ("decision.md", "00-brief.md", "design-spec.md",
                                                       "DESIGN.md", "solicitudes-libreria.md"):
                        continue
                    encontrados.append(os.path.join(raiz, a))
        encontrados.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        rutas += [(p, clase) for p in encontrados[:limite]]
    try:
        cfg = json.load(open(os.path.join(m.coord, "config.json"), encoding="utf-8"))
        extras = (cfg.get("memoria") or {}).get("fuentes") or []
        brain = (cfg.get("brain") or {}).get("path")
        if brain:
            extras = list(extras) + [brain]
        for base in extras:
            base = os.path.abspath(os.path.expanduser(base))
            n = 0
            for raiz, dirs, archivos in os.walk(base):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
                for a in archivos:
                    if a.endswith(".md") and n < 1500:
                        rutas.append((os.path.join(raiz, a), "fuente"))
                        n += 1
    except Exception:
        pass
    return rutas


def trocear(texto):
    """Trozos por encabezado Markdown, con la ruta de titulos como contexto."""
    trozos, titulos, actual = [], [], []

    def cerrar():
        cuerpo = "\n".join(actual).strip()
        if len(cuerpo) >= 40:
            ruta = " > ".join(t for t in titulos if t)
            for i in range(0, len(cuerpo), MAX_TROZO):
                trozos.append((ruta, cuerpo[i:i + MAX_TROZO]))
        actual.clear()

    en_codigo = False
    for linea in texto.splitlines():
        if linea.strip().startswith("```"):
            en_codigo = not en_codigo
        h = None if en_codigo else re.match(r"^(#{1,4})\s+(.*)", linea)
        if h:
            cerrar()
            nivel = len(h.group(1))
            titulos[:] = titulos[:nivel - 1] + [""] * max(0, nivel - 1 - len(titulos)) + [h.group(2).strip()]
        else:
            actual.append(linea)
    cerrar()
    return trozos


def cmd_indexar(m, silencioso=False):
    previo = {}
    try:
        previo = json.load(open(m.indice, encoding="utf-8"))
    except Exception:
        pass
    viejos = {d["ruta"]: d for d in previo.get("archivos", [])}
    archivos, reusados = [], 0
    for ruta, clase in fuentes_docs(m):
        try:
            mt = int(os.path.getmtime(ruta))
        except OSError:
            continue
        v = viejos.get(ruta)
        if v and v.get("mt") == mt:
            archivos.append(v)
            reusados += 1
            continue
        try:
            texto = open(ruta, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        trozos = [{"t": titulo, "x": cuerpo, "k": tokens(titulo + " " + cuerpo)} for titulo, cuerpo in trocear(texto)]
        archivos.append({"ruta": ruta, "clase": clase, "mt": mt, "trozos": trozos})
    os.makedirs(m.dir, exist_ok=True)
    with open(m.indice, "w", encoding="utf-8") as f:
        json.dump({"hecho": iso(), "archivos": archivos}, f, ensure_ascii=False)
    n = sum(len(a["trozos"]) for a in archivos)
    if not silencioso:
        print(f"Indice: {len(archivos)} documentos, {n} fragmentos ({reusados} sin cambios) → {m.indice}")
    return archivos


def cargar_indice(m):
    try:
        datos = json.load(open(m.indice, encoding="utf-8"))
        hecho = datetime.datetime.strptime(datos["hecho"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        if (ahora() - hecho).total_seconds() < 6 * 3600:
            return datos["archivos"]
    except Exception:
        pass
    return cmd_indexar(m, silencioso=True)


# ------------------------------------------------------------------ recuperacion

def bm25(consulta_tokens, documentos):
    """documentos: lista de listas de tokens. Devuelve puntajes."""
    n = len(documentos)
    if not n:
        return []
    largo_medio = sum(len(d) for d in documentos) / n or 1
    df = {}
    for d in documentos:
        for t in set(d):
            df[t] = df.get(t, 0) + 1
    puntajes = []
    for d in documentos:
        tf = {}
        for t in d:
            tf[t] = tf.get(t, 0) + 1
        s = 0.0
        for q in set(consulta_tokens):
            if q in tf:
                idf = math.log(1 + (n - df[q] + 0.5) / (df[q] + 0.5))
                s += idf * tf[q] * (K1 + 1) / (tf[q] + K1 * (1 - B + B * len(d) / largo_medio))
        puntajes.append(s)
    return puntajes


def recuperar(m, consulta, k=5, tipo=None, agente=None, solo=None, registrar=True, quien=""):
    q = tokens(consulta)
    resultados = []
    if solo != "docs":
        lecciones = [l for l in m.cargar_lecciones() if l.get("estado", "activa") == "activa"
                     and (not tipo or l.get("tipo") == tipo)]
        puntajes = bm25(q, [tokens(texto_leccion(l)) for l in lecciones])
        for l, s in zip(lecciones, puntajes):
            if s <= 0:
                continue
            s *= senal(l)
            if agente and (l.get("agente") == agente or l.get("tipo") in DOMINIO.get(agente, ())):
                s *= 1.25
            resultados.append({"clase": "leccion", "id": l["id"], "puntaje": s, "texto": l["texto"],
                               "meta": f"{l.get('tipo')}/{l.get('fuente')} · confirmaciones {l.get('peso', 1)} · "
                                       f"util {l.get('util', 0)}/no {l.get('no_util', 0)}"
                                       + (f" · {l['ref']}" if l.get("ref") else "")})
    if solo != "lecciones" and not tipo:
        planos = [(a, t) for a in cargar_indice(m) for t in a["trozos"]]
        puntajes = bm25(q, [t["k"] for _, t in planos])
        for (a, t), s in zip(planos, puntajes):
            if s > 0:
                rel = os.path.relpath(a["ruta"], m.coord) if a["ruta"].startswith(m.coord) else a["ruta"]
                peso = {"wiki": 1.15, "retro": 1.05, "diseno": 1.05}.get(a["clase"], 1.0)
                resultados.append({"clase": a["clase"], "id": rel, "puntaje": s * peso,
                                   "texto": t["x"], "meta": t["t"]})
    resultados.sort(key=lambda r: r["puntaje"], reverse=True)
    top = resultados[:k]
    if registrar and top:
        ids = [r["id"] for r in top if r["clase"] == "leccion"]
        anexar_jsonl(m.consultas, {"ts": iso(), "consulta": consulta, "agente": quien or agente or "",
                                   "ids": ids, "n": len(top)})
        if ids:
            lecciones = m.cargar_lecciones()
            for l in lecciones:
                if l["id"] in ids:
                    l["usos"] = l.get("usos", 0) + 1
            escribir_jsonl(m.lecciones, lecciones)
    return top


def cmd_buscar(m):
    if len(sys.argv) < 3 or sys.argv[2].startswith("--"):
        fallar("uso: buscar \"consulta\" [--tipo T] [--agente A] [--k 5] [--solo lecciones|docs] [--json]")
    consulta = sys.argv[2]
    top = recuperar(m, consulta, k=int(arg("--k", "5")), tipo=arg("--tipo"), agente=arg("--agente"),
                    solo=arg("--solo"))
    if "--json" in sys.argv:
        print(json.dumps(top, ensure_ascii=False, indent=2))
        return
    if not top:
        print(f"Sin resultados para «{consulta}». (La memoria crece con `aprender` y con la wiki.)")
        return
    for i, r in enumerate(top, 1):
        cuerpo = " ".join(r["texto"].split())
        if r["clase"] == "leccion":
            print(f"{i}. LECCION {r['id']} ({r['meta']})\n   {cuerpo[:600]}")
        else:
            print(f"{i}. [{r['clase']}] {r['id']}" + (f" — {r['meta']}" if r["meta"] else "") + f"\n   {cuerpo[:500]}")
    if any(r["clase"] == "leccion" for r in top):
        print("\nAl terminar, di si sirvieron: memoria.py feedback <ID> util|no-util")


def texto_para_agente(coord, agente, tarea="", k=4, registrar=False):
    """Bloque corto de lecciones para inyectar al iniciar un agente. Nunca lanza."""
    try:
        m = Mem(coord)
        activas = [l for l in m.cargar_lecciones() if l.get("estado", "activa") == "activa"
                   and (l.get("agente") == agente or l.get("tipo") in DOMINIO.get(agente, ()))]
        if not activas:
            return ""
        elegidas = []
        if tarea.strip():
            puntajes = bm25(tokens(tarea), [tokens(texto_leccion(l)) for l in activas])
            con = sorted(((s * senal(l), l) for l, s in zip(activas, puntajes) if s > 0),
                         key=lambda x: x[0], reverse=True)
            elegidas = [l for _, l in con[:k]]
        if len(elegidas) < k:  # completa con las mas validadas del agente
            resto = sorted((l for l in activas if l not in elegidas),
                           key=lambda l: (l.get("agente") == agente, senal(l)), reverse=True)
            elegidas += [l for l in resto if senal(l) >= 1.2][:k - len(elegidas)]
        if not elegidas:
            return ""
        if registrar:
            anexar_jsonl(m.consultas, {"ts": iso(), "consulta": tarea[:200], "agente": agente,
                                       "ids": [l["id"] for l in elegidas], "n": len(elegidas), "src": "inicio"})
        lineas = [f"- {l['id']} [{l.get('tipo')}/{l.get('fuente')}]: {l['texto'][:260]}" for l in elegidas]
        return ("LECCIONES DEL EQUIPO para esta tarea (memoria del proyecto; aplicalas, y al terminar "
                "marca cada una con memoria.py feedback <ID> util|no-util):\n" + "\n".join(lineas))
    except Exception:
        return ""


def cmd_para_agente(m):
    if len(sys.argv) < 3:
        fallar("uso: para-agente AGENTE [--tarea \"...\"] [--k 4]")
    print(texto_para_agente(m.coord, sys.argv[2], arg("--tarea", ""), int(arg("--k", "4")))
          or "(sin lecciones para este agente)")


# ------------------------------------------------------------------ correcciones del usuario

def correcciones_pendientes(coord, maximo=8):
    """Mensajes del usuario con forma de correccion/preferencia aun no revisados."""
    m = Mem(coord)
    try:
        visto = json.load(open(m.estado, encoding="utf-8")).get("pedidos_revisados_hasta", "")
    except Exception:
        visto = ""
    out = []
    for e in leer_jsonl(os.path.join(coord, "metrics", "pedidos-usuario.jsonl")):
        if e.get("ts", "") > visto and CORRECCION.search(e.get("texto", "")):
            out.append(e)
    return out[-maximo:]


def cmd_pendientes(m):
    pend = correcciones_pendientes(m.coord, 20)
    if "--revisadas" in sys.argv:
        os.makedirs(m.dir, exist_ok=True)
        with open(m.estado, "w", encoding="utf-8") as f:
            json.dump({"pedidos_revisados_hasta": iso()}, f)
        print("Marcadas como revisadas.")
        return
    if not pend:
        print("Sin correcciones del usuario pendientes de convertir en leccion.")
        return
    print(f"{len(pend)} mensaje(s) del usuario con forma de correccion o preferencia. Por cada uno que "
          "sea una regla para el futuro: memoria.py aprender --fuente usuario --tipo … --texto \"…\".\n"
          "Luego: memoria.py pendientes --revisadas\n")
    for e in pend:
        print(f"- {e['ts']}: {' '.join(e['texto'].split())[:420]}")


# ------------------------------------------------------------------ consolidar / metricas / evaluar

def cmd_consolidar(m):
    lecciones = m.cargar_lecciones()
    activas = [l for l in lecciones if l.get("estado", "activa") == "activa"]
    os.makedirs(m.manuales, exist_ok=True)
    por_agente = {}
    for agente, dominios in DOMINIO.items():
        propias = [l for l in activas if l.get("agente") == agente or
                   (not l.get("agente") and l.get("tipo") in dominios)]
        if propias:
            por_agente[agente] = sorted(propias, key=senal, reverse=True)
    for agente, ls in por_agente.items():
        partes = [f"# Aprendizajes de {agente}", "",
                  f"Generado por `memoria.py consolidar` el {iso()[:10]} desde `memoria/lecciones.jsonl`. "
                  "No editar a mano: corrige o retira la leccion de origen.", ""]
        for tipo in TIPOS:
            del_tipo = [l for l in ls if l.get("tipo") == tipo][:12]
            if del_tipo:
                partes += [f"## {tipo}", ""]
                for l in del_tipo:
                    marca = "★ " if l.get("fuente") == "usuario" else ""
                    partes.append(f"- {marca}{l['texto']} _( {l['id']} · {l.get('fuente')} · confirmada "
                                  f"{l.get('peso', 1)}× · util {l.get('util', 0)}"
                                  + (f" · {l['ref']}" if l.get("ref") else "") + " )_")
                partes.append("")
        with open(os.path.join(m.manuales, f"{agente}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(partes))
    candidatas = [l for l in activas if l.get("util", 0) >= 3 or l.get("peso", 1) >= 3
                  or (l.get("fuente") == "usuario" and l.get("peso", 1) >= 2)]
    dudosas = [l for l in activas if l.get("no_util", 0) > l.get("util", 0) and l.get("no_util", 0) >= 2]
    sin_uso = [l for l in activas if l.get("usos", 0) == 0 and
               (ahora() - datetime.datetime.strptime(l["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(
                   tzinfo=datetime.timezone.utc)).days > 90]
    informe = [f"# Consolidacion de la memoria — {iso()[:10]}", "",
               f"{len(activas)} lecciones activas · {len(lecciones) - len(activas)} retiradas · "
               f"manuales para {len(por_agente)} agentes en `memoria/aprendizajes/`.", "",
               "## Candidatas a regla permanente", "",
               "Validadas por uso repetido. Proponlas al usuario para incorporarlas al prompt del agente "
               "o a una skill del plugin (PR al marketplace); una vez incorporadas, retiralas de aqui.", ""]
    informe += [f"- **{l['id']}** [{l.get('tipo')}/{l.get('agente') or 'equipo'}] {l['texto']} "
                f"(confirmada {l.get('peso', 1)}×, util {l.get('util', 0)})" for l in candidatas] or ["- ninguna aun"]
    informe += ["", "## Para revisar (mas rechazos que aciertos)", ""]
    informe += [f"- {l['id']}: {l['texto'][:200]} (util {l.get('util', 0)} / no {l.get('no_util', 0)})"
                for l in dudosas] or ["- ninguna"]
    informe += ["", "## Sin uso en 90 dias", ""]
    informe += [f"- {l['id']}: {l['texto'][:160]}" for l in sin_uso] or ["- ninguna"]
    with open(os.path.join(m.dir, "consolidacion.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(informe) + "\n")
    print(f"Manuales: {len(por_agente)} agentes → {m.manuales}")
    print(f"Candidatas a regla permanente: {len(candidatas)} · para revisar: {len(dudosas)} · sin uso: {len(sin_uso)}")
    print(f"Informe: {os.path.join(m.dir, 'consolidacion.md')}")


def evaluar(m, k=5):
    casos = leer_jsonl(m.casos)
    if not casos:
        return None
    aciertos, mrr = 0, 0.0
    for c in casos:
        ids = [r["id"] for r in recuperar(m, c["consulta"], k=k, solo="lecciones", registrar=False)]
        rangos = [ids.index(e) + 1 for e in c["esperado"] if e in ids]
        if rangos:
            aciertos += 1
            mrr += 1 / min(rangos)
    return {"casos": len(casos), "recall": aciertos / len(casos), "mrr": mrr / len(casos), "k": k}


def cmd_evaluar(m):
    r = evaluar(m, int(arg("--k", "5")))
    if not r:
        print("Aun no hay casos confirmados: se crean solos cuando alguien marca una leccion como `util`.")
        return
    print(f"Recuperacion sobre {r['casos']} casos confirmados: recall@{r['k']} = {r['recall']:.0%} · MRR = {r['mrr']:.2f}")
    if r["recall"] < 0.7:
        print("Bajo 70 %: revisa lecciones duplicadas o mal redactadas (texto sin las palabras con que se busca).")


def cmd_metricas(m):
    ls = m.cargar_lecciones()
    activas = [l for l in ls if l.get("estado", "activa") == "activa"]
    consultas = leer_jsonl(m.consultas)
    votos_u = sum(l.get("util", 0) for l in ls)
    votos_n = sum(l.get("no_util", 0) for l in ls)
    print(f"Lecciones: {len(activas)} activas, {len(ls) - len(activas)} retiradas")
    for clave in ("tipo", "fuente"):
        cuenta = {}
        for l in activas:
            cuenta[l.get(clave) or "-"] = cuenta.get(l.get(clave) or "-", 0) + 1
        print(f"  por {clave}: " + ", ".join(f"{k} {v}" for k, v in sorted(cuenta.items(), key=lambda x: -x[1])))
    print(f"Consultas registradas: {len(consultas)} · con lecciones devueltas: {sum(1 for c in consultas if c.get('ids'))}")
    total = votos_u + votos_n
    print(f"Retroalimentacion: {votos_u} util / {votos_n} no-util" + (f" ({votos_u / total:.0%} util)" if total else ""))
    usadas_sin_voto = sum(1 for l in activas if l.get("usos", 0) and not (l.get("util", 0) + l.get("no_util", 0)))
    print(f"Lecciones usadas sin voto: {usadas_sin_voto} (pide el feedback a quien las uso)")
    r = evaluar(m)
    if r:
        print(f"Recuperacion: recall@{r['k']} {r['recall']:.0%} · MRR {r['mrr']:.2f} ({r['casos']} casos)")
    pend = correcciones_pendientes(m.coord, 50)
    print(f"Correcciones del usuario sin convertir en leccion: {len(pend)}")
    for l in sorted(activas, key=senal, reverse=True)[:5]:
        print(f"  ↑ {l['id']} ({senal(l):.2f}) {l['texto'][:110]}")


def cmd_listar(m):
    for l in m.cargar_lecciones():
        if arg("--tipo") and l.get("tipo") != arg("--tipo"):
            continue
        if arg("--agente") and l.get("agente") != arg("--agente"):
            continue
        if l.get("estado", "activa") != arg("--estado", "activa"):
            continue
        print(f"{l['id']} [{l.get('tipo')}/{l.get('fuente')}/{l.get('agente') or 'equipo'}] "
              f"x{l.get('peso', 1)} util {l.get('util', 0)}/no {l.get('no_util', 0)} — {l['texto'][:150]}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    cmds = {"indexar": cmd_indexar, "buscar": cmd_buscar, "aprender": cmd_aprender, "feedback": cmd_feedback,
            "para-agente": cmd_para_agente, "pendientes": cmd_pendientes, "consolidar": cmd_consolidar,
            "metricas": cmd_metricas, "evaluar": cmd_evaluar, "listar": cmd_listar}
    if sys.argv[1] not in cmds:
        fallar(f"comando desconocido: {sys.argv[1]}. Usa: {', '.join(cmds)}")
    cmds[sys.argv[1]](Mem(coord_dir()))


if __name__ == "__main__":
    main()
