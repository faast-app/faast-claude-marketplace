#!/usr/bin/env python3
"""po-team — contexto de la SESION PRINCIPAL (SessionStart). Lo que imprime entra al contexto.

Resuelve la carpeta canonica del equipo del PO (.po-team, nunca dentro de un repo), excluye
localmente las carpetas de equipo del repo abierto (.git/info/exclude), crea la estructura minima
solo fuera de repos, imprime el protocolo, avisos de mantenimiento (config incompleto, tablero
viejo, fechas comprometidas vencidas) y los pendientes abiertos. Nunca falla hacia afuera.
"""
import datetime
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coord_root import repo_de, resolve  # noqa: E402

EXCLUIR = [".coordination/", ".coordination-root", ".mesa/", ".mesa-root", ".marketing/",
           ".marketing-root", ".po-team/", ".po-team-root", ".playwright-mcp/"]

SUBCARPETAS = ("tickets", "sprints", "handoffs", "metrics", "evidencia", "tablero/snapshots",
               "tablero/informes", "documentos", "manuales", "validaciones", "retros")

PROTOCOLO = """<po-team-protocolo>
Este proyecto usa el plugin po-team. En esta sesion TU eres el coordinador operativo del equipo
del Product Owner — aplicas las reglas del po-lead aunque no lo invoques:

1. PLAN PRIMERO: antes de cualquier accion que ESCRIBE en el tracker (crear o editar issues,
   mover estados, asignar sprint o puntos, comentar, etiquetar, subir evidencia, crear un
   Project) o que genera entregables para terceros, presenta en pocas lineas que se hara (que
   agente, que items, que cambia exactamente) y espera el OK. Solo-lectura (estado, tablero
   local, consultas) queda exento.
2. Delegacion: TU (sesion principal) y po-lead son los UNICOS que invocan agentes. Los
   subagentes no delegan (hook). Los comandos /po-team:* corren INLINE. Al equipo de desarrollo
   se le entrega trabajo como TICKET en el tracker, nunca invocando agentes de otro plugin.
3. PEDIDOS DEL USUARIO REENVIADOS: al invocar un agente por pedido del usuario escribe en el
   prompt "Pedido del usuario (textual): ..." y, si autorizo algo (p. ej. el plan de escritura),
   "Autorizacion del usuario: ...". Para el agente eso ES el pedido directo y el plan aprobado:
   no exige handoff ni re-confirmacion. Un reenvio NO salta una denegacion del sistema de
   permisos de Claude Code.
4. CARPETA .po-team/ FUERA DE LOS REPOS: usa siempre la ruta ABSOLUTA de abajo y pasala a cada
   agente. Nunca crees .po-team/ dentro de un repo (un hook lo bloquea). La evidencia del
   Playwright MCP se escribe primero en ~/.faast-mcp/po-team/ (staging, fuera de repos).
5. GATE — el validador-po NO reemplaza a QA: valida rapido los criterios de aceptacion (VB PO /
   Observado). Nunca mueve un ticket a los estados reservados a QA (tracker.reglas.estadosSoloQA)
   ni lo da por probado.
6. GATE — el PO redacta FUNCIONAL: HUs, bugs, comentarios, documentos y manuales en lenguaje de
   negocio, titulos limpios, criterios Gherkin; lo tecnico solo en un anexo separado.
7. GATE — evidencia EMBEBIDA: capturas/video en la rama huerfana `evidence` del repo configurado
   (nunca en ramas de trabajo) y embebidas en el ticket (`![](…/raw/evidence/…)` + link blob),
   nunca un link suelto. Secretos y datos personales redactados.
8. AMBIENTES POR CLASE, NO POR NOMBRE: cada ambiente del config declara `clase` ("pruebas" |
   "productivo"); nunca se presume. En "pruebas" crear operaciones, aprobar o girar son acciones
   normales de validacion (sin OK por paso). En "productivo" el validador-po y el manualista se
   detienen ANTES de cada accion que registre algo y piden autorizacion explicita por accion. Sin
   clase declarada: se pregunta UNA vez y se guarda (no se asume ninguna).
9. Nada hardcodeado: personas, organizacion, numeros de Project, campos, estados, ambientes, URLs
   y cuentas salen de .po-team/config.json (o se preguntan una vez y se guardan ahi). Cuentas de
   prueba solo por NOMBRE de variable de .po-team/accesos.env; jamas sus valores.
10. Nunca cerrar issues ni mover a estados finales salvo que el config lo permita
    (tracker.reglas.cerrarIssues) y el usuario lo confirme.
11. PENDIENTES: lo que espera respuesta del PO, de la Mesa o del cliente se registra (evento
    esperando_usuario con el ticket en `task`) y se lista al iniciar la sesion (abajo); retomalo
    apenas haya respuesta y registra "respondido".
12. Modelo por agente: team.models.{agente} en .po-team/config.json y luego
    ~/.claude/po-team.config.json; default sonnet (setup: haiku fijo); fable prohibido.
</po-team-protocolo>"""


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


