---
description: El Tech Writer actualiza la documentacion tecnica - README, OpenAPI, ADRs, diagramas, changelog, onboarding. Puede publicar en GitHub docs/wiki o Azure DevOps Wiki.
argument-hint: Que documentar (ej. "la feature de filtros que se mergeo", "ADR de la eleccion de RabbitMQ", "onboarding para devs nuevos")
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Document: Actualizar documentacion tecnica

Pedido: $ARGUMENTS

Invoca al agente `tech-writer` para ejecutar este flujo:

1. **Identificar que cambio**: leer el pedido, los handoffs recientes y los ultimos
   merges (`git log`) para entender que hay que documentar
2. **Determinar los documentos afectados**:
   - Feature nueva → README del repo/carpeta + CHANGELOG
   - Contrato de API → validar que `docs/openapi.yml` este completo y claro
   - Decision arquitectonica → `docs/adr/NNN-titulo.md` (formato ADR del agente)
   - Servicio nuevo → diagrama Mermaid en architecture.md + repos.md
   - Onboarding → `.coordination/onboarding.md` o `docs/setup.md`
3. **Escribir/actualizar** siguiendo el estilo del agente: lo importante primero,
   comandos copy-paste verificados, sin duplicar (linkear)
4. **Publicar** si el proyecto lo usa: wiki de GitHub o `az devops wiki page create/update`
5. **Commitear** en branch `docs/{tema}` con commits `docs: ...`
6. Handoff al Lead confirmando que se documento

Recordatorio: las HUs y el backlog son del Product Owner, NO de este comando.
Si el pedido es de negocio → derivar a `/dev-team:refine`.
