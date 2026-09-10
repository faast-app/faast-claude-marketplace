import { test, expect } from '@playwright/test';

// Regresion visual (puerta 4). Baselines en git (*-snapshots/), generados SOLO en CI
// (Linux) con `npm run test:visual:update` y con OK del ui-designer o del PO.
// Enmascarar zonas dinamicas (fechas, avatares, graficos en vivo).
test.describe('[VISUAL] Pantallas clave', () => {
  test('home', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('navigation')).toBeVisible();
    await expect(page).toHaveScreenshot('home.png', {
      fullPage: true,
      mask: [page.getByTestId('fecha-actual'), page.getByTestId('avatar')],
    });
  });
});
