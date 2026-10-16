// Renderiza un HTML a PDF con Chromium (Playwright) y pie de pagina con numeracion.
// Uso: node render-pdf.mjs <entrada.html> <salida.pdf> "<texto del pie>"
// Requiere playwright-core: se toma de PLAYWRIGHT_CORE (ruta al paquete) o del resolvedor de node.
import { pathToFileURL } from "node:url";

const [, , entrada, salida, pie = "FaaST · Manual de usuario"] = process.argv;
if (!entrada || !salida) {
  console.error("Uso: node render-pdf.mjs <entrada.html> <salida.pdf> \"<pie>\"");
  process.exit(1);
}
const mod = process.env.PLAYWRIGHT_CORE
  ? await import(pathToFileURL(process.env.PLAYWRIGHT_CORE + "/index.mjs").href).catch(() => import(process.env.PLAYWRIGHT_CORE + "/index.js"))
  : await import("playwright-core");
const { chromium } = mod.default ?? mod;

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(pathToFileURL(entrada).href, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
const escapar = (t) => t.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
await page.pdf({
  path: salida,
  format: "A4",
  printBackground: true,
  preferCSSPageSize: true,
  displayHeaderFooter: true,
  headerTemplate: "<span></span>",
  footerTemplate: `
    <div style="width:100%;font-family:Helvetica,Arial,sans-serif;font-size:7.5pt;color:#4a4f45;
                padding:0 16mm;display:flex;justify-content:space-between;align-items:center;">
      <span><span style="display:inline-block;width:7px;height:7px;background:#71af26;border-radius:2px;
            margin-right:6px;vertical-align:middle;"></span>${escapar(pie)}</span>
      <span>Página <span class="pageNumber"></span> de <span class="totalPages"></span></span>
    </div>`,
});
await browser.close();
console.log("PDF:", salida);
