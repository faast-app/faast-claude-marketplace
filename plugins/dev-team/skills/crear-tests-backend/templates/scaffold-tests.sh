#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# scaffold-tests.sh — Fase 4 de la skill `crear-tests-backend`.
#
# GENERA EL ÁRBOL DE TESTS FUERA DEL REPO DE CÓDIGO.
#
# Regla 7 de la skill dockerizar-componente y regla de la casa: desde la
# coordinación NUNCA se escribe en un repo de código. Este script deja el
# scaffold en $SALIDA/<repo>/tests/ para que se revise y entre por el flujo
# normal de ramas (ADR-039).
#
# Uso:
#   set -a; . ./parametros-tests.env; set +a
#   ./scaffold-tests.sh <repo> <Proyecto> <ruta-relativa-del-csproj-de-la-app>
#
# Ejemplo (micro-api-back):
#   ./scaffold-tests.sh micro-api-back Cloud.Faast.Back \
#       Cloud.Faast.Back/Cloud.Faast.Back
#
# Después, a mano y revisando cada archivo:
#   cp -R "$SALIDA/<repo>/tests" "<repo>/tests"
#   cd <repo> && dotnet sln <sln> add tests/*/*.csproj
#   # ← y ANTES de commitear, verificar T-DOCK-01: que el Dockerfile siga
#   #   construyendo con los proyectos nuevos en el .sln
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO="${1:?uso: scaffold-tests.sh <repo> <Proyecto> <ruta-app>}"
PROYECTO="${2:?falta el nombre base del proyecto, p.ej. Cloud.Faast.Back}"
RUTA_APP="${3:?falta la ruta relativa del .csproj de la app (sin el archivo)}"

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SALIDA="${SALIDA:-${COORD:?Defini COORD (carpeta de coordinacion, ruta absoluta) o SALIDA}/inventario/tests}"
DEST="$SALIDA/$REPO/tests"

echo "→ Generando scaffold en: $DEST"
echo "  (NO se escribe en el repo de código)"

mkdir -p "$DEST"

# ── Directory.Build.props común ──────────────────────────────────────────────
cp "$AQUI/Directory.Build.props.tests" "$DEST/Directory.Build.props"
cp "$AQUI/coverage.runsettings"        "$DEST/coverage.runsettings"

# ── .gitignore: los .received.* NUNCA se commitean (T-SNAP-03) ───────────────
cat > "$DEST/.gitignore" <<'EOF'
# Verify: el .verified.* SÍ se commitea (es la línea base);
# el .received.* NO (es el resultado de una corrida que difirió).
*.received.*
TestResults/
EOF

# ── Los cuatro proyectos ─────────────────────────────────────────────────────
for suite in Unit Caracterizacion Integracion Contrato; do
  dir="$DEST/${PROYECTO}.Tests.${suite}"
  mkdir -p "$dir"

  case "$suite" in
    Integracion) plantilla="Tests.Integracion.csproj" ;;
    *)           plantilla="Tests.Unit.csproj" ;;
  esac

  sed -e "s|<PROYECTO>|${PROYECTO}|g" \
      -e "s|<RUTA_APP>|${RUTA_APP}|g" \
      "$AQUI/$plantilla" > "$dir/${PROYECTO}.Tests.${suite}.csproj"

  # appsettings de test: SOLO valores inventados (T-SEC-01 / T-CFG-01)
  cat > "$dir/appsettings.json" <<EOF
{
  "_comentario": "Valores INVENTADOS, solo para tests. Ningún secreto real acá (T-SEC-01).",
  "AppSettings": {
    "JwtSecret": "clave-solo-para-tests-no-usar-en-ningun-ambiente-0123456789",
    "Pais": "CL"
  },
  "ConnectionStrings": {
    "_comentario": "Vacías a propósito: las inyecta el fixture de Testcontainers."
  },
  "Logging": { "LogLevel": { "Default": "Warning" } }
}
EOF
done

