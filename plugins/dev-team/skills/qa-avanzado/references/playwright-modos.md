# Tres modos de trabajo con Playwright

Material de consulta del equipo QA: se LEE antes de usar el Playwright MCP, de automatizar un
caso en la suite o de usar los Test Agents.

### Modo 1: Exploratorio con Playwright MCP (browser interactivo)
El MCP viene INCLUIDO en el plugin (`.mcp.json`, con `--caps=testing,devtools,vision`,
`--isolated`, salida en `~/.faast-mcp/dev-team/`). Usas las tools `browser_*`
directamente — sin escribir codigo:
- `browser_verify_element_visible` / `browser_verify_text_visible` /
  `browser_verify_list_visible` / `browser_verify_value` → **cierran cada criterio**;
  sin verificacion explicita no hay veredicto
- `browser_highlight` + `browser_take_screenshot` → captura que PRUEBA el criterio
- `browser_start_video` (con `size` = viewport, en navegador limpio) y DESPUES
  `browser_start_tracing` → clip y trace como evidencia, sin scripts ad hoc; la traza nunca va
  antes que el video (el video saldria chico y borroso). Verificacion con `normalizar_video.py`
  de la skill `visual-evidence`
- `browser_generate_locator` → locator estable para el test automatizado
- `browser_navigate` → abrir la app en el ambiente de desarrollo
- `browser_snapshot` → leer el estado de la pagina (accesibilidad tree)
- `browser_click`, `browser_type`, `browser_fill_form`, `browser_select_option` → interactuar
- `browser_take_screenshot` → evidencia visual para el reporte
- `browser_console_messages`, `browser_network_requests` → registrar errores JS/HTTP como
  evidencia (se reportan, no se diagnostican)

**Cuando usarlo:** validar una HU recien implementada, reproducir un bug reportado,
smoke test rapido antes de escribir la suite automatizada.

### Modo 2: Suite E2E automatizada (Playwright en codigo)
Escribes tests TypeScript que corren en CI sin supervision:

```
{repo-de-tests}/e2e/            # mono: e2e/ en la raiz; multi: repo {proyecto}-e2e
├── tests/
│   ├── hu-042-filtro-fechas.spec.ts    # 1 archivo por HU
│   └── regression/                      # suite de regresion acumulada
├── pages/                               # Page Object Model
│   ├── LoginPage.ts
│   └── CobranzasPage.ts
├── fixtures/                            # datos de prueba y auth state
├── playwright.config.ts                 # proyectos: chromium (+ firefox/webkit si se pide)
└── .github/workflows/e2e.yml            # corre en cada PR
```

**Convencion obligatoria — trazabilidad HU → test:**
```typescript
// tests/hu-042-filtro-fechas.spec.ts
import { test, expect } from '@playwright/test';

test.describe('[HU-042] Filtro de fechas en cobranzas', () => {
  // Criterio 1: Dado un rango valido, cuando filtro, entonces veo solo registros del rango
  test('CA-1: filtra registros dentro del rango', async ({ page }) => { ... });

  // Criterio 2: Dado un rango invalido, cuando filtro, entonces veo mensaje de error
  test('CA-2: muestra error con rango invalido', async ({ page }) => { ... });
});
```
Cada criterio de aceptacion de la HU = al menos un test. Si un criterio no es
automatizable, documentar por que y cubrirlo con prueba manual en el plan. Si un criterio tiene
varios casos, `CA-1 › C02: ...` en el titulo (la matriz del plan cita exactamente ese titulo).

### Buenas practicas Playwright (obligatorias)
- Selectores: `getByRole`, `getByLabel`, `getByTestId` — NUNCA selectores CSS fragiles ni XPath
- Esperas: auto-waiting de Playwright + `expect(...).toBeVisible()` — NUNCA `waitForTimeout` fijo
- Auth: hacer login una vez en `globalSetup` y reusar `storageState` — no loguearse en cada test
  (un `storageState` por rol/tenant cuando la HU prueba permisos)
- Datos: cada test crea/limpia sus datos o usa fixtures — tests independientes entre si
- Flakiness: si un test falla intermitente, arreglarlo o marcarlo `test.fixme()` con issue — nunca ignorar
- Page Object Model para paginas que se usan en mas de un test
- **Doble corrida antes de aprobar**: la suite de la HU debe estar verde DOS veces
  seguidas (`npx playwright test tests/hu-{nnn}* --repeat-each=2`); un test que pasa
  una y falla otra es FLAKY → cuarentena (`test.fixme()` + issue) y el criterio queda
  NO validado, jamas aprobado "porque paso la segunda"
- `retries: 2` SOLO en CI, `trace: 'on-first-retry'`, `video: 'retain-on-failure'`;
  en local `retries: 0` para no tapar flakiness
- Baselines visuales (`toHaveScreenshot`) se generan/actualizan SOLO en CI (Linux) con
  `--update-snapshots` y con OK del ui-designer/PO; en local solo se comparan
- Accesibilidad: fixture unico `makeAxeBuilder` que importan todos los tests de pantalla;
  objetivo **WCAG 2.2 AA** (tags `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa`; si el
  fixture del repo de tests aun no incluye `wcag22aa`, se agrega en tu rama `test/`);
  0 violaciones `critical`/`serious`
- `locale`/`timezoneId` del proyecto en la config (es-CL / America/Santiago por defecto); un
  proyecto de Playwright por pais cuando la HU depende de formato o calendario local

### Modo 3: Playwright Test Agents (planner → generator → healer)
Playwright (≥ 1.56) trae tres agentes que se generan para Claude Code en el repo de
tests con `npx playwright init-agents --loop=claude` (crea sus definiciones en
`.claude/agents/`, el MCP `playwright-test` en `.mcp.json`, `specs/` y `tests/seed.spec.ts`;
se REGENERAN al actualizar Playwright). Como se usan en este equipo:

| Agente Playwright | Quien lo usa | Para que |
|---|---|---|
| **planner** | tu (QA Lead) | Explora la app y produce `specs/hu-{nnn}.md` — la base de tu plan en `.coordination/test-plans/` |
| **generator** | qa-frontend / qa-backend | Convierte el plan en `tests/hu-{nnn}-{slug}.spec.ts` verificando cada locator en vivo; mantiene la convencion `[HU-042] … CA-N:` |
| **healer** | tu, SOLO en regresion | Cuando la suite falla en CI, reproduce y propone el parche del TEST (locator, espera, dato) |

**Regla dura del healer:** jamas "cura" un test cambiando la asercion esperada ni
tocando codigo de aplicacion. Si la asercion tiene que cambiar, cambio el criterio de
aceptacion — y eso lo decide el PO. Si el fallo es de la app, es un BUG para el dev.
Todo parche del healer se lista en el reporte de la corrida.

