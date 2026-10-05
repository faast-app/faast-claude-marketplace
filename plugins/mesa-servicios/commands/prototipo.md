---
description: El prototipador arma una maqueta tipo wireframe (boceto gris, placeholders, navegable entre pantallas, un solo HTML) con las 3-6 pantallas clave para que el cliente VEA la idea del requerimiento o de la propuesta - aplica a funcionalidad nueva con cambios en pantalla, proyecto nuevo y cotizacion (no a bugs). Captura cada pantalla para el documento y prepara las preguntas de validacion. Uso - /mesa-servicios:prototipo {ID} [--fidelidad baja|media] [--validar "..."]
argument-hint: '{ID} [--fidelidad baja|media] [--movil] [--validar "lo que decidio el cliente al verla"]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Prototipo: que el cliente vea la idea

Solicitud: $ARGUMENTS

## Cuando aplica
PRY con cambio visible en pantalla, proyecto nuevo, CTZ. **No** para BUG ni para pedidos sin
cambio de pantalla (si se pide igual, explicar y ofrecer un diagrama de flujo simple).

## Modo A — armar la maqueta
1. Prerequisito: solicitud `CERRADA` (o al menos con el flujo deseado y los perfiles claros en
   `preguntas.md`). Si el cambio es sobre una pantalla existente y no hay capturas de "hoy",
   sugerir `/mesa-servicios:reproducir {ID} --hoy` primero (opcional).
2. **Plan primero**: proponer las 3-6 pantallas clave (nombre de negocio + proposito) y la
   fidelidad; esperar OK.
3. Invocar al agente `prototipador`: `maqueta.html` desde `templates/prototipo/maqueta-base.html`
   (estilo boceto, kit de componentes, navegacion `data-ir`, notas al margen numeradas),
   capturas con Playwright MCP (`captura-NN-{pantalla}.png`, 1280x720; 375x812 con `--movil`),
   `NOTAS.md` y 3-5 preguntas de validacion por pantalla.
4. Salida: ruta de `maqueta.html` (se abre en cualquier navegador), lista de pantallas y las
   preguntas de validacion para que mesa las lleve al cliente. Estado `EN PROTOTIPO`.

## Modo B — registrar la validacion (`--validar`)
El prototipador anota en `NOTAS.md` lo que el cliente decidio al ver cada pantalla; lo que cierra
preguntas se vuelca a `preguntas.md` del analista. Si hay cambios → `v2` (la v1 se conserva); la
validada es la que va al documento. Estado vuelve a `CERRADA` con `prototipo: v{N} validado`.
Siguiente: `/mesa-servicios:documento {ID}`.

## Reglas
- Estilo boceto siempre; sin colores de marca; datos ficticios en el idioma del cliente.
- 3-6 pantallas; no es diseño final ni compromiso (se dice en las notas y en el documento).
- La maqueta vive en `.mesa/solicitudes/{ID}/prototipo/`, nunca en un repo de producto.
- Mesa la presenta al cliente; el equipo prepara maqueta y preguntas.
