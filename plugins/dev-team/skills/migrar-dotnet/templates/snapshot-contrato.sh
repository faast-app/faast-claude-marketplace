#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# snapshot-contrato.sh — línea base y comparación del contrato OpenAPI.
#
# El snapshot "antes" se toma contra el componente CORRIENDO HOY, antes de tocar
# el csproj. Sin él no hay Definition of Done (regla 4 de la skill): 44 de 61
# repos backend no tienen tests, así que esto ES la red de seguridad.
#
# Uso:
#   BASE_URL=https://qa-total-microbanco.faast.pe ./snapshot-contrato.sh antes
#   BASE_URL=http://localhost:8080               ./snapshot-contrato.sh despues
#   ./snapshot-contrato.sh diff
#
# Variables:
#   BASE_URL       obligatorio para antes/despues
#   SWAGGER_PATH   default /swagger/v1/swagger.json
#   REPO           nombre del componente (para el nombre de archivo)
#   SALIDA         carpeta de snapshots
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO="${REPO:?falta REPO}"
SALIDA="${SALIDA:-./snapshots}"
SWAGGER_PATH="${SWAGGER_PATH:-/swagger/v1/swagger.json}"
mkdir -p "$SALIDA"

# Normaliza el JSON de OpenAPI para que el diff muestre cambios de CONTRATO
# y no ruido del generador: ordena claves, borra la versión y los campos que
# cambian en cada build.
normalizar() {
  python3 - "$1" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
d.pop("servers", None)
info = d.get("info", {})
for k in ("version", "x-generator", "description"):
    info.pop(k, None)
# Los nombres de esquema generados llevan hash en algunas versiones de Swashbuckle
print(json.dumps(d, sort_keys=True, indent=2, ensure_ascii=False))
PY
}

case "${1:-}" in
  antes|despues)
    FASE="$1"
    : "${BASE_URL:?falta BASE_URL}"
    RAW="$SALIDA/${REPO}.${FASE}.raw.json"
    NRM="$SALIDA/${REPO}.${FASE}.json"

    echo "→ GET ${BASE_URL}${SWAGGER_PATH}"
    if ! curl -fsSL --max-time 30 "${BASE_URL}${SWAGGER_PATH}" -o "$RAW"; then
      echo "ERROR: no se pudo obtener el OpenAPI." >&2
      echo "  · ¿Swagger está deshabilitado en Production? (E-SWAG-02)" >&2
      echo "  · ¿El path es otro? probá /swagger/v1/swagger.json, /swagger/index.html" >&2
      echo "  · Si el componente NO expone OpenAPI, la línea base son las respuestas" >&2
      echo "    reales: usar comparar-respuestas.sh y decirlo en el informe." >&2
      exit 1
    fi
    normalizar "$RAW" > "$NRM"

    echo "✓ $NRM"
    echo "  endpoints: $(python3 -c "import json;print(len(json.load(open('$NRM')).get('paths',{})))")"
    ;;

  diff)
    A="$SALIDA/${REPO}.antes.json"; B="$SALIDA/${REPO}.despues.json"
    [ -f "$A" ] || { echo "Falta $A. El snapshot 'antes' NO es opcional." >&2; exit 1; }
    [ -f "$B" ] || { echo "Falta $B." >&2; exit 1; }

    echo "=== Endpoints que aparecen o desaparecen (BLOQUEA) ==="
    python3 - "$A" "$B" <<'PY'
import json, sys
a = set(json.load(open(sys.argv[1])).get("paths", {}))
b = set(json.load(open(sys.argv[2])).get("paths", {}))
for p in sorted(a - b): print(f"  DESAPARECIÓ  {p}")
for p in sorted(b - a): print(f"  APARECIÓ     {p}")
if a == b: print("  (ninguno — correcto)")
PY

    echo
    echo "=== Diff completo del contrato ==="
    diff -u "$A" "$B" && echo "  (idéntico — el mejor resultado posible)"

    echo
    echo "Criterio (03-plan-de-pruebas §3):"
    echo "  · orden de claves / info.version ......... ruido, aceptable"
    echo "  · format que aparece o desaparece ........ REVISAR"
    echo "  · tipo que cambia, nullable nuevo ........ BLOQUEA"
    echo "  · endpoint que desaparece ................ BLOQUEA"
    echo "  · required nuevo ......................... BLOQUEA"
    ;;

  *) echo "uso: snapshot-contrato.sh {antes|despues|diff}" >&2; exit 1 ;;
esac
