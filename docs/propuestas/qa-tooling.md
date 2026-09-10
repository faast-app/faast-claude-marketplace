# Propuesta: Equipo QA de precisión — Playwright MCP, agentes de prueba y evidencia visual

**Estado:** propuesta (pendiente de aprobación) · **Fecha:** 2026-09-10 · **Fase sugerida:** 6

## 0. Resumen ejecutivo

El equipo QA de dev-team (qa + qa-frontend + qa-backend) ya tiene las reglas correctas
(no debuggea, reporta a la primera falla, evidencia siempre, gate de conformidad). Lo que
le falta es **herramienta de precisión**: hoy el Playwright MCP existe en la máquina pero
está configurado de forma que **los proyectos no lo ven**, corre **sin las capacidades de
verificación** (`browser_verify_*`), sin trazas ni video, y la evidencia se arma a mano.

La propuesta convierte al QA en un equipo con margen de error objetivo del **0,1 %**
(1 veredicto equivocado por cada 1.000 criterios validados) mediante cinco capas:

| Capa | Herramienta recomendada | Alternativas evaluadas | Por qué la recomendada |
|---|---|---|---|
| Exploración y validación interactiva | **Playwright MCP** (`@playwright/mcp`) con `--caps=testing,devtools` | Chrome DevTools MCP, Browserbase/Stagehand, Selenium | Es la que ya usa el equipo; agrega verificación explícita, trace y video sin escribir código; es de Microsoft y gratis |
| Generación y mantenimiento de la suite E2E | **Playwright Test Agents** (planner / generator / healer) | Escribir specs a mano, Cypress, TestRigor/mabl | Vienen incluidos en Playwright ≥ 1.56, se generan para Claude Code con un comando y se reparan solos |
| Regresión visual (pixel) | **`toHaveScreenshot()`** nativo de Playwright (baselines en git) | Argos (5.000 capturas/mes gratis), Lost Pixel, Chromatic, Applitools | Cero costo y cero dependencia; Argos queda como opción si el volumen de pantallas crece |
| Accesibilidad | **`@axe-core/playwright`** (Deque, oficial) | axe-playwright (comunidad), Lighthouse | Estándar de la industria, se ejecuta dentro del mismo test y entrega violaciones WCAG con selector |
| Contratos de API | **Schemathesis** (property-based desde OpenAPI) + `request` de Playwright para escenarios | Pact, Dredd, Postman/Newman | Genera cientos de casos desde el `openapi.yml` sin escribirlos; Pact solo tiene sentido si los equipos consumidores lo adoptan |

Todo lo anterior es open source y se instala en minutos. Ninguna capa exige servicio pago.

## 1. Diagnóstico (lo que encontré hoy en esta máquina)

### 1.1 El Playwright MCP existe, pero en el alcance equivocado

```
$ claude mcp list            # ejecutado desde la carpeta del marketplace
claude.ai Microsoft 365 ✔ · claude.ai Sentry ✔ · Gamma (auth) · FaaST Pruebas (502)
                             # → NO aparece playwright

$ cd ~ && claude mcp list
playwright: npx @playwright/mcp@latest --browser=chromium --ignore-https-errors - ✔ Connected
```

El servidor está registrado en `~/.claude.json` bajo `projects["/Users/carlosfuentes"]`,
es decir, **alcance de proyecto con la carpeta home como proyecto**. Claude Code solo lo
carga cuando la sesión arranca exactamente en esa carpeta. Cualquier sesión abierta en un
repo real (Confirming 2.0, Portal Digital, este marketplace) no ve las tools `browser_*`,
y el agente qa-frontend termina pidiendo `/dev-team:setup` o improvisando con `curl`.

Además, ningún otro integrante del equipo lo tiene: no vive en el plugin.

### 1.2 Corre sin las capacidades que hacen QA de verdad

La configuración actual no pasa `--caps`. Por defecto el servidor expone solo el núcleo
(navegar, snapshot, click, type, screenshot, consola, red). Quedan **apagadas**:

