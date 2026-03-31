# Guia de Uso: Microservices Agents Plugin

## Instalacion

```bash
# 1. Agregar el marketplace (una sola vez)
/plugin marketplace add faast-app/faast-claude-marketplace

# 2. Instalar el plugin
/plugin install microservices-agents@faast-marketplace

# 3. Actualizar (cuando haya cambios)
/plugin marketplace update faast-marketplace
/plugin update microservices-agents
```

---

## 12 Commands disponibles

| Command | Descripcion |
|---------|-------------|
| `/microservices-agents:new-project` | Crear proyecto nuevo desde documento de requerimientos |
| `/microservices-agents:onboard` | Adoptar proyecto existente con repos en GitHub |
| `/microservices-agents:status` | Ver estado del proyecto (backlog, sprint, repos) |
| `/microservices-agents:sync-github` | Sincronizar con GitHub Issues/Projects |
| `/microservices-agents:assign-task` | Asignar ticket a un agente (Lead) |
| `/microservices-agents:inbox` | Leer handoffs pendientes |
| `/microservices-agents:handoff` | Crear handoff a otro agente |
| `/microservices-agents:git-check` | Verificar git antes de commit |
| `/microservices-agents:review-pr` | Revisar un Pull Request |
| `/microservices-agents:deploy-check` | Verificar readiness para deploy |
| `/microservices-agents:security-audit` | Auditoria de seguridad |
| `/microservices-agents:db-health` | Health check de base de datos |

## 7 Agentes

| Agente | Rol | Cuando se invoca |
|--------|-----|-----------------|
| **architect** | Diseña la arquitectura desde requerimientos | `/new-project` |
| **lead** | Coordina, asigna tareas, mergea | `/assign-task`, `/status` |
| **backend** | Desarrolla microservicios | Cuando trabaja en repos de backend |
| **frontend** | Desarrolla SPA / microfrontends | Cuando trabaja en repos de frontend |
| **dba** | Analiza y optimiza bases de datos | `/db-health`, cuando se revisan migraciones |
| **infra** | Dockerfiles, CI/CD, gateways | `/deploy-check`, cuando se toca infra |
| **cybersec** | Audita seguridad, no commitea codigo | `/security-audit`, antes de merge a main |

---

## Flujo A: Proyecto NUEVO (desde cero)

```
Paso 1                    Paso 2                      Paso 3
/new-project              Arquitecto analiza          Usuario aprueba
docs/requerimientos.docx  y propone servicios,        o ajusta el plan
                          BD, gateway, frontend
      │                         │                          │
      ▼                         ▼                          ▼
Paso 4                    Paso 5                      Paso 6
Se crean repos            Lead asigna                 Agentes trabajan
independientes            tickets del backlog         cada uno en su repo
con scaffolding           a los agentes               coordinados via handoffs
```

### Paso 1: Crear el proyecto
```bash
/microservices-agents:new-project docs/requerimientos-ecommerce.docx
```
- Lee el documento de requerimientos
- Invoca al agente **Arquitecto**

### Paso 2: El Arquitecto propone
El Arquitecto genera `architecture.md` con:
- Bounded contexts y microservicios
- Stack por servicio (no asume que todo es .NET)
- Patron por servicio (Clean Architecture, Hexagonal, Vertical Slice, CQRS, Minimal API)
- API Gateway (Traefik, YARP, Ocelot, o ninguno)
- Frontend (SPA o microfrontends)
- Comunicacion entre servicios (HTTP, gRPC, RabbitMQ)
- Diagrama Mermaid

### Paso 3: Aprobar
El usuario revisa. Puede decir:
- "Aprobado" → se crean los repos
- "Quita el servicio X" → Arquitecto ajusta
- "Prefiero YARP en vez de Traefik" → Arquitecto ajusta

