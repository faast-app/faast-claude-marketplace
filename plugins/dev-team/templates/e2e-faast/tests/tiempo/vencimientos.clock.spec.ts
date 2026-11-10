import { test, expect } from '@playwright/test';

// Tiempo controlado: los casos que dependen de la FECHA (vencimientos, mora, dias habiles,
// fin de mes, cambio de año) no pueden esperar a que llegue el dia ni depender de cuando
// corre la suite. Se fija el reloj del navegador y se avanza: el mismo test da el mismo
// resultado hoy y dentro de un año. (El reloj del SERVIDOR es otra cosa: se controla con
// datos semilla fechados o con la fecha que el ambiente permita inyectar; ver skill
// qa-avanzado, references/tiempo-y-fechas.md.)
test.describe('[TIEMPO] HU-000 vencimientos @tiempo', () => {
  test.skip(true, 'Ejemplo: reemplazar ruta, datos y textos por los de la HU real');

  test('CA-1 › C04 · un dia antes del vencimiento la operacion NO esta en mora', async ({ page }) => {
    await page.clock.install({ time: new Date('2026-06-29T10:00:00-04:00') });
    await page.goto('/operaciones/OP-2026-0418');
    await expect(page.getByTestId('estado-operacion')).toHaveText('Vigente');
  });

  test('CA-1 › C05 · el dia siguiente al vencimiento pasa a mora (limite exacto)', async ({ page }) => {
    await page.clock.install({ time: new Date('2026-06-30T23:59:00-04:00') });
    await page.goto('/operaciones/OP-2026-0418');
    await expect(page.getByTestId('estado-operacion')).toHaveText('Vigente');
    await page.clock.fastForward('00:02:00'); // cruza la medianoche
    await page.reload();
    await expect(page.getByTestId('estado-operacion')).toHaveText('En mora');
  });

  test('CA-2 › C09 · la sesion avisa antes de expirar sin esperar 15 minutos reales', async ({ page }) => {
    await page.clock.install();
    await page.goto('/');
    await page.clock.fastForward('14:00');
    await expect(page.getByRole('dialog', { name: /sesión/i })).toBeVisible();
  });
});
