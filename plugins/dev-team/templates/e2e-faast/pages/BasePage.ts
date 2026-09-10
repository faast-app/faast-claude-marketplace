import { Page, Locator, expect } from '@playwright/test';

// Page Object base. Selectores SOLO por rol/label/testid — nunca CSS fragil ni XPath.
export abstract class BasePage {
  constructor(protected readonly page: Page) {}
  abstract readonly path: string;

  async goto() {
    await this.page.goto(this.path);
    await this.expectLoaded();
  }
  abstract expectLoaded(): Promise<void>;

  byTestId(id: string): Locator {
    return this.page.getByTestId(id);
  }
  async expectToast(text: string | RegExp) {
    await expect(this.page.getByRole('status')).toContainText(text);
  }
}
