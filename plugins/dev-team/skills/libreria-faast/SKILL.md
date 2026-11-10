---
name: libreria-faast
description: La libreria UI de FaaST (@faast-app/tokens, @faast-app/themes, @faast-app/ui, rama develop de faast-app/faast-ui-library) es la fuente unica del tema y de los componentes de TODA propuesta de diseño, prototipo, deck y pantalla. Cargala antes de diseñar, maquetar, revisar o implementar cualquier interfaz - trae el kit de propuestas (una hoja CSS, markup real de componentes, tokens DTCG, logos), como usarlo, como verificar que un HTML hereda de la libreria y que hacer cuando la libreria no tiene lo que el diseño necesita.
---

# Libreria FaaST: el diseño hereda, no redibuja

**Regla madre.** El tema (color, tipografia, espaciado, radios, sombras, movimiento, claro y
oscuro) y los componentes de cualquier propuesta salen de la libreria UI de FaaST, en una
version conocida. El equipo de diseño decide **composicion, jerarquia, flujo, contenido y
estados**; no decide una paleta, una fuente ni un boton nuevos. Si la propuesta se ve distinta
del producto, la propuesta esta mal.

Esto aplica a proyectos FaaST (el default). Un proyecto con marca propia de un cliente usa el
tema de tenant de la misma libreria (seccion 6). Solo un proyecto que el usuario declara
ajeno a FaaST (`design.libreria.usar: false` en `config.json`) diseña su propio sistema con
`dev-team:design-tokens-dtcg`.

## 1. Que es la libreria

| Paquete | Que trae |
| --- | --- |
| `@faast-app/tokens` | Primitivos (color, tipografia, espaciado, radios, sombras, motion, breakpoints) como CSS `--faast-*`, TypeScript y **DTCG** (`tokens.json`); logo oficial y su variante sobre oscuro |
| `@faast-app/themes` | Roles semanticos claro/oscuro (`--faast-text-primary`, `--faast-bg-surface`, `--faast-status-*`…), `base.css`, fuente Inter, **DTCG** (`themes.json`) y temas de cliente (`createTenantTheme`) |
| `@faast-app/ui` | Componentes React accesibles y mobile-first + `styles.css` + el **kit de propuestas** |

Repositorio `faast-app/faast-ui-library`, rama de referencia **`develop`** (cada push que sube
la version publica en npm). Documentos que mandan: `docs/branding.md` (marca y contraste),
`docs/components.md` (catalogo y comportamiento movil), `docs/proposal-kit.md`,
`docs/guidelines/` (Web Interface Guidelines fijadas y revisiones).

## 2. Traer el kit a la carpeta de diseño (primer paso de toda propuesta)

```bash
KIT="${CLAUDE_PLUGIN_ROOT}/skills/libreria-faast/scripts/kit_libreria.py"
# desde npm (lo publicado desde develop):
python3 "$KIT" obtener --destino "<coordinacion>/design/DSN-nnn-slug/faast-kit"
# o desde un clon local de la libreria en develop (lo mas nuevo, aun sin publicar):
python3 "$KIT" obtener --destino "<...>/faast-kit" --fuente "<ruta al clon de faast-ui-library>"
```

La fuente y la version salen de `config.json` → `design.libreria`
(`{"usar": true, "fuente": "npm" | "<ruta al clon>", "version": "latest" | "0.8.0"}`); sin
config, npm `latest`. El clon debe estar en `develop` y compilado (`pnpm install && pnpm run
build`); el script lo dice si no. Queda en `faast-kit/`:

| Archivo | Para que |
| --- | --- |
| `faast-kit.css` | LA hoja de estilos: Inter + tokens + temas claro/oscuro + base + componentes |
| `markup.json` | Markup real de cada componente (renderizado desde React): se copia tal cual |
| `catalogo.html` | Galeria navegable de todos los ejemplos, con cambio de tema |
| `tokens.json`, `themes.json` | Tokens DTCG (primitivos y roles) para Figma/Penpot/Pencil y `DESIGN.md` |
| `faast-logo*.svg` | Logo oficial y variante sobre oscuro (no se redibuja ni recolorea) |
| `LIBRERIA.json` | Version, fuente, commit y sha256: lo que se cita en la propuesta |

Con libreria anterior a 0.8.0 el script compone la hoja con las hojas publicadas y avisa que
falta `markup.json`: se trabaja con esa hoja y el Storybook, y se anota en la propuesta.

## 3. Como se usa en un HTML de propuesta

Parte de `${CLAUDE_PLUGIN_ROOT}/templates/design/propuesta-base.html` (barra de propuesta
con selector de estado y de tema, lienzo, los 4 estados).

1. **Una hoja de producto:** `<link rel="stylesheet" href="../faast-kit/faast-kit.css">`. Nada
   de Tailwind, Bootstrap, fuentes de Google ni un reset propio.
2. **Componentes = markup copiado** de `markup.json` (o del desplegable "Markup" del
   catalogo). Cambias el **contenido** (textos, montos, filas, iconos del allowlist), nunca
   las clases. Una clase `faast-*` escrita de memoria es una adivinanza.
