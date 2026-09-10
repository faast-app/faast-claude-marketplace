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
3. **Validacion interactiva** con el Playwright MCP del plugin (`browser_navigate`,
   `browser_snapshot`, `browser_click`, `browser_fill_form`...): recorrer cada criterio
   y CERRARLO con `browser_verify_*` + captura resaltada (`browser_highlight` →
   `browser_take_screenshot`); trace/clip con `browser_start_tracing` /
   `browser_start_video` en bugs. Todo queda en `.coordination/evidence/{HU}/` con su
   bloque en `informe-qa.md`
4. **Automatizar**: escribir `tests/hu-{nnn}-{slug}.spec.ts` con un test por criterio
   (convencion CA-N), Page Objects si aplica, selectores getByRole/getByTestId — o
   generarlo con el Test Agent `generator` desde `specs/hu-{nnn}.md` (planner)
5. Ejecutar la suite nueva DOS veces: `npx playwright test tests/hu-{nnn}* --repeat-each=2`
   — todo verde en ambas; lo intermitente va a cuarentena y NO aprueba
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
- NUNCA aprobar una HU con criterios sin ejecutar ni sin verificacion explicita
- Las 7 puertas de aprobacion del QA Lead son obligatorias (ver `qa.md`)
- Los bugs encontrados se crean en el tracker con pasos exactos y evidencia EMBEBIDA
- La evidencia vive en `.coordination/evidence/` del proyecto; a GitHub SOLO por la rama
  `evidence`; JAMAS en una rama de codigo ni en el commit `test/{HU-ID}`
- Si faltan las tools `browser_*` (el MCP viene en el plugin), Playwright, axe o
  Schemathesis: sugerir `/dev-team:setup playwright`
