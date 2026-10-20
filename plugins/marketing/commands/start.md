---
description: Punto de entrada unico del equipo de Marketing, Ventas y Publicidad. Detecta si el equipo esta configurado para este proyecto (la carpeta .marketing/ SIEMPRE fuera de los repos) y te guia - configurar por primera vez (producto, fuentes reales del dev-team y de la Mesa, ambiente demo, publico, marca), arrancar una propuesta comercial o campana, seguir una en curso, o ver el estado. Si no sabes que comando usar, usa este.
argument-hint: (opcional) que quieres vender o hacer, en tus palabras - p. ej. "propuesta de Faast2.0 para el CEO de X"
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su procedimiento en
> la sesion actual. NUNCA lo corras dentro de un subagente ni lo invoques via Agent/Task. Solo se
> delegan los AGENTES del equipo, y unicamente cuando este procedimiento lo indica.

# Start: ¿que vendemos hoy?

Pedido (puede venir vacio): $ARGUMENTS

Este comando existe para que nadie tenga que memorizar los demas. Detecta el contexto y lleva al
flujo correcto. Nunca responde "no entendi": siempre ofrece las opciones con una linea cada una.

## Paso 1 — Detectar contexto
Resolver la carpeta canonica de Marketing:
`python3 "${CLAUDE_PLUGIN_ROOT}/hooks/coord_root.py" "$PWD"` (imprime JSON con `path` y `en_repo`, o
nada si no hay proyecto).
- **Hay `path` con `config.json` y `en_repo: false`** → equipo configurado → Paso 3.
- **`en_repo: true`** → la carpeta esta dentro de un repo: proponer moverla (`mv`) a la carpeta del
  proyecto fuera del repo y registrarla en `~/.claude/marketing.config.json` → `"proyectos"`; no
  seguir produciendo ahi (un hook lo bloquea).
- **Nada** → Paso 2.

## Paso 2 — Primera vez: configurar (una sola ronda de preguntas)
1. **Donde vive `.marketing/`**: proponer la carpeta del proyecto (p. ej.
   `~/Documents/Trabajo/Faast/Proyectos/{Proyecto}/`). Verificar ANTES de crear:
   `git -C "{carpeta}" rev-parse --is-inside-work-tree` → si responde `true`, subir a la carpeta
   contenedora que no es repo o preguntar. Nunca dentro de un repo.
2. Preguntar en UN mensaje lo minimo (con lo detectado ya propuesto como opcion):
   - Producto a vender y version (p. ej. Faast2.0).
   - Fuentes reales: `.coordination/` del dev-team (buscar en la carpeta del proyecto), `.mesa/` de la
     Mesa de Servicios, prototipos, repos.
   - Ambiente demo/pruebas con datos ficticios para capturar (URL y nombre de la variable con la
     credencial; nunca la credencial escrita) — o "no hay".
   - Publicos habituales (CEO, gerente comercial, cliente final) y paises.
   - Marca: ¿hay manual o kit oficial? (si no, se parte de la skill `marca-faast`).
3. Crear `.marketing/` desde `templates/marketing/config.json` con las respuestas; subcarpetas
   `campanas/ tendencias/ marca/ metrics/ handoffs/`; `correlativos.json` = `{}`; registrar en
   `~/.claude/marketing.config.json` → `"proyectos": {"<carpeta de trabajo>": "<carpeta del proyecto>"}`.
4. Herramientas (solo verificar y reportar; instalar solo con OK del usuario): `node -v` (≥ 22 para
   HyperFrames), `ffmpeg -version`, `npx hyperframes --version` (o skill `hyperframes` presente),
   LibreOffice/`soffice` (PDF/DOCX), Playwright MCP del plugin (`browser_*` disponible), skills de
   diseño (`pptx`, `pdf`, `high-end-visual-design`, `impeccable`, `product-launch-video`...).
5. Ofrecer `/marketing:marca` (cargar y validar el kit) y `/marketing:tendencias` (sembrar la base).
6. Cerrar mostrando como empezar: `/marketing:propuesta-comercial "{producto} para {publico}"`.

## Paso 3 — Equipo activo: resumen + siguiente accion
Mostrar maximo 5 lineas:
```
Marketing ({ruta absoluta de .marketing}): {n} campanas en curso · {n} esperando aprobacion · {n} entregadas
Ultimas: {ID} ({estado}), {ID} ({estado})
Marca: kit {cargado|pendiente} · Tendencias: {n} vigentes, {n} vencidas
```
Interpretar $ARGUMENTS:
- "propuesta / vender / CEO / cliente / pitch / reunion comercial" → `/marketing:propuesta-comercial`
- "desglose / mapa del producto / fichas / partes" → `/marketing:desglose`
- "video / keynote / clip / teaser / reel / motion / lanzamiento" → `/marketing:video`
- "presentacion / deck / laminas / ppt" → `/marketing:presentacion`
- "panfleto / one-pager / folleto / redes / linkedin / post" → `/marketing:pieza`
- "competencia / mercado / benchmark / cifras / tendencias del sector" → `/marketing:investigar`
- "refrescar tendencias / que esta de moda / actualizar base" → `/marketing:tendencias`
- "marca / logo / colores / tipografia / kit" → `/marketing:marca`
- "como vamos / estado / pendientes / que falta" → `/marketing:estado`
- "no se / que sigue" → recomendar lo mas util (campana sin mapa aprobado → desglose; fichas
  aprobadas sin video → video; piezas esperando aprobacion → mostrarlas; tendencias vencidas →
  tendencias).
Ejecutar el flujo elegido directamente, sin pedir que escriba otro comando.

## Paso 3.5 — Protocolo del equipo
Si no esta en contexto el bloque `<marketing-protocolo>` (sesion abierta fuera de la carpeta),
cargarlo: `CLAUDE_PROJECT_DIR="{carpeta del proyecto}" "${CLAUDE_PLUGIN_ROOT}/hooks/inject-protocol.sh"`
y adoptar su salida (plan primero, desglose antes que piezas, nada inventado, aprobacion por pieza).

## Reglas
- `.marketing/` nunca dentro de un repo; siempre ruta absoluta.
- Plan primero antes de producir; solo-lectura exento.
- Nada se inventa en la configuracion: lo que el usuario no sabe queda `PENDIENTE`.
