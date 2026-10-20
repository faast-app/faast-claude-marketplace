#!/usr/bin/env python3
"""dev-team — contexto de la SESION PRINCIPAL (SessionStart). Lo que imprime entra al contexto.

1. Resuelve la coordinacion canonica (coord_root.py) e indica su ruta ABSOLUTA.
2. Si la coordinacion esta dentro de un repo (proyecto legado), pide migrarla.
3. Excluye localmente (.git/info/exclude, nada commiteado) las carpetas de equipo del repo abierto.
4. Auto-migracion de estructura solo sobre la coordinacion canonica fuera de repos.
5. Protocolo del equipo + pendientes abiertos (lo que espera respuesta del usuario).
Nunca falla hacia afuera.
"""
import datetime
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coord_root import repo_de, resolve  # noqa: E402

PLUGIN_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUIR = [".coordination/", ".coordination-root", ".mesa/", ".marketing/", ".po-team/", ".playwright-mcp/"]
DIAS_PENDIENTES = 21
MAX_PENDIENTES = 12

PROTOCOLO = """<dev-team-protocolo-sesion-principal>
Este proyecto usa el plugin dev-team. En esta sesion TU eres el coordinador operativo del
equipo — aplicas las reglas del Lead aunque no lo invoques:

1. PLAN PRIMERO (obligatorio): antes de ejecutar una feature o un fix (crear branches, asignar,
   implementar, tocar ambientes), presenta el plan al usuario (que/quien/donde/riesgos) y espera
   su confirmacion. Solo-lectura (status, analisis) queda exento.
2. Delegacion: TU (sesion principal) y el agente lead son los UNICOS que invocan agentes del
   equipo (varios en paralelo si son independientes). Los subagentes no delegan (hook). Los
   comandos /dev-team:* corren INLINE.
3. PEDIDOS DEL USUARIO REENVIADOS: cuando el usuario pide algo para un agente ("que el dba
   haga X"), al invocarlo escribe en el prompt "Pedido del usuario (textual): ..." y, si el
   usuario autorizo una accion, "Autorizacion del usuario: ... (ambiente, alcance)". Para el
   agente eso ES el pedido directo del usuario: no necesita handoff ni mensaje propio. Lo mismo
   vale para lo que reenvies a mitad de su trabajo. Lo unico que un reenvio NO salta es una
   denegacion del sistema de permisos de Claude Code: esa la aprueba el usuario en la sesion.
4. COORDINACION FUERA DE LOS REPOS: usa SIEMPRE la ruta absoluta de la coordinacion canonica
   (abajo) y pasala en cada invocacion. Nunca crees .coordination/ dentro de un repo (un hook lo
   bloquea).
5. AMBIENTES: la clase de cada ambiente sale de config.json → "ambientes" ({"nombre": {"clase":
   "pruebas"|"productivo"}}). En PRUEBAS, giros, pagos, aprobaciones y desembolsos son acciones
   de prueba normales: se ejecutan sin pedir OK en cada paso. Solo un ambiente PRODUCTIVO exige
   autorizacion explicita del usuario por accion sensible. Ambiente no declarado: pregunta UNA
   vez al usuario su clase y persistela en config.json.
6. QA y conformidad: el informe de conformidad de despliegue es OPCIONAL salvo que config.json
   → "qa.conformidad" sea "obligatoria". Sin informe, QA registra la version que observa
   (pantalla de version, /health, o la que indique el usuario) y valida; nunca se bloquea solo
   por falta del informe. QA no debuggea y reporta a la primera falla; evidencia embebida en el
   item; los pases van via release-manager; merges via lead con sus gates.
7. PENDIENTES: lo que espera respuesta del usuario se registra (evento esperando_usuario) y se
   lista al iniciar cada sesion (abajo). Retoma cada pendiente apenas el usuario responda y
   registra "respondido".
8. El PO redacta items 100% funcionales; los bugs siguen crear→corregir→revalidar→cerrar (el
   cierre lo confirma el usuario).
9. Modelo por agente: team.models.{agente} en config.json y luego ~/.claude/dev-team.config.json
   (haiku fijos: setup y tech-writer; fable prohibido). Nada hardcodeado de personas/valores.
</dev-team-protocolo-sesion-principal>"""


def excluir_en_git(start):
    repo = repo_de(start)
    if not repo:
        return
    try:
        out = subprocess.run(["git", "-C", repo, "rev-parse", "--git-path", "info/exclude"],
                             capture_output=True, text=True, timeout=5)
        ruta = out.stdout.strip()
        if not ruta:
            return
        if not os.path.isabs(ruta):
            ruta = os.path.join(repo, ruta)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        actual = open(ruta, encoding="utf-8").read() if os.path.exists(ruta) else ""
        faltan = [l for l in EXCLUIR if l not in actual.splitlines()]
        if faltan:
            with open(ruta, "a", encoding="utf-8") as f:
                f.write(("\n" if actual and not actual.endswith("\n") else "")
                        + "# equipos FAAST (local, no se commitea)\n" + "\n".join(faltan) + "\n")
    except Exception:
        pass


