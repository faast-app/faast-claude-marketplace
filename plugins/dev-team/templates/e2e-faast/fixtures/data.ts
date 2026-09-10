import { APIRequestContext } from '@playwright/test';

// Datos de prueba: cada test crea y limpia lo suyo o usa datos SEMILLA sembrados por el
// DBA con scripts idempotentes (misma regla global de scripts). NUNCA depender de datos
// que "deberian existir" en el ambiente: si faltan, es bloqueante, no un reto.
const API_URL = process.env.API_URL ?? 'http://localhost:5000';

export function uniqueSuffix() {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`;
}

export async function createFixture<T>(request: APIRequestContext, path: string, body: unknown): Promise<T> {
  const res = await request.post(`${API_URL}${path}`, { data: body });
  if (!res.ok()) throw new Error(`No se pudo crear dato de prueba en ${path}: ${res.status()} ${await res.text()}`);
  return (await res.json()) as T;
}

export async function deleteFixture(request: APIRequestContext, path: string): Promise<void> {
  const res = await request.delete(`${API_URL}${path}`);
  if (!res.ok() && res.status() !== 404) throw new Error(`No se pudo limpiar ${path}: ${res.status()}`);
}
