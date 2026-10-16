#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# comparar-respuestas.sh — diff de respuestas reales antes/después de migrar.
#
# Es la única evidencia de comportamiento en los 44 repos sin tests.
# Se compara contra LA VERSIÓN ACTUAL EN QA, no contra lo que "debería" devolver:
# el objetivo de una migración de runtime es que NADA cambie, incluidos los bugs.
#
# Uso:
#   1. Llenar endpoints.txt (formato abajo)
#   2. URL_BASE=https://qa-total-microbanco.faast.pe ./comparar-respuestas.sh antes
#   3. ... migración ...
#   4. URL_BASE=http://localhost:8080 ./comparar-respuestas.sh despues
#   5. ./comparar-respuestas.sh diff
#
# endpoints.txt — una línea por caso:
#   METODO<TAB>RUTA<TAB>[cuerpo JSON en una línea]
# Ejemplo:
#   GET	/api/banco/listar
#   GET	/api/banco/5
#   POST	/api/banco/buscar	{"rut":"12345678-9","desde":"2026-01-01"}
#
# NO poner datos de producción ni secretos en endpoints.txt. Es un archivo de
# trabajo; si necesita un token, sale de la variable TOKEN.
# ─────────────────────────────────────────────────────────────────────────────
set -uo pipefail

REPO="${REPO:?falta REPO}"
SALIDA="${SALIDA:-./snapshots}"
LISTA="${LISTA:-./endpoints.txt}"
TOKEN="${TOKEN:-}"
mkdir -p "$SALIDA"

# Normaliza el cuerpo para que el diff no se llene de ruido: ordena claves y
# enmascara los campos que cambian en cada llamada por naturaleza.
normalizar_cuerpo() {
  python3 - <<'PY'
import json, sys, re
raw = sys.stdin.read()
VOLATILES = {"timestamp","fecha_consulta","fechaConsulta","traceId","requestId",
             "elapsed","duration","serverTime","correlationId"}
def limpiar(o):
    if isinstance(o, dict):
        return {k: ("<VOLATIL>" if k in VOLATILES else limpiar(v)) for k, v in o.items()}
    if isinstance(o, list):
        return [limpiar(x) for x in o]
    if isinstance(o, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T[\d:.]+(Z|[+-]\d{2}:?\d{2})?", o):
        return o          # las fechas NO se enmascaran: son justamente lo que hay que mirar
    return o
try:
    print(json.dumps(limpiar(json.loads(raw)), sort_keys=True, indent=2, ensure_ascii=False))
except Exception:
    print(raw)            # no era JSON: se compara tal cual
PY
}

capturar() {
  local fase="$1" out="$SALIDA/${REPO}.resp.${fase}.txt"
  : "${URL_BASE:?falta URL_BASE}"
  [ -f "$LISTA" ] || { echo "Falta $LISTA" >&2; exit 1; }
  : > "$out"
  local n=0
  while IFS=$'\t' read -r metodo ruta cuerpo; do
    case "${metodo:-}" in ''|'#'*) continue;; esac
    n=$((n+1))
    local hdr=(-H "Accept: application/json")
    [ -n "$TOKEN" ] && hdr+=(-H "Authorization: Bearer $TOKEN")
    [ -n "${cuerpo:-}" ] && hdr+=(-H "Content-Type: application/json" --data "$cuerpo")

    local tmp code ct
    tmp="$(mktemp)"
    code=$(curl -s -o "$tmp" -w '%{http_code}' --max-time 45 \
             -X "$metodo" "${hdr[@]}" "${URL_BASE}${ruta}" || echo "000")
    ct=$(curl -s -o /dev/null -w '%{content_type}' --max-time 45 \
             -X "$metodo" "${hdr[@]}" "${URL_BASE}${ruta}" 2>/dev/null || echo "?")

    {
      echo "════════════════════════════════════════════════════════"
      echo "CASO $n  $metodo $ruta"
      echo "STATUS: $code"
      echo "CONTENT-TYPE: ${ct%%;*}"
      echo "--------------------------------------------------------"
      normalizar_cuerpo < "$tmp"
    } >> "$out"
    rm -f "$tmp"
    printf '  %-4s %-45s → %s\n' "$metodo" "$ruta" "$code"
  done < "$LISTA"
  echo "✓ $n casos en $out"
}

case "${1:-}" in
  antes|despues) capturar "$1" ;;
  diff)
    A="$SALIDA/${REPO}.resp.antes.txt"; B="$SALIDA/${REPO}.resp.despues.txt"
    [ -f "$A" ] || { echo "Falta la línea base $A. Sin ella no hay DoD." >&2; exit 1; }
    [ -f "$B" ] || { echo "Falta $B." >&2; exit 1; }
    if diff -u "$A" "$B"; then
      echo "✓ Respuestas idénticas. Es el resultado esperado de una migración de runtime."
    else
      echo
      echo "Cada línea de diff necesita una explicación en el informe. Sospechosos:"
      echo "  · casing de propiedades / enums / nulls .... E-JSON-01 (serializador)"
      echo "  · fechas con otro offset o corridas 5 h .... E-TZ-01 (zona horaria)"
      echo "  · separador decimal o de miles ............. E-CULT-02 (ICU/cultura)"
      echo "  · conteo de filas distinto ................. E-EF-02 (traducción de consulta)"
      echo "  · 401/403 donde había 200 .................. E-JWT-01 / E-MW-01"
      echo "  · status 500 nuevo ......................... revisar docker logs"
      exit 1
    fi
    ;;
  *) echo "uso: comparar-respuestas.sh {antes|despues|diff}" >&2; exit 1 ;;
esac
