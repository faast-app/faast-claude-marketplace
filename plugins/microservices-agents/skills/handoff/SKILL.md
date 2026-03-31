---
description: Crea un handoff para comunicarte con otro agente del equipo
---

Crea un handoff para comunicarte con otro agente:

1. Pregunta:
   - Para quien? (architect | lead | backend | frontend | dba | infra | cybersec)
   - Tipo? (solicitud | reporte | bloqueo | completado)
2. Detecta automaticamente:
   - Tu rol actual (segun el agente activo)
   - Branch actual y ultimos commits relevantes
   - Archivos modificados recientemente (`git diff --name-only HEAD~3`)
3. Genera `.coordination/handoffs/{tu-rol}-to-{destino}-{YYYYMMDD-HHmm}.md` con:
   - Remitente, destinatario, fecha, tipo
   - Contexto: branch, repo, ultimos cambios
   - Lo que necesitas o lo que completaste
   - Siguiente paso sugerido para el destinatario
4. Confirma la creacion del handoff
