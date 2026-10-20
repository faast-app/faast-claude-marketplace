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
    pass
sys.exit(0)
