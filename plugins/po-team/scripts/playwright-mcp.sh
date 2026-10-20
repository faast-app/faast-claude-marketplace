#!/bin/bash
# po-team — lanza el Playwright MCP del plugin.
# - Staging de archivos en ~/.faast-mcp/po-team (fuera de cualquier repo).
# - Las cuentas de prueba (.po-team/accesos.env de la carpeta CANONICA) se pasan como SECRETOS
#   (--secrets): el agente escribe el NOMBRE de la variable en browser_type / browser_fill_form,
#   el MCP sustituye el valor y lo redacta de sus respuestas y archivos. El valor nunca pasa por el
#   modelo. Si accesos.env no existe todavia, se arranca sin secretos (--secrets con un archivo
#   inexistente impediria que el MCP arranque). Los valores se leen al ARRANCAR: si el PO completa
#   accesos.env con la sesion abierta, hay que reconectar el MCP (/mcp) o reiniciar la sesion.
DIR="$(cd "$(dirname "$0")" && pwd)"
START="${1:-}"
case "$START" in ''|'${'*) START="${CLAUDE_PROJECT_DIR:-$PWD}";; esac
OUT="$HOME/.faast-mcp/po-team"
mkdir -p "$OUT" 2>/dev/null
PO="$(python3 "$DIR/../hooks/coord_root.py" "$START" 2>/dev/null | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    print(d["path"] if d.get("path") and not d.get("en_repo") else "")
except Exception:
    print("")' 2>/dev/null)"
SECRETS=()
if [ -n "$PO" ] && [ -f "$PO/accesos.env" ]; then SECRETS=("--secrets=$PO/accesos.env"); fi
exec npx -y @playwright/mcp@0.0.80 --browser=chromium --caps=testing,devtools,vision --isolated \
  --output-dir="$OUT" --test-id-attribute=data-testid --timeout-action=8000 \
  --timeout-navigation=45000 --console-level=warning --ignore-https-errors "${SECRETS[@]}"
