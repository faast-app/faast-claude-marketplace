---
description: Adopta un proyecto existente con repos en GitHub. Detecta repos, analiza codigo, trae tickets de GitHub Issues/Projects y prepara el equipo de agentes para trabajar.
argument-hint: Nombre del proyecto o repos (ej. "backoffice" o "faast-app/micro-backoffice-github faast-app/gw-backoffice-github")
---

# Onboard: Adoptar proyecto existente

Adopta el proyecto: $ARGUMENTS

## Paso 0: Validar prerequisitos

### GitHub CLI (gh)
Verificar que `gh` esta instalado y autenticado:
```bash
gh --version 2>/dev/null
gh auth status 2>/dev/null
```

**Si `gh` NO esta instalado:**
```
GitHub CLI (gh) no esta instalado. Es necesario para traer tickets e interactuar con GitHub.

Instalar con:
  Windows:  winget install GitHub.cli
  macOS:    brew install gh
  Linux:    sudo apt install gh

Despues de instalar: gh auth login
```
Detener aqui y esperar a que el usuario lo instale.

**Si `gh` esta instalado pero NO autenticado:**
```
GitHub CLI no esta autenticado. Ejecuta:
  gh auth login
Y selecciona tu cuenta de GitHub.
```
Detener aqui y esperar autenticacion.

**Si `gh` esta OK:** Obtener la org/usuario autenticado:
```bash
gh auth status --hostname github.com 2>&1
gh api user --jq '.login' 2>/dev/null
```
Guardar el usuario/org para usarlo en los pasos siguientes. Si el usuario pertenece a multiples orgs, preguntar cual usar:
```bash
gh api user/orgs --jq '.[].login' 2>/dev/null
```

### Git
Verificar que git esta disponible:
```bash
git --version
```

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

5. Clasificar cada repo como: **micro** (microservicio), **gw** (gateway), **front** (frontend), **shared** (libreria), **infra** (infraestructura), **otro**

6. **Detectar base de datos** en repos de backend (micro, gw):
   ```bash
   # Buscar en connection strings, appsettings, .env, docker-compose
   grep -ri "mysql\|MySql\|Pomelo" {repo}/src/ --include="*.cs" --include="*.csproj" --include="*.json" -l 2>/dev/null
   grep -ri "sqlserver\|SqlServer\|Microsoft.EntityFrameworkCore.SqlServer" {repo}/src/ --include="*.cs" --include="*.csproj" --include="*.json" -l 2>/dev/null
   grep -ri "npgsql\|postgres\|PostgreSQL" {repo}/src/ --include="*.cs" --include="*.csproj" --include="*.json" -l 2>/dev/null
   grep -ri "mongodb\|MongoClient" {repo}/src/ --include="*.cs" --include="*.ts" --include="*.json" -l 2>/dev/null

   # Buscar en docker-compose
   grep -i "mysql\|mariadb\|postgres\|sqlserver\|mssql\|mongo" {repo}/docker-compose* 2>/dev/null

   # Buscar en appsettings / .env
   grep -i "connectionstring\|DB_HOST\|DATABASE_URL" {repo}/src/appsettings*.json {repo}/.env* 2>/dev/null
   ```

   Clasificar BD detectada:
   - **MySQL** → Pomelo.EntityFrameworkCore.MySql, mysql en docker-compose, Server= en connection string
   - **SQL Server** → Microsoft.EntityFrameworkCore.SqlServer, mssql en docker-compose, Data Source= en connection string
   - **PostgreSQL** → Npgsql.EntityFrameworkCore.PostgreSQL, postgres en docker-compose
   - **MongoDB** → MongoDB.Driver, mongo en docker-compose
   - **No detectada** → Preguntar al usuario: "No pude detectar la BD de {repo}. ¿Cual usa? (mysql/sqlserver/postgres/mongodb)"

   Esta informacion se usa en el Paso 2b para configurar la conexion.

### Paso 2b: Configurar conexion a base de datos

