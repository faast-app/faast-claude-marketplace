---
description: Muestra el estado actual del proyecto de microservicios (backlog, sprint, handoffs, repos)
---

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
