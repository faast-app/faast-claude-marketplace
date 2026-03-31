# Microservices Agents

Sistema de agentes IA para arquitectura de microservicios reales.

## Que incluye

### 7 Agentes
| Agente | Rol |
|--------|-----|
| **architect** | Analiza requerimientos y diseña la arquitectura (bounded contexts, servicios, stack, BD) |
| **lead** | Coordina agentes, gestiona backlog/sprint, unico que mergea a main |
| **backend** | Desarrolla microservicios (.NET, Node.js, Python, Java) |
| **frontend** | Desarrolla SPA y microfrontends (React, Vue, Angular, Module Federation) |
| **dba** | Gestiona N bases de datos independientes desde repo centralizado dba-scripts/ |
| **infra** | Dockerfiles, CI/CD, docker-compose, gateways (Traefik, YARP, Ocelot) |
| **cybersec** | Audita seguridad por servicio y comunicacion inter-servicio. No commitea codigo. |

### 10 Skills (slash commands)
| Comando | Descripcion |
|---------|-------------|
| `/microservices-agents:new-project` | Crea proyecto desde documento de requerimientos |
| `/microservices-agents:status` | Estado del proyecto (backlog, sprint, repos) |
| `/microservices-agents:inbox` | Lee handoffs pendientes |
| `/microservices-agents:handoff` | Crea handoff a otro agente |
| `/microservices-agents:assign-task` | Asigna tarea del backlog (Lead) |
| `/microservices-agents:git-check` | Verifica estado git antes de commit |
| `/microservices-agents:security-audit` | Auditoria de seguridad del repo |
| `/microservices-agents:db-health` | Health check de base de datos |
| `/microservices-agents:deploy-check` | Verifica readiness para deploy |
| `/microservices-agents:review-pr` | Revisa un Pull Request |

## Instalacion

```bash
# 1. Agregar el marketplace (si no lo tienes)
claude plugin marketplace add faast-app/faast-claude-marketplace

# 2. Instalar el plugin
claude plugin install microservices-agents@faast-marketplace
```

## Uso rapido

```bash
# Crear un proyecto nuevo desde requerimientos
/microservices-agents:new-project docs/requerimientos.docx

# Operaciones diarias
/microservices-agents:status
/microservices-agents:inbox
/microservices-agents:assign-task
```

## Estructura de proyecto generada

```
~/projects/{proyecto}/
├── .coordination/                    # Coordinacion (no es repo git)
│   ├── handoffs/
│   ├── backlog.md
│   ├── sprint-actual.md
│   └── architecture.md
├── docker-compose.dev.yml            # Dev local (todos los servicios)
├── {proyecto}-user-service/          # Repo git independiente
├── {proyecto}-order-service/         # Repo git independiente
├── {proyecto}-gateway/               # Repo git independiente
├── {proyecto}-frontend-shell/        # Repo git independiente
└── ...
```

## Principios de arquitectura

- **Database-per-service:** Cada servicio tiene su propia BD
- **Repos independientes:** Cada servicio es un repo git con su propio CI/CD
- **Un agente = un branch = una tarea**
- **Solo el Lead mergea a main**
- **Cybersec nunca commitea codigo** — reporta via handoffs
- **DBA tiene repo centralizado** (`dba-scripts/`) para todos los proyectos