### Paso 4: Se crean los repos
Automaticamente se genera:
```
~/projects/ecommerce/
├── .coordination/
│   ├── handoffs/
│   ├── backlog.md
│   ├── sprint-actual.md
│   └── architecture.md
├── docker-compose.dev.yml
├── ecommerce-user-service/       ← git init
├── ecommerce-order-service/      ← git init
├── ecommerce-gateway/            ← git init
├── ecommerce-frontend-shell/     ← git init
└── ...
```

### Paso 5: Asignar trabajo
```bash
/microservices-agents:assign-task
```
- Muestra tareas del backlog
- Eliges a quien asignar (backend, frontend, dba, infra)
- Crea branch y handoff automaticamente

### Paso 6: Los agentes trabajan
Cada agente usa `/inbox` para ver su trabajo, implementa en su repo, y al terminar
crea handoff al Lead.

---

## Flujo B: Proyecto EXISTENTE (onboard)

```
Paso 1                    Paso 2                      Paso 3
/onboard backoffice       Detecta repos               Configura acceso
                          locales o en GitHub          del DBA a la BD
      │                         │                          │
      ▼                         ▼                          ▼
Paso 4                    Paso 5                      Paso 6
Trae tickets de           Crea carpeta paraguas       Asigna tickets
GitHub Issues/Projects    con backlog real             y empiezan a trabajar
```

### Paso 1: Onboard del proyecto
```bash
/microservices-agents:onboard backoffice
```

### Paso 2: Detectar repos
- Busca repos que matcheen con "backoffice" (local y GitHub)
- Si no encuentra → pregunta los nombres exactos
- Analiza cada repo (stack, estructura, branches)
- Presenta resumen:
  ```
  micro-backoffice-github  → Microservicio .NET 8
  gw-backoffice-github     → Gateway .NET 8
  front-backoffice-github  → Frontend React + TypeScript
  ```

### Paso 3: Configurar BD para el DBA
- Pregunta que motor usa (MySQL, SQL Server, PostgreSQL, MongoDB)
- Valida que el cliente CLI esta instalado (`mysql`, `sqlcmd`, etc.)
- Si no esta → ofrece instalarlo
- Pide credenciales de acceso del DBA (host, puerto, user, password)
- Prueba la conexion
- Se puede saltar y configurar despues con `/db-health`

### Paso 4: Traer tickets de GitHub
- Lee issues abiertos de cada repo
- Lee el GitHub Project (si existe) con estados
- Clasifica: To Do, In Progress, In Review, Done

### Paso 5: Crear carpeta paraguas
```
~/projects/backoffice/
├── .coordination/
│   ├── handoffs/
│   ├── backlog.md         ← desde GitHub Issues reales
│   ├── sprint-actual.md   ← desde GitHub Project
│   ├── architecture.md    ← desde analisis del codigo
│   ├── repos.md           ← mapa de repos
│   └── dba-access.json    ← credenciales del DBA (local, no en git)
├── micro-backoffice-github/
├── gw-backoffice-github/
└── front-backoffice-github/
```

### Paso 6: Asignar y trabajar
```bash
/microservices-agents:assign-task
```
Asigna tickets reales de GitHub a los agentes.

---

## Flujo C: Trabajo diario

### Inicio del dia
```bash
# 1. Ver estado general
/microservices-agents:status

# 2. Sincronizar con GitHub (traer issues nuevos, actualizar estados)
/microservices-agents:sync-github pull

# 3. Asignar trabajo pendiente
/microservices-agents:assign-task
```

### Trabajando en un ticket (como agente)
```bash
# 1. Ver que tengo asignado
/microservices-agents:inbox

# 2. Trabajar en el codigo...
# (el agente implementa en su repo)

# 3. Antes de commitear, verificar git
/microservices-agents:git-check

# 4. Si necesito algo de otro agente
/microservices-agents:handoff
```

### Completando un ticket
```bash
# 1. Verificar que esta listo para deploy
/microservices-agents:deploy-check

# 2. Si toca auth o datos sensibles, pedir auditoria
/microservices-agents:security-audit

# 3. Crear PR y actualizar GitHub
/microservices-agents:sync-github push
# → Crea PR linkeado al issue (closes #N)
# → Mueve issue a "In Review"
# → Comenta en el issue

# 4. Lead revisa el PR
/microservices-agents:review-pr 123
```