| Capacidad | Tools que habilita | Para qué las necesita QA |
|---|---|---|
| `testing` | `browser_verify_element_visible`, `browser_verify_text_visible`, `browser_verify_list_visible`, `browser_verify_value`, `browser_generate_locator` | Afirmar un criterio con una verificación explícita (pasa/falla) en vez de "mirar" el snapshot; generar el locator estable para el test automatizado |
| `devtools` | `browser_start_tracing` / `browser_stop_tracing`, `browser_start_video` / `browser_stop_video`, `browser_video_chapter`, `browser_highlight`, `browser_annotate`, `browser_start_recording` | Trace y clip como evidencia sin escribir un script; resaltar y anotar el elemento en la captura |
| `vision` | `browser_mouse_click_xy`, `browser_mouse_drag_xy` … | Canvas, mapas, drag & drop que no tienen árbol de accesibilidad |

Tampoco se define `--output-dir` (las capturas caen en un temporal), `--isolated`
(el perfil persiste entre sesiones y contamina pruebas), `--secrets` (las credenciales de
QA se escriben en el chat), ni `--test-id-attribute`.

### 1.3 Los prompts prometen más de lo que la herramienta entrega

`qa.md` y `qa-frontend.md` piden "clip corto con `video: 'on'`" y "trace adjuntable", pero
para obtenerlos el agente debe escribir y correr un script Playwright aparte. `qa-backend.md`
pide contract testing contra `docs/openapi.yml` pero lo hace endpoint por endpoint con
`request.get`, sin generación de casos ni validación de esquema real. No hay regresión
visual ni accesibilidad automatizada: solo "roles y labels vía snapshot".

### 1.4 La evidencia es correcta pero artesanal

Las reglas de evidencia (screenshot por paso, embebido en GitHub/Azure) son las correctas y
se conservan íntegras. Lo que no existe es un **formato de informe QA único** que combine
criterio → verificación → captura → veredicto, ni la generación automática de ese informe
desde el reporte HTML/trace de Playwright.

## 2. Qué significa "margen de error 0,1 %" y cómo se logra

Definimos error QA como **veredicto equivocado**: aprobar algo roto (falso positivo) o
rechazar algo correcto (falso negativo). La meta: ≤ 1 veredicto equivocado por cada 1.000
criterios validados. No se logra "probando más", se logra eliminando las fuentes de error:

| Fuente de error | Mecanismo que la elimina |
|---|---|
| "Se ve bien" subjetivo | Cada criterio cierra con `browser_verify_*` (interactivo) o `expect()` (automatizado). Sin verificación explícita no hay veredicto |
| Selectores frágiles | Solo `getByRole` / `getByLabel` / `getByTestId`; `browser_generate_locator` propone el locator; `--test-id-attribute` acordado con frontend |
| Timing / flakiness | Auto-wait de Playwright, prohibido `waitForTimeout`; `retries: 2` solo en CI; `trace: 'on-first-retry'`; **doble corrida** (`--repeat-each=2`) antes de aprobar una HU |
| Test verde por casualidad | Un test que falla intermitente se **cuarentena** (`test.fixme` + issue) y cuenta como NO validado, nunca como aprobado |
| Datos contaminados | `--isolated` en el MCP; datos semilla idempotentes que entrega el DBA (misma regla global de scripts); cada test crea y limpia lo suyo |
| Ambiente incorrecto | La REGLA DE ORO se mantiene: sin informe de conformidad (o stack completo en desa) no se valida. El MCP se apunta solo a `urls.dev` de `config.json` |
| Contrato "según el dev" | Schemathesis genera los casos desde el `openapi.yml` real; toda desviación es hallazgo, no interpretación |
| Regresión visual no vista | `toHaveScreenshot()` por pantalla clave con baseline en git; diff automático con máscara de zonas dinámicas |
| Accesibilidad "a ojo" | `AxeBuilder` en cada pantalla nueva; cero violaciones `critical`/`serious` para aprobar |
| Evidencia que no prueba nada | Informe por criterio con captura antes / acción / después, elemento resaltado (`browser_highlight`) y resultado de la verificación |

## 3. Arquitectura propuesta del equipo QA