# ── Plantillas de test, por suite ────────────────────────────────────────────
copiar() {  # copiar <archivo> <suite> <namespace-suffix>
  sed -e "s|<Namespace>|${PROYECTO}|g" \
      "$AQUI/$1" > "$DEST/${PROYECTO}.Tests.$2/$1"
}

copiar NucleoPuroTests.cs                Unit
copiar CaracterizacionOpenApiTests.cs    Caracterizacion
copiar CaracterizacionRespuestasTests.cs Caracterizacion
copiar JwtCaracterizacionTests.cs        Caracterizacion
copiar CifradoGoldenTests.cs             Caracterizacion
copiar FechasCulturaTests.cs             Caracterizacion
copiar FaastWebApplicationFactory.cs     Integracion
copiar TestcontainersFixture.cs          Integracion
copiar ContratoQaTests.cs                Contrato

# ── Colección para el estado global (T-FLAKE-01) ─────────────────────────────
cat > "$DEST/${PROYECTO}.Tests.Caracterizacion/ColeccionEstadoGlobal.cs" <<EOF
// Las clases que tocan estado compartido del proceso (CurrentCulture, variables
// de entorno, configuración estática) van en esta colección: xUnit NO las corre
// en paralelo entre sí. Sin esto, los tests se pisan de a ratos (T-FLAKE-01).
namespace ${PROYECTO}.Tests.Caracterizacion;

[CollectionDefinition("estado-global", DisableParallelization = true)]
public class ColeccionEstadoGlobal { }
EOF

# ── Workflow, para revisar y copiar a .github/workflows/ ─────────────────────
mkdir -p "$SALIDA/$REPO/.github/workflows"
cp "$AQUI/ci-tests.yml" "$SALIDA/$REPO/.github/workflows/tests.yml"

# ── README del scaffold, con los pasos que faltan ────────────────────────────
cat > "$SALIDA/$REPO/LEEME-scaffold.md" <<EOF
# Scaffold de tests — $REPO

Generado por \`crear-tests-backend/templates/scaffold-tests.sh\` (skill del plugin dev-team).
**No se escribió nada en el repo de código.**

## Qué falta, en orden

1. **Revisar cada archivo.** Las plantillas traen placeholders
   (\`<TipoUsuario>\`, \`<Emisor>\`, \`<Cifrador>\`, \`<IRepositorio>\`, rutas de endpoints)
   y \`TODO\`s deliberados. Nada de esto compila tal cual, a propósito.
2. **\`public partial class Program { }\`** al final de \`Program.cs\` si va a haber
   tests de integración (T-WAF-01). Es un cambio en el repo: se pide y se aprueba.
3. **Copiar** \`tests/\` al repo, en la rama del componente.
4. **\`dotnet sln <sln> add tests/*/*.csproj\`**
5. **Verificar T-DOCK-01**: \`docker build\` local con los proyectos ya en el \`.sln\`.
   Si el Dockerfile hace \`dotnet restore <sln>\` copiando solo los \`.csproj\` de la
   app, **el build de la imagen se rompe** y hay que ajustarlo (una línea).
6. **Generar las líneas base ANTES de migrar**: token de oro, vectores de cifrado,
   snapshots de OpenAPI. Después de migrar ya no sirven.
7. **Copiar el workflow** a \`.github/workflows/tests.yml\`.
8. Completar \`reference/checklist.md\` y el informe.

## Lo que este scaffold NO decide

- Qué endpoints entran en el contrato: sale del inventario de consumidores y lo
  valida QA.
- Si la integración con base es viable: depende de si el esquema está en el repo
  (T-DB-04).
EOF

echo
echo "✓ Listo. Archivos generados:"
find "$SALIDA/$REPO" -type f | sed "s|$SALIDA/|  |"
echo
echo "→ Siguiente paso: leer $SALIDA/$REPO/LEEME-scaffold.md"
echo "→ RECORDATORIO: nada de esto entra al repo sin revisión y sin el flujo de ramas."
