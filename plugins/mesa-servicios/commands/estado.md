---
description: Estado de la Mesa de un vistazo - solicitudes por estado (recibidas, en analisis, esperando cliente, en prototipo, en reproduccion, documentadas, registradas, pendientes de aprobacion comercial), cuanto llevan esperando, bloqueos, y que conviene hacer ahora. Solo lectura. Uso - /mesa-servicios:estado [--cliente CODIGO] [--tipo bug|proyecto|cotizacion] [--esperando]
argument-hint: '[--cliente ACME] [--tipo bug|proyecto|cotizacion] [--esperando] [--desde YYYY-MM-DD]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Estado: la Mesa de un vistazo

Filtros: $ARGUMENTS

SOLO LECTURA: no cambia estados, no asigna, no registra. Lee `.mesa/solicitudes/*/estado.json`,
`.mesa/backlog.md`, `.mesa/handoffs/` (pendientes) y `.mesa/metrics/activity.jsonl`.

## Salida
```
Mesa de Servicios — {fecha}
Por estado:  recibidas {n} · en analisis {n} · esperando cliente {n} · en prototipo {n} · en reproduccion {n}
             documentadas {n} · registradas {n} · pendientes aprobacion comercial {n}

Atender primero (bloqueos y esperas largas):
  - {ID} {titulo} — esperando cliente hace {d} dias (ronda {N}) → recordar via mesa
  - {ID} {titulo} — BLOQUEADO: {motivo} → escalar a {rol}
  - {ID} (CTZ) — pendiente de aprobacion comercial hace {d} dias

En curso:
  | ID | Tipo | Alcance | Titulo | Estado | Desde | Responsable | Ticket |
  |----|------|---------|--------|--------|-------|-------------|--------|

Listas para el siguiente paso:
  - documentadas sin ticket: {IDs} → /mesa-servicios:ticket
  - registradas sin ingest al brain: {IDs} → /mesa-servicios:brain ingest --pendientes
  - cerradas sin documento: {IDs} → /mesa-servicios:documento

Brain: {n} paginas · ultimo ingest {fecha} · {n} solicitudes sin ingerir
```
Con `--esperando` solo las que esperan al cliente, ordenadas por dias. Con `--cliente` /
`--tipo`, filtradas.

## Reglas
- Solo lectura. Si detecta algo accionable, lo SEÑALA con el comando sugerido, sin ejecutarlo.
- Los bloqueos y las esperas largas van primero.
- Lenguaje claro; se lee en 20 segundos.
