---
description: Adopta un proyecto existente (mono-repo o multi-repo, en GitHub o Azure DevOps, o solo local). Valida prerequisitos, detecta y analiza repos, trae tickets del tracker y prepara al equipo completo para trabajar.
argument-hint: Nombre del proyecto o repos (ej. "backoffice" o "faast-app/micro-backoffice-github faast-app/gw-backoffice-github")
---

# Onboard: Adoptar proyecto existente

Adopta el proyecto: $ARGUMENTS

## Paso 0: Prerequisitos (agente setup)

Preguntar al usuario donde vive el trabajo del proyecto:
- **GitHub** (Issues + Projects) → el setup valida `gh` instalado y autenticado
- **Azure DevOps** (Boards) → el setup valida `az` + extension `azure-devops` + login
- **Solo local** (sin tracker remoto) → solo git

Invocar al agente `setup` para validar e instalar lo que falte (git, gh/az segun
eleccion). El setup pregunta UNA vez antes de instalar y guarda el resultado en
`.coordination/setup-status.json`. NO continuar si falta el CLI del tracker elegido.

Si es GitHub: obtener org/usuario (`gh api user --jq '.login'`; si hay varias orgs,
preguntar cual). Si es Azure: obtener organizacion y proyecto
(`az devops configure --defaults organization=... project=...`).

## Paso 1: Detectar repos del proyecto

### Caso A: El usuario dio repos especificos
Usarlos directamente. Ejemplo: `onboard faast-app/micro-backoffice-github faast-app/gw-backoffice-github`

### Caso B: El usuario dio un nombre de proyecto
Buscar repos que matcheen con el nombre (ej: "backoffice"):

1. Buscar repos locales que matcheen:
   ```bash
   ls ~/OneDrive/Documents/Trabajo/Repositorios/ | grep -i "{nombre}"
   ```
2. En paralelo, buscar en GitHub:
   ```bash
   gh repo list {org} --limit 100 --json name,description,url | jq '.[] | select(.name | test("{nombre}"; "i"))'
   ```
3. Presentar la lista combinada al usuario:
   ```
   Repos encontrados para "backoffice":
     1. micro-backoffice-github  (local + GitHub)
     2. gw-backoffice-github     (local + GitHub)
     3. front-backoffice-github  (solo GitHub, no clonado)
   ¿Confirmas estos repos? ¿Quieres agregar o quitar alguno?
   ```

### Caso C: No se encontraron matches
Preguntar directamente:
```
No encontre repos que matcheen con "{nombre}".
¿Cuales son los nombres exactos de los repos del proyecto?
Puedes darme:
  - Nombres de repos: micro-backoffice-github, gw-backoffice-github
  - URLs: github.com/faast-app/micro-backoffice-github
  - O la organizacion para buscar: faast-app
```

### Resolver repos
Para cada repo confirmado:
- Si existe local: usar la ruta local
- Si no existe local: preguntar si clonar → `gh repo clone {org}/{repo}` en el directorio de trabajo
- Verificar que es un repo git valido: `git -C {repo} status`

## Paso 2: Analizar cada repo

Por cada repo, ejecutar:

1. **Stack detection:**
   ```bash
   # Detectar stack por archivos presentes
   ls {repo}/*.csproj {repo}/*.sln 2>/dev/null    # .NET
   ls {repo}/package.json 2>/dev/null              # Node.js
   ls {repo}/requirements.txt {repo}/pyproject.toml 2>/dev/null  # Python
   ```

2. **Leer CLAUDE.md o README.md** si existen para entender el contexto

3. **Estructura del proyecto:**
   ```bash
   find {repo}/src -type f -name "*.cs" -o -name "*.ts" -o -name "*.tsx" | head -50
   ```

4. **Git reciente:**
   ```bash
   git -C {repo} log --oneline -10
   git -C {repo} branch -a
   ```

5. Clasificar cada repo como: **micro** (microservicio), **gw** (gateway), **front** (frontend), **shared** (libreria), **infra** (infraestructura), **e2e** (tests), **otro**

### Paso 2a-bis: Detectar topologia

