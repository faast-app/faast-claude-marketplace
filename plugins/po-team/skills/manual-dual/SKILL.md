---
name: manual-dual
description: Manuales de usuario en DOS versiones del mismo flujo (po-team), con recorrido repetible (steps.yaml con localizadores estables para actualizar el manual en la proxima version) - version QA (pasos numerados, precondiciones, ambiente, perfil, datos de prueba, resultado esperado por paso, checklist) y version para cualquier persona (lenguaje simple sin tecnicismos, capturas anotadas con marcadores numerados, consejos y preguntas frecuentes), mismo recorrido y mismas capturas base, reglas de captura y anotacion con el Playwright MCP, plantillas HTML, salida HTML + PDF (+ DOCX) con LibreOffice, nombres y versionado. Cargala al crear o actualizar un manual.
---

# Manual dual (po-team)

Un flujo, dos lectores. El **manual QA** sirve para probar el flujo de forma repetible; el
**manual general** sirve para que cualquier persona (usuario del cliente, comercial, gerencia) lo
use sin ayuda. Se construyen del MISMO recorrido real y comparten las capturas base, asi nunca se
contradicen.

## Que se necesita antes
- Nombre del flujo y su alcance ("Aprobar una operacion de factoring como Jefe Comercial").
- Ambiente (de `ambientes.*`) y perfil(es) por NOMBRE de variable de `.po-team/accesos.env`.
- HU(s) o criterios relacionados si existen (para el manual QA, el resultado esperado de cada
  paso sale de ahi; no se inventa).
Si falta algo, se pregunta UNA vez antes de recorrer.

## Recorrido y capturas (una sola pasada)
1. `browser_resize` 1280x720. Login con la cuenta de la variable indicada.
2. Por cada paso: llegar → `browser_highlight` sobre el control del paso → `browser_take_screenshot`
   `NN-{paso}.png` (version QA) → `browser_hide_highlight`, marcadores numerados en la pagina →
   `NN-{paso}-anotada.png` (version general) → quitar marcadores → anotar en `recorrido.md`:
   pantalla, accion, dato usado, resultado visto y que señala cada marcador.
3. Resultado final con su `browser_verify_*`.
4. Redactar datos personales (skill `evidencia-po`). Nada de credenciales visibles.
Si el flujo falla a mitad: se detiene, se informa al PO (lenguaje de negocio, sin buscar causas)
y el manual queda en borrador con lo recorrido.

## Recorrido repetible (`steps.yaml`)
Junto a `recorrido.md` queda `manuales/{flujo}/steps.yaml`, para que la proxima version (o QA)
repita el MISMO recorrido sin redescubrirlo:
```yaml
flujo: aprobar-operacion-jefe-comercial
ambiente: demo-co            # clave del config; la clase se lee de ahi
perfil: PO_DEMO_JEFE_COMERCIAL   # NOMBRE de variable, nunca el valor
viewport: {width: 1280, height: 720}
pasos:
  - n: 1
    pantalla: Bandeja de operaciones pendientes
    accion: click
    locator: "getByRole('button', { name: 'Aprobar' })"   # de browser_generate_locator
    dato: null
    registra: true            # crea o cambia algo: en productivo exige autorizacion por accion
    espera: "La operacion pasa a estado Aprobada"
    captura: 03-aprobar
```
Reglas: localizadores por rol/etiqueta/test-id (estables), nunca por posicion; datos de prueba,
nunca reales; `registra: true` en todo paso que crea o cambia algo. Para actualizar el manual se
ejecuta este archivo paso a paso; si un localizador ya no existe, se reporta "cambio de pantalla
en el paso N" y se pregunta, sin inventar el camino nuevo.

## Version QA (`templates/manual/manual-qa.html`)
- Portada: flujo, version del manual, fecha, ambiente, autor (del config).
- **Precondiciones**: perfil requerido, datos que deben existir, parametros, estado inicial.
- **Ambiente y datos de prueba**: nombre del ambiente, variable de la cuenta (nunca el valor),
  datos de ejemplo usados (montos, fechas, clientes de prueba).
- **Pasos numerados**: tabla `# · Accion · Dato · Resultado esperado · Captura`. Un resultado
  esperado OBSERVABLE por paso.
