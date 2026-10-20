---
description: Estado del equipo del PO de un vistazo, sin regenerar nada - sprint en curso por etapa del ciclo de pase, proximos hitos y fechas en riesgo, observados y bloqueados, tickets de la Mesa sin refinar, items sin estimar, validaciones y documentos recientes, handoffs pendientes y que conviene hacer ahora. Lee lo ultimo guardado en .po-team/ (no consulta el tracker). Solo lectura. Uso - /po-team:estado [--sprint N]
argument-hint: '[--sprint N] [--pendientes]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica, SIEMPRE con su nombre completo `po-team:{agente}`
> (dev-team y mesa-servicios tambien tienen un agente `setup`: sin prefijo se puede invocar el
> de otro equipo). Al invocar: ruta ABSOLUTA de `.po-team/`, "Pedido del usuario (textual): ..."
> y, si el usuario aprobo un plan, "Autorizacion del usuario: {plan literal}".

# Estado: el equipo del PO de un vistazo

Filtros: $ARGUMENTS

SOLO LECTURA y sin llamadas al tracker (para datos frescos: `/po-team:tablero`). Lee
`.po-team/tablero/tablero-datos.json`, `.po-team/sprints/*.json`, `.po-team/backlog.md`,
`.po-team/tickets/lote-*.json`, `.po-team/handoffs/` (pendientes) y
`.po-team/metrics/activity.jsonl` (pendientes = `esperando_usuario` / `blocked` sin su
`respondido` / `unblocked`), y `.po-team/retros/` (acciones abiertas). Usa la ruta absoluta de la
carpeta canonica (la imprime el hook de sesion; si no, `hooks/coord_root.py`).

## Salida
```
{equipo} — estado al {fecha} (tablero de hace {h} h)
Sprint {N} ({inicio}–{fin}): {pts} pts · Desarrollo {a} · QA {b} · Demo {c} · Validacion {d} · VB {e}
Proximos hitos: Demo {fecha} · Preprod {cliente} {fecha} · VB cliente {fecha}

Atender primero:
  - ⚠ Fecha de Demo {fecha} en riesgo: {n} tickets ({pts}) aun en QA
  - #130 observado en Demo CO hace 2 dias sin devolver → /po-team:refinar --observacion #130
  - #118 bloqueado: {motivo}
  - Esperando respuesta: #131 (Mesa) — 2 preguntas desde el 14/10 (eventos esperando_usuario sin respondido)
  - #152 arreglado por desarrollo, sin revalidar → /po-team:validar --revalidar #152
Listo para el siguiente paso:
  - {n} tickets de la Mesa sin refinar → /po-team:refinar #{n}
  - {n} tickets en Demo sin VB PO → /po-team:validar --lote sprint {N}
  - {n} con VB PO sin acta → /po-team:documento aceptacion #{n}
  - Sprint {N-1} terminado sin cierre → /po-team:sprint cierre {N-1}
  - Acciones abiertas de la ultima retro: {n} ({responsable}: {accion})
Ultima actividad del equipo: {agente} {evento} {hace cuanto}
```
Con `--pendientes` solo la seccion "Atender primero". Si el tablero tiene mas de 24 h, decirlo y
sugerir `/po-team:tablero`.

## Reglas
- Solo lectura; si detecta algo accionable lo SEÑALA con el comando, sin ejecutarlo.
- Se lee en 20 segundos; lo urgente primero.
