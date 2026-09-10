---
description: El equipo de diseño produce una PROPUESTA FUNCIONAL DE DISEÑO profesional (UX, pantallas, identidad, motion, 3D, prototipo navegable, tokens, deck HTML+PDF) para que el usuario elija antes de implementar. Subcomandos - {pedido} (propuesta completa), pantalla {HU}, identidad, motion, 3d, prototipo, tokens, sync, review {url|carpeta}, video.
argument-hint: '{pedido en lenguaje natural} | pantalla HU-042 | identidad | motion | 3d | prototipo | tokens | sync | review {url} | video {tema}'
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

## Propuesta completa (default: "{pedido}")
1. **Brief** (ui-designer, ≤ 3 preguntas): `00-brief.md` con la lectura de diseño.
2. **EN PARALELO**: `ux-researcher` (personas, flujos, IA, wireframes low-fi, hallazgos)
   y `visual-designer` (direccion de arte, identidad si falta, iconos, ilustraciones).
3. **Pantallas** (ui-designer): 2-3 direcciones que divergen en un eje nombrado,
   `design-spec.md`, capturas 1280/375.
4. **Presentar direcciones al usuario y esperar su eleccion** (plan primero: nada de
   prototipo final sin direccion elegida). Si el usuario pide "decide tu", el
   ui-designer recomienda una y sigue.
5. **EN PARALELO**: `motion-designer` (motion-spec + prototipo animado) y `artist-3d`
   (solo si el brief lo justifica).
6. **`design-engineer`**: prototipo navegable de alta fidelidad, `tokens.json` (DTCG),
   `DESIGN.md`, componentes, sincronizacion al lienzo segun `design.tools.canvas`.
7. **Deck** (ui-designer): `propuesta.html` + `propuesta.pdf` con las 13 secciones y las
   10 puertas de calidad verificadas. Registrar `evidence_added`.
8. **Decision del usuario** → handoff `ui-designer-to-frontend` con lo fijo y lo flexible.
   Frontend NO implementa una pantalla nueva sin este handoff (gate del Lead).

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
- **`tokens`** → design-engineer: crear/actualizar `tokens.json` DTCG desde el prototipo o
  desde el codigo existente, generar `tokens.css`/Tailwind, validar, `DESIGN.md`.
- **`sync`** → design-engineer: sincronizar el prototipo/tokens al lienzo configurado
  (`pencil` | `figma` | `penpot`); si `none`, explicar como habilitar uno con
  `/dev-team:setup design`.
- **`review {url|carpeta}`** → ui-designer + ux-researcher: auditoria de diseño de algo
  existente (heuristicas, accesibilidad, anti-generico, consistencia con tokens) con
  capturas y hallazgos priorizados; sin implementar nada.
- **`video {tema}`** → motion-designer: video de producto/lanzamiento/demo con HyperFrames
  (guion → storyboard → composicion → check → render); sin HyperFrames, guion + storyboard.

## Reglas
- **Plan primero**: las direcciones se presentan y el usuario elige; el equipo no "decide
  por el" salvo pedido explicito.
- Los diseñadores JAMAS commitean en el codigo de la aplicacion; sus entregables viven en
  `.coordination/design/` (videos y raster pesado en `.coordination/design/_media/`,
  gitignored) y llegan a frontend por handoff.
- El HTML autocontenido es la fuente de verdad; Pencil/Figma/Penpot son espejos.
- Toda entrega visual lleva su captura (1280 y 375). Sin captura no hay entrega.
- Accesibilidad WCAG 2.2 AA y `prefers-reduced-motion` no se negocian.
- Si falta una herramienta (MCP de lienzo, generador de imagenes, HyperFrames): se anota
  y se entrega igual en HTML/SVG; se sugiere `/dev-team:setup design`.
