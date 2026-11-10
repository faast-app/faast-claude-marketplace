---
description: El equipo de diseño produce una PROPUESTA FUNCIONAL DE DISEÑO profesional (UX, pantallas, identidad, motion, 3D, prototipo navegable, tokens, deck HTML+PDF) para que el usuario elija antes de implementar. Subcomandos - {pedido} (propuesta completa), pantalla {HU}, identidad, motion, 3d, prototipo, tokens, libreria, sync, review {url|carpeta}, video. Toda propuesta hereda el tema y los componentes de la libreria UI de FaaST (@faast-app) y pasa las puertas de herencia, taste y Web Interface Guidelines.
argument-hint: '{pedido en lenguaje natural} | pantalla HU-042 | identidad | motion | 3d | prototipo | tokens | libreria {actualizar|verificar|solicitudes} | sync | review {url} | video {tema}'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Design: propuesta funcional de diseño

Pedido: $ARGUMENTS

Invoca al agente `ui-designer` (Design Lead). Asigna un ID `DSN-nnn` (correlativo en
`.coordination/design/`) y trabaja en `.coordination/design/DSN-nnn-{slug}/`.
El paralelismo del equipo de diseño lo orquesta la sesion principal / el Lead a partir
del reparto que el ui-designer deja en handoffs (`ui-designer-to-{agente}-...`).

## Paso 0 — La libreria primero (siempre, antes de invocar a nadie)
Toda propuesta HEREDA el tema y los componentes de la libreria UI de FaaST
(`@faast-app/tokens|themes|ui`, rama `develop`; skill `dev-team:libreria-faast`):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/libreria-faast/scripts/kit_libreria.py" obtener \
  --destino "<coordinacion>/design/DSN-nnn-{slug}/faast-kit"   # + --fuente / --version de config.json → design.libreria
python3 "${CLAUDE_PLUGIN_ROOT}/skills/memoria-equipo/scripts/memoria.py" buscar "diseño {tema del pedido}" --tipo diseno
```

Pasa al `ui-designer` la ruta del kit, la version obtenida y las lecciones encontradas (que
eligio y que rechazo el usuario antes). Si `obtener` falla (sin red, sin npm): dilo y sigue
con un clon local si existe; nunca se diseña "a ojo" una paleta de reemplazo. Solo se omite
este paso si `config.json` → `design.libreria.usar` es `false` (proyecto ajeno a FaaST) o el
pedido es `identidad`.

## Propuesta completa (default: "{pedido}")
1. **Brief** (ui-designer, ≤ 3 preguntas): `00-brief.md` con la lectura de diseño, el
   registro (Operar / Presentar / Persuadir) y los 2 ejes sobre los que divergiran las
   direcciones (`dev-team:taste-faast`).
2. **EN PARALELO**: `ux-researcher` (personas, flujos, IA, wireframes low-fi, hallazgos)
   y `visual-designer` (direccion de arte, identidad si falta, iconos, ilustraciones).
3. **Pantallas** (ui-designer): 2-3 direcciones **sobre la misma libreria** que divergen
   en composicion (ejes nombrados y repartidos, no elegidos por reflejo), `design-spec.md`,
   `herencia.txt` (`HERENCIA: PASA`), capturas 1440/390 en claro y oscuro.
4. **Presentar direcciones al usuario y esperar su eleccion** (plan primero: nada de
   prototipo final sin direccion elegida). Si el usuario pide "decide tu", el
   ui-designer recomienda una y sigue.
5. **EN PARALELO**: `motion-designer` (motion-spec + prototipo animado) y `artist-3d`
   (solo si el brief lo justifica).
6. **`design-engineer`**: prototipo navegable con el markup real del kit, `components.html`
   (componente de `@faast-app/ui` y props por pieza + fichas «Nuevo para la libreria»),
   `DESIGN.md`, `tokens.json`/`themes.json` citados del kit, sincronizacion al lienzo segun
   `design.tools.canvas`, y las **tres puertas** sobre todo HTML del entregable: herencia
   (`kit_libreria.py verificar`), `dev-team:web-interface-guidelines` y la puerta final de
   `dev-team:taste-faast` (capturas 1440/1024/768/390, claro y oscuro, hasta 3 rondas).
7. **Deck** (ui-designer): `propuesta.html` + `propuesta.pdf` (tambien con el kit: el deck
   se ve como el producto) con las 13 secciones y las 12 puertas de calidad verificadas.
   Registrar `evidence_added`.
8. **Decision del usuario** → handoff `ui-designer-to-frontend` con lo fijo y lo flexible y
   la version de la libreria. Frontend NO implementa una pantalla nueva sin este handoff
   (gate del Lead).
9. **Aprender** (siempre, aunque el usuario rechace todo): registra la decision como
   leccion para la proxima propuesta —
   `memoria.py aprender --tipo diseno --agente ui-designer --ref DSN-nnn --texto "Eligio la
   direccion B (tabla protagonista, densidad compacta) porque…; rechazo A por…"` — y, si
   hubo piezas «Nuevo para la libreria», handoff al Lead con las fichas para abrirlas en
   `faast-ui-library`.