- **Varios repos**, cada uno con un servicio → `topology: "multi"`
- **Un solo repo** que contiene todo (src/services/*, src/frontend/, o un monolito) → `topology: "mono"`
- Caso ambiguo → preguntar al usuario

La topologia detectada se guarda en `.coordination/config.json` (Paso 4) y NUNCA
se propone migrarla salvo pedido explicito del usuario.

Detectar tambien si existe suite E2E (carpeta `e2e/`, `tests/e2e/`, repo `*-e2e`,
`playwright.config.*`). Si no existe, anotarlo: QA la creara cuando valide su primera HU.

### Paso 2b: Configurar acceso del DBA a la base de datos

Esto NO es la conexion del proyecto (eso vive en appsettings.json/.env del repo).
Esto es el **acceso directo del agente DBA** para poder analizar esquemas, indices,
slow queries, datos, etc. Son credenciales que el usuario le da al DBA para que trabaje.

**Preguntar al usuario:**
```
El agente DBA necesita acceso directo a la base de datos para poder
analizar esquemas, optimizar queries e indices, revisar migraciones, etc.

¿Que motor de base de datos usa el proyecto?
  1. MySQL
  2. SQL Server
  3. PostgreSQL
  4. MongoDB
  5. Multiples (indicar cual usa cada servicio)
  6. No necesito DBA por ahora (saltar)
```

Si elige saltar, continuar sin configurar BD. El DBA se configura despues con
`/dev-team:db-health` cuando sea necesario.

Si elige una BD, preguntar las credenciales de acceso del DBA:
```
Credenciales de acceso del DBA a {MySQL/SQL Server/PostgreSQL/MongoDB}:
  - Host: 
  - Puerto: (default: MySQL=3306, SQL Server=1433, PostgreSQL=5432, MongoDB=27017)
  - Base de datos: 
  - Usuario: 
  - Password: 
```

### Paso 2c: Validar que el cliente de BD esta instalado

Verificar que el cliente CLI correspondiente existe en el sistema:

| BD | Comando | Si no esta instalado |
|----|---------|---------------------|
| MySQL | `mysql --version` | `winget install Oracle.MySQL` / `brew install mysql-client` / `apt install mysql-client` |
| SQL Server | `sqlcmd --version` | `winget install Microsoft.Sqlcmd` / `brew install microsoft/mssql-release/mssql-tools18` |
| PostgreSQL | `psql --version` | `winget install PostgreSQL.PostgreSQL` / `brew install libpq` / `apt install postgresql-client` |
| MongoDB | `mongosh --version` | `winget install MongoDB.Shell` / `brew install mongosh` |

Si NO esta instalado:
1. Informar al usuario que es necesario
2. Preguntar: "¿Quieres que intente instalarlo ahora?"
3. Si dice si → ejecutar el comando de instalacion segun el OS
4. Si dice no → continuar sin conexion, el DBA no podra ejecutar queries directas

Despues de instalar, verificar de nuevo que funciona.

### Paso 2d: Probar conexion del DBA

```bash
# MySQL
mysql -h {host} -P {port} -u {user} -p{password} -e "SELECT 1; SHOW DATABASES;" {database}

# SQL Server
sqlcmd -S {host},{port} -U {user} -P {password} -d {database} -Q "SELECT 1; SELECT name FROM sys.databases;"

# PostgreSQL
PGPASSWORD={password} psql -h {host} -p {port} -U {user} -d {database} -c "SELECT 1; \l"

# MongoDB
mongosh "mongodb://{user}:{password}@{host}:{port}/{database}" --eval "db.runCommand({ping:1}); db.getCollectionNames();"
```

- Conexion OK → ✓ "DBA conectado a {database} en {host}"
- Conexion FALLA → mostrar el error exacto, preguntar:
  - "¿Corregir credenciales?"
  - "¿Continuar sin conexion de DBA?" (se configura despues)

### Paso 2e: Guardar configuracion del DBA

Guardar en `.coordination/dba-access.json` (NUNCA en git, NUNCA commitear):
```json
{
  "connections": [
    {
      "name": "backoffice-dev",
      "type": "mysql",
      "host": "dev-db.faast.cl",
      "port": 3306,
      "database": "backoffice_dev",
      "user": "dba_user",
      "password": "***",
      "status": "connected",
      "repos": ["micro-backoffice-github"]
    }
  ],
  "tools": {
    "mysql": true,
    "sqlcmd": false,
    "psql": false,
    "mongosh": false
  }
}
```

El agente DBA lee este archivo para saber como conectarse. El password se guarda
en el mismo archivo porque es LOCAL y no se commitea. Agregar a .gitignore si existe.

Presentar resumen al usuario:
```
Repos detectados:
  micro-backoffice-github  → Microservicio .NET 8
  gw-backoffice-github     → Gateway .NET 8 (YARP/Ocelot), sin BD propia
  front-backoffice-github  → Frontend React + TypeScript

Base de datos:
  micro-backoffice-github  → MySQL @ dev-db.faast.cl:3306/backoffice_dev (conexion OK ✓)

Herramientas:
  gh CLI      → OK ✓
  mysql       → OK ✓ (v8.0.35)
  git         → OK ✓
```

## Paso 3: Traer tickets del tracker

**Si el tracker es Azure DevOps:** traer los work items con
```bash
az boards query --wiql "SELECT [System.Id],[System.Title],[System.State],[System.WorkItemType] FROM WorkItems WHERE [System.TeamProject]='{proyecto}' AND [System.State] <> 'Closed' ORDER BY [Microsoft.VSTS.Common.Priority]" --output json
```
y clasificar por estado (New/Approved → To Do, Active/Committed → In Progress,
Resolved → In Review, Closed/Done → Done). Luego saltar a la clasificacion por repo.

**Si el tracker es GitHub:**

1. **Obtener issues abiertos** de cada repo:
   ```bash
   gh issue list --repo {org}/{repo} --state open --json number,title,labels,assignees,milestone,state,body --limit 100
   ```

2. **Obtener el GitHub Project** asociado (si existe):
   ```bash
   gh project list --owner {org} --format json
   gh project item-list {project-number} --owner {org} --format json --limit 200
   ```

3. **Para cada item del Project**, obtener su estado (columna):
   ```bash
   gh project item-list {project-number} --owner {org} --format json | jq '.items[] | {title, status: .status, repo: .content.repository, number: .content.number}'
   ```

4. Clasificar tickets por estado:
   - **To Do / Backlog** → pendientes de asignar
   - **In Progress** → alguien ya esta trabajando
   - **In Review** → esperando review/merge
   - **Done** → completados

5. Clasificar tickets por repo/agente:
   - Issues en repo micro → Backend
   - Issues en repo gw → Backend (gateway)
   - Issues en repo front → Frontend
   - Issues sin repo especifico → Lead decide

## Paso 4: Crear estructura de coordinacion

Segun la topologia detectada:
- **multi** → carpeta paraguas `~/projects/{proyecto}/` con `.coordination/` y los repos
- **mono** → `.coordination/` en la raiz del repo unico (agregar `dba-access.json` y
  `setup-status.json` al .gitignore)

```
.coordination/
├── config.json             ← Fuente de verdad: topologia, tracker, urls (ver abajo)
├── handoffs/
│   └── archive/
├── test-plans/             ← Planes de prueba de QA
├── wiki/                   ← Wiki viva del proyecto (crear con /dev-team:wiki init)
├── metrics/                ← activity.jsonl (eventos de los agentes)
├── evidence/               ← Evidencia de QA (screenshots/clips)
├── backlog.md              ← Generado desde los tickets reales del tracker
├── sprint-actual.md        ← Generado desde el estado del Project/Board
├── architecture.md         ← Generado desde analisis de repos
└── repos.md                ← Mapa de repos con rutas locales y URLs
```

**config.json:**
```json
{
  "project": "{nombre}",
  "topology": "mono|multi",
  "tracker": {
    "provider": "github|azure",
    "github": { "org": "{org}", "project": "{project-number-o-nombre}" },
    "azure": { "organization": "https://dev.azure.com/{org}", "project": "{proyecto}" }
  },
  "urls": { "dev": "http://localhost:{puerto}" },
  "e2e": { "exists": true, "path": "{ruta-suite-o-repo}" }
}
```

**repos.md** debe contener:
```markdown
# Repos del proyecto

| Repo | Tipo | Stack | Ruta local | GitHub URL |
|------|------|-------|------------|------------|
| micro-backoffice-github | micro | .NET 8 | /path/to/local | github.com/org/repo |
```

**backlog.md** se genera desde los issues reales:
```markdown
# Backlog (sincronizado con GitHub Issues)

## En Progreso
- [ ] [#45](url) Agregar filtro de fecha — Repo: micro + front — Asignado: Backend + Frontend

## Pendientes (To Do)
- [ ] [#52](url) Endpoint de exportacion PDF — Repo: micro — Sin asignar
- [ ] [#53](url) Mejorar tabla de cobranzas — Repo: front — Sin asignar

## En Review
- [~] [#41](url) Fix paginacion — PR #89 — Esperando merge
```

## Paso 4.5: Wiki y metricas
1. Ejecutar `/dev-team:wiki init` (tech-writer): crea `.coordination/wiki/` e
   ingiere lo detectado (architecture.md, backlog, repos.md)
2. Crear `.coordination/metrics/` para el event log de los agentes
3. Sugerir: abrir la wiki como vault de Obsidian y `/dev-team:team-office` para
   ver al equipo en vivo

## Paso 5: Presentar resumen y preguntar siguiente paso

Mostrar:
- Topologia detectada (mono/multi) y repos adoptados (N repos, stacks)
- Tracker configurado (GitHub/Azure) y tickets totales: N abiertos (X to-do, Y in-progress, Z in-review)
- Estado del entorno segun el setup (herramientas, conexion BD, suite E2E existe o no)
- Tickets sin asignar que se pueden empezar

Preguntar:
- "¿Asigno tickets a los agentes y empiezan a trabajar?" → /dev-team:assign-task
- "¿Revisamos el backlog primero?" → /dev-team:refine si faltan HUs bien definidas
- "¿Analisis de arquitectura mas profundo?" → agente architect
- Recordar: "/dev-team:start te orienta en cualquier momento"
