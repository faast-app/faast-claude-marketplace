---
description: Asigna una tarea del backlog a un agente (uso exclusivo del Lead)
---

Asigna una tarea del backlog a un agente:

1. Lee `.coordination/backlog.md` y muestra tareas pendientes/sin asignar
2. Pregunta:
   - Que tarea asignar? (por ID, o describe una nueva)
   - A quien? (backend | frontend | dba | infra | cybersec)
   - Prioridad? (alta | media | baja)
   - En que repo? (lista repos disponibles en la carpeta paraguas)
3. En el repo correspondiente, crea el branch:
   `git -C {repo} checkout -b feature/{id}-{descripcion}`
4. Genera handoff en `.coordination/handoffs/lead-to-{agente}-{YYYYMMDD-HHmm}.md` con:
   - Descripcion de la tarea
   - Criterios de aceptacion
   - Repo y branch asignado
   - Dependencias (de architecture.md y backlog)
5. Actualiza `.coordination/backlog.md` marcando la tarea como asignada
6. Actualiza `.coordination/sprint-actual.md` si la tarea entra al sprint activo
7. Confirma la asignacion con resumen
