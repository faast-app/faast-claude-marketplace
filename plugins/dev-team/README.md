# Dev Team

Equipo completo de desarrollo con 23 agentes IA. Cubre todo el ciclo de vida:
Historias de Usuario → diseño UI/UX → arquitectura → desarrollo → QA en equipo con
Playwright y evidencia → ciberseguridad ofensiva (pentest autorizado) → pases a
ambientes → deploy → documentacion.

- **Proyectos nuevos o existentes** (`/new-project`, `/onboard`)
- **Mono-repo o multi-repo** — el equipo se adapta a tu topologia
- **Backlog en GitHub Projects o Azure DevOps Boards** — HUs, PBIs y bugs reales
- **QA de precision con Playwright** — MCP incluido en el plugin (verificacion explicita, trace, video), Test Agents, regresion visual, axe y Schemathesis; evidencia por criterio; suite lista desde `templates/e2e-faast/`
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
| **ui-designer** | Design Lead: brief, direcciones de pantallas, propuesta funcional (deck HTML+PDF) |
| **ux-researcher** | Personas, flujos, arquitectura de informacion, wireframes, heuristicas, WCAG 2.2 |
| **visual-designer** | Identidad y brand kit, iconografia SVG, ilustracion, referencias, tipografia |
| **motion-designer** | Motion tokens, micro-interacciones, prototipos animados, video (HyperFrames) |
| **artist-3d** | Escenas 3D web (Three.js/R3F), glTF optimizado, fallback 2D |
| **design-engineer** | Prototipo pixel-perfect, tokens DTCG, DESIGN.md, sync Pencil/Figma/Penpot |
| **dba** | Esquemas, indices, queries, migraciones, scripts de pase, comparacion de BDs |
| **qa** | QA Lead: plan de pruebas, consolida veredicto, suite de regresion |
| **qa-frontend** | Especialista QA de UI (Playwright MCP, evidencia visual) |
| **qa-backend** | Especialista QA de APIs (contract testing, evidencia) |
| **release-manager** | Solicitudes de pase (doc Word+PDF), audita scripts del DBA, Scripts.zip |
| **infra** | Docker, CI/CD, gateways, deploy |
| **cybersec** | Cybersec Lead: define RoE/alcance, reparte, consolida hallazgos (CVSS), informe PDF; gate de merge (nunca commitea) |
| **pentester** | Ethical hacking autorizado (DAST): IDOR/BOLA, auth bypass, inyeccion, SSRF, logica de negocio, con PoC |
| **appsec** | Seguridad de codigo estatica: SAST, dependencias (SCA), secretos, auth/cripto |
| **cloudsec** | Seguridad de infra: Docker, red, TLS/headers, CORS, CI/CD, GHCR |
| **tech-writer** | README, OpenAPI, ADRs, diagramas, wiki |

## Principios

- Las HUs son de **negocio** (las escribe el PO); lo tecnico vive en las tareas
- **QA y Cybersec son gates de merge** — nada llega a main sin validacion
- **QA no debuggea**: reproduce, documenta y reporta con evidencia (screenshots/clips)
- **Ciberseguridad ofensiva con autorizacion**: pentest autorizado (RoE + alcance firmado,
  solo activos propios, no destructivo) con equipo Lead + pentester/appsec/cloudsec;
  hallazgos con PoC y CVSS, informe PDF con evidencia (`/dev-team:pentest`, `/dev-team:security-report`)
- **Estandar de despliegue FAAST**: dockerizacion con reglas duras (un puerto interno, non-root,
  cero secretos en imagen, `version.txt`), prueba en local (BD local Docker o remota), y operacion
  segura de servidores — descubrir en solo lectura, cambiar solo con plan y confirmacion, sin
  romper nada (`/dev-team:deploy`, skill `deployment-standard`)
- **Flujos de negocio registrables y re-ejecutables**: cada flujo es una carpeta ordenada
  (`.coordination/flows/{dominio}/{flujo}/`) con pasos numerados, verificaciones y evidencia;
  se crea, se graba recorriendolo, y se re-ejecuta con puntos de parada, cambios de BD guardados
  y rollback (`/dev-team:flow`, skill `flow-recording`)
- **Documentos de negocio del PO en PDF/DOCX**: el Product Owner genera documentos presentables
  (documento de una HU, especificacion funcional, informe de sprint, acta de aceptacion) en
  lenguaje de negocio desde plantillas, complementando los tickets (`/dev-team:doc`, skill `business-docs`)
- **Evidencia visual de alta fidelidad**: captura, analisis y entrega mejores — traza navegable,
  video con acciones y capitulos, capturas resaltadas, snapshot de accesibilidad, consola/red
  correlacionadas, y par antes/despues al revalidar un fix (skill `visual-evidence`, en QA, `/bug`,
  `/e2e`, `/hotfix`, flujos y pentest)
- **Operacion del equipo**: `/dev-team:standup` (el dia de un vistazo), `/dev-team:retro`
  (retrospectiva con datos y acciones) y `/dev-team:hotfix` (urgencia con los gates intactos)
- **Pases con gate**: el release-manager audita los scripts del DBA y puede rechazarlos
- **Wiki viva (patron LLM Wiki de Karpathy)**: `.coordination/wiki/` — el tech-writer
  destila handoffs a paginas enlazadas `[[wikilinks]]`; los agentes leen la wiki
  primero (menos tokens); abrela como vault de Obsidian para el graph view
- **/dev-team:team-office**: oficina virtual 2D en vivo (estilo Gather Town) — cada
  agente en su escritorio, estado, tarea actual y handoffs volando entre salas
- **/dev-team:team-metrics**: productividad y consumo de tokens por agente
- Un agente = un branch = una tarea; **solo el Lead mergea**
- Los agentes usan el modelo Claude optimo para su funcion (opus/sonnet/haiku)
- Coordinacion via handoffs en `.coordination/` — sin estado oculto
