import { defineConfig, devices } from '@playwright/test';
import 'dotenv/config';

// Evidencia: SIEMPRE en .coordination/evidence/ del proyecto (regla dura dev-team).
// mono: e2e/ en la raiz del repo -> ../.coordination ; multi: repo {proyecto}-e2e -> ../.coordination
const EVIDENCE_DIR = process.env.EVIDENCE_DIR ?? '../.coordination/evidence/_suite';
const IS_CI = !!process.env.CI;
// Otros navegadores: solo con CROSS_BROWSER=1 y solo para los flujos criticos (*.cross.spec.ts).
const CROSS = process.env.CROSS_BROWSER === '1';

export default defineConfig({
  testDir: './tests',
  outputDir: `${EVIDENCE_DIR}/test-results`,
  snapshotPathTemplate: '{testDir}/{testFileDir}/{testFileName}-snapshots/{arg}{-projectName}{ext}',
  fullyParallel: true,
  forbidOnly: IS_CI,
  // retries SOLO en CI (en local 0 para no tapar flakiness). Doble corrida: `--repeat-each=2`.
  retries: IS_CI ? 2 : 0,
  workers: IS_CI ? 2 : undefined,
  timeout: 45_000,
  expect: {
    timeout: 8_000,
    // Regresion visual: baselines en git, generados/actualizados SOLO en CI (Linux)
    toHaveScreenshot: { maxDiffPixelRatio: 0.01, animations: 'disabled', caret: 'hide' },
  },
  // En CI con shards cada maquina emite un reporte 'blob' y el job final los une (merge-reports).
  reporter: process.env.PW_SHARD ? [['blob'], ['list']] : [
    ['list'],
    ['html', { outputFolder: `${EVIDENCE_DIR}/playwright-report`, open: 'never' }],
    ['json', { outputFile: `${EVIDENCE_DIR}/results.json` }],
    ['junit', { outputFile: `${EVIDENCE_DIR}/results.xml` }],
  ],
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    testIdAttribute: 'data-testid',
    trace: 'on-first-retry',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
    locale: 'es-CL',
    timezoneId: 'America/Santiago',
    viewport: { width: 1280, height: 720 },
  },
  projects: [
    // 1) Login UNA vez y guarda storageState (fixtures/auth.setup.ts)
    { name: 'setup', testMatch: /auth\.setup\.ts/, testDir: './fixtures' },
    // 2) Escritorio (obligatorio)
    {
      name: 'chromium',
      dependencies: ['setup'],
      // Rendimiento solo cuando se pide (npm run test:perf): medir en cada PR daria falsos rojos.
      grepInvert: process.env.PERF === '1' ? undefined : /@perf/,
      use: { ...devices['Desktop Chrome'], storageState: '.auth/user.json' },
    },
    // 3) Movil (criterios responsive)
    {
      name: 'mobile',
      dependencies: ['setup'],
      testMatch: /.*\.(mobile|visual)\.spec\.ts/,
      use: { ...devices['iPhone 13'], storageState: '.auth/user.json' },
    },
    // 4) Otros navegadores (puerta condicional, flujos R1): WebKit = Safari, y Firefox
    ...(CROSS
      ? [
          {
            name: 'webkit',
            dependencies: ['setup'],
            testMatch: /.*\.cross\.spec\.ts/,
            use: { ...devices['Desktop Safari'], storageState: '.auth/user.json' },
          },
          {
            name: 'firefox',
            dependencies: ['setup'],
            testMatch: /.*\.cross\.spec\.ts/,
            use: { ...devices['Desktop Firefox'], storageState: '.auth/user.json' },
          },
        ]
      : []),
  ],
});
