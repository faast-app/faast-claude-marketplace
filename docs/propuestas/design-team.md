# Propuesta: Equipo de diseño de ultima generacion (UX, UI, imagen, motion, 3D, maquetacion)

**Estado:** implementada en dev-team v2.11.0 · **Fecha:** 2026-09-10 · **Fase:** 7

## 0. Resumen ejecutivo

dev-team tenia UN diseñador (`ui-designer`) que entregaba mockups HTML y una spec. El
usuario pidio un **equipo de diseño completo y actual**: investigacion UX, diseño de
interfaz, diseño grafico e ilustracion, animacion, 3D y maquetadores expertos en
herramientas de ultima generacion (Figma, Pencil), capaz de entregar una **propuesta
funcional profesional** que gerencia pueda leer y aprobar antes de construir.

La propuesta convierte al `ui-designer` en **Design Lead** (mismo patron que `qa` con sus
especialistas) y agrega cinco especialistas:

| Agente | Rol | Herramientas que usa (si existen) |
|---|---|---|
| `ui-designer` (Design Lead) | Brief, direccion, pantallas, consolidacion del deck | Playwright MCP, skills de taste (impeccable, design-taste-frontend, high-end-visual-design) |
| `ux-researcher` | Personas, flujos, arquitectura de informacion, wireframes low-fi, heuristicas, WCAG 2.2, usabilidad | Playwright MCP (snapshot a11y), axe |
| `visual-designer` | Identidad y brand kit, iconografia SVG, ilustracion, referencias, tipografia | brandkit, imagegen-frontend-*, MCP de generacion de imagenes (opcional), media-use |
| `motion-designer` | Motion tokens, micro-interacciones, prototipos animados, video de producto | animate, emil-design-eng, review/improve-animations, apple-design, **HyperFrames** (instalado) |
| `artist-3d` | Escenas Three.js/R3F, glTF optimizado, Spline/Blender, fallback 2D | gltf-transform, Three.js CDN, Spline export |
| `design-engineer` | Prototipo navegable pixel-perfect, tokens **DTCG**, `DESIGN.md`, componentes, sync con **Pencil / Figma / Penpot** via MCP | prototype, impeccable document, stitch-design-taste, Style Dictionary, MCP de lienzo |

Ademas el plugin incorpora **cinco skills propias** (siempre disponibles, sin depender de
las personales del usuario): `design-foundations`, `motion-foundations`, `a11y-checklist`,
`design-tokens-dtcg`, `web-3d-foundations`; y el comando **`/dev-team:design`**.

## 1. Diagnostico

- En esta maquina hay **37 skills personales de diseño** instaladas con la CLI `skills` desde
  5 fuentes (`emilkowalski/skills` ×12, `Leonxlnx/taste-skill` ×13, `pbakaus/impeccable` ×1,
  `heygen-com/hyperframes` ×10, `tt-a1i/archify` ×1) (impeccable, design-taste-frontend,
  high-end-visual-design, emil-design-eng, animate, brandkit, imagegen-frontend-web/mobile,
  image-to-code, prototype, stitch-design-taste, apple-design, minimalist-ui,
  industrial-brutalist-ui, redesign-existing-projects, pick-ui-library, archify…) y el plugin
  **HyperFrames** de HeyGen (HTML → video). Nada del plugin dev-team las aprovechaba.
- No hay MCP de lienzo configurado (ni Figma, ni Pencil, ni Penpot) ni generador de
  imagenes; tampoco Blender ni Spline instalados. FFmpeg y Node 26 si.
- El `ui-designer` no tenia flujo de propuesta formal ni entregables de UX, identidad,
  motion o 3D; frontend podia implementar pantallas sin diseño aprobado.

## 2. Estado del arte evaluado (septiembre 2026)

