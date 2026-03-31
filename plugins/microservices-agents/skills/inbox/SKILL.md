---
description: Lee y procesa handoffs pendientes dirigidos al agente actual
---

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
