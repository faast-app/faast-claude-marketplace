#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# analizar-testabilidad.sh — Fase 1 de la skill `crear-tests-backend`.
#
# SOLO LECTURA. No hace checkout, no escribe en el repo, no compila, no ejecuta
# la app. Lee un ref (tag o rama remota) con `git grep` / `git ls-tree` / `git show`.
#
# Uso:
#   ./analizar-testabilidad.sh <repo> [ref]
#   ./analizar-testabilidad.sh micro-api-back v2.0.33
#   ./analizar-testabilidad.sh --todos
#
# Salida: bloque Markdown para pegar en templates/informe-testabilidad.md §1-§4.
#
# Los números que produce NO son un veredicto: son la entrada del análisis.
# Cómo interpretarlos: reference/01-analisis-testabilidad.md
# ─────────────────────────────────────────────────────────────────────────────
set -uo pipefail

REPOS_DIR="${REPOS_DIR:?Defini REPOS_DIR (carpeta que contiene los clones de los repos)}"

resolver_ref() {
  local r="$1"
  for c in origin/develop origin/main origin/master; do
    git -C "$REPOS_DIR/$r" rev-parse --verify -q "$c" >/dev/null 2>&1 && { echo "$c"; return; }
  done
  git -C "$REPOS_DIR/$r" for-each-ref --format='%(refname:short)' refs/remotes/origin \
    | grep -v HEAD | head -1
}

