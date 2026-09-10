import { test as setup, expect } from '@playwright/test';
import fs from 'node:fs';

// Login UNA sola vez por corrida; los tests reusan .auth/user.json (gitignored).
// Regla LEY QA: si el login falla al primer intento, NO se reintenta: se reporta `blocked`.
const AUTH_FILE = '.auth/user.json';

setup('autenticar usuario QA', async ({ page }) => {
  const user = process.env.QA_USER;
  const pass = process.env.QA_PASS;
  if (!user || !pass) throw new Error('Faltan QA_USER/QA_PASS en .env — bloqueante, pedir al Lead');

  await page.goto('/login');
  await page.getByLabel(/correo|usuario|email/i).fill(user);
  await page.getByLabel(/contrase/i).fill(pass);
  await page.getByRole('button', { name: /ingresar|iniciar sesi/i }).click();
  // Verificacion EXPLICITA de que el login ocurrio (ajustar al indicador real de la app)
  await expect(page.getByRole('navigation')).toBeVisible();

  fs.mkdirSync('.auth', { recursive: true });
  await page.context().storageState({ path: AUTH_FILE });
});
