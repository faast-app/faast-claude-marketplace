---
description: QA valida HUs y mantiene la suite E2E con Playwright. Subcomandos - HU-nnn (validar con evidencia por criterio + automatizar), run (regresion, doble corrida), plan/generate/heal (Playwright Test Agents), visual, a11y, api (Schemathesis), explorar {url}.
argument-hint: 'HU-042 | run | plan HU-042 | generate HU-042 | heal | visual [update] | a11y | api HU-042 [regex] | explorar {url}'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# E2E: validacion y suite automatizada con Playwright

Pedido: $ARGUMENTS

Invoca al agente `qa` (QA Lead). Antes de cualquier subcomando que valide: **REGLA DE
ORO** — sin informe de conformidad (o stack COMPLETO en desa) no se valida; `blocked`.
Si no existe suite (`e2e/` o repo `{proyecto}-e2e` con `playwright.config.ts`): crearla
desde `templates/e2e-faast/` del plugin (reemplazar `{{ProjectName}}`, `npm install`,
`npx playwright install chromium`, copiar `.env.example` → `.env` con los NOMBRES de
variables; los valores los pone el usuario) y registrarla en `config.json` (`e2e.path`).

## Validar una HU (ej. "HU-042")
1. Leer el plan de pruebas (`.coordination/test-plans/hu-{nnn}.md`) — si no existe,
   generarlo primero (flujo de /dev-team:test-plan o subcomando `plan`)
2. Verificar que el ambiente esta arriba (docker compose ps / URL de config responde);
   si no, `blocked` y pedir a infra — no levantarlo "a mano" desde QA
3. **Validacion interactiva** con el Playwright MCP del plugin (`browser_navigate`,
   `browser_snapshot`, `browser_click`, `browser_fill_form`...): recorrer cada criterio
   y CERRARLO con `browser_verify_*` + captura resaltada (`browser_highlight` →
   `browser_take_screenshot`); trace/clip con `browser_start_tracing` /
   `browser_start_video` en bugs. Todo queda en `.coordination/evidence/{HU}/` con su
   bloque en `informe-qa.md`. El reparto UI/API entre qa-frontend y qa-backend lo hace
   el QA Lead por handoff; el paralelismo lo orquesta el Lead
4. **Automatizar**: `tests/hu-{nnn}-{slug}.spec.ts` con un test por criterio (convencion
   `CA-N`), Page Objects si aplica, selectores getByRole/getByLabel/getByTestId — o
   generarlo con el Test Agent `generator` desde `specs/hu-{nnn}.md` (ver `generate`)
5. **Doble corrida**: `npx playwright test --grep "HU-{nnn}" --repeat-each=2` — todo verde
   en ambas; lo intermitente va a cuarentena (`test.fixme` + issue) y NO aprueba
6. Si la HU toca endpoints: subcomando `api HU-{nnn} '{regex de rutas}'` (puerta 6)
7. Si la HU toca pantallas: `a11y` sobre las pantallas tocadas (puerta 5) y `visual`
   si hay pantalla clave nueva (puerta 4, baseline solo con OK de ui-designer/PO)
8. Commitear SOLO los tests en branch `test/{HU-ID}` (la evidencia JAMAS: vive en
   `.coordination/evidence/`, gitignored; a GitHub solo por la rama `evidence`)
9. Handoff a Lead con veredicto y las 7 puertas: APROBADA / RECHAZADA (+ bugs creados
   en el tracker con evidencia embebida). Registrar evento `verdict` en
   `.coordination/metrics/activity.jsonl` (`task` = HU, `detail` = APROBADA|RECHAZADA)

## Correr la regresion ("run")
```bash
npx playwright test --repeat-each=2          # doble corrida (puerta 2 y 3)
npx playwright show-report ../.coordination/evidence/_suite/playwright-report
```
Reportar: total/pass/fail/flaky. Cada fallo se clasifica en el reporte: **bug de la
app** (→ PO crea el bug, con evidencia) o **test fragil** (→ cuarentena + subcomando
`heal`). QA no diagnostica la causa del bug.

## Playwright Test Agents
Requieren `npx playwright init-agents --loop=claude` en la suite (una vez; regenerar
al actualizar Playwright). Crea `.claude/agents/` (planner/generator/healer), el MCP
`playwright-test` y `specs/`.
- **`plan HU-042`** → el QA Lead usa el `🎭 planner` para explorar la app y producir
  `specs/hu-042.md`; lo revisa y lo referencia desde `.coordination/test-plans/hu-042.md`
- **`generate HU-042`** → qa-frontend/qa-backend usan el `🎭 generator` para convertir el
  plan en `tests/hu-042-{slug}.spec.ts`, verificando cada locator en vivo. Mantener la
  convencion `[HU-042]` / `CA-N:`. Correr doble corrida antes de entregar
- **`heal`** → SOLO en regresion y SOLO el QA Lead: el `🎭 healer` reproduce los tests
  fallidos y propone el parche del TEST (locator, espera, dato). **Regla dura:** jamas
  cambia una asercion esperada ni codigo de aplicacion; si la asercion debe cambiar,
  cambio el criterio → lo decide el PO. Cada parche se lista en el reporte

## Visual ("visual" | "visual update")
```bash
npx playwright test tests/visual                       # compara contra baselines (puerta 4)
npx playwright test tests/visual --update-snapshots    # SOLO en CI/Linux y con OK de ui-designer/PO
```
Un diff es hallazgo: se adjunta la imagen `-diff.png` como evidencia y lo aprueba (o
rechaza) el ui-designer/PO. Los baselines (`*-snapshots/`) SI se versionan; la
evidencia del diff NO.

## Accesibilidad ("a11y")
```bash
npx playwright test tests/a11y
```
Fixture unico `fixtures/axe.ts` (WCAG 2.1 AA). Puerta 5: 0 violaciones
`critical`/`serious`. El JSON de violaciones se adjunta como evidencia; cada violacion
grave se reporta como bug (regla, selector, pantalla), sin diagnosticar.

## Contrato de API ("api HU-042 ['^/api/cobranzas']")
```bash
bash api/contract.sh HU-042 '^/api/cobranzas'   # Schemathesis desde docs/openapi.yml
```
Solo contra `urls.dev`/qa, acotado a las operaciones de la HU (`--max-examples 200`);
regresion completa en nightly. junit + consola → `.coordination/evidence/HU-042/api/`.
Si `schemathesis` falta: `blocked` + `/dev-team:setup playwright`.

## Exploratoria ("explorar {url}")
Navegar la app con el Playwright MCP, revisar consola y network
(`browser_console_messages`, `browser_network_requests`), reportar hallazgos con
evidencia (captura resaltada + `browser_verify_*` de lo que se afirma). No requiere HU.

## Reglas
- NUNCA aprobar una HU con criterios sin ejecutar ni sin verificacion explicita
- Las 7 puertas de aprobacion del QA Lead son obligatorias (ver `qa.md`); no existe
  "aprobada con observaciones"
- Los bugs encontrados se crean en el tracker con pasos exactos y evidencia EMBEBIDA
- La evidencia vive en `.coordination/evidence/` del proyecto; a GitHub SOLO por la rama
  `evidence`; JAMAS en una rama de codigo ni en el commit `test/{HU-ID}`
- Si faltan las tools `browser_*` (el MCP viene en el plugin), Playwright, axe,
  Test Agents o Schemathesis: `/dev-team:setup playwright`
