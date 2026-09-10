import { test, expect } from '@playwright/test';

// Seed test: lo usan los Playwright Test Agents (planner/generator) como ejemplo del
// entorno: como se llega a la app autenticada y que indica que cargo.
test('seed: la app carga autenticada', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('navigation')).toBeVisible();
});
