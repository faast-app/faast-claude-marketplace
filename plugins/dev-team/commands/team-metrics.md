---
description: Dashboard del Lead - productividad y consumo de tokens por agente. Quien trabaja mas, que hace cada uno ahora mismo, cuanto consume cada agente y en que modelo corre. Soporta modo live (--watch).
argument-hint: "[--watch] [--sprint | --semana | --todo]"
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


Genera el dashboard de desempeño del equipo de agentes. Lo ejecuta el `lead`.

Argumentos: $ARGUMENTS (default: periodo del sprint actual; `--watch` = modo live)

## Fuentes de datos (usar todas las disponibles)

### 0. Event log — fuente PRIMARIA
`.coordination/metrics/activity.jsonl`: cada agente registra por protocolo sus
eventos (`task_start`, `task_end`, `handoff_sent`, `blocked`, ...). De aqui sale
directo: tareas completadas, lead time real (task_start → task_end), bloqueos y
su duracion, y quien esta activo ahora mismo. Es la misma fuente que alimenta la
oficina virtual (`/dev-team:team-office`). Las fuentes siguientes complementan o
sirven de fallback si el log esta incompleto.

### 1. Productividad — artefactos de coordinacion
- **Handoffs:** parsear `.coordination/handoffs/` y `archive/` — los nombres
  `{from}-to-{to}-{timestamp}.md` dan: quien entrega trabajo, a quien, y cuando.
  Contar por agente: entregas realizadas, tareas recibidas, pendientes sin procesar.
- **Sprint y backlog:** `.coordination/sprint-actual.md` y `backlog.md` — tareas
  asignadas vs completadas por agente.
- **Git:** en cada repo/carpeta de servicio, `git log --since={periodo}` agrupando
  por convencion de branch (`feature/BACK-*` → backend, `test/*` → qa,
  `fix/*-{agente}-*`) y por scope del commit (`feat(servicio):`, `test(e2e):`,
  `feat(db/...)` → dba). Contar commits, archivos tocados, lineas +/-.
- **Ciclo:** tiempo entre el handoff de asignacion del Lead y el handoff de
  completado del agente (lead-to-X → X-to-lead) = lead time por tarea.

### 2. Consumo de tokens — transcripts de Claude Code
Las sesiones viven en `~/.claude/projects/{carpeta-del-proyecto}/*.jsonl`. Cada
mensaje del asistente trae `message.usage` (input_tokens, output_tokens,
cache_read_input_tokens) y las invocaciones de subagentes traen el `subagent_type`
en el input de la herramienta Task. Con un script Python:
1. Recorrer los .jsonl del proyecto (filtrar por mtime segun el periodo)
2. Atribuir los mensajes sidechain (`isSidechain: true`) al agente de la invocacion
   Task que los origino (por `sessionId`/orden temporal)
3. Sumar por agente: input, output, cache reads, nº de invocaciones
4. Estimar costo con la tarifa del modelo de cada agente (leer el `model` del
   frontmatter de cada agente del plugin: haiku < sonnet < opus)
Si los transcripts no estan disponibles, reportarlo como "sin datos de tokens" —
NUNCA inventar cifras.

## Salida (tabla ranking)

```
# Metricas del equipo — {periodo}

| Agente | Modelo | Tareas ✅ | Handoffs out/in | Commits | Lead time prom | Tokens in/out | Costo est. |
|--------|--------|----------|-----------------|---------|----------------|---------------|-----------|
| backend | sonnet | 5 | 7 / 6 | 23 | 3.2h | 1.2M / 85k | $X.XX |
| ...ordenado por tareas completadas... |

## Ahora mismo (actividad reciente, ultimos 30 min)
- {agente}: {ultimo handoff / branch con commits recientes / sesion activa}

## Alertas
- {agente} tiene N handoffs sin procesar hace > 1 dia
- {agente} consume {X}% de los tokens con {Y}% de las tareas — revisar si su
  modelo asignado es el correcto (optimizacion de costo)
```

## Modo live (`--watch`)
Repetir cada 30-60 segundos, mostrando solo deltas:
- Handoffs nuevos en `.coordination/handoffs/` (quien acaba de entregar/recibir)
- Branches con commits en los ultimos minutos (`git log --since="2 minutes ago"`)
- Sesiones .jsonl modificadas recientemente (= agente ejecutando ahora)
Salir cuando el usuario lo pida (Ctrl+C o "stop").

## Reglas
- Datos reales o "sin datos" — NUNCA estimar sin fuente
- No interrumpir el trabajo de los agentes para medir (solo lectura)
- Cerrar con 1-3 recomendaciones accionables (rebalancear carga, bajar/subir el
  modelo de un agente, handoffs estancados)
