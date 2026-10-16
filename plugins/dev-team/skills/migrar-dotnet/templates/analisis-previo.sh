#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# analisis-previo.sh — Fase 1 de la skill `migrar-dotnet`.
#
# SOLO LECTURA. No hace checkout, no escribe en el repo, no compila.
# Lee un ref remoto (origin/develop por defecto) con `git grep` / `git ls-tree`.
#
# Uso:
#   ./analisis-previo.sh <repo> [ref]
#   ./analisis-previo.sh micro-banco origin/develop
#   ./analisis-previo.sh --todos            # barrido de toda la flota
#
# Salida: bloque Markdown listo para pegar en el informe de migración
#         (templates/informe-migracion.md §1).
#
# Este script es la versión ejecutable de reference/01-analisis-previo.md.
# Los hallazgos que produce NO son un veredicto: son la entrada del análisis.
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
  # grep contando ocurrencias sobre un ref (sin checkout)
  cnt() { $G grep -c -I -E "$1" "$ref" -- "${@:2}" 2>/dev/null | awk -F: '{s+=$NF} END{print s+0}'; }
  hit() { $G grep -n -I -E "$1" "$ref" -- "${@:2}" 2>/dev/null | head -"${LIM:-3}"; }
  files() { $G ls-tree -r --name-only "$ref" 2>/dev/null; }

  echo "### $r  (ref: $ref)"
  echo

  # ── 1. TFM e infraestructura de build ────────────────────────────────────
  echo "**TFM / build**"
  echo '```'
  echo "TargetFramework(csproj): $($G grep -h -o -E '<TargetFrameworks?>[^<]+' "$ref" -- '*.csproj' 2>/dev/null \
        | sed -E 's/.*>//' | tr ';' '\n' | sort -u | paste -sd, -)"
  echo "TargetFramework(props):  $($G grep -h -o -E '<TargetFrameworks?>[^<]+' "$ref" -- '*.props' 2>/dev/null \
        | sed -E 's/.*>//' | sort -u | paste -sd, -)"
  echo "csproj:                  $(files | grep -c '\.csproj$')   sln: $(files | grep -c '\.sln$')"
  echo "sln (ruta):              $(files | grep -m2 '\.sln$' | paste -sd' ' -)"
  echo "global.json:             $(files | grep -m1 'global\.json$') $( f=$(files|grep -m1 'global\.json$'); [ -n "$f" ] && $G show "$ref:$f" 2>/dev/null | tr -d '\n ' )"
  echo "Directory.Build.props:   $(files | grep -m1 'Directory\.Build\.props$')"
  echo "Proyectos de test:       $(files | grep -c -iE '(test|spec)s?/.*\.csproj$|\.(Tests|UnitTests|IntegrationTests)\.csproj$')"
  echo "AssemblyName declarado:  $($G grep -h -o -E '<AssemblyName>[^<]+' "$ref" -- '*.csproj' 2>/dev/null | sed -E 's/.*>//' | sort -u | paste -sd, -)"
  echo '```'
  echo

  # ── 2. Bloqueadores duros (si hay, la migración NO es mecánica) ──────────
  echo "**Bloqueadores duros**  (>0 ⇒ leer 02-ruta-por-saltos §4)"
  echo '```'
  printf '%-34s %s\n' "BinaryFormatter"              "$(cnt 'BinaryFormatter' '*.cs')"
  printf '%-34s %s\n' "AppDomain.CreateDomain"       "$(cnt 'AppDomain\.(CreateDomain|Unload)' '*.cs')"
  printf '%-34s %s\n' "Remoting"                     "$(cnt 'System\.Runtime\.Remoting' '*.cs')"
  printf '%-34s %s\n' "System.Web (HttpContext.Curr)" "$(cnt 'HttpContext\.Current' '*.cs')"
  printf '%-34s %s\n' "WCF cliente (ServiceModel)"   "$(cnt 'System\.ServiceModel' '*.cs' '*.csproj')"
  printf '%-34s %s\n' "WCF servidor (ServiceHost)"   "$(cnt 'ServiceHost|\[ServiceContract' '*.cs')"
  printf '%-34s %s\n' "EF6 (pkg EntityFramework)"    "$(cnt 'Include="EntityFramework"' '*.csproj')"
  printf '%-34s %s\n' "GDI+ real (Bitmap/Graphics)"  "$(cnt '\b(new Bitmap|Graphics\.From|Image\.From|System\.Drawing\.(Bitmap|Image|Graphics))\b' '*.cs')"
  printf '%-34s %s\n' "pkg System.Drawing.Common"    "$(cnt 'Include="System\.Drawing\.Common"' '*.csproj')"
  printf '%-34s %s\n' "using System.Drawing (ruido)" "$(cnt 'using System\.Drawing' '*.cs')"
  printf '%-34s %s\n' "DirectoryServices / LDAP"     "$(cnt 'DirectoryServices' '*.cs' '*.csproj')"
  echo '```'
  echo "> \`using System.Drawing\` **no** es un bloqueador por sí solo: Color/Point/Size/Rectangle"
  echo "> viven en System.Drawing.Primitives y funcionan en Linux. Lo que rompe es el **paquete**"
  echo "> \`System.Drawing.Common\` con Bitmap/Graphics/Image. Si la fila 'GDI+ real' y la fila 'pkg'"
  echo "> están en 0, el \`using\` es huérfano y **no bloquea nada**."
  echo

  # ── 3. Hosting y binding ─────────────────────────────────────────────────
  echo "**Hosting / binding**"
  echo '```'
  printf '%-34s %s\n' "class Startup (modelo viejo)" "$(cnt 'class Startup' '*.cs')"
  printf '%-34s %s\n' "WebApplication.CreateBuilder" "$(cnt 'WebApplication\.CreateBuilder' '*.cs')"
  printf '%-34s %s\n' "UseUrls"                      "$(cnt 'UseUrls' '*.cs')"
  printf '%-34s %s\n' "UseKestrel/ListenAnyIP"       "$(cnt 'UseKestrel|ListenAnyIP|ListenLocalhost' '*.cs')"
  printf '%-34s %s\n' "IHostingEnvironment (obsol.)" "$(cnt 'IHostingEnvironment' '*.cs')"
  printf '%-34s %s\n' "rutas Windows C:\\ o D:\\"     "$(cnt '\"[A-Da-d]:\\\\\\\\' '*.cs' '*.json')"
  echo '```'
  LIM=4 hit 'UseUrls' '*.cs'
  echo "> Ojo con \`UseUrls\`: **no importa si dice localhost o \`*\`** — en ambos casos"
  echo "> **pisa \`ASPNETCORE_URLS\`**, así que el contenedor no va a escuchar en 8080."
  echo

  # ── 4. Serialización, cultura, fechas ────────────────────────────────────
  echo "**Serialización / cultura / fechas**"
  echo '```'
  printf '%-34s %s\n' "Newtonsoft.Json"              "$(cnt 'Newtonsoft' '*.cs' '*.csproj')"
  printf '%-34s %s\n' "AddNewtonsoftJson"            "$(cnt 'AddNewtonsoftJson' '*.cs')"
  printf '%-34s %s\n' "System.Text.Json"             "$(cnt 'System\.Text\.Json' '*.cs')"
  printf '%-34s %s\n' "InvariantGlobalization"       "$($G grep -h -o -E '<InvariantGlobalization>[^<]*' "$ref" -- '*.csproj' 2>/dev/null | sed -E 's/.*>//' | sort -u | paste -sd, -)"
  printf '%-34s %s\n' "new CultureInfo(\"xx-XX\")"     "$(cnt 'new CultureInfo\("[a-z]{2}-[A-Z]{2}"\)' '*.cs')"
  printf '%-34s %s\n' "CultureInfo.InvariantCulture" "$(cnt 'CultureInfo\.InvariantCulture' '*.cs')"
  printf '%-34s %s\n' "DateTime.Now (vs UtcNow)"     "$(cnt 'DateTime\.Now' '*.cs')"
  printf '%-34s %s\n' "TimeZoneInfo.FindSystemTime"  "$(cnt 'TimeZoneInfo\.FindSystemTimeZoneById' '*.cs')"
  echo '```'
  echo "> \`InvariantGlobalization=true\` + \`new CultureInfo(\"es-PE\")\` ⇒ **CultureNotFoundException**"
  echo "> (PredefinedCulturesOnly). Si la fila de culturas concretas es >0 y la bandera es true,"
  echo "> es un bug latente que la migración va a destapar. Ver 04-catalogo-errores E-CULT-01."
  echo

  # ── 5. Datos y almacenamiento ────────────────────────────────────────────
  echo "**Acceso a datos**"
  echo '```'
  $G grep -h -o -E 'Include="(Microsoft\.EntityFrameworkCore[^"]*|Pomelo\.EntityFrameworkCore\.MySql|MySql\.(Data|EntityFrameworkCore)|MySqlConnector|Microsoft\.Data\.SqlClient|System\.Data\.SqlClient|Dapper|Npgsql[^"]*)" *Version="[^"]+"' "$ref" -- '*.csproj' 2>/dev/null \
    | sed -E 's/Include="//; s/" *Version="/  /; s/"$//' | sort -u
  printf '%-34s %s\n' "Encrypt= en connection str"   "$(cnt 'Encrypt *=' '*.json' '*.cs')"
  printf '%-34s %s\n' "TrustServerCertificate"       "$(cnt 'TrustServerCertificate' '*.json' '*.cs')"
  echo '```'
  echo "> \`System.Data.SqlClient\` ⇒ migrar a \`Microsoft.Data.SqlClient\`, que trae **Encrypt=true**"
  echo "> por defecto (4.0+). Contra SQL Server viejo sin cert válido: **E-SQL-01**."
  echo

  # ── 6. Auth / crypto (gate de cybersec) ──────────────────────────────────
  echo "**Auth / crypto**  (si hay algo acá ⇒ gate de cybersec, 05-rollback §5)"
  echo '```'
  $G grep -h -o -E 'Include="(System\.IdentityModel\.Tokens\.Jwt|Microsoft\.IdentityModel\.[^"]*|Microsoft\.AspNetCore\.Authentication\.[^"]*|BouncyCastle[^"]*)" *Version="[^"]+"' "$ref" -- '*.csproj' 2>/dev/null \
    | sed -E 's/Include="//; s/" *Version="/  /; s/"$//' | sort -u
  printf '%-34s %s\n' "new X509Certificate2("        "$(cnt 'new X509Certificate2\(' '*.cs')"
  printf '%-34s %s\n' "JwtSecurityTokenHandler"      "$(cnt 'JwtSecurityTokenHandler' '*.cs')"
  printf '%-34s %s\n' "MapInboundClaims"             "$(cnt 'MapInboundClaims' '*.cs')"
  printf '%-34s %s\n' "SameSite"                     "$(cnt 'SameSite' '*.cs')"
  printf '%-34s %s\n' "AllowAnyOrigin"               "$(cnt 'AllowAnyOrigin' '*.cs')"
  printf '%-34s %s\n' "AllowCredentials"             "$(cnt 'AllowCredentials' '*.cs')"
  echo '```'
  echo

  # ── 7. Paquetes con salto propio ─────────────────────────────────────────
  echo "**Paquetes que tienen su propia migración**"
  echo '```'
  $G grep -h -o -E 'Include="(Swashbuckle\.AspNetCore|Ocelot[^"]*|Yarp\.[^"]*|Hangfire[^"]*|Sentry[^"]*|Serilog\.[^"]*|NLog[^"]*|AutoMapper[^"]*|MediatR|SkiaSharp[^"]*|QuestPDF|PuppeteerSharp|Selenium\.[^"]*|GemBox\.[^"]*|iText[^"]*|itext[^"]*|ClosedXML|EPPlus|ExcelDataReader|SSH\.NET|Renci[^"]*|AWSSDK\.[^"]*|FirebaseAdmin|MailKit|Newtonsoft\.Json|FaaST[^"]*|Faast[^"]*)" *Version="[^"]+"' "$ref" -- '*.csproj' 2>/dev/null \
    | sed -E 's/Include="//; s/" *Version="/  /; s/"$//' | sort -u
  echo '```'
  echo

  # ── 8. Versiones flotantes (build no reproducible) ───────────────────────
  local flot
  flot="$($G grep -h -o -E 'Include="[^"]+" *Version="[^"]*\*[^"]*"' "$ref" -- '*.csproj' 2>/dev/null \
          | sed -E 's/Include="//; s/" *Version="/  /; s/"$//' | sort -u)"
  if [ -n "$flot" ]; then
    echo "**Versiones flotantes (\`*\`) — fijar ANTES de migrar**"
    echo '```'; echo "$flot"; echo '```'; echo
  fi

  # ── 9. Archivos en disco que el contenedor necesita ──────────────────────
  echo "**Artefactos en disco**"
  echo '```'
  files | grep -iE '^(cert|Templates?|Assets|TemplateEmail|TemplateExcel|FileServer|Logs)/' | head -8
  echo "ocelot*.json:   $(files | grep -ci 'ocelot.*\.json$')"
  echo "appsettings*:   $(files | grep -c 'appsettings.*\.json$')"
  echo "Dockerfile:     $(files | grep -c '^Dockerfile')"
  echo '```'
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
  analizar "${1:?uso: analisis-previo.sh <repo> [ref] | --todos}" "${2:-}"
fi
