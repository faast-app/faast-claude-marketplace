import { expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class LoginPage extends BasePage {
  readonly path = '/login';
  readonly email = this.page.getByLabel(/correo|usuario|email/i);
  readonly password = this.page.getByLabel(/contrase/i);
  readonly submit = this.page.getByRole('button', { name: /ingresar|iniciar sesi/i });

  async expectLoaded() {
    await expect(this.submit).toBeVisible();
  }
  async login(user: string, pass: string) {
    await this.email.fill(user);
    await this.password.fill(pass);
    await this.submit.click();
  }
}
