import { test, expect, seriousViolations } from '../../fixtures/axe';

// Accesibilidad (puerta 5): 0 violaciones critical/serious por pantalla nueva o tocada.
// Patron: navegar -> escanear -> afirmar. El detalle (regla, selector, ayuda) queda en
// el reporte JSON adjunto como evidencia.
test.describe('[A11Y] Pantallas clave', () => {
  test('home sin violaciones graves', async ({ page, makeAxeBuilder }, testInfo) => {
    await page.goto('/');
    const results = await makeAxeBuilder().analyze();
    await testInfo.attach('axe-home.json', {
      body: JSON.stringify(results.violations, null, 2),
      contentType: 'application/json',
    });
    expect(seriousViolations(results), 'violaciones critical/serious').toEqual([]);
  });
});
