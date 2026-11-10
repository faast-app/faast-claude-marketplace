#!/usr/bin/env python3
"""Registro de pedidos del usuario — la prueba de que un reenvio es del usuario.

Problema que resuelve: un agente del equipo recibe "Autorizacion del usuario: ..." del
coordinador y, como no puede saber si de verdad lo dijo el usuario, exige que el usuario
"le escriba en su hilo". En Remote Control, movil o con agentes en segundo plano eso no es
posible: el usuario solo habla con la sesion principal, y el trabajo queda bloqueado.

Solucion: este hook (UserPromptSubmit) lo ejecuta Claude Code, no un agente, cada vez que el
USUARIO envia un mensaje en la sesion principal, y guarda sus palabras textuales en
<carpeta del equipo>/metrics/pedidos-usuario.jsonl (fuera de los repos). Un agente que duda de
un reenvio lo comprueba aqui en vez de pedir otro canal:

  python3 pedidos_usuario.py verificar "aplica en Puente"      # sale 0 si el usuario lo escribio
  python3 pedidos_usuario.py ultimos 5

Modo hook (sin argumentos): lee el payload por stdin. Nunca falla hacia afuera ni bloquea.
No registra mensajes que no escribio el usuario (reportes de subagentes, notificaciones,
mensajes de otras sesiones), redacta secretos evidentes y se puede apagar con
`"equipo": {"registrarPedidos": false}` en el config.json del equipo.
"""
import datetime
import json
import os
import re
import sys
import unicodedata

# Windows: la consola no es UTF-8 por defecto; sin esto los acentos y simbolos rompen la salida.
for _flujo in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coord_root import resolve  # noqa: E402

ARCHIVO = "pedidos-usuario.jsonl"
MAX_TEXTO = 6000
MAX_LINEAS = 2000
# Mensajes que llegan por UserPromptSubmit pero NO los escribio el usuario.
NO_USUARIO = ("<task-notification", "[subagent hand-back]", "<agent-message", "[system notification",
              "<webhook-payload", "<wake ", "<child-session-event", "<system-reminder", "<event source=")
SECRETOS = [
    (re.compile(r"(?i)\b(password|passwd|pwd|contrase(?:ñ|n)a|clave|secret|secreto|token|api[_-]?key|"
                r"apikey|authorization|bearer)\b(\s*[:=]\s*|\s+es\s+|\s+)(\"[^\"]+\"|'[^']+'|\S+)"),
     lambda m: f"{m.group(1)}{m.group(2)}[REDACTADO]"),
    (re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|"
                r"AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|npm_[A-Za-z0-9]{20,})\b"), "[REDACTADO]"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}\b"), "[JWT REDACTADO]"),
    (re.compile(r"(?i)\b([a-z][a-z0-9+.-]*://[^\s:/@]+):([^\s@/]+)@"), r"\1:[REDACTADO]@"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
     "[CLAVE PRIVADA REDACTADA]"),
]


def redactar(texto):
    for patron, reemplazo in SECRETOS:
        texto = patron.sub(reemplazo, texto)
    return texto


def normalizar(texto):
    sin = unicodedata.normalize("NFD", texto.lower())
    sin = "".join(c for c in sin if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9ñ#/._-]+", " ", sin)).strip()


def ruta_registro(cwd=None):
    r = resolve(cwd or os.getcwd())
    if not r.get("path") or r.get("en_repo"):
        return None, r
    return os.path.join(r["path"], "metrics", ARCHIVO), r


def _apagado(coord):
    try:
        cfg = json.load(open(os.path.join(coord, "config.json"), encoding="utf-8"))
        return (cfg.get("equipo") or {}).get("registrarPedidos") is False
    except Exception:
        return False


def registrar():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    if payload.get("hook_event_name") != "UserPromptSubmit" or payload.get("agent_id"):
        return
    texto = (payload.get("prompt") or "").strip()
    if not texto:
        return
    cabeza = texto[:400].lower()
    if any(marca in cabeza for marca in NO_USUARIO):
        return
    ruta, r = ruta_registro(payload.get("cwd"))
    if not ruta or _apagado(r["path"]):
        return
    linea = {
        "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sesion": (payload.get("session_id") or "")[:12],
        "texto": redactar(texto)[:MAX_TEXTO],
        "src": "hook",
    }
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")
    try:  # recorte: el registro es una ventana reciente, no un historial
        lineas = open(ruta, encoding="utf-8").read().splitlines()
        if len(lineas) > MAX_LINEAS + 200:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("\n".join(lineas[-MAX_LINEAS:]) + "\n")
    except Exception:
        pass


def leer(ruta):
    out = []
    try:
        for l in open(ruta, encoding="utf-8"):
            try:
                out.append(json.loads(l))
            except Exception:
                continue
    except FileNotFoundError:
        pass
    return out


def _arg(nombre, defecto):
    if nombre in sys.argv:
        i = sys.argv.index(nombre)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return defecto


def verificar():
    frase = sys.argv[2] if len(sys.argv) > 2 else ""
    horas = float(_arg("--horas", "72"))
    ruta, _ = ruta_registro(_arg("--cwd", None))
    if not ruta:
        print("SIN REGISTRO: no hay carpeta del equipo fuera de un repo. Pide al coordinador la ruta "
              "(--cwd) o que confirme con el usuario.")
        sys.exit(2)
    objetivo = normalizar(frase)
    if not objetivo:
        print("Uso: pedidos_usuario.py verificar \"<frase textual del usuario>\" [--horas 72] [--cwd DIR]")
        sys.exit(2)
    limite = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=horas)
    patron = re.compile(r"(?<![a-z0-9ñ])" + re.escape(objetivo) + r"(?![a-z0-9ñ])")
    hallados = []
    for e in leer(ruta):
        try:
            ts = datetime.datetime.strptime(e["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        except Exception:
            continue
        if ts >= limite and patron.search(normalizar(e.get("texto", ""))):
            hallados.append(e)
    if not hallados:
        print(f"NO ENCONTRADO en las ultimas {horas:g} h: el usuario no escribio «{frase}» en la sesion "
              "principal (o el registro esta apagado / es anterior al plugin).\n"
              "Que hacer: devuelve el control al coordinador con la pregunta exacta (evento "
              "esperando_usuario). NO pidas al usuario que escriba en tu hilo.")
        sys.exit(1)
    print(f"VERIFICADO: el usuario escribio «{frase}» en la sesion principal ({len(hallados)} vez/veces).")
    for e in hallados[-3:]:
        t = e["texto"]
        pos = normalizar(t).find(objetivo)
        ini = max(0, min(len(t), pos) - 200)
        print(f"- {e['ts']} (sesion {e.get('sesion', '')}): …{t[ini:ini + 600].strip()}…")
    print("Es palabra del usuario: comprueba que cubre TU accion (que, ambiente, alcance) y ejecuta.")
    sys.exit(0)


def ultimos():
    n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 5
    ruta, _ = ruta_registro(_arg("--cwd", None))
    if not ruta:
        print("SIN REGISTRO: no hay carpeta del equipo fuera de un repo.")
        sys.exit(2)
    for e in leer(ruta)[-n:]:
        print(f"- {e['ts']}: {e['texto'][:700]}")


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "verificar":
            verificar()
        elif len(sys.argv) > 1 and sys.argv[1] == "ultimos":
            ultimos()
        else:
            registrar()
    except SystemExit:
        raise
    except Exception:
        pass
    sys.exit(0)
