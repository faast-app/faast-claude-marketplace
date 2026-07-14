---
description: Muestra el estado actual del proyecto de microservicios (backlog, sprint, handoffs, repos)
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


Revisa el estado actual del proyecto:

1. Lee `.coordination/backlog.md` y cuenta tareas pendientes vs completadas por prioridad
2. Lee `.coordination/sprint-actual.md` y muestra tareas del sprint con su estado
3. Lista archivos en `.coordination/handoffs/` pendientes de procesar (excluir archive/)
4. Para cada repo de servicio en la carpeta paraguas:
   - Muestra branch actual: `git -C {repo} branch --show-current`
   - Ultimos 3 commits: `git -C {repo} log --oneline -3`
   - Cambios sin commitear: `git -C {repo} status --short`
5. Presenta resumen:

**Estado del Proyecto**
- Sprint: [nombre/numero]
- Tareas sprint: X completadas / Y total
- Backlog total: N pendientes (A alta, B media, C baja)
- Handoffs pendientes: N
- Repos con cambios sin commitear: [lista]
