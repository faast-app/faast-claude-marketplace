---
name: web-interface-guidelines
description: Revision de interfaz contra las Web Interface Guidelines de Vercel (accesibilidad, foco, formularios, animacion, tipografia, contenido, imagenes, rendimiento, navegacion y estado, tactil, areas seguras, tema oscuro, i18n, hidratacion, anti-patrones), con la copia FIJADA que usa la libreria FaaST para que la auditoria sea reproducible. Cargala para revisar un HTML de propuesta, un prototipo o codigo de frontend antes de entregarlo, en /design review, en la puerta de diseño y en la revision de PR de UI.
---

# Web Interface Guidelines (Vercel) en dev-team

Las reglas estan en `references/web-interface-guidelines.upstream.md`: copia **sin modificar**
de `vercel-labs/web-interface-guidelines` (`command.md`, commit `434b7f913646`, SHA-256
`d246b026f4f29b5823a9cc857f9edf3d2507002e055e32040cadeaf3b38e0234`, MIT). Es la **misma copia
fijada** que versiona la libreria en `docs/guidelines/` — diseño, frontend y libreria auditan
contra el mismo texto. No se descarga `main` en cada revision: una auditoria debe poder
repetirse.

## Como se revisa

1. Lee `references/web-interface-guidelines.upstream.md` completo (son ~190 lineas).
2. Lee los archivos a revisar (HTML de la propuesta, prototipo, o los `.tsx/.css` del PR).
3. Aplica TODAS las reglas. Salida en el formato del propio documento, breve y con señal:

```text
## 02-ui/propuesta-A.html
propuesta-A.html:41 - boton de solo icono sin aria-label
propuesta-A.html:88 - input sin autocomplete ni name
✓ foco, encabezados, tabla

## 06-prototipo/index.html
✓ pasa
```

4. Clasifica cada hallazgo: **corregir** (en el HTML propio) · **de la libreria** (el markup
   vino del kit: no se parcha aqui, va a `faast-kit/solicitudes-libreria.md` y por handoff al
   Lead como mejora de `faast-ui-library`) · **no aplica** (con el motivo en una linea).
5. Guarda el resultado junto al entregable (`revision-wig.md`) y resumelo en el deck.

## Decisiones ya tomadas por FaaST frente a estas reglas

- **Botones en Title Case** ("Guardar Cambios"): adoptada tal cual. Titulos y texto en oracion.
- **Reglas con sintaxis Tailwind** (`focus-visible:ring-*`, `motion-safe:`…): se leen por su
  intencion. En FaaST el foco, el movimiento y el tema los da la libreria
  (`:focus-visible` con `--faast-focus-ring`, tokens `--faast-duration-*`,
  `data-theme`); no se agrega Tailwind para "cumplir".
- **`color-scheme` y `theme-color`**: los temas de la libreria declaran `color-scheme`; un
  prototipo de pagina completa agrega `<meta name="theme-color">` con el valor del rol
  `--faast-bg-ground`.
- **Numeros**: `tabular-nums` ya viene en tablas y cifras de la libreria; `Intl.NumberFormat`
  / `Intl.DateTimeFormat` con la configuracion regional del pais del ambiente.
- Revisiones previas de la libreria: `docs/guidelines/review-*.md` en `faast-ui-library`
  (lo que ya se audito no se re-reporta contra el markup del kit).

## Actualizar la copia fijada

Solo a pedido: descargar un commit nuevo, reemplazar el archivo **en la libreria y aqui**,
actualizar SHA y fecha en ambos lados y volver a correr la revision. Nunca una sola de las dos.

## Relacion con las otras skills

`dev-team:libreria-faast` decide de donde sale lo visual · `dev-team:taste-faast` decide si
se ve profesional · esta skill comprueba que la interfaz se comporte bien ·
`dev-team:a11y-checklist` profundiza WCAG 2.2 AA · `dev-team:vercel-react-patterns` cubre
el codigo React.
