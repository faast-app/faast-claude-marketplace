#!/usr/bin/env python3
"""marketing — contexto de la SESION PRINCIPAL (SessionStart). Lo que imprime entra al contexto.

Resuelve la carpeta canonica de Marketing (.marketing, nunca dentro de un repo), excluye
localmente las carpetas de equipo del repo abierto (.git/info/exclude), crea la estructura minima
solo fuera de repos, imprime el protocolo, las tendencias vencidas y los pendientes abiertos.
Nunca falla hacia afuera.
"""
import datetime
import json
import os
import re
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

PROTOCOLO = """<marketing-protocolo>
Este proyecto usa el plugin marketing. En esta sesion TU eres el coordinador operativo del equipo
de Marketing, Ventas y Publicidad — aplicas las reglas del director-marketing aunque no lo invoques:

1. PLAN PRIMERO: antes de investigar en serio, desglosar, producir una pieza o refrescar
   tendencias, presenta en pocas lineas que se hara (que agente, que produce, que necesita del
   usuario) y espera el OK. Solo-lectura (estado, consultas) queda exento.
2. EL PRODUCTO DESGLOSADO, NUNCA GENERICO: el primer entregable de toda campana es el MAPA DEL
   PRODUCTO (modulos, capacidades, mejoras) con una FICHA por parte (que es y para quien; problema
   y su costo; como funciona con pantallas reales; que gana el cliente en numeros con fuente;
   antes/despues; benchmark). Sin mapa y fichas APROBADOS por el usuario no se produce ninguna
   pieza. Las piezas siguen el desglose (deck: una seccion por parte; video: un capitulo por parte
   + clip por parte; impreso: one-pager con el desglose + panfleto por parte).
3. Delegacion: TU (sesion principal) y director-marketing son los UNICOS que invocan agentes. Los
   subagentes no delegan (hook). Los comandos /marketing:* corren INLINE.
4. PEDIDOS DEL USUARIO REENVIADOS: al invocar un agente por pedido del usuario escribe en el prompt
   "Pedido del usuario (textual): ..." y, si autorizo algo, "Autorizacion del usuario: ...". Para el
   agente eso ES el pedido directo: no exige handoff ni mensaje propio. Un reenvio NO salta una
   denegacion del sistema de permisos de Claude Code.
5. CARPETA .marketing/ FUERA DE LOS REPOS: usa siempre la ruta absoluta de abajo y pasala a cada
   agente. Nunca crees .marketing/ dentro de un repo (un hook lo bloquea).
6. Reglas duras: nada se inventa (cada cifra, comparacion o afirmacion con fuente y fecha; sin
   respaldo = SUPUESTO marcado); el producto se muestra REAL (capturas, prototipos o maquetas del
   proyecto, nunca pantallas imaginadas); ninguna pieza sale sin aprobacion del usuario;
   confidencialidad (sin datos de clientes ni informacion interna en piezas externas); nada de
   marcas de terceros como si fueran propias; precios solo los que entrega comercial.
7. Capturas del producto solo en ambientes de pruebas/demo con datos ficticios.
8. PENDIENTES: lo que espera respuesta se registra (evento esperando_usuario) y se lista al iniciar
   la sesion (abajo); retomalo apenas haya respuesta y registra "respondido".
9. Modelo por agente: team.models.{agente} en .marketing/config.json y luego
   ~/.claude/marketing.config.json; default sonnet; fable prohibido. Nada hardcodeado.
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
H9. NIVEL: por defecto habla para alguien de negocio. Usa detalle tecnico solo si config.json →
    "equipo.perfilUsuario" es "tecnico" o la persona escribe en esos terminos.
CANAL, ROLES Y PERMISOS (aplican siempre):
A. CANAL UNICO CON EL USUARIO: el usuario solo habla CONTIGO. Con Remote Control, movil o
   agentes en segundo plano no puede escribir en el hilo de un agente: NUNCA le pidas "escribelo
   en el hilo del agente" ni "por /agents". Cuando un agente necesite una decision, TU se la
   preguntas al usuario y le reenvias la respuesta con la cita textual — "Autorizacion del
   usuario (textual): «...» (ambiente, alcance)" — reanudando al MISMO agente (SendMessage con
   su id) o invocandolo de nuevo. Un hook guarda cada mensaje del usuario en
   .marketing/metrics/pedidos-usuario.jsonl y el agente verifica ahi la cita
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
</marketing-protocolo>"""


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