### Merge y cierre
```bash
# Lead mergea y sync-github actualiza todo
/microservices-agents:sync-github push
# → Issue pasa a "Done"
# → Comenta confirmacion en el issue
```

---

## Flujo D: Ticket que involucra multiples repos

Ejemplo: "Agregar filtro de fecha a cobranzas" requiere cambios en micro + gw + front.

```
Lead asigna ticket #52 a 3 agentes:

Backend (micro-backoffice):
  1. /inbox → lee ticket
  2. Implementa endpoint GET /api/cobranzas?fecha_desde=&fecha_hasta=
  3. Actualiza docs/openapi.yml
  4. /handoff → avisa al Frontend que el endpoint esta listo
  5. /sync-github push → PR + issue "In Progress"

Backend (gw-backoffice):
  1. /inbox → lee ticket
  2. Agrega ruta al gateway para el nuevo endpoint
  3. /handoff → confirma que el gateway rutea

Frontend (front-backoffice):
  1. /inbox → lee ticket + lee handoff del Backend con el contrato
  2. Implementa UI del filtro de fecha
  3. Conecta al endpoint via cliente HTTP tipado
  4. /sync-github push → PR

Lead:
  1. /review-pr (micro) → aprueba
  2. /review-pr (gw) → aprueba
  3. /review-pr (front) → aprueba
  4. /sync-github push → issue #52 → Done ✅
```

---

## Flujo E: Bug reportado

```bash
# 1. Lead hace triage
/microservices-agents:onboard  # (si no esta configurado aun)
/microservices-agents:sync-github pull  # traer el issue del bug

# 2. Lead identifica que repo esta afectado y asigna
/microservices-agents:assign-task
# → Asigna bug #78 al agente Backend en micro-backoffice
# → Crea branch fix/78-fix-paginacion

# 3. Backend arregla el bug
/microservices-agents:inbox  # lee el ticket
# implementa el fix...
/microservices-agents:git-check  # verifica antes de commit
/microservices-agents:sync-github push  # PR + issue "In Review"

# 4. Si toca seguridad
/microservices-agents:security-audit

# 5. Lead revisa y mergea
/microservices-agents:review-pr 92
/microservices-agents:sync-github push  # issue → Done
```

---

## Flujo F: Analisis de base de datos

```bash
# 1. Configurar acceso del DBA (si no se hizo en onboard)
/microservices-agents:db-health
# → Pregunta motor, credenciales, prueba conexion

# 2. Health check completo
/microservices-agents:db-health full
# → Esquema, indices, slow queries, tamaño de tablas

# 3. Si hay hallazgos, el DBA crea handoff al Lead
/microservices-agents:handoff
# → "Indice faltante en tabla X, query Y tarda 3s"

# 4. Lead asigna al Backend para implementar la migracion
/microservices-agents:assign-task
```

---

## Resumen rapido de commands

| Quiero... | Comando |
|-----------|---------|
| Crear proyecto nuevo | `/microservices-agents:new-project docs/req.docx` |
| Adoptar proyecto existente | `/microservices-agents:onboard backoffice` |
| Ver estado general | `/microservices-agents:status` |
| Traer tickets de GitHub | `/microservices-agents:sync-github pull` |
| Actualizar GitHub con mi trabajo | `/microservices-agents:sync-github push` |
| Asignar ticket a agente | `/microservices-agents:assign-task` |
| Ver mis tareas | `/microservices-agents:inbox` |
| Avisar a otro agente | `/microservices-agents:handoff` |
| Verificar git antes de commit | `/microservices-agents:git-check` |
| Revisar un PR | `/microservices-agents:review-pr 123` |
| Verificar si esta listo para deploy | `/microservices-agents:deploy-check` |
| Auditoria de seguridad | `/microservices-agents:security-audit` |
| Analizar base de datos | `/microservices-agents:db-health` |