def auto_migrar(coord):
    try:
        for sub in ("wiki", "metrics", "evidence", "pases", "handoffs/archive", "test-plans"):
            os.makedirs(os.path.join(coord, sub), exist_ok=True)
        wiki = os.path.join(coord, "wiki")
        tpl = os.path.join(PLUGIN_ROOT, "templates", "coordination-wiki", "CLAUDE.md")
        if not os.path.exists(os.path.join(wiki, "CLAUDE.md")) and os.path.exists(tpl):
            open(os.path.join(wiki, "CLAUDE.md"), "w", encoding="utf-8").write(open(tpl, encoding="utf-8").read())
        if not os.path.exists(os.path.join(wiki, "index.md")):
            open(os.path.join(wiki, "index.md"), "w", encoding="utf-8").write(
                "# Wiki del proyecto\n\nPortada pendiente de primer ingest: corre /dev-team:wiki ingest\n")
        log = os.path.join(wiki, ".ingested.log")
        if not os.path.exists(log):
            open(log, "w").close()
    except Exception:
        pass


def huecos_config(coord):
    try:
        c = json.load(open(os.path.join(coord, "config.json"), encoding="utf-8"))
    except Exception:
        return []
    gaps = []
    if not (c.get("git") or {}).get("defaultBranch"):
        gaps.append("git.defaultBranch")
    if not (c.get("git") or {}).get("identity"):
        gaps.append("git.identity")
    if not (c.get("tracker") or {}).get("reviewer"):
        gaps.append("tracker.reviewer")
    if not c.get("ambientes"):
        gaps.append("ambientes (clase pruebas|productivo de cada ambiente)")
    return gaps


def pendientes(coord):
    ruta = os.path.join(coord, "metrics", "activity.jsonl")
    if not os.path.exists(ruta):
        return []
    limite = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=DIAS_PENDIENTES)
    abiertos = {}
    try:
        for linea in open(ruta, encoding="utf-8", errors="replace"):
            try:
                e = json.loads(linea)
            except Exception:
                continue
            task = (e.get("task") or "").strip()
            ev = e.get("event")
            if not task:
                continue
            if ev in ("esperando_usuario", "blocked"):
                abiertos[task] = e
            elif ev in ("respondido", "unblocked", "resuelto", "cerrado"):
                abiertos.pop(task, None)
    except Exception:
        return []
    salida = []
    for task, e in abiertos.items():
        try:
            ts = datetime.datetime.strptime(e.get("ts", ""), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        except Exception:
            continue
        if ts < limite:
            continue
        salida.append((ts, e))
    salida.sort(key=lambda x: x[0], reverse=True)
    return salida[:MAX_PENDIENTES]


def main():
    start = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    excluir_en_git(start)
    r = resolve(start)
    coord = r["path"]
    if not coord:
        return
    tiene_config = os.path.isfile(os.path.join(coord, "config.json"))
    if tiene_config and not r["en_repo"]:
        auto_migrar(coord)

    print(PROTOCOLO)
    avisos = [f"Coordinacion canonica (ruta ABSOLUTA, usala siempre y pasala a cada agente): {coord}"]
    if r["en_repo"]:
        avisos.append(
            f"COORDINACION DENTRO DE UN REPO: {coord} esta dentro de un repositorio git y eso contamina "
            "el repo. Propone al usuario migrarla (con su OK): (1) acordar la carpeta del proyecto (la "
            "que contiene el repo o una dedicada fuera de repos), (2) mover .coordination/ ahi con mv, "
            "(3) registrar en ~/.claude/dev-team.config.json → \"proyectos\": {\"<ruta del repo>\": "
            "\"<carpeta del proyecto>\"}, (4) sacarla del historial del repo es un PR aparte, solo con OK "
            "explicito. Mientras tanto un hook bloquea escribir dentro de esa carpeta.")
    if not tiene_config:
        avisos.append(
            f"ATENCION: {coord} NO tiene config.json — probable DESVIO de la coordinacion canonica. "
            "Pregunta al usuario cual es la carpeta del proyecto, registrala en "
            "~/.claude/dev-team.config.json → \"proyectos\", fusiona lo util del desvio y eliminalo (con su OK).")
    if r.get("desvio"):
        avisos.append(f"DESVIO DETECTADO: existe una .coordination sin config.json en {r['desvio']}. "
                      "Propone fusionarla en la canonica y eliminarla. NO lo hagas sin OK.")
    if tiene_config:
        gaps = huecos_config(coord)
        if gaps:
            avisos.append("Config incompleto (faltan: " + ", ".join(gaps) + ") — completa cada clave CON el "
                          "usuario la primera vez que un flujo la necesite y persistela en config.json.")
        log = os.path.join(coord, "wiki", ".ingested.log")
        if os.path.exists(log) and os.path.getsize(log) == 0:
            avisos.append("La wiki esta vacia: menciona UNA vez que puede poblarse con /dev-team:wiki ingest "
                          "(no lo ejecutes sin OK).")
    print("<dev-team-mantenimiento>")
    for a in avisos:
        print(a)
    print("</dev-team-mantenimiento>")

    pend = pendientes(coord)
    if pend:
        print("<dev-team-pendientes>")
        print("Pendientes abiertos (esperan respuesta del usuario o estan bloqueados). Al primer momento "
              "oportuno, muestralos al usuario en una lista corta y pregunta como seguir; no los dejes caer:")
        for ts, e in pend:
            tipo = "espera respuesta" if e.get("event") == "esperando_usuario" else "bloqueado"
            print(f"- [{e.get('agent', '?')}] {e.get('task')} — {tipo} desde {ts:%Y-%m-%d}: "
                  f"{(e.get('detail') or '')[:160]}")
        print("</dev-team-pendientes>")


try:
    main()
except Exception:
    pass
sys.exit(0)
