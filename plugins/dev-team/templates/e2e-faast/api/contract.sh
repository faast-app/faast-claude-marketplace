#!/usr/bin/env bash
# Barrido de contrato con Schemathesis (puerta 6) — lo corre qa-backend.
# Genera cientos de requests validos/invalidos desde el openapi.yml REAL. SOLO contra
# urls.dev / qa (JAMAS contra ambientes de cliente). La salida (junit + consola) es
# evidencia y va a .coordination/evidence/{HU}/api/.
set -euo pipefail
[ -f .env ] && set -a && . ./.env && set +a
SPEC="${OPENAPI_SPEC:-../docs/openapi.yml}"
URL="${API_URL:-http://localhost:5000}"
HU="${1:-regresion}"                       # ej: HU-042 -> .coordination/evidence/HU-042/api
FILTER="${2:-}"                            # ej: '^/api/cobranzas' (solo operaciones de la HU)
OUT="${EVIDENCE_DIR:-../.coordination/evidence/_suite}"; OUT="$(dirname "$OUT")/${HU}/api"
mkdir -p "$OUT"
command -v schemathesis >/dev/null || { echo "schemathesis no instalado: pedir /dev-team:setup playwright (pipx install schemathesis)"; exit 2; }
ARGS=(run "$SPEC" --url "$URL" --checks all --max-examples "${MAX_EXAMPLES:-200}" --report junit --report-dir "$OUT")
[ -n "$FILTER" ] && ARGS+=(--include-path-regex "$FILTER")
[ -n "${QA_TOKEN:-}" ] && ARGS+=(--header "Authorization: Bearer $QA_TOKEN")
echo "schemathesis ${ARGS[*]}" | sed "s/Bearer [^ ]*/Bearer ***/" | tee "$OUT/schemathesis.txt"
schemathesis "${ARGS[@]}" 2>&1 | tee -a "$OUT/schemathesis.txt"
