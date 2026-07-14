---
description: Lee y procesa handoffs pendientes dirigidos al agente actual
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


Revisa handoffs pendientes en `.coordination/handoffs/`:

1. Lista todos los archivos `.md` en `.coordination/handoffs/` (excluyendo archive/)
2. Filtra los dirigidos a ti segun tu rol actual (el nombre del archivo contiene "to-{tu-rol}")
   - Si no hay filtro claro, muestra todos los pendientes
3. Para cada handoff pendiente:
   - Muestra: remitente, fecha, tipo (tarea/bug/reporte/bloqueo), resumen
4. Pregunta: "Cual handoff quieres procesar?"
5. Al procesar:
   - Lee el handoff completo
   - Muestra el contenido
   - Sugiere los pasos a seguir segun tu rol
   - Pregunta si quieres archivarlo: mover a `.coordination/handoffs/archive/`