analizar() {
  local r="$1" ref="${2:-}"
  [ -d "$REPOS_DIR/$r/.git" ] || { echo "### $r — NO es un repo git en $REPOS_DIR"; return; }
  [ -n "$ref" ] || ref="$(resolver_ref "$r")"

  local G="git -C $REPOS_DIR/$r"
  cnt()   { $G grep -c -I -E "$1" "$ref" -- "${@:2}" 2>/dev/null | awk -F: '{s+=$NF} END{print s+0}'; }
  hit()   { $G grep -n -I -E "$1" "$ref" -- "${@:2}" 2>/dev/null | head -"${LIM:-3}"; }
  files() { $G ls-tree -r --name-only "$ref" 2>/dev/null; }
  loc()   { local t=0 c; for f in $(files | grep -E "$1" ); do
              c=$($G show "$ref:$f" 2>/dev/null | wc -l | tr -d ' '); t=$((t+${c:-0}));
            done; echo "$t"; }

  echo "### $r  (ref: $ref)"
  echo

  # ── 1. ¿Ya hay tests? ────────────────────────────────────────────────────
  echo "**Tests existentes**"
  echo '```'
  local ntest; ntest=$(files | grep -c -iE '(^|/)tests?/.*\.csproj$|\.(Tests|UnitTests|IntegrationTests|Spec)\.csproj$')
  printf '%-36s %s\n' "Proyectos de test" "$ntest"
  files | grep -iE '(^|/)tests?/.*\.csproj$|\.(Tests|UnitTests|IntegrationTests|Spec)\.csproj$' | head -8
  printf '%-36s %s\n' "PackageRef xunit/nunit/mstest" "$(cnt 'Include="(xunit|NUnit|MSTest)' '*.csproj')"
  printf '%-36s %s\n' "FluentAssertions (ver licencia)" "$($G grep -h -o -E 'Include="FluentAssertions" *Version="[^"]+"' "$ref" -- '*.csproj' 2>/dev/null | sed -E 's/.*Version="//; s/"//' | sort -u | paste -sd, -)"
  printf '%-36s %s\n' "Moq (SponsorLink < 4.20.2)" "$($G grep -h -o -E 'Include="Moq" *Version="[^"]+"' "$ref" -- '*.csproj' 2>/dev/null | sed -E 's/.*Version="//; s/"//' | sort -u | paste -sd, -)"
  printf '%-36s %s\n' "'dotnet test' en workflows" "$(cnt 'dotnet test' '.github/workflows/*')"
  echo '```'
  echo "> Si hay \`dotnet test\` en CI y 0 proyectos de test: **T-CI-01**, el pipeline"
  echo "> pasa en verde sin ejecutar nada. Es confianza falsa, no un detalle."
  echo

  # ── 2. Superficie: endpoints por controller ──────────────────────────────
  echo "**Superficie HTTP**"
  echo '```'
  local total=0 n
  for f in $(files | grep -E 'Controllers?/.*\.cs$'); do
    n=$($G show "$ref:$f" 2>/dev/null | grep -cE '^[[:space:]]*\[Http(Get|Post|Put|Delete|Patch)')
    [ "${n:-0}" -gt 0 ] && printf '%4s  %s\n' "$n" "$(basename "$f")"
    total=$((total+${n:-0}))
  done | sort -rn | head -30
  echo "----"
  printf '%-36s %s\n' "Controllers" "$(files | grep -cE 'Controllers?/.*\.cs$')"
  printf '%-36s %s\n' "Endpoints [Http*] (total)" "$(cnt '^[[:space:]]*\[Http(Get|Post|Put|Delete|Patch)' '*Controller*.cs')"
  printf '%-36s %s\n' "AllowAnonymous (entrada barata)" "$(cnt '\[AllowAnonymous\]' '*.cs')"
  printf '%-36s %s\n' "MapGet/MapPost (minimal API)" "$(cnt 'app\.Map(Get|Post|Put|Delete)' '*.cs')"
  echo '```'
  echo

  # ── 3. Dónde vive el código ──────────────────────────────────────────────
  echo "**LOC por capa** (dónde está el negocio de verdad)"
  echo '```'
  for capa in Controllers Services Repositories Interfaces Common Contexts Domain UseCases Handlers Features; do
    local l; l=$(loc "/$capa/.*\.cs$")
    [ "${l:-0}" -gt 0 ] && printf '%-36s %s\n' "$capa/" "$l"
  done
  echo '```'
  echo "> Si \`Repositories/\` es varias veces más grande que \`Services/\`, el negocio está"
  echo "> mezclado con el SQL: la lógica no se puede testear sin base (01-analisis §2)."
  echo

  # ── 4. Bloqueadores de WebApplicationFactory ─────────────────────────────
  echo "**Bloqueadores de \`WebApplicationFactory\`**"
  echo '```'
  printf '%-36s %s\n' "WebApplication.CreateBuilder"   "$(cnt 'WebApplication\.CreateBuilder' '*.cs')"
  printf '%-36s %s\n' "class Startup"                  "$(cnt 'class Startup' '*.cs')"
  printf '%-36s %s\n' "partial class Program (T-WAF-01)" "$(cnt 'partial class Program' '*.cs')"
  printf '%-36s %s\n' "InternalsVisibleTo"             "$(cnt 'InternalsVisibleTo' '*.cs' '*.csproj')"
  printf '%-36s %s\n' "ServerVersion.AutoDetect (T-DB-02)" "$(cnt 'ServerVersion\.AutoDetect' '*.cs')"
  printf '%-36s %s\n' "UseHttpsRedirection (T-WAF-02)" "$(cnt 'UseHttpsRedirection' '*.cs')"
  printf '%-36s %s\n' "Middleware propio (UseMiddleware)" "$(cnt 'UseMiddleware<' '*.cs')"
  printf '%-36s %s\n' "UseUrls (rompe el contenedor)"  "$(cnt 'UseUrls' '*.cs')"
  echo '```'
  echo "> \`WebApplication.CreateBuilder\` > 0 y \`partial class Program\` == 0 ⇒ **T-WAF-01**:"
  echo "> hace falta 1 línea aditiva en Program.cs para que haya tests de integración."
  echo

  # ── 5. Configuración (T-CFG-01) ──────────────────────────────────────────
  echo "**Configuración**"
  echo '```'
  printf '%-36s %s\n' "new ConfigurationBuilder() (T-CFG-01)" "$(cnt 'new ConfigurationBuilder\(' '*.cs')"
  printf '%-36s %s\n' "AddJsonFile fuera del host"     "$(cnt 'AddJsonFile\(' '*.cs')"
  printf '%-36s %s\n' "IOptions<>"                     "$(cnt 'IOptions<' '*.cs')"
  printf '%-36s %s\n' "builder.Configuration"          "$(cnt 'builder\.Configuration' '*.cs')"
  printf '%-36s %s\n' "Environment.GetEnvironmentVar"  "$(cnt 'GetEnvironmentVariable' '*.cs')"
  printf '%-36s %s\n' "campos static de config"        "$(cnt 'public static (string|bool|int) ' '*.cs')"
  echo '```'
  LIM=3 hit 'new ConfigurationBuilder\(' '*.cs'
  echo "> Un \`ConfigurationBuilder\` privado dentro de una clase estática **ignora las"
  echo "> variables de entorno**: choca con la regla 'todo el appsettings a variables'"
  echo "> (ADR-016) y rompe los tests con TypeInitializationException. Ver T-CFG-01."
  echo

  # ── 6. Dependencias externas ─────────────────────────────────────────────
  echo "**Dependencias externas**"
  echo '```'
  printf '%-36s %s\n' "DbContext (clases)"             "$(cnt ': DbContext' '*.cs')"
  printf '%-36s %s\n' "UseSqlServer / UseMySql / Npgsql" "$(cnt 'UseSqlServer|UseMySql|UseNpgsql' '*.cs')"
  printf '%-36s %s\n' "FromSqlRaw/ExecuteSql (T-DB-01)" "$(cnt 'FromSql(Raw|Interpolated)|ExecuteSql(Raw|Interpolated)' '*.cs')"
  printf '%-36s %s\n' "EXEC sp_ (stored procedures)"   "$(cnt 'EXEC +sp_|\"sp_' '*.cs')"
  printf '%-36s %s\n' "new HttpClient() (no doblable)" "$(cnt 'new HttpClient\(' '*.cs')"
  printf '%-36s %s\n' "IHttpClientFactory (doblable)"  "$(cnt 'IHttpClientFactory' '*.cs')"
  printf '%-36s %s\n' "WebRequest.Create"              "$(cnt 'WebRequest\.Create' '*.cs')"
  printf '%-36s %s\n' "Hangfire (T-HF-01)"             "$(cnt 'Hangfire' '*.cs' '*.csproj')"
  printf '%-36s %s\n' "SMTP / MailKit"                 "$(cnt 'SmtpClient|MailKit|MimeKit' '*.cs' '*.csproj')"
  printf '%-36s %s\n' "S3 / AWS SDK"                   "$(cnt 'AWSSDK|IAmazonS3' '*.cs' '*.csproj')"
  printf '%-36s %s\n' "Sentry / telemetría (T-OBS-01)" "$(cnt 'Sentry|Faast\.Telemetry|OpenTelemetry' '*.cs' '*.csproj')"
  printf '%-36s %s\n' "lectura de archivos en runtime" "$(cnt 'ContentRootPath|AppContext\.BaseDirectory|File\.Read' '*.cs')"
  echo '```'
  echo

  # ── 7. Esquema: ¿Testcontainers es viable? (01-analisis §5) ──────────────
  echo "**¿De dónde sale el esquema?** (decide si Testcontainers sirve — T-DB-04)"
  echo '```'
  printf '%-36s %s\n' "Migraciones de EF (carpeta)"    "$(files | grep -c -iE 'Migrations/.*\.cs$')"
  printf '%-36s %s\n' "Archivos .sql en el repo"       "$(files | grep -c '\.sql$')"
  files | grep -i '\.sql$' | head -5
  echo '```'
  echo "> 0 migraciones + pocos .sql + muchos \`EXEC sp_\` ⇒ **el esquema no está en el"
  echo "> repo**: la integración con base NO es viable hasta que el dba entregue un dump"
  echo "> de estructura. Decirlo en el análisis, no en la semana 3."
  echo

  # ── 8. Determinismo: reloj, cultura, TZ ──────────────────────────────────
  echo "**Determinismo** (T-TIME-01 / T-CULT-01)"
  echo '```'
  printf '%-36s %s\n' "DateTime.Now / Today"           "$(cnt 'DateTime\.(Now|Today)' '*.cs')"
  printf '%-36s %s\n' "DateTime.UtcNow"                "$(cnt 'DateTime\.UtcNow' '*.cs')"
  printf '%-36s %s\n' "TimeProvider (inyectable)"      "$(cnt 'TimeProvider' '*.cs')"
  printf '%-36s %s\n' "new Guid / Guid.NewGuid"        "$(cnt 'Guid\.NewGuid' '*.cs')"
  printf '%-36s %s\n' "new CultureInfo(\"xx-XX\")"       "$(cnt 'new CultureInfo\("[a-z]{2}-[A-Z]{2}"\)' '*.cs')"
  printf '%-36s %s\n' "InvariantGlobalization"         "$($G grep -h -o -E '<InvariantGlobalization>[^<]*' "$ref" -- '*.csproj' 2>/dev/null | sed -E 's/.*>//' | sort -u | paste -sd, -)"
  printf '%-36s %s\n' "Random sin semilla"             "$(cnt 'new Random\(\)' '*.cs')"
  echo '```'
  echo

  # ── 9. Auth y cifrado: prioridad 1 y 3 ───────────────────────────────────
  echo "**Auth y cifrado** (prioridad 1 y 3 — gate de cybersec)"
  echo '```'
  printf '%-36s %s\n' "JwtSecurityTokenHandler"        "$(cnt 'JwtSecurityTokenHandler|JsonWebTokenHandler' '*.cs')"
  printf '%-36s %s\n' "AddJwtBearer / AddAuthentication" "$(cnt 'AddJwtBearer|AddAuthentication' '*.cs')"
  printf '%-36s %s\n' "TokenValidationParameters"      "$(cnt 'TokenValidationParameters' '*.cs')"
  printf '%-36s %s\n' "ValidateIssuer = false"         "$(cnt 'ValidateIssuer *= *false' '*.cs')"
  printf '%-36s %s\n' "BCrypt / PasswordHasher"        "$(cnt 'BCrypt|PasswordHasher' '*.cs' '*.csproj')"
  printf '%-36s %s\n' "Aes/Rijndael/TripleDES"         "$(cnt 'RijndaelManaged|Aes\.Create|TripleDES|DESCryptoServiceProvider' '*.cs')"
  printf '%-36s %s\n' "Rfc2898DeriveBytes"             "$(cnt 'Rfc2898DeriveBytes' '*.cs')"
  printf '%-36s %s\n' "new X509Certificate2("          "$(cnt 'new X509Certificate2\(' '*.cs')"
  echo '```'
  echo

  # ── 10. Núcleo puro: el retorno rápido ───────────────────────────────────
  echo "**Candidatos a unitario inmediato** (static puro, sin dependencias)"
  echo '```'
  $G grep -l -I -E 'public static (string|int|decimal|bool|DateTime\??) ' "$ref" -- '*.cs' 2>/dev/null \
    | sed "s|^$ref:||" | grep -viE 'Controller|Repository|Program\.cs' | head -12
  echo '```'
  echo "> Estas clases se testean HOY, sin DI, sin base, sin Docker. Es el primer bloque"
  echo "> de trabajo y el de mejor retorno (02-estrategia §1)."
  echo

  # ── 11. Riesgo de romper la imagen (T-DOCK-01) ───────────────────────────
  echo "**Impacto en el build de la imagen** (T-DOCK-01)"
  echo '```'
  local dockerfile; dockerfile=$(files | grep -m1 '^Dockerfile')
  if [ -n "$dockerfile" ]; then
    $G show "$ref:$dockerfile" 2>/dev/null | grep -nE '^(COPY|RUN).*(restore|\.sln|\.csproj)' | head -8
  else
    echo "(sin Dockerfile en este ref)"
  fi
  echo '```'
  echo "> Si el Dockerfile hace \`dotnet restore <algo>.sln\` copiando solo los .csproj de"
  echo "> la app, agregar proyectos de test al .sln **rompe el build de la imagen**."
  echo
}

if [ "${1:-}" = "--todos" ]; then
  for d in "$REPOS_DIR"/*/; do
    r="$(basename "$d")"
    case "$r" in *-wt-*|front-*|database-scripts|faast-app.github.io) continue;; esac
    [ -d "$d/.git" ] || continue
    analizar "$r"
  done
else
  analizar "${1:?uso: analizar-testabilidad.sh <repo> [ref] | --todos}" "${2:-}"
fi
