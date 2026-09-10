import { test, expect } from '@playwright/test';

// Convencion OBLIGATORIA de trazabilidad HU -> test: 1 archivo por HU, 1 test por criterio.
// El QA Lead cruza este archivo con .coordination/test-plans/hu-000.md y con
// .coordination/evidence/HU-000/informe-qa.md (verificacion explicita + capturas).
test.describe('[HU-000] Ejemplo: filtro de fechas en cobranzas', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/cobranzas');
  });

  // Criterio 1: Dado un rango valido, cuando filtro, entonces veo solo registros del rango
  test('CA-1: filtra registros dentro del rango', async ({ page }) => {
    await page.getByLabel('Desde').fill('2026-01-01');
    await page.getByLabel('Hasta').fill('2026-01-31');
    await page.getByRole('button', { name: 'Filtrar' }).click();
    const filas = page.getByRole('row').filter({ hasNot: page.getByRole('columnheader') });
    await expect(filas.first()).toBeVisible();
    for (const fecha of await filas.getByTestId('fecha').allTextContents()) {
      expect(fecha >= '2026-01-01' && fecha <= '2026-01-31').toBeTruthy();
    }
  });

  // Criterio 2: Dado un rango invalido, cuando filtro, entonces veo mensaje de error
  test('CA-2: muestra error con rango invalido', async ({ page }) => {
    await page.getByLabel('Desde').fill('2026-02-31');
    await page.getByLabel('Hasta').fill('2026-01-01');
    await page.getByRole('button', { name: 'Filtrar' }).click();
    await expect(page.getByRole('alert')).toHaveText('El rango de fechas no es válido');
  });

  // Criterio no automatizable: documentar por que y cubrirlo en el plan como manual.
  test.fixme('CA-3: envia el reporte por correo (requiere buzon real — manual)', async () => {});
});