- **Resultado final esperado** y **checklist** de verificacion (casillas).
- **Variantes conocidas** (otro perfil, otro tipo de operacion) solo si estan en las HUs.
- Trazabilidad: HUs relacionadas (numeros del tracker) en un anexo.

## Version general (`templates/manual/manual-general.html`)
- Lenguaje simple, segunda persona ("Presiona **Aprobar**"), frases cortas, sin siglas sin
  explicar, sin "endpoint", "ambiente", "variable", "QA".
- Estructura: **Para que sirve** (2 lineas) → **Antes de empezar** (que necesitas) → **Paso a paso**
  (un paso = una captura anotada + 1-3 lineas) → **Listo** (como sabes que salio bien) →
  **Si algo no sale** (situaciones comunes en lenguaje de usuario) → **Preguntas frecuentes**.
- **Capturas anotadas**: cada captura lleva marcadores numerados (circulo con numero) QUEMADOS
  en la imagen sobre los controles que se mencionan, y el texto del paso remite al numero
  ("presiona el boton ②"). Se agregan en la pagina justo antes de capturar (abajo); asi el PDF y
  el DOCX los conservan (LibreOffice ignora superposiciones HTML con `position:absolute`, por eso
  la clase `.marca` de la plantilla es solo un respaldo para la version HTML).

## Como se anotan las capturas (marcadores en la pagina)
Para la version general, en cada paso y ANTES de `browser_take_screenshot`, por cada control a
señalar (ref del `browser_snapshot`) se llama `browser_evaluate` con ese elemento y una funcion
que agrega un marcador numerado fijo sobre el:
```js
(el) => { const r = el.getBoundingClientRect(); const m = document.createElement('div');
  m.className = 'po-marca'; m.textContent = '1';            // numero del marcador en este paso
  Object.assign(m.style, { position: 'fixed', left: (r.left - 14) + 'px', top: (r.top - 14) + 'px',
    width: '28px', height: '28px', borderRadius: '50%', background: '#e4572e', color: '#fff',
    font: '700 14px/28px sans-serif', textAlign: 'center', border: '2px solid #fff',
    boxShadow: '0 1px 4px rgba(0,0,0,.35)', zIndex: 2147483647, pointerEvents: 'none' });
  document.body.appendChild(m); }
```
Despues de capturar, se quitan: `() => document.querySelectorAll('.po-marca').forEach(m => m.remove())`.
Si el MCP ofrece `browser_annotate`, puede usarse en su lugar. La version QA usa la captura limpia
con `browser_highlight` (sin marcadores), asi que por paso se toman dos capturas: `NN-{paso}.png`
(QA) y `NN-{paso}-anotada.png` (general).

## Salida y conversion
```
.po-team/manuales/{flujo-slug}/
├── recorrido.md                 pasos reales, datos y posiciones de los controles
├── capturas/NN-{paso}.png · NN-{paso}-anotada.png
├── {Flujo} - Manual QA - v{N}.html / .pdf / .docx
└── {Flujo} - Manual de usuario - v{N}.html / .pdf / .docx
```
```bash
soffice --headless --convert-to pdf  --outdir "{salida}" "{archivo}.html"
soffice --headless --convert-to "docx:MS Word 2007 XML" --outdir "{salida}" "{archivo}.html"   # si se pide DOCX
```
Las imagenes se referencian con ruta relativa `capturas/…` (el HTML vive junto a la carpeta).
Verificar acentos, eñes e imagenes en el PDF. DOCX por defecto tambien, salvo que se pida solo PDF.
`--version qa|general|ambas` (default `ambas`).

## Versionado
`v1` al crear. Si cambia la pantalla o el flujo: se recorre de nuevo y se genera `v{N+1}` con
"Cambios respecto a v{N}" al final. Nunca se sobreescribe una version entregada.

## Reglas
- Ambas versiones salen del mismo recorrido real: nada se describe sin haberlo visto.
- Nada inventado: si un resultado esperado no esta en una HU ni se vio, queda como pendiente.
- Sin credenciales ni datos personales; cuentas por nombre de variable solo en la version QA.
- La version general jamas tiene jerga; aplicar el test de lectura de `redaccion-negocio`.
