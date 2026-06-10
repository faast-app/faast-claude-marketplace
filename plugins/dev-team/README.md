# Dev Team

Equipo completo de desarrollo con 11 agentes IA. Cubre todo el ciclo de vida:
Historias de Usuario → arquitectura → desarrollo → QA automatizado con Playwright →
seguridad → deploy → documentacion.

- **Proyectos nuevos o existentes** (`/new-project`, `/onboard`)
- **Mono-repo o multi-repo** — el equipo se adapta a tu topologia
- **Backlog en GitHub Projects o Azure DevOps Boards** — HUs, PBIs y bugs reales
- **QA con Playwright** — validacion interactiva (MCP) + suite E2E en CI
- **Prerequisitos automaticos** — el agente setup instala lo que falte antes de empezar

## Instalacion

```bash
/plugin marketplace add faast-app/faast-claude-marketplace
/plugin install dev-team@faast-marketplace
```

## Uso

```bash
/dev-team:start
```

Eso es todo. El equipo detecta tu contexto y te guia. Para la guia completa de
comandos y flujos, ver **[GUIDE.md](GUIDE.md)**.

## El equipo

| Agente | Rol |
|--------|-----|
| **setup** | Valida e instala prerequisitos (git, gh/az, Docker, BD, Playwright) |
| **product-owner** | HUs de negocio con criterios de aceptacion, backlog en GitHub/Azure |
| **architect** | Arquitectura: topologia, servicios, stack, BD, gateway |
| **lead** | Coordina, asigna, exige gates de calidad, unico que mergea |
| **backend** | Servicios backend (.NET 8, Node.js, Python, Java) |
| **frontend** | SPA y microfrontends (React, Vue, Angular) |
| **dba** | Esquemas, indices, queries, migraciones |
| **qa** | Planes de prueba + E2E automatizado con Playwright |
| **infra** | Docker, CI/CD, gateways, deploy |
| **cybersec** | Auditoria de seguridad (nunca commitea) |
| **tech-writer** | README, OpenAPI, ADRs, diagramas, wiki |

## Principios

- Las HUs son de **negocio** (las escribe el PO); lo tecnico vive en las tareas
- **QA y Cybersec son gates de merge** — nada llega a main sin validacion
- Un agente = un branch = una tarea; **solo el Lead mergea**
- Los agentes usan el modelo Claude optimo para su funcion (opus/sonnet/haiku)
- Coordinacion via handoffs en `.coordination/` — sin estado oculto