3. **Layout propio solo con variables:** `var(--faast-space-4)`, `var(--faast-text-secondary)`,
   `var(--faast-border-default)`, `var(--faast-radius-md)`, `var(--faast-font-size-sm)`. Cero
   hex/rgb, cero `font-family` literal, cero `font-size` en px. Prefijo propio para tus
   clases de composicion (`dsn-`), nunca `faast-`.
4. **Roles, no primitivos:** `--faast-text-*`, `--faast-bg-*`, `--faast-border-*`,
   `--faast-status-*`, `--faast-action-*`. Los primitivos (`--faast-color-green-500`) son la
   paleta cruda: la UI no los usa. La tabla completa: `kit_libreria.py roles --kit faast-kit`.
5. **Claro y oscuro salen gratis** (`data-theme="light|dark"` en `<html>`; sin atributo sigue
   al sistema). La propuesta se captura en los dos.
6. **Comportamiento con estado** (dialogos, toasts, tour, tablas de datos, cajon del shell):
   se muestra en reposo o se enlaza la historia de Storybook; no se reimplementa en JS suelto.

Reglas de la libreria que el diseño respeta (resumen de `branding.md` y `components.md`):
una sola accion `primary` por vista · botones en Title Case ("Guardar Cambios"), titulos y
textos en oracion · estado siempre en palabras ademas del color · superficies planas con
borde de 1 px, sombra solo en lo que flota · controles de 44 px en tactil (36 px con puntero
fino desde `md`) · inputs a 16 px · montos con cifras tabulares a la derecha · el verde de
marca `accent.base` es decorativo: para texto o UI funcional `accent.text`/`accent.hover` ·
el violeta es solo un tono de estado ("aprobada") · iconos solo del allowlist de `Icon`.

## 4. Verificar la herencia (puerta obligatoria antes de entregar)

```bash
python3 "$KIT" verificar 02-ui/propuesta-A.html 06-prototipo/index.html --kit faast-kit
# ... HERENCIA: PASA (2/2 archivos)
```

Falla (y se corrige, no se discute) por: pagina sin el kit · kit editado o de otra version ·
color literal · `font-family` literal o fuente externa · clase `faast-*` que la libreria no
define · clase o variable de la libreria redefinida en el CSS propio · variable `--faast-*`
inexistente. Avisos (se corrigen o se justifican en una linea): colores fijos en SVG,
`font-size` en px, animaciones sin `prefers-reduced-motion`. La salida va al entregable
(`herencia.txt`) y al deck. Sin `HERENCIA: PASA` no hay entrega.

Para compartir un solo archivo: `python3 "$KIT" incrustar propuesta-A.html --kit faast-kit`.

## 5. Cuando la libreria no tiene lo que el diseño necesita

Es un hallazgo, no una licencia para improvisar:

1. Busca primero: ¿lo resuelve un componente existente con otro contenido, o una
   composicion de dos? (`catalogo.html`, `docs/components.md`.)
2. Si de verdad falta, la propuesta lo marca como **«Nuevo para la libreria»** y lo dibuja
   SOLO con variables del kit, dentro de un bloque `data-nuevo-libreria="nombre"`.
3. Registra la ficha en `faast-kit/solicitudes-libreria.md`: que es y donde se usa (HU,
   pantalla), anatomia y estados, variantes, comportamiento movil, accesibilidad (rol,
   teclado, nombre accesible), roles de tema que consume, y si necesita un token nuevo (cual
   y por que ninguno existente sirve).
4. El Design Lead la pasa por handoff al Lead: el cambio se hace **en el repo de la libreria**
   (rama desde `develop`, componente + estilos + historia de Storybook + test + ejemplo en
   `packages/ui/kit/examples.mjs` + `CHANGELOG`), se publica, y recien entonces lo usa una
   aplicacion. Frontend no implementa una copia local "mientras tanto".
5. Nunca: una paleta paralela, una segunda escala tipografica o de espaciado, un boton
   "parecido", un token redefinido en el CSS de la propuesta.

## 6. Marca de un cliente (tenant)

El tema de un cliente se **genera** con `createTenantTheme` de `@faast-app/themes` a partir
de su color de marca (calcula la escala, valida contraste y devuelve ajustes y avisos). La
propuesta muestra el resultado de esa funcion, no un color puesto a mano; si la funcion
ajusta o rechaza el color, eso se le explica al cliente con el motivo que entrega.

## 7. Puentes

- **Figma / Penpot / Pencil** (`design.tools.canvas`): las variables del lienzo se importan
  de `tokens.json` + `themes.json` (modos light/dark); el lienzo es espejo, la libreria manda.
- **`tokens.json` del proyecto**: es una copia citada de los del kit (con la version), no un
  archivo nuevo. `DESIGN.md` documenta roles y componentes **por su nombre en la libreria**.
- **Frontend**: `pnpm add @faast-app/ui @faast-app/themes @faast-app/tokens` en la misma
  version que cita la propuesta; el handoff nombra componente y props, no clases.
