---
description: QA genera el plan de pruebas de una HU desde sus criterios de aceptacion - que se automatiza (E2E/API), que se prueba manual, casos borde y datos necesarios.
argument-hint: ID de la HU (ej. "HU-042" o "#42") o descripcion de que probar
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Test Plan: Plan de pruebas de una HU

HU o alcance: $ARGUMENTS

Invoca al agente `qa` para ejecutar este flujo:

1. **Leer la HU** en el tracker o `.coordination/backlog.md` — extraer los criterios
   de aceptacion. Si la HU no tiene criterios verificables, devolverla al PO
   (handoff) en vez de inventarlos.
2. **Clasificar cada criterio**: E2E con Playwright / API con request context /
   manual (justificar por que no es automatizable)
3. **Agregar casos borde** que los criterios no cubren: vacios, limites, permisos,
   concurrencia, estados de error
4. **Identificar datos de prueba** necesarios (coordinar seed con DBA si hace falta)
5. **Generar el plan** en `.coordination/test-plans/hu-{nnn}.md` con la tabla de
   trazabilidad criterio → test
6. **Mostrar resumen** al usuario y sugerir `/dev-team:e2e {HU}` para automatizar