## Subcomandos
- **`pantalla HU-042`** → solo pasos 1, 3, 4 y 6 acotados a esa HU (propuesta ligera de
  una pantalla, 2 direcciones, prototipo de esa pantalla, tokens solo si hay nuevos).
- **`identidad`** → visual-designer: brand kit completo (logo, paleta, tipografia,
  aplicaciones, guidelines) con 2-3 direcciones; deck de identidad.
- **`motion`** → motion-designer: auditoria de movimiento del producto actual + motion-spec
  + prototipo animado de las 3 pantallas clave.
- **`3d`** → artist-3d: concepto, escena, assets, performance, fallback (con justificacion
  explicita de por que 3D).
- **`prototipo`** → design-engineer: prototipo navegable desde la direccion ya elegida.
- **`tokens`** → design-engineer: traer/actualizar el kit y dejar `tokens.json` +
  `themes.json` citados de la libreria con la tabla de roles (`kit_libreria.py roles`) en
  `DESIGN.md`. Solo en un proyecto ajeno a FaaST: crear `tokens.json` DTCG propio y generar
  `tokens.css`/Tailwind.
- **`libreria`** → design-engineer: `actualizar` (re-obtener el kit en la ultima version y
  re-verificar las propuestas abiertas, reportando lo que cambio), `verificar {carpeta}`
  (herencia de todos los HTML) o `solicitudes` (consolidar las fichas «Nuevo para la
  libreria» de todos los DSN en un handoff al Lead).
- **`sync`** → design-engineer: sincronizar el prototipo/tokens al lienzo configurado
  (`pencil` | `figma` | `penpot`); si `none`, explicar como habilitar uno con
  `/dev-team:setup design`.
- **`review {url|carpeta}`** → ui-designer + ux-researcher: auditoria de diseño de algo
  existente con capturas y hallazgos priorizados, sin implementar nada: herencia de la
  libreria (que usa y que reinventa), `dev-team:web-interface-guidelines`, checklist de
  `dev-team:taste-faast` (`references/revision.md`), heuristicas y accesibilidad.
- **`video {tema}`** → motion-designer: video de producto/lanzamiento/demo con HyperFrames
  (guion → storyboard → composicion → check → render); sin HyperFrames, guion + storyboard.

## Reglas
- **Plan primero**: las direcciones se presentan y el usuario elige; el equipo no "decide
  por el" salvo pedido explicito.
- Los diseñadores JAMAS commitean en el codigo de la aplicacion; sus entregables viven en
  `.coordination/design/` (videos y raster pesado en `.coordination/design/_media/`,
  gitignored) y llegan a frontend por handoff.
- **La libreria FaaST es el sistema visual.** Ninguna propuesta define paleta, tipografia,
  escala ni componentes propios; lo que falta se pide a la libreria. Sin `HERENCIA: PASA`
  no hay entrega.
- El HTML (enlazando o incrustando el kit) es la fuente de verdad; Pencil/Figma/Penpot son
  espejos alimentados por `tokens.json` + `themes.json`.
- Toda entrega visual lleva sus capturas (1440 y 390, claro y oscuro). Sin captura no hay entrega.
- Cada decision o correccion del usuario sobre diseño se registra como leccion
  (`dev-team:memoria-equipo`) y se consulta en la siguiente propuesta.
- Accesibilidad WCAG 2.2 AA y `prefers-reduced-motion` no se negocian.
- Si falta una herramienta (MCP de lienzo, generador de imagenes, HyperFrames): se anota
  y se entrega igual en HTML/SVG; se sugiere `/dev-team:setup design`.
