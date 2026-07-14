---
description: QA automatiza y/o ejecuta pruebas E2E con Playwright. Puede validar una HU interactivamente (Playwright MCP), escribir la suite automatizada, o correr la regresion completa.
argument-hint: Que hacer - "HU-042" (validar y automatizar esa HU), "run" (correr la suite), "explorar {url}" (prueba exploratoria)
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# E2E: Pruebas automatizadas con Playwright

Pedido: $ARGUMENTS

Invoca al agente `qa`. Segun el pedido:

## Validar una HU (ej. "HU-042")
1. Leer el plan de pruebas (`.coordination/test-plans/hu-{nnn}.md`) — si no existe,
   generarlo primero (flujo de /dev-team:test-plan)
2. Verificar que el ambiente esta arriba (docker compose ps / URL de config responde);
   si no, levantarlo o pedir a infra
3. **Validacion interactiva** con Playwright MCP (`browser_navigate`, `browser_snapshot`,
   `browser_click`, `browser_fill_form`...): recorrer cada criterio de aceptacion y
   capturar evidencia (`browser_take_screenshot`)
4. **Automatizar**: escribir `tests/hu-{nnn}-{slug}.spec.ts` con un test por criterio
   (convencion CA-N), Page Objects si aplica, selectores getByRole/getByTestId
5. Ejecutar la suite nueva: `npx playwright test tests/hu-{nnn}*` — todo verde
6. Commitear en branch `test/{HU-ID}` y agregar a la regresion
7. Handoff a Lead con veredicto: APROBADA / RECHAZADA (+ bugs creados en el tracker)

## Correr la regresion ("run")
```bash
npx playwright test                  # suite completa
npx playwright show-report           # si hay fallos
```
Reportar: total/pass/fail/flaky + analisis de cada fallo (¿bug real o test fragil?).

## Exploratoria ("explorar {url}")
Navegar la app con Playwright MCP, revisar consola y network
(`browser_console_messages`, `browser_network_requests`), reportar hallazgos
con evidencia. No requiere HU previa.

## Reglas
- NUNCA aprobar una HU con criterios sin ejecutar
- Los bugs encontrados se crean en el tracker con pasos exactos y evidencia
- Si Playwright no esta disponible: sugerir `/dev-team:setup playwright`