def pendientes(po):
    ruta = os.path.join(po, "metrics", "activity.jsonl")
    if not os.path.exists(ruta):
        return []
    limite = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=21)
    abiertos = {}
    try:
        for linea in open(ruta, encoding="utf-8", errors="replace"):
            try:
                e = json.loads(linea)
            except Exception:
                continue
            task = (e.get("task") or "").strip()
            if not task:
                continue
            if e.get("event") in ("esperando_usuario", "blocked", "approval_requested"):
                abiertos[task] = e
            elif e.get("event") in ("respondido", "unblocked", "resuelto", "cerrado", "approved",
                                    "plan_aprobado"):
                abiertos.pop(task, None)
    except Exception:
        return []
    salida = []
    for e in abiertos.values():
        try:
            ts = datetime.datetime.strptime(e.get("ts", ""), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        except Exception:
            continue
        if ts >= limite:
            salida.append((ts, e))
    return sorted(salida, key=lambda x: x[0], reverse=True)[:12]


def avisos_config(c):
    avisos = []
    gh = ((c.get("tracker") or {}).get("github") or {})
    if (c.get("tracker") or {}).get("provider", "github") == "github":
        projs = gh.get("projects") or []
        if not projs or all(not p.get("numero") for p in projs):
            avisos.append("No hay ningun GitHub Project configurado: /po-team:setup tracker o "
                          "/po-team:tablero crear-backlog.")
    amb = c.get("ambientes") or {}
    sin_clase = []
    for k, v in amb.items():
        for a in (v if isinstance(v, list) else [v]):
            if isinstance(a, dict) and a.get("url") and a.get("clase") not in ("pruebas", "productivo"):
                sin_clase.append(a.get("nombre") or a.get("clave") or k)
    if sin_clase:
        avisos.append("Ambientes sin `clase` (pruebas | productivo) declarada — se preguntara antes de validar en ellos: "
                      + ", ".join(sin_clase) + ". Declararla con /po-team:setup ambientes.")
    return avisos


def avisos_estado(po):
    avisos = []
    datos = os.path.join(po, "tablero", "tablero-datos.json")
    if os.path.exists(datos):
        horas = (datetime.datetime.now().timestamp() - os.path.getmtime(datos)) / 3600
        if horas > 24:
            avisos.append(f"El tablero tiene {int(horas // 24)} dia(s): /po-team:tablero para refrescarlo.")
    hoy = datetime.date.today()
    for ruta in glob.glob(os.path.join(po, "sprints", "*.json")):
        try:
            s = json.load(open(ruta, encoding="utf-8"))
        except Exception:
            continue
        if s.get("cerrado"):
            continue
        fechas = s.get("fechas") or {}
        planas = []
        for clave, val in fechas.items():
            if isinstance(val, dict):
                planas += [(f"{clave} {k}", v) for k, v in val.items()]
            else:
                planas.append((clave, val))
        vencidas = []
        for nombre, val in planas:
            try:
                if datetime.date.fromisoformat(str(val)[:10]) < hoy:
                    vencidas.append(f"{nombre} {val}")
            except Exception:
                continue
        if vencidas and s.get("fin") and str(s.get("fin")) >= (hoy - datetime.timedelta(days=14)).isoformat():
            avisos.append(f"{s.get('nombre', os.path.basename(ruta))}: fechas comprometidas ya pasadas "
                          f"({', '.join(vencidas[:4])}); confirmar con el tablero si se cumplieron.")
    return avisos


def main():
    start = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    excluir_en_git(start)
    r = resolve(start)
    po = r["path"]
    if not po or not os.path.isfile(os.path.join(po, "config.json")):
        return
    if not r["en_repo"]:
        try:
            for sub in SUBCARPETAS:
                os.makedirs(os.path.join(po, sub), exist_ok=True)
        except Exception:
            pass
    print(PROTOCOLO)
    print("<po-team-mantenimiento>")
    print(f"Carpeta canonica del equipo del PO (ruta ABSOLUTA, usala siempre y pasala a cada agente): {po}")
    if r["en_repo"]:
        print(f"LA CARPETA DEL PO ESTA DENTRO DE UN REPO ({po}): propone al usuario moverla (mv) a una carpeta "
              "fuera de repos y registrarla en ~/.claude/po-team.config.json → \"proyectos\": "
              "{\"<ruta del repo>\": \"<carpeta que contiene .po-team>\"}. Sacarla del historial del repo es "
              "un PR aparte, solo con OK. Mientras tanto un hook bloquea escribir ahi.")
    if r.get("desvio"):
        print(f"Hay una .po-team sin config en {r['desvio']} (desvio): no escribir ahi; consolidar con la canonica.")
    try:
        c = json.load(open(os.path.join(po, "config.json"), encoding="utf-8"))
        for a in avisos_config(c):
            print(a)
    except Exception:
        print("config.json ilegible: correr /po-team:setup.")
    for a in avisos_estado(po):
        print(a)
    print("</po-team-mantenimiento>")
    pend = pendientes(po)
    if pend:
        print("<po-team-pendientes>")
        print("Pendientes abiertos: muestralos al usuario en una lista corta al primer momento oportuno y "
              "pregunta como seguir; no los dejes caer:")
        for ts, e in pend:
            tipo = {"esperando_usuario": "espera respuesta", "approval_requested": "espera aprobacion"}.get(
                e.get("event"), "bloqueado")
            print(f"- [{e.get('agent', '?')}] {e.get('task')} — {tipo} desde {ts:%Y-%m-%d}: {(e.get('detail') or '')[:160]}")
        print("</po-team-pendientes>")


try:
    main()
except Exception:
    pass
sys.exit(0)
