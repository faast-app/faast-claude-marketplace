#!/bin/sh
# infra/frontend-entrypoint.sh — genera env.js y health.json EN RUNTIME y
# arranca nginx.
#
# Por qué: hoy cada front lleva su env.js con las URLs del ambiente horneadas
# (y en un caso, un password de usuario técnico versionado). En contenedor, el
# contrato window.env no cambia — cambia de dónde salen los valores.
#
# Por qué en /tmp y no en /usr/share/nginx/html: el proceso corre con el UID/GID
# del usuario de despliegue que inyecta docker-compose.yml (regla dura #2) y esa carpeta es de
# root. No se arregla con un chown en el Dockerfile — el UID real lo pone el
# servidor y la imagen no lo conoce. /tmp es 1777: escribible por cualquier UID.
# nginx.conf sirve /env.js y /health con `alias` desde /tmp.
#
# Regla: si falta una variable obligatoria, el contenedor ABORTA. Un front que
# arranca apuntando a "undefined" es peor que un front que no arranca.
set -eu

: "${AMBIENTE:?falta AMBIENTE}"
: "${GW_FINTEC:?falta GW_FINTEC}"

cat > /tmp/env.js <<EOF
window.env = {
  AMBIENTE:        "${AMBIENTE}",
  GW_FINTEC:       "${GW_FINTEC}",
  GW_BACKOFFICE:   "${GW_BACKOFFICE:-}",
  GW_CONFIRMING:   "${GW_CONFIRMING:-}",
  GW_PORTAL:       "${GW_PORTAL:-}"
};
EOF

# El import map de la contenedora single-spa se parametriza igual: se genera
# acá desde variables, nunca se hornea con los hostnames de un ambiente.

# ---- health.json (paso 4.5) -------------------------------------------------
# La versión sale de UNA sola fuente: version.txt copiado a la imagen. Si no
# está, se aborta: un /health que devuelve "unknown" bloquea el cutover igual,
# y es mejor enterarse en el arranque que en la validación de QA.
VERSION_FILE=/usr/share/nginx/html/version.txt
[ -r "$VERSION_FILE" ] || { echo "FATAL: falta $VERSION_FILE en la imagen" >&2; exit 1; }
VERSION=$(tr -d ' \t\r\n' < "$VERSION_FILE")
[ -n "$VERSION" ] || { echo "FATAL: version.txt vacío" >&2; exit 1; }

cat > /tmp/health.json <<EOF
{"component":"${COMPONENT:-frontend}","version":"${VERSION}","status":"Healthy","environment":"${AMBIENTE}","commit":"${COMMIT_SHA:-}","timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
EOF

exec nginx -g 'daemon off;'
