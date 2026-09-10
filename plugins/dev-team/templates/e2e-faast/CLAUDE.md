# {{ProjectName}}-e2e — suite de QA (dev-team e2e-faast)

Suite E2E del equipo QA: Playwright Test + Playwright MCP (del plugin dev-team) +
`@axe-core/playwright` + Schemathesis. La usan `qa`, `qa-frontend` y `qa-backend`.

## Comandos
- `npm test` — suite completa · `npm run test:hu -- "HU-042"` — una HU
- `npm run test:double` — doble corrida (puerta 2) · `npm run test:regression`
- `npm run test:visual` / `test:visual:update` (SOLO en CI, con OK de ui-designer/PO)
- `npm run test:a11y` · `npm run test:api -- HU-042 '^/api/cobranzas'`
- `npm run report` · `npm run agents:init` (Test Agents planner/generator/healer)

## Reglas que este repo hace cumplir
- **Evidencia**: SIEMPRE en `../.coordination/evidence/` (config `EVIDENCE_DIR`). En CI es
  artifact del run. JAMAS se commitea evidencia aqui ni en ninguna rama de codigo; a
  GitHub va solo por la rama `evidence` del repo; a Azure como attachment embebido.
- **Baselines** `*-snapshots/` SI se versionan (son activos de la suite, no evidencia).
- Trazabilidad: `tests/hu-{nnn}-{slug}.spec.ts`, `describe('[HU-nnn] …')`, `test('CA-N: …')`.
- Selectores: `getByRole` / `getByLabel` / `getByTestId` (`data-testid`). Sin `waitForTimeout`.
- Auth una vez (`fixtures/auth.setup.ts` → `.auth/user.json`). Datos: `fixtures/data.ts`.
- Test intermitente → `test.fixme()` + issue (cuarentena). Nunca se aprueba "porque paso la 2da".
- El healer NO cambia aserciones ni codigo de aplicacion.
- Credenciales solo en `.env` (gitignored); en el chat, solo nombres de variables.
