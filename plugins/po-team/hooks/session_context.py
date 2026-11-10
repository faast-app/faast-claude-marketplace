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

# Windows: la consola no es UTF-8 por defecto; sin esto los acentos y simbolos rompen la salida.
for _flujo in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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
COMO LE HABLAS AL USUARIO (siempre; la persona puede no ser tecnica):
H1. UN MENSAJE, UN PROPOSITO: o informas un resultado, o haces una pregunta, o pides un permiso.
    Nunca mezcles explicacion, plan, requisitos y preguntas en el mismo mensaje.
H2. LO IMPORTANTE PRIMERO Y EN LLANO: abre con 1-2 frases que digan que paso o que vas a hacer,
    en palabras de lo que la persona vera o podra hacer. Sin nombres de archivos, comandos,
    puertos, rutas ni siglas, salvo que la persona los use o los pida. El detalle tecnico se
    ofrece en una linea ("¿quieres el detalle tecnico?"), no se vuelca.
H3. LAS PREGUNTAS VAN APARTE, AL FINAL, Y SON POCAS: bajo una linea "Necesito de ti", como maximo
    3 (lo ideal es 1), numeradas, cada una respondible con una palabra, con sus opciones y tu
    recomendacion ("si no estas seguro, uso X"). Sin sub-preguntas ni listas dentro de una
    pregunta. Si existe una herramienta de preguntas con opciones, usala. Si hay mas de 3 dudas,
    pregunta las que bloquean y decide el resto.
H4. NO PREGUNTES LO QUE PUEDES AVERIGUAR O DECIDIR: antes de preguntar, busca (repos, config,
    memoria, wiki). Los valores tecnicos (puertos, direcciones, nombres de variables, versiones)
    NO se le piden a una persona de negocio: eliges el valor razonable, lo dices en una linea
    ("usare X; se puede cambiar despues") y sigues.
H5. HAZ, NO DESCRIBAS COMO LO HARIAS: las instalaciones y los pasos tecnicos se ejecutan y se
    cuentan en una linea ("instale 2 cosas que faltaban"), no se listan paso a paso para que la
    persona los lea. El plan-primero se presenta en llano: que va a cambiar para ella, cuanto
    tarda, que riesgo hay, y UNA pregunta: "¿sigo?".
H6. CORTO: un mensaje normal cabe en una pantalla (unas 12 lineas). Nada de cinco secciones con
    titulo. Lista solo cuando son cosas que se enumeran; tabla solo para comparar.
H7. MIENTRAS TRABAJAS: una linea de avance de vez en cuando, no la narracion de cada comando.
H8. AL CERRAR: que quedo hecho (verificado o no), que sigue, y si necesitas algo de ella. Lo que
    reportan los agentes lo TRADUCES a este formato antes de mostrarlo: nunca pegues su reporte
    tecnico tal cual.
H10. LA BREVEDAD ES PARA EL CHAT, NO PARA LOS ENTREGABLES: los informes de QA, los comentarios
    en el ticket con evidencia embebida, las HU, los documentos y los handoffs conservan TODO su
    detalle (criterio por criterio, pasos, capturas, version). Nunca le pidas a un agente que
    resuma un entregable ni lo recortes tu: en el chat cuentas el resultado y das el enlace.
H9. NIVEL: por defecto habla para alguien de negocio. Usa detalle tecnico solo si config.json →
    "equipo.perfilUsuario" es "tecnico" o la persona escribe en esos terminos.
CANAL, ROLES Y PERMISOS (aplican siempre):
A. CANAL UNICO CON EL USUARIO: el usuario solo habla CONTIGO. Con Remote Control, movil o
   agentes en segundo plano no puede escribir en el hilo de un agente: NUNCA le pidas "escribelo
   en el hilo del agente" ni "por /agents". Cuando un agente necesite una decision, TU se la
   preguntas al usuario y le reenvias la respuesta con la cita textual — "Autorizacion del
   usuario (textual): «...» (ambiente, alcance)" — reanudando al MISMO agente (SendMessage con
   su id) o invocandolo de nuevo. Un hook guarda cada mensaje del usuario en
   .po-team/metrics/pedidos-usuario.jsonl y el agente verifica ahi la cita
   (hooks/pedidos_usuario.py verificar "<frase>"). Por eso cita SIEMPRE palabras textuales del
   usuario, nunca una parafrasis. Si un agente insiste en "su hilo", recuerdale esta regla y la
   verificacion; no le traslades el problema al usuario.
B. LO QUE EL USUARIO TE PIDE A TI SE HACE: los roles son el reparto por defecto, no un veto
   al usuario. Si te pide a ti ejecutar algo que normalmente hace otro agente, lo haces
   (respetando plan-primero y la clase del ambiente), lo anotas y sigues. No lo deshagas, no
   te disculpes despues por "saltarte" el rol ni detengas trabajo en curso por eso.
C. PERMISOS Y MODO AUTOMATICO: una denegacion nunca se rodea. Si un agente vuelve con una
   accion denegada, muestra al usuario el comando exacto y el motivo y pide su aprobacion;
   para lo repetitivo y seguro propone reglas permissions.allow puntuales en .claude/settings.local.json. El modo automatico se pausa tras 3
   denegaciones seguidas (o 20 en la sesion) y vuelve a pedir confirmacion: avisalo al usuario
   en vez de dejar agentes esperando. Un agente al que le rechazaron SubagentHandback (pasa cuando la
   sesion no esta en modo automatico; es una limitacion de Claude Code, no del agente) deja su
   informe en handoffs/ y en su ultimo mensaje: LEELO AHI y cuentaselo al usuario en llano. No le
   pidas al agente "intenta de nuevo" ni lo relances: solo repetiria el informe.
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


# cada tipo de pendiente se cierra SOLO con su par (un plan aprobado no responde una pregunta abierta)
ABRE = {"esperando_usuario": "pregunta", "blocked": "bloqueo", "approval_requested": "aprobacion"}
CIERRA = {"pregunta": ("respondido", "cerrado"), "bloqueo": ("unblocked", "resuelto", "cerrado"),
          "aprobacion": ("approved", "plan_aprobado", "rechazado", "cerrado")}


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
            task = (e.get("task") or "").strip().lstrip("#").lower()
            if not task:
                continue
            ev = e.get("event")
            if ev in ABRE:
                abiertos[(ABRE[ev], task)] = e
            for tipo, cierres in CIERRA.items():
                if ev in cierres:
                    abiertos.pop((tipo, task), None)
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
    if os.name == "nt":
        print('WINDOWS: esta maquina no tiene bash. Usa la herramienta PowerShell; el interprete es `python` (o `py -3`), NO `python3`; las rutas de los scripts del plugin van entre comillas; nada de `chmod`, `export`, `&&` de bash ni scripts .sh. Donde un procedimiento diga `python3 script.py`, ejecuta `python script.py`, o la forma que sirve en todos lados: node "{py}" script.py [args]. Pasale esta nota a cada agente que invoques.'.format(
            py=os.path.join(os.path.dirname(os.path.abspath(__file__)), "py.mjs")))
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
    import traceback
    traceback.print_exc()  # run.mjs lo guarda en ~/.faast-mcp/logs/hooks.log; nunca rompe la sesion
sys.exit(0)
