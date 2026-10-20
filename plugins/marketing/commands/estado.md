---
description: Estado del equipo de Marketing de un vistazo - campanas por estado (brief, desglose, mapa y fichas aprobados, produccion, revision, esperando aprobacion, entregadas), piezas por campana (video keynote y clips, deck, one-pager, panfletos, redes) con su version y aprobacion, pendientes del usuario, bloqueos, kit de marca y tendencias vencidas, y que conviene hacer ahora. Solo lectura. Uso - /marketing:estado [--campana CMP-...] [--esperando]
argument-hint: '[--campana CMP-...] [--esperando] [--piezas]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su procedimiento en
> la sesion actual. NUNCA lo corras dentro de un subagente ni lo invoques via Agent/Task. Solo se
> delegan los AGENTES del equipo, y unicamente cuando este procedimiento lo indica.

# Estado: Marketing de un vistazo

Filtros: $ARGUMENTS

SOLO LECTURA: no cambia estados, no asigna, no produce. Lee `.marketing/campanas/*/estado.json`,
`aprobaciones.md`, `.marketing/handoffs/` (pendientes), `.marketing/metrics/activity.jsonl`
(`esperando_usuario`, `approval_requested`, `blocked` sin cierre), `.marketing/marca/kit.md` y
`.marketing/tendencias/INDEX.md`.

## Salida
```
Marketing — {fecha} · {ruta absoluta de .marketing}
Campanas: brief {n} · desglose {n} · fichas aprobadas {n} · produccion {n} · esperando aprobacion {n} · entregadas {n}

Atender primero:
  - {ID} — esperando aprobacion de {pieza v{N}} hace {d} dias → mostrarla al usuario
  - {ID} — BLOQUEADO: {motivo} → {accion}
  - {ID} — mapa sin aprobar hace {d} dias

Por campana:
  | ID | Producto / publico | Estado | Partes | Video (keynote / clips) | Deck | One-pager | Redes | Siguiente |
  |----|---|---|---|---|---|---|---|---|

Marca: kit {cargado AAAA-MM-DD | pendiente} · {n} pendientes de marca
Tendencias: {n} vigentes · {n} vencidas → /marketing:tendencias refrescar
```
Con `--esperando` solo lo que espera al usuario, ordenado por dias; con `--campana`, el detalle de una
campana (piezas, versiones, aprobaciones con fecha, pendientes); con `--piezas`, la lista de archivos
entregados.

## Reglas
- Solo lectura. Si detecta algo accionable, lo SEÑALA con el comando sugerido, sin ejecutarlo.
- Lo que espera al usuario y los bloqueos van primero. Se lee en 20 segundos.
