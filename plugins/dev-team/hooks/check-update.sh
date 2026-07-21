#!/bin/bash
# dev-team — aviso de nueva version del plugin al abrir/reanudar sesion.
# SessionStart hook: si hay version mas nueva en el marketplace, imprime un aviso
# (se agrega como contexto → la sesion informa al usuario y ofrece actualizar).
# Best-effort total: sin red, sin gh o cualquier error → silencio (exit 0).

INSTALLED=$(python3 -c "import json,sys;print(json.load(open('$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json'))['version'])" 2>/dev/null)
[ -z "$INSTALLED" ] && exit 0

CACHE="$HOME/.claude/.dev-team-latest-version"
NOW=$(date +%s)
LATEST=""
if [ -f "$CACHE" ]; then
  read -r TS CACHED < "$CACHE" 2>/dev/null
  if [ -n "$TS" ] && [ $((NOW - TS)) -lt 21600 ]; then LATEST="$CACHED"; fi   # cache 6h
fi
if [ -z "$LATEST" ]; then
  LATEST=$(gh api repos/faast-app/faast-claude-marketplace/contents/plugins/dev-team/.claude-plugin/plugin.json \
    --jq '.content' 2>/dev/null | base64 -d 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['version'])" 2>/dev/null)
  [ -n "$LATEST" ] && printf '%s %s\n' "$NOW" "$LATEST" > "$CACHE" 2>/dev/null
fi
[ -z "$LATEST" ] && exit 0
[ "$LATEST" = "$INSTALLED" ] && exit 0
# solo avisar si LATEST es realmente mayor (sort -V)
NEWEST=$(printf '%s\n%s\n' "$INSTALLED" "$LATEST" | sort -V | tail -1)
[ "$NEWEST" != "$LATEST" ] && exit 0

cat <<NOTICE
<dev-team-actualizacion-disponible>
Hay una nueva version del plugin dev-team: instalada v$INSTALLED → disponible v$LATEST.
INFORMA al usuario AL INICIO de tu primera respuesta de esta sesion, en una linea
amable, y pregunta si desea actualizar ahora. Si acepta, ejecuta:
  claude plugin marketplace update faast-marketplace
  claude plugin update dev-team@faast-marketplace
y recuerdale que debe reiniciar la sesion para cargar la version nueva. Si
prefiere seguir sin actualizar, continua normal y NO vuelvas a insistir en esta
sesion.
</dev-team-actualizacion-disponible>
NOTICE
exit 0