```
                       ┌──────────────── qa (QA Lead) ────────────────┐
                       │ plan por HU · reparte CA · consolida veredicto │
                       └──────┬───────────────────────────────┬────────┘
                              │                               │
              ┌───────────────▼──────────────┐   ┌────────────▼──────────────┐
              │ qa-frontend                   │   │ qa-backend                │
              │ Playwright MCP (verify,trace, │   │ Schemathesis (OpenAPI)    │
              │ video, highlight, axe)        │   │ Playwright request        │
              │ toHaveScreenshot baselines    │   │ casos borde, permisos     │
              └───────────────┬──────────────┘   └────────────┬──────────────┘
                              │                               │
                 ┌────────────▼───────────────────────────────▼───────────┐
                 │ Playwright Test Agents (planner → generator → healer)   │
                 │ specs/*.md → tests/*.spec.ts → suite de regresión en CI  │
                 └────────────────────────────┬───────────────────────────┘
                                              │
                        .coordination/evidence/{HU}/informe-qa.md
                        (capturas + trace + report HTML) → tracker (embebido)
```

### 3.1 Playwright MCP empaquetado en el plugin (cero configuración para el equipo)

Claude Code permite que un plugin traiga sus propios servidores MCP en `.mcp.json` en la
raíz del plugin. Así **todos** los que instalan dev-team reciben el servidor con los flags
correctos, en cualquier carpeta, sin `claude mcp add`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--browser=chromium",
        "--caps=testing,devtools,vision",
        "--isolated",
        "--output-dir=${CLAUDE_PROJECT_DIR}/.coordination/evidence/_mcp",
        "--test-id-attribute=data-testid",
        "--timeout-action=8000",
        "--timeout-navigation=45000",
        "--console-level=warning",
        "--ignore-https-errors"
      ]
    }
  }
}
```

Notas:
- `--output-dir` apunta a `.coordination/evidence/` del proyecto: la evidencia nace ya en la
  carpeta del proyecto (§3.7), nunca en un temporal.
- `--headless` **no** se fija: en local el QA (y el usuario) ven el browser; en CI se pasa
  por variable `PLAYWRIGHT_MCP_HEADLESS=1`.
- Credenciales de QA: archivo `.coordination/qa-secrets.env` (gitignored) pasado con
  `--secrets`; el agente usa el nombre de la variable, nunca el valor.
- El servidor actual en `~/.claude.json` se elimina para no duplicar tools
  (`claude mcp remove playwright`).

### 3.2 Playwright Test Agents integrados al equipo

Playwright ≥ 1.56 trae tres agentes (planner, generator, healer) que se generan para Claude
Code con:

```bash
npx playwright init-agents --loop=claude
```

Genera las definiciones en `.claude/agents/` del repo de tests, el servidor MCP
`playwright-test` en `.mcp.json` y la estructura `specs/` + `tests/seed.spec.ts`.
En dev-team:

| Agente Playwright | Quién lo invoca | Rol en el flujo |
|---|---|---|
| **planner** | qa (QA Lead) | Explora la app y produce `specs/hu-{nnn}.md`: el plan de pruebas humano que hoy el QA Lead redacta a mano en `.coordination/test-plans/` |
| **generator** | qa-frontend / qa-backend | Convierte el plan en `tests/hu-{nnn}.spec.ts` verificando cada locator en vivo. Mantiene la convención `[HU-042] … CA-1:` |
| **healer** | qa (solo en regresión) | Cuando la suite falla en CI, reproduce, propone el parche del test (locator, espera, dato). **Nunca toca código de aplicación**: si el fallo es de la app, es un bug para el dev |

Regla: el healer no puede "curar" un test cambiando la aserción esperada. Si la aserción
cambia, es porque cambió el criterio de aceptación, y eso lo decide el PO.

### 3.3 Template `e2e-faast/` (nuevo)

Un template listo para copiar en `/new-project` (mono: `e2e/`; multi: repo `{proyecto}-e2e`):

```
e2e/
├── playwright.config.ts      # retries: CI ? 2 : 0 · trace: 'on-first-retry' · video: 'retain-on-failure'
│                             # screenshot: 'only-on-failure' · expect.toHaveScreenshot maxDiffPixelRatio 0.01
│                             # reporter: [['html'], ['list'], ['json']] · testIdAttribute: 'data-testid'
├── fixtures/
│   ├── axe.ts                # fixture makeAxeBuilder (WCAG 2.1 AA, exclude zonas conocidas)
│   ├── auth.setup.ts         # login una vez → storageState (por rol)
│   └── data.ts               # helpers de datos semilla (llaman scripts del DBA, idempotentes)
├── pages/                    # Page Object Model
├── specs/                    # planes en Markdown (planner)
├── tests/
│   ├── seed.spec.ts
│   ├── hu-{nnn}-*.spec.ts    # 1 por HU, CA → test
│   ├── visual/*.spec.ts      # toHaveScreenshot por pantalla clave
│   ├── a11y/*.spec.ts        # AxeBuilder por pantalla nueva
│   └── regression/
├── api/
│   └── schemathesis.yml      # base-url, auth header, checks: all, hypothesis max-examples
└── .github/workflows/e2e.yml # PR: suite HU + regresión · nightly: visual + a11y + schemathesis
```

### 3.4 Contratos de API con Schemathesis

```bash
pip install schemathesis          # el setup lo instala (pipx)
schemathesis run docs/openapi.yml --url http://localhost:5001 \
  --checks all --max-examples 200 --report junit --report-dir .coordination/evidence/HU-042/api
```

Genera automáticamente peticiones válidas e inválidas para cada operación del contrato,
detecta 500, respuestas fuera de esquema, headers faltantes y violaciones de
`required`/`enum`/`format`. qa-backend conserva Playwright `request` para los escenarios
de negocio (permisos, integración A→B, acentos) y usa Schemathesis para el barrido masivo.

### 3.5 Evidencia visual: el informe QA por criterio

Todo criterio de frontend cierra con este bloque, generado por qa-frontend y consolidado por
qa en `.coordination/evidence/{HU}/informe-qa.md` (y embebido en el tracker):

```markdown
### CA-2 · Mostrar error con rango inválido — ✅ CUMPLE
| Paso | Acción | Captura |
|---|---|---|
| 1 | Estado inicial del filtro | ![](ca2-01-inicial.png) |
| 2 | Ingreso rango 31/02 → 01/01 y presiono Filtrar | ![](ca2-02-accion.png) |
| 3 | Mensaje "El rango de fechas no es válido" visible (resaltado) | ![](ca2-03-resultado.png) |

Verificación: `browser_verify_text_visible("El rango de fechas no es válido")` → OK
Trace: `ca2.trace.zip` · Clip: `ca2.webm` (12 s) · Consola: 0 errores · Red: 0 fallos
```

Reglas del informe:
- Capturas con el elemento **resaltado** (`browser_highlight` antes de `browser_take_screenshot`).
- Viewport declarado (1280×720 escritorio; 375×812 móvil cuando el criterio es responsive).
- Trace y clip **siempre** en bugs; en criterios aprobados basta la captura y la verificación.
- El reporte HTML de Playwright (`playwright-report/`) se adjunta comprimido al veredicto de la HU.
- La subida al tracker sigue la **regla dura de ubicación de la evidencia** (§3.7): rama `evidence` + `![](raw)` en GitHub, attachment + `<img>` embebido en Azure.

### 3.7 Dónde vive la evidencia (REGLA DURA, sin excepciones)

1. **Toda captura, clip, trace, reporte HTML y junit queda en la carpeta del proyecto**:
   `.coordination/evidence/{HU-ID|BUG-ID}/`. El MCP escribe ahí (`--output-dir`), la suite
   Playwright también (`outputDir` y `reporter html` apuntan a esa carpeta). Nada de
   evidencia se guarda en temporales del sistema ni en carpetas del código fuente.
2. **`.coordination/evidence/` está en el `.gitignore` de todas las ramas de trabajo.**
   Un PR de feature/fix/release que incluya una imagen o clip de evidencia se RECHAZA en
   `/review-pr` (el lead lo verifica). Las imágenes de evidencia nunca viajan dentro del
   código, ni en `develop`, ni en `main`, ni en ninguna rama de trabajo.
3. **Cuando la evidencia debe verse en el tracker** (GitHub Issue/Project, Azure WI, o el
   destino que se decida), el equipo QA tiene la capacidad y la obligación de subirla
   embebida:
   - **Azure DevOps**: attachment vía API + `<img>` en el HTML del WI (como hoy). No se
     toca ningún repo.
   - **GitHub**: la imagen se publica **únicamente en la rama `evidence` del repo**,
     creada una sola vez como rama huérfana (`git checkout --orphan evidence`, sin
     historia de código), permanente, jamás mergeada ni borrada, y trabajada desde un
     worktree aparte (`git worktree add ../{repo}-evidence evidence`) para que nunca se
     mezcle con la rama de trabajo del QA. Estructura: `evidence/issues/<n>-<slug>/`,
     `evidence/smokes/<fecha>-<nombre>/`, prefijos `00-`, `01-`, `INDEX.md`.
     El embed es `![](https://github.com/{org}/{repo}/raw/evidence/...)` con el enlace
     `blob` de respaldo.
   - **Otro destino** (SharePoint, S3, wiki): se sube ahí y se embebe/enlaza; el repo de
     código no se toca.
4. **Prohibido** subir evidencia a cualquier otra rama, carpeta del repo, o repo distinto
   del propio (salvo el destino decidido en el punto 3). Sin excepción por urgencia.
5. Los **baselines de regresión visual** (`tests/**/*-snapshots/`) NO son evidencia: son
   activos de la suite y viven con el código de tests. La evidencia es lo que prueba un
   veredicto puntual; el baseline es la referencia que la suite compara.
6. El informe `informe-qa.md` de la HU cita cada archivo por su ruta local y, cuando
   aplique, por su URL en el tracker. Así el veredicto es auditable desde el proyecto
   aunque el tracker cambie.

### 3.6 Puertas de aprobación (lo que qa exige antes de APROBADA)

1. 100 % de los criterios con verificación explícita y captura.
2. Suite de la HU verde en **dos corridas** consecutivas (`--repeat-each=2`), 0 tests en cuarentena para esa HU.
3. Regresión existente verde.
4. Visual: 0 diffs no aprobados por el ui-designer o el PO.
5. Accesibilidad: 0 violaciones `critical`/`serious`.
6. API: Schemathesis sin fallos en las operaciones tocadas por la HU.
7. Consola sin errores JS y red sin 4xx/5xx inesperados durante el flujo.

Si cualquiera falla → RECHAZADA con el informe. Sin excepciones ni "aprobada con observaciones".

## 4. Cambios concretos en el plugin (Fase 6)

| # | Cambio | Archivos |
|---|---|---|
| 6.1 | `.mcp.json` del plugin con Playwright MCP configurado (§3.1); setup detecta el servidor duplicado en `~/.claude.json` y propone quitarlo; instala `pipx`+Schemathesis y `@axe-core/playwright` | `plugins/dev-team/.mcp.json`, `agents/setup.md` §5 |
| 6.2 | qa-frontend: verificación explícita obligatoria (`browser_verify_*`), highlight + screenshot, trace/video por tool (sin scripts ad hoc), viewport declarado, axe por pantalla nueva, informe por criterio §3.5, regla de ubicación §3.7 (worktree de la rama `evidence`) | `agents/qa-frontend.md` |
| 6.3 | qa-backend: Schemathesis como barrido de contrato + Playwright `request` para escenarios; evidencia = junit + responses | `agents/qa-backend.md` |
| 6.4b | lead / `/review-pr`: rechazar PRs que incluyan archivos de `.coordination/evidence/` o imágenes de evidencia fuera de la rama `evidence`; `.gitignore` de templates incluye `.coordination/evidence/` | `agents/lead.md`, `commands/review-pr.md`, `templates/*/.gitignore` |
| 6.4 | qa (Lead): puertas §3.6, doble corrida, política de cuarentena, uso del planner para el plan y del healer solo en regresión (con la regla de no cambiar aserciones) | `agents/qa.md` |
| 6.5 | Template `e2e-faast/` (§3.3) con config, fixtures axe/auth/datos, workflow CI y `schemathesis.yml`; `/new-project` lo copia cuando hay frontend o APIs; `/onboard` lo ofrece si no existe carpeta e2e | `templates/e2e-faast/`, `commands/new-project.md`, `commands/onboard.md` |
| 6.6 | `/e2e`: subcomandos `plan` (planner), `generate` (generator), `heal` (healer, solo regresión), `visual` (actualizar baselines con aprobación), `a11y`, `api` (schemathesis) | `commands/e2e.md` |
| 6.7 | GUIDE: caso "Validar una HU con evidencia" reescrito con el informe por criterio y las 7 puertas; FAQ "¿por qué QA rechazó si a mí me funciona?" | `GUIDE.md` |
| 6.8 | Métricas: `team-metrics` agrega tasa de veredictos revertidos (bugs reabiertos / HUs aprobadas) como indicador del 0,1 % | `commands/team-metrics.md`, `hooks/log-activity.py` (evento `verdict`) |

Orden sugerido: 6.1 → 6.2/6.3/6.4 → 6.5 → 6.6 → 6.7 → 6.8. Estimación: una versión
menor (v2.8.0) para 6.1–6.4 y otra (v2.9.0) para 6.5–6.8.

## 5. Alternativas descartadas y por qué

| Alternativa | Veredicto | Motivo |
|---|---|---|
| Chrome DevTools MCP (Google) | Complemento, no reemplazo | Excelente para performance/Core Web Vitals, pero sin `verify_*`, sin multi-browser ni generación de tests. Se puede sumar después para auditorías de rendimiento |
| Browserbase / Stagehand / agentes "IA pura" | No | Browser en la nube pago y selección de elementos por lenguaje natural: más flakiness, no menos. Contradice el 0,1 % |
| Cypress | No | Sin soporte multi-tab ni WebKit real, sin MCP oficial, sin agentes; migrar no aporta |
| Applitools / Percy / Chromatic | Aún no | Visual AI pago; `toHaveScreenshot` cubre el caso FaaST hoy. Argos (gratis hasta 5.000 capturas/mes) es el siguiente paso si los baselines en git se vuelven pesados |
| Pact (contract testing consumer-driven) | Aún no | Requiere que consumidores y proveedores publiquen contratos; en FaaST el contrato es el `openapi.yml` del proveedor, que Schemathesis explota directamente |
| Dredd | No | Proyecto sin mantenimiento activo |
| TestRigor / mabl / Testim (SaaS no-code) | No | Costo por usuario, lock-in, y el planner/generator de Playwright ya cubre el "escribir tests sin código" dentro de Claude Code |

## 6. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| `npx @playwright/mcp@latest` cambia tools entre versiones | Fijar versión en `.mcp.json` (`@playwright/mcp@0.0.80` hoy) y subirla con cada release del plugin; regenerar los Test Agents cuando se actualice Playwright |
| Baselines visuales distintos por SO/fuentes | Generar baselines solo en CI (Linux) con `--update-snapshots`; local solo compara, no actualiza |
| Healer "arregla" un test ocultando un bug real | Regla dura §3.2: el healer no cambia aserciones; todo parche pasa por qa y se lista en el informe |
| Schemathesis genera carga sobre desa | `--max-examples` acotado (200) y solo contra `urls.dev`; nunca contra ambientes de cliente |
| Evidencia filtrada a una rama de código | `.gitignore` + chequeo en `/review-pr` + worktree separado para la rama `evidence`; el QA nunca hace `git add` en su rama de trabajo |
| Credenciales en el chat | `--secrets` en el MCP; `storageState` por rol en la suite; archivo gitignored |

## 7. Fuentes

- Playwright MCP — capacidades y tools por `--caps`: https://playwright.dev/mcp/capabilities
- Playwright MCP — flags CLI y archivo de configuración: https://github.com/microsoft/playwright-mcp
- Playwright Test Agents (planner / generator / healer): https://playwright.dev/docs/test-agents
- Playwright — pruebas de accesibilidad con `@axe-core/playwright`: https://playwright.dev/docs/accessibility-testing
- Playwright — comparación visual `toHaveScreenshot`: https://playwright.dev/docs/test-snapshots
- Playwright — reintentos, trace y flakiness: https://playwright.dev/docs/test-retries
- Claude Code — plugins con servidores MCP (`.mcp.json`): https://code.claude.com/docs/en/plugins
- Schemathesis (property-based testing desde OpenAPI): https://schemathesis.readthedocs.io
- Argos (regresión visual, plan gratuito): https://argos-ci.com
- Checkly — integrar axe en tests Playwright: https://www.checklyhq.com/blog/integrating-accessibility-checks-in-playwright-tes/

Versiones verificadas en esta máquina: `@playwright/mcp` 0.0.80 · `playwright` 1.63.0 · Claude Code con soporte de `.mcp.json` en plugins.