| Necesidad | Recomendacion | Alternativas | Por que |
|---|---|---|---|
| Lienzo de diseño sincronizado con codigo | **Pencil** (gratis, MCP automatico al instalar, `.pen` versionable en git) como opcion por defecto para equipos que arrancan; **Figma MCP remoto** (`https://mcp.figma.com/mcp`, OAuth, lee contexto de diseño y ESCRIBE al canvas) donde ya hay Figma | **Penpot** (open source, self-hosted + MCP con `execute_code` y 66 tools en la version comunitaria) | Los tres tienen MCP; el equipo no depende de ninguno: el HTML autocontenido es la fuente de verdad y el lienzo es espejo |
| Tokens | **W3C DTCG** (`tokens.json` con `$type/$value`, alias, modos) + Style Dictionary o script Node | Tokens Studio, designtoken.md | Estandar; Figma Variables, Pencil y Penpot lo consumen; una sola fuente para CSS y Tailwind |
| Motion | CSS/WAAPI + GSAP para coreografias; **Rive** para interactivo con maquina de estados; Lottie para ilustracion animada; **HyperFrames** para video | Framer Motion (solo React), After Effects | Cubre UI, marketing y demos con lo que ya esta instalado |
| 3D | **Three.js / React Three Fiber**, glTF + Draco/meshopt + KTX2, Spline como fuente de assets | Babylon.js, Spline embed | Estandar web, control de rendimiento y fallback |
| Imagen | Vector nativo (SVG) primero; MCP de generacion opcional (Gemini/OpenAI via `mcp-image` u otro) con API key del usuario; asset search de HyperFrames (`media-use`) | ImagineArt/Pixa MCP (pago) | Sin costo ni dependencia por defecto; se enchufa un generador cuando la organizacion lo decida |
| Accesibilidad | WCAG 2.2 AA con checklist operativa + axe en la suite E2E | — | Ya exigido por QA (puerta 5); ahora nace en diseño |

## 3. El entregable: PROPUESTA FUNCIONAL DE DISEÑO

Carpeta `.coordination/design/DSN-nnn-{tema}/` con brief, UX, UI (2-3 direcciones), visual,
motion, 3D (si aplica), prototipo navegable + `tokens.json` + `DESIGN.md`, y el **deck
`propuesta.html` + `propuesta.pdf`** de 13 secciones (problema, usuarios y flujos, lo que
hay hoy, direcciones, recomendada, sistema visual, movimiento, 3D, prototipo,
accesibilidad y rendimiento, plan, decision). Diez puertas de calidad antes de presentar.

## 4. Adaptadores de herramientas (`design.tools` en config.json)

```json
"design": { "tools": { "canvas": "pencil|figma|penpot|none", "imagegen": "none|{mcp}", "video": "hyperframes|none" } }
```
`/dev-team:setup design` detecta MCPs (`claude mcp list`), HyperFrames, FFmpeg, Node ≥ 22,
`gltf-transform`, y ofrece: `claude mcp add --transport http --scope user figma
https://mcp.figma.com/mcp`, instalar Pencil, o desplegar Penpot (infra).

## 5. Cambios en el plugin (v2.11.0)

- 5 agentes nuevos + `ui-designer` como Design Lead; `skills/` con 5 skills; `commands/design.md`.
- `lead.md`: gate "pantalla nueva sin diseño aprobado no se implementa"; `frontend.md`:
  consume `tokens.json`/`DESIGN.md`/prototipo; `setup.md` §6 herramientas de diseño;
  `/start` enruta diseño; `/new-project` ofrece la propuesta de diseño tras la arquitectura.
- Hooks (roster), oficina virtual (Estudio de Diseño con 6 puestos), GUIDE (Caso 5 y equipo
  de 20), README, CLAUDE.md, manifiestos.

## 6. Fuentes
- Figma MCP remoto e instalacion: https://developers.figma.com/docs/figma-mcp-server/remote-server-installation/
- Figma Dev Mode MCP (anuncio): https://www.figma.com/blog/introducing-figma-mcp-server/
- Pencil (pen.dev) documentacion: https://docs.pencil.dev/ · skill comunitaria: https://github.com/Nisus74/pencil-skill
- Penpot MCP self-hosted: https://github.com/ancrz/penpot-mcp-server · https://seehiong.github.io/posts/2026/03/claude-code-meets-self-hosted-penpot/
- Design Tokens Community Group (DTCG): https://www.designtokens.org/ · guia: https://tasteprofile.io/blog/w3c-dtcg-design-tokens-practical-guide
- Motion 2026 (Rive vs Lottie, Spline): https://lottiefiles.com/blog/design-guides-and-tips/best-motion-design-tools-ranked-by-use-case · https://www.illustration.app/blog/which-tool-wins-for-motion-led-branding-in-2026
- Tendencias UI/UX 2026: https://muz.li/blog/web-design-trends-2026/
- Generacion de imagenes via MCP: https://github.com/shinpr/mcp-image · https://github.com/guinacio/claude-image-gen
- HyperFrames (HeyGen): https://hyperframes.heygen.com
- Claude Code plugins (skills, .mcp.json): https://code.claude.com/docs/en/plugins