def pendientes(mk):
    ruta = os.path.join(mk, "metrics", "activity.jsonl")
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
                                    "changes_requested"):
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


def tendencias_vencidas(mk):
    """Cuenta tendencias con `vigente_hasta: AAAA-MM-DD` anterior a hoy."""
    carpeta = os.path.join(mk, "tendencias")
    if not os.path.isdir(carpeta):
        return 0, 0
    hoy = datetime.date.today()
    total = vencidas = 0
    patron = re.compile(r"vigente_hasta:\s*(\d{4}-\d{2}-\d{2})")
    try:
        for nombre in os.listdir(carpeta):
            if not nombre.endswith(".md") or nombre.upper() == "INDEX.MD":
                continue
            try:
                texto = open(os.path.join(carpeta, nombre), encoding="utf-8", errors="replace").read(2000)
            except Exception:
                continue
            m = patron.search(texto)
            if not m:
                continue
            total += 1
            try:
                if datetime.date.fromisoformat(m.group(1)) < hoy:
                    vencidas += 1
            except Exception:
                pass
    except Exception:
        pass
    return total, vencidas


def main():
    start = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    excluir_en_git(start)
    r = resolve(start)
    mk = r["path"]
    if not mk or not os.path.isfile(os.path.join(mk, "config.json")):
        return
    if not r["en_repo"]:
        try:
            for sub in ("campanas", "handoffs", "metrics", "tendencias", "marca"):
                os.makedirs(os.path.join(mk, sub), exist_ok=True)
            corr = os.path.join(mk, "correlativos.json")
            if not os.path.exists(corr):
                open(corr, "w").write("{}")
        except Exception:
            pass
    print(PROTOCOLO)
    if os.name == "nt":
        print('WINDOWS: esta maquina no tiene bash. Usa la herramienta PowerShell; el interprete es `python` (o `py -3`), NO `python3`; las rutas de los scripts del plugin van entre comillas; nada de `chmod`, `export`, `&&` de bash ni scripts .sh. Donde un procedimiento diga `python3 script.py`, ejecuta `python script.py`, o la forma que sirve en todos lados: node "{py}" script.py [args]. Pasale esta nota a cada agente que invoques.'.format(
            py=os.path.join(os.path.dirname(os.path.abspath(__file__)), "py.mjs")))
    print("<marketing-mantenimiento>")
    print(f"Carpeta canonica de Marketing (ruta ABSOLUTA, usala siempre y pasala a cada agente): {mk}")
    if r["en_repo"]:
        print(f"LA CARPETA DE MARKETING ESTA DENTRO DE UN REPO ({mk}): propone al usuario moverla (mv) a una "
              "carpeta fuera de repos y registrarla en ~/.claude/marketing.config.json → \"proyectos\": "
              "{\"<ruta del repo>\": \"<carpeta que contiene .marketing>\"}. Sacarla del historial del repo es "
              "un PR aparte, solo con OK. Mientras tanto un hook bloquea escribir ahi.")
    try:
        c = json.load(open(os.path.join(mk, "config.json"), encoding="utf-8"))
        if not (c.get("marca") or {}).get("kit"):
            print("Kit de marca sin cargar: antes de producir piezas corre /marketing:marca.")
    except Exception:
        pass
    total, vencidas = tendencias_vencidas(mk)
    if vencidas:
        print(f"Tendencias: {vencidas} de {total} vencidas (vigente_hasta < hoy). Antes de usarlas en una pieza, "
              "refrescalas con /marketing:tendencias (se puede programar semanal con /schedule).")
    print("</marketing-mantenimiento>")
    pend = pendientes(mk)
    if pend:
        print("<marketing-pendientes>")
        print("Pendientes abiertos: muestralos al usuario en una lista corta al primer momento oportuno y "
              "pregunta como seguir; no los dejes caer:")
        for ts, e in pend:
            tipo = {"esperando_usuario": "espera respuesta", "approval_requested": "espera aprobacion"}.get(
                e.get("event"), "bloqueado")
            print(f"- [{e.get('agent', '?')}] {e.get('task')} — {tipo} desde {ts:%Y-%m-%d}: {(e.get('detail') or '')[:160]}")
        print("</marketing-pendientes>")


try:
    main()
except Exception:
    pass
sys.exit(0)
