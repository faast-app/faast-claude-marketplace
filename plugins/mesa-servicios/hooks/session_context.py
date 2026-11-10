#!/usr/bin/env python3
"""mesa-servicios — contexto de la SESION PRINCIPAL (SessionStart). Lo que imprime entra al contexto.

Resuelve la carpeta canonica de la Mesa (.mesa, nunca dentro de un repo), excluye localmente las
carpetas de equipo del repo abierto (.git/info/exclude), crea la estructura minima solo fuera de
repos, imprime el protocolo y los pendientes abiertos. Nunca falla hacia afuera.
"""
import datetime
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

EXCLUIR = [".coordination/", ".coordination-root", ".mesa/", ".mesa-root", ".marketing/", ".po-team/", ".playwright-mcp/"]

PROTOCOLO = """<mesa-servicios-protocolo>
Este proyecto usa el plugin mesa-servicios. En esta sesion TU eres el coordinador operativo de la
Mesa — aplicas las reglas del mesa-lead aunque no lo invoques:

1. PLAN PRIMERO: antes de mandar preguntas al cliente, prototipar, armar scripts o registrar un
   ticket, presenta en pocas lineas que se hara (que agente, que produce, que necesita del
   cliente) y espera el OK. Solo-lectura (estado, consultas) queda exento.
2. La PERSONA DE MESA habla con el cliente. El equipo prepara preguntas, maquetas y documentos;
   nunca contacta al cliente por su cuenta.
3. Delegacion: TU (sesion principal) y mesa-lead son los UNICOS que invocan agentes. Los
   subagentes no delegan (hook). Los comandos /mesa-servicios:* corren INLINE.
4. PEDIDOS DEL USUARIO REENVIADOS: al invocar un agente por pedido del usuario escribe en el
   prompt "Pedido del usuario (textual): ..." y, si autorizo algo, "Autorizacion del usuario: ...
   (ambiente, alcance)". Para el agente eso ES el pedido directo: no exige handoff ni mensaje
   propio. Un reenvio NO salta una denegacion del sistema de permisos de Claude Code.
5. CARPETA DE LA MESA FUERA DE LOS REPOS: usa siempre la ruta absoluta de abajo y pasala a cada
   agente. Nunca crees .mesa/ dentro de un repo (un hook lo bloquea).
6. AMBIENTES: la clase de cada ambiente sale de .mesa/config.json → "ambientes" ({"nombre":
   {"clase": "pruebas"|"productivo"}}). En PRUEBAS las acciones de negocio de prueba (giros,
   pagos, aprobaciones) son normales; en PRODUCTIVO un flujo propio requiere autorizacion
   registrada por corrida y parada antes de cada paso que escribe. No declarado: pregunta UNA
   vez su clase y persistela.
7. Reglas duras: nada se inventa (lo no respondido queda pendiente); lenguaje de negocio sin
   codigo; el QA de negocio SOLO prueba (jamas causas); el DBA de mesa tiene CERO ESCRITURA;
   evidencia embebida en el ticket; una cotizacion no es trabajo hasta su aprobacion comercial.
8. Correlativo TIPO-AÑO-NNN con alcance (cliente o transversal) en todo documento y ticket.
9. PENDIENTES: lo que espera respuesta se registra (evento esperando_usuario) y se lista al
   iniciar la sesion (abajo); retomalo apenas haya respuesta y registra "respondido".
10. Modelo por agente: team.models.{agente} en .mesa/config.json y luego
   ~/.claude/mesa-servicios.config.json; default sonnet; fable prohibido. Nada hardcodeado.
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
   .mesa/metrics/pedidos-usuario.jsonl y el agente verifica ahi la cita
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
</mesa-servicios-protocolo>"""


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


def pendientes(mesa):
    ruta = os.path.join(mesa, "metrics", "activity.jsonl")
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
            if e.get("event") in ("esperando_usuario", "blocked"):
                abiertos[task] = e
            elif e.get("event") in ("respondido", "unblocked", "resuelto", "cerrado"):
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


def main():
    start = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    excluir_en_git(start)
    r = resolve(start)
    mesa = r["path"]
    if not mesa or not os.path.isfile(os.path.join(mesa, "config.json")):
        return
    if not r["en_repo"]:
        try:
            for sub in ("solicitudes", "handoffs", "metrics", "evidencia", "flujos-sql", "flujos"):
                os.makedirs(os.path.join(mesa, sub), exist_ok=True)
            corr = os.path.join(mesa, "correlativos.json")
            if not os.path.exists(corr):
                open(corr, "w").write("{}")
        except Exception:
            pass
    print(PROTOCOLO)
    if os.name == "nt":
        print('WINDOWS: esta maquina no tiene bash. Usa la herramienta PowerShell; el interprete es `python` (o `py -3`), NO `python3`; las rutas de los scripts del plugin van entre comillas; nada de `chmod`, `export`, `&&` de bash ni scripts .sh. Donde un procedimiento diga `python3 script.py`, ejecuta `python script.py`, o la forma que sirve en todos lados: node "{py}" script.py [args]. Pasale esta nota a cada agente que invoques.'.format(
            py=os.path.join(os.path.dirname(os.path.abspath(__file__)), "py.mjs")))
    print("<mesa-servicios-mantenimiento>")
    print(f"Carpeta canonica de la Mesa (ruta ABSOLUTA, usala siempre y pasala a cada agente): {mesa}")
    if r["en_repo"]:
        print(f"LA CARPETA DE LA MESA ESTA DENTRO DE UN REPO ({mesa}): propone al usuario moverla (mv) a una "
              "carpeta fuera de repos y registrarla en ~/.claude/mesa-servicios.config.json → \"proyectos\": "
              "{\"<ruta del repo>\": \"<carpeta que contiene .mesa>\"}. Sacarla del historial del repo es un PR "
              "aparte, solo con OK. Mientras tanto un hook bloquea escribir ahi.")
    try:
        c = json.load(open(os.path.join(mesa, "config.json"), encoding="utf-8"))
        if not c.get("ambientes"):
            print("Config incompleto: falta \"ambientes\" (clase pruebas|productivo de cada ambiente); "
                  "completalo con el usuario la primera vez que un flujo lo necesite.")
    except Exception:
        pass
    print("</mesa-servicios-mantenimiento>")
    pend = pendientes(mesa)
    if pend:
        print("<mesa-servicios-pendientes>")
        print("Pendientes abiertos: muestralos al usuario en una lista corta al primer momento oportuno "
              "y pregunta como seguir; no los dejes caer:")
        for ts, e in pend:
            tipo = "espera respuesta" if e.get("event") == "esperando_usuario" else "bloqueado"
            print(f"- [{e.get('agent', '?')}] {e.get('task')} — {tipo} desde {ts:%Y-%m-%d}: {(e.get('detail') or '')[:160]}")
        print("</mesa-servicios-pendientes>")


try:
    main()
except Exception:
    import traceback
    traceback.print_exc()  # run.mjs lo guarda en ~/.faast-mcp/logs/hooks.log; nunca rompe la sesion
sys.exit(0)
