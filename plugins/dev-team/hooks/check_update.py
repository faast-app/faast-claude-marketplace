#!/usr/bin/env python3
"""Aviso de nueva version del plugin al abrir o reanudar una sesion (SessionStart).

Si el marketplace publica una version mas nueva que la instalada, imprime un aviso que entra
al contexto para que la sesion se lo diga al usuario y le ofrezca actualizar. Sin bash ni
herramientas de Unix: funciona igual en Windows (PowerShell, cmd, Windows Terminal), macOS y
Linux. Mejor esfuerzo total: sin red, sin `gh` o ante cualquier error, silencio.
"""
import base64
import json
import os
import re
import subprocess
import sys
import time

# Windows: la consola no es UTF-8 por defecto; sin esto los acentos y simbolos rompen la salida.
for _flujo in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PLUGIN_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "faast-app/faast-claude-marketplace"
HORAS_CACHE = 6


def version_tupla(v):
    return tuple(int(n) for n in re.findall(r"\d+", v or "")[:4])


def main():
    manifiesto = json.load(open(os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8"))
    plugin, instalada = manifiesto["name"], manifiesto["version"]
    cache = os.path.join(os.path.expanduser("~"), ".claude", f".{plugin}-latest-version")
    ultima = ""
    try:
        ts, guardada = open(cache, encoding="utf-8").read().split()[:2]
        if time.time() - float(ts) < HORAS_CACHE * 3600:
            ultima = guardada
    except Exception:
        pass
    if not ultima:
        r = subprocess.run(["gh", "api", f"repos/{REPO}/contents/plugins/{plugin}/.claude-plugin/plugin.json",
                            "--jq", ".content"], capture_output=True, text=True, timeout=10)
        if r.returncode != 0 or not r.stdout.strip():
            return
        ultima = json.loads(base64.b64decode(r.stdout))["version"]
        try:
            os.makedirs(os.path.dirname(cache), exist_ok=True)
            with open(cache, "w", encoding="utf-8") as f:
                f.write(f"{int(time.time())} {ultima}\n")
        except Exception:
            pass
    if version_tupla(ultima) <= version_tupla(instalada):
        return
    print(f"""<{plugin}-actualizacion-disponible>
Hay una nueva version del plugin {plugin}: instalada v{instalada} → disponible v{ultima}.
INFORMA al usuario AL INICIO de tu primera respuesta de esta sesion, en una linea
amable, y pregunta si desea actualizar ahora. Si acepta, ejecuta:
  claude plugin marketplace update faast-marketplace
  claude plugin update {plugin}@faast-marketplace
y recuerdale que debe reiniciar la sesion para cargar la version nueva. Si
prefiere seguir sin actualizar, continua normal y NO vuelvas a insistir en esta
sesion.
</{plugin}-actualizacion-disponible>""")


try:
    main()
except Exception:
    pass
sys.exit(0)
