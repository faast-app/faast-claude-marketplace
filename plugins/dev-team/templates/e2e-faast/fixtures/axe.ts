import { test as base } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

// Fixture UNICO de accesibilidad: todos los tests lo importan desde aqui, asi un cambio
// de configuracion (tags, exclusiones) se propaga a toda la suite.
type AxeFixture = { makeAxeBuilder: () => AxeBuilder };

export const test = base.extend<AxeFixture>({
  makeAxeBuilder: async ({ page }, use) => {
    const make = () =>
      new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
        // Zonas de terceros que no controla el proyecto (ajustar):
        .exclude('#chat-widget');
    await use(make);
  },
});
export { expect } from '@playwright/test';

// Puerta 5 del QA Lead: 0 violaciones critical/serious para aprobar.
export function seriousViolations(results: Awaited<ReturnType<AxeBuilder['analyze']>>) {
  return results.violations.filter((v) => v.impact === 'critical' || v.impact === 'serious');
}
