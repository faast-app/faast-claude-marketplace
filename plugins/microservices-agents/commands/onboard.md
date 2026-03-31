---
description: Adopta un proyecto existente con repos en GitHub. Detecta repos, analiza codigo, trae tickets de GitHub Issues/Projects y prepara el equipo de agentes para trabajar.
argument-hint: Nombre del proyecto o repos (ej. "backoffice" o "faast-app/micro-backoffice-github faast-app/gw-backoffice-github")
---

# Onboard: Adoptar proyecto existente

Adopta el proyecto: $ARGUMENTS

## Paso 1: Detectar repos del proyecto

Si el usuario dio repos especificos, usarlos. Si dio un nombre de proyecto (ej: "backoffice"):

1. Buscar repos locales que matcheen:
   ```bash
   ls ~/OneDrive/Documents/Trabajo/Repositorios/ | grep -i "{nombre}"
   ```
2. Si no hay repos locales, buscar en GitHub:
   ```bash
   gh repo list {org} --limit 50 --json name,description | grep -i "{nombre}"
   ```
3. Presentar la lista al usuario y preguntar: "Estos son los repos que encontre. Confirmas? Quieres agregar o quitar alguno?"

Para cada repo confirmado:
- Si existe local: usar la ruta local
- Si no existe local: `gh repo clone {org}/{repo}` en el directorio de trabajo

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

Presentar resumen al usuario:
```
Repos detectados:
  micro-backoffice-github  → Microservicio .NET 8, MySQL
  gw-backoffice-github     → Gateway .NET 8 (YARP/Ocelot)
  front-backoffice-github  → Frontend React + TypeScript
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
