import { test, expect } from '@playwright/test';

// Otros navegadores (puerta condicional): SOLO los flujos criticos (R1) se repiten en WebKit
// (Safari, iPhone) y Firefox. Un archivo *.cross.spec.ts corre en chromium, webkit y firefox
// cuando la suite se lanza con CROSS_BROWSER=1 (npm run test:cross); el resto de la suite sigue
// solo en chromium para no triplicar el tiempo.
test.describe('[CROSS] Flujo critico @cross', () => {
  test.skip(true, 'Ejemplo: reemplazar por el flujo R1 del proyecto (login + operacion principal)');

  test('el flujo principal se completa en este navegador', async ({ page, browserName }) => {
    await page.goto('/');
    await expect(page.getByRole('main')).toBeVisible();
    test.info().annotations.push({ type: 'navegador', description: browserName });
  });
});
