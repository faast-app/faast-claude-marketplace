---
description: Daily standup del equipo - resumen de un vistazo de que hizo cada agente, que esta en progreso, que esta bloqueado y que sigue, a partir de la actividad registrada, los handoffs y el sprint. Solo lectura. Uso - /dev-team:standup [hoy|ayer|--desde {fecha}]
argument-hint: '[hoy | ayer | --desde YYYY-MM-DD]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Standup: el dia del equipo de un vistazo

Periodo: $ARGUMENTS (por defecto hoy)

Resumen operativo, SOLO LECTURA (no cambia estados, no asigna). Responde las tres preguntas del
standup por agente: que hizo, que esta haciendo, que lo bloquea — mas lo que sigue.

## Fuentes (leer, no escribir)
1. `.coordination/metrics/activity.jsonl` — filtrar por el periodo: eventos `task_start`/`task_end`
   (de hooks), `handoff_sent`, `blocked`/`unblocked`, `evidence_added`, `verdict`, `reopened`.
2. `.coordination/handoffs/` (y `archive/`) — handoffs del periodo: quien pidio que a quien, y cuales
   siguen SIN procesar (destinatario no respondio).
3. `.coordination/sprint-actual.md` y `backlog.md` — tareas en curso, su HU y su estado.

## Salida (tabla + bloques, en lenguaje claro)
```
Standup — {fecha} — Sprint {n}
Hecho hoy:
  - {agente}: {tarea/HU} — {evento clave} (evidencia/handoff si aplica)
En progreso:
  - {agente}: {tarea/HU} — desde {cuando}
Bloqueado (atender primero):
  - {agente}: {motivo del blocked} — bloquea a {quien/que} — escalar a {rol}
Handoffs sin procesar:
  - {de} → {para}: {tema} (pendiente hace {tiempo})
Sigue:
  - {lo mas util segun el estado: HUs listas sin asignar, revalidaciones pendientes, gates de merge}
```

## Reglas
- SOLO lectura: no mueve tarjetas, no asigna, no cierra. Si detecta algo accionable (un bloqueo, un
  handoff estancado, un gate pendiente), lo SEÑALA y sugiere el comando (`/dev-team:inbox`,
  `/dev-team:assign-task`, `/dev-team:e2e`), sin ejecutarlo.
- Prioriza los BLOQUEOS: van primero, con a quien afectan y a quien escalar.
- Si no hay actividad registrada en el periodo, decirlo y proponer `/dev-team:status`.
- Lenguaje claro; nada de jerga innecesaria. Un standup se lee en 20 segundos.
