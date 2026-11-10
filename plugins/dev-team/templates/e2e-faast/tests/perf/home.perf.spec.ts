import { test, expect } from '@playwright/test';

// Rendimiento percibido (puerta condicional de rendimiento): Core Web Vitals medidos en el
// navegador real contra un PRESUPUESTO. No reemplaza una prueba de carga: responde "¿esta
// pantalla se siente rapida para una persona?". Presupuestos por defecto = umbrales "bueno" de
// Google (LCP 2.5 s, CLS 0.1) y un tope de peso; el proyecto puede endurecerlos por variable.
const LCP_MS = Number(process.env.PERF_LCP_MS ?? 2500);
const CLS = Number(process.env.PERF_CLS ?? 0.1);
const PESO_KB = Number(process.env.PERF_PESO_KB ?? 1500);

test.describe('[PERF] Pantallas clave @perf', () => {
  test('home dentro del presupuesto', async ({ page }, testInfo) => {
    let bytes = 0;
    page.on('response', async (res) => {
      const largo = Number(res.headers()['content-length'] ?? 0);
      bytes += Number.isFinite(largo) ? largo : 0;
    });
    await page.goto('/', { waitUntil: 'networkidle' });

    const vitals = await page.evaluate(
      () =>
        new Promise<{ lcp: number; cls: number }>((resolve) => {
          let lcp = 0;
          let cls = 0;
          new PerformanceObserver((lista) => {
            const ultima = lista.getEntries().at(-1);
            if (ultima) lcp = ultima.startTime;
          }).observe({ type: 'largest-contentful-paint', buffered: true });
          new PerformanceObserver((lista) => {
            for (const e of lista.getEntries() as unknown as Array<{ value: number; hadRecentInput: boolean }>) {
              if (!e.hadRecentInput) cls += e.value;
            }
          }).observe({ type: 'layout-shift', buffered: true });
          setTimeout(() => resolve({ lcp, cls }), 1500);
        }),
    );
    const medido = { lcpMs: Math.round(vitals.lcp), cls: Number(vitals.cls.toFixed(3)), pesoKb: Math.round(bytes / 1024) };
    await testInfo.attach('web-vitals.json', { body: JSON.stringify({ medido, presupuesto: { LCP_MS, CLS, PESO_KB } }, null, 2), contentType: 'application/json' });

    expect(medido.lcpMs, `LCP ${medido.lcpMs} ms (presupuesto ${LCP_MS})`).toBeLessThanOrEqual(LCP_MS);
    expect(medido.cls, `CLS ${medido.cls} (presupuesto ${CLS})`).toBeLessThanOrEqual(CLS);
    expect(medido.pesoKb, `peso ${medido.pesoKb} kB (presupuesto ${PESO_KB})`).toBeLessThanOrEqual(PESO_KB);
  });
});