Una vez detectado el tipo de BD, preguntar al usuario las credenciales de conexion.
El appsettings.json puede tener placeholders, variables de entorno, o estar incompleto — no asumir que las credenciales estan ahi.

**Preguntar al usuario:**
```
Detecte que {repo} usa {MySQL/SQL Server/PostgreSQL/MongoDB}.
Necesito configurar la conexion para que el DBA pueda trabajar.

¿Cual es la conexion de DESARROLLO?
  - Host: (ej: localhost, 192.168.1.100, dev-db.faast.cl)
  - Puerto: (default: MySQL=3306, SQL Server=1433, PostgreSQL=5432, MongoDB=27017)
  - Base de datos: (nombre)
  - Usuario: (ej: root, sa, admin)
  - Password: (se guarda solo localmente en .coordination/, NUNCA se commitea)
```

**Si el usuario tiene multiples BDs** (ej: un micro usa MySQL y otro usa SQL Server):
Preguntar la conexion de cada una por separado.

**Guardar la conexion** en `.coordination/db-connections.json` (NUNCA en git):
```json
{
  "connections": {
    "micro-backoffice-github": {
      "type": "mysql",
      "host": "dev-db.faast.cl",
      "port": 3306,
      "database": "backoffice_dev",
      "user": "dev_user"
    },
    "micro-otro-servicio": {
      "type": "sqlserver",
      "host": "192.168.1.50",
      "port": 1433,
      "database": "otro_dev",
      "user": "sa"
    }
  }
}
```
**El password se guarda aparte** en `.coordination/.db-secrets` (archivo plano, gitignored):
```
micro-backoffice-github=mi_password_dev
micro-otro-servicio=sa_password
```

**Verificar la conexion** si es posible:
```bash
# MySQL
mysql -h {host} -P {port} -u {user} -p{password} -e "SELECT 1" {database} 2>/dev/null

# SQL Server (si sqlcmd esta disponible)
sqlcmd -S {host},{port} -U {user} -P {password} -d {database} -Q "SELECT 1" 2>/dev/null

# PostgreSQL
PGPASSWORD={password} psql -h {host} -p {port} -U {user} -d {database} -c "SELECT 1" 2>/dev/null
```

Si la conexion falla, avisar pero no bloquear — el usuario puede corregir despues.

Esta informacion se pasa al agente DBA para que configure su workspace en `dba-scripts/{proyecto}/`.

Presentar resumen al usuario:
```
Repos detectados:
  micro-backoffice-github  → Microservicio .NET 8
  gw-backoffice-github     → Gateway .NET 8 (YARP/Ocelot), sin BD propia
  front-backoffice-github  → Frontend React + TypeScript

Base de datos:
  micro-backoffice-github  → MySQL 8 @ dev-db.faast.cl:3306/backoffice_dev (conexion OK ✓)
```

## Paso 3: Traer tickets de GitHub Issues y Projects

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

## Paso 4: Crear carpeta paraguas y coordinacion

Crear la estructura de coordinacion:

```
~/projects/{nombre-proyecto}/
├── .coordination/
│   ├── handoffs/
│   │   └── archive/
│   ├── backlog.md          ← Generado desde GitHub Issues reales
│   ├── sprint-actual.md    ← Generado desde GitHub Project (columna actual)
│   ├── architecture.md     ← Generado desde analisis de repos
│   └── repos.md            ← Mapa de repos con rutas locales y URLs
├── {repo-1}/ → symlink o ruta al repo local
├── {repo-2}/ → symlink o ruta al repo local
└── ...
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

## Paso 5: Presentar resumen y preguntar siguiente paso

Mostrar:
- Repos adoptados (N repos, stacks)
- Tickets totales: N abiertos (X to-do, Y in-progress, Z in-review)
- Tickets sin asignar que se pueden empezar

Preguntar:
- "Quieres que asigne tickets a los agentes y empiecen a trabajar?"
- "Quieres revisar el backlog primero?"
- "Quieres que haga un analisis de arquitectura mas profundo?"
