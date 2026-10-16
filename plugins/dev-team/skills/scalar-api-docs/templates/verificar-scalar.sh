#!/usr/bin/env bash
# =============================================================================
# verificar-scalar.sh — Paso 5 de la skill scalar-api-docs
#
# Uso:
#   ./verificar-scalar.sh <base-url> [ruta-documento] [doc1] [doc2] ...
#
# Ejemplos:
#   ./verificar-scalar.sh http://localhost:18080 '/swagger/{documentName}/swagger.json' BackOffice GestionCobranza
#   ./verificar-scalar.sh http://localhost:18080 '/openapi/{documentName}.json' v1
#   ./verificar-scalar.sh http://localhost:18080            # rama B, doc por defecto v1
#
# Verifica lo automatizable del checklist §4. Lo que NO puede verificar y hay
# que mirar a ojo: que la UI PINTE los endpoints en el navegador, y que "Try it"
# con un JWT real devuelva 200.
# =============================================================================
set -uo pipefail

BASE="${1:?falta la base-url, ej. http://localhost:18080}"
DOC_PATTERN="${2:-/openapi/{documentName}.json}"
shift 2 2>/dev/null || shift 1 2>/dev/null || true
DOCS=("$@"); [ ${#DOCS[@]} -eq 0 ] && DOCS=("v1")

SCALAR_PATH="${SCALAR_PATH:-/scalar}"
HEALTH_PATH="${HEALTH_PATH:-/health}"

ok=0; fail=0
pass() { printf '  \033[32mOK\033[0m   %s\n' "$1"; ok=$((ok+1)); }
bad()  { printf '  \033[31mFALLA\033[0m %s\n' "$1"; fail=$((fail+1)); }
info() { printf '\n\033[1m%s\033[0m\n' "$1"; }

code() { curl -s -o /dev/null -w '%{http_code}' "$1"; }
codeL() { curl -sL -o /dev/null -w '%{http_code}' "$1"; }

# -----------------------------------------------------------------------------
info "1. La UI responde"
# -----------------------------------------------------------------------------
# Sin -L da 3xx por el redirect a la barra final: es esperado, NO es un fallo
# (E-SC-03). Lo que importa es que siguiendo el redirect dé 200.
raw=$(code "$BASE$SCALAR_PATH")
[ "$raw" = "200" ] || [[ "$raw" =~ ^30 ]] \
  && pass "$SCALAR_PATH responde ($raw sin seguir redirect)" \
  || bad "$SCALAR_PATH devolvió $raw"

body=$(curl -sL "$BASE$SCALAR_PATH")
[ "$(codeL "$BASE$SCALAR_PATH")" = "200" ] \
  && pass "$SCALAR_PATH/ devuelve 200 siguiendo el redirect" \
  || bad "$SCALAR_PATH/ no devuelve 200 — ¿302 al login? ver E-SC-02"

# HTML real, no un JSON ni una página de error
if grep -qi '<html' <<<"$body" && grep -qi 'scalar' <<<"$body"; then
  pass "el cuerpo es HTML real de Scalar"
else
  bad "el cuerpo NO parece el HTML de Scalar (¿ruta equivocada?)"
fi

# -----------------------------------------------------------------------------
info "2. Los assets JS (E-SC-02 — el bug de FallbackPolicy global)"
# -----------------------------------------------------------------------------
for asset in scalar.js scalar.aspnetcore.js; do
  c=$(code "$BASE$SCALAR_PATH/$asset")
  [ "$c" = "200" ] \
    && pass "$SCALAR_PATH/$asset → 200" \
    || bad "$SCALAR_PATH/$asset → $c  ← firma de E-SC-02: envolver en MapGroup().AllowAnonymous()"
done

# -----------------------------------------------------------------------------
info "3. Cada documento OpenAPI carga"
# -----------------------------------------------------------------------------
doc_versions=()
for d in "${DOCS[@]}"; do
  url="$BASE${DOC_PATTERN//\{documentName\}/$d}"
  c=$(code "$url")
  if [ "$c" = "200" ]; then
    pass "documento '$d' → 200"
    v=$(curl -s "$url" | { jq -r '.info.version // empty' 2>/dev/null || true; })
    [ -n "${v:-}" ] && doc_versions+=("$d=$v") \
      || bad "documento '$d': no se pudo leer .info.version (¿jq instalado?)"
  else
    bad "documento '$d' → $c en $url  ← E-SC-01: ¿la ruta y las MAYÚSCULAS son las reales?"
  fi
done

# -----------------------------------------------------------------------------
info "4. Security schemes (E-SC-04 — sin esto no hay botón de auth)"
# -----------------------------------------------------------------------------
first_url="$BASE${DOC_PATTERN//\{documentName\}/${DOCS[0]}}"
schemes=$(curl -s "$first_url" | { jq -r '.components.securitySchemes // .securityDefinitions // empty' 2>/dev/null || true; })
if [ -n "${schemes:-}" ] && [ "$schemes" != "null" ]; then
  pass "el documento declara security schemes"
else
  bad "el documento NO declara security schemes → Scalar no mostrará autenticación (E-SC-04)"
fi

# -----------------------------------------------------------------------------
info "5. VERSIÓN ÚNICA (regla dura) — /health == info.version == version.txt"
# -----------------------------------------------------------------------------
health_version=$(curl -s "$BASE$HEALTH_PATH" | { jq -r '.version // empty' 2>/dev/null || true; })
if [ -z "${health_version:-}" ]; then
  bad "$HEALTH_PATH no devolvió .version (¿falta el health del Paso 4.5?)"
else
  pass "$HEALTH_PATH.version = '$health_version'"
  for dv in "${doc_versions[@]}"; do
    d="${dv%%=*}"; v="${dv#*=}"
    [ "$v" = "$health_version" ] \
      && pass "info.version de '$d' coincide con /health ('$v')" \
      || bad "info.version de '$d' = '$v' ≠ /health = '$health_version'  ← E-SC-05: dos fuentes de versión"
  done
  case "$health_version" in
    unknown|""|1.0.0|v1)
      bad "la versión es '$health_version' — sospechoso: ¿version.txt no llegó a la imagen, o está hardcodeada?" ;;
  esac
fi

if [ -n "${CONTAINER:-}" ]; then
  file_version=$(docker exec "$CONTAINER" cat /app/version.txt 2>/dev/null | tr -d '\r\n ')
  [ -n "$file_version" ] && {
    [ "$file_version" = "$health_version" ] \
      && pass "version.txt de la imagen = '$file_version' (coincide)" \
      || bad "version.txt = '$file_version' ≠ /health = '$health_version'"
  }
else
  printf '  \033[33mNOTA\033[0m exportá CONTAINER=<nombre> para comparar también con version.txt dentro de la imagen\n'
fi

# -----------------------------------------------------------------------------
printf '\n\033[1mResultado: %d OK, %d fallas\033[0m\n' "$ok" "$fail"
[ "$fail" -eq 0 ] || {
  cat <<'EOF'

Catálogo: reference/03-catalogo-errores.md
  E-SC-01 documento no encontrado (ruta/mayúsculas)   E-SC-04 sin security schemes
  E-SC-02 assets .js detrás del login (UI en blanco)  E-SC-05 dos fuentes de versión
  E-SC-03 redirect a barra final (falso negativo)

Falta verificar A MANO (el script no puede):
  - la UI PINTA los endpoints en el navegador
  - "Try it" con un JWT real en un endpoint protegido devuelve 200
  - el diff de contrato OpenAPI antes/después está VACÍO
  - todo lo anterior POR EL CAMINO REAL (vhost/proxy), no solo localhost
EOF
  exit 1
}
