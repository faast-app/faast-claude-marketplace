---
description: El planificador arma o ajusta el sprint segun capacidad (puntos o velocidad), propone sacar lo que no tiene HU, entrega definida o es demasiado grande, fija las fechas de pase del ciclo FaaST (Demo, Preprod, VB cliente) y detecta riesgos; con tu OK asigna el sprint y las fechas en el Project. Uso - /po-team:sprint [planificar N | replanificar | fechas | riesgos]
argument-hint: '[planificar {N} | replanificar | fechas | riesgos] [--capacidad {pts}]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Sprint: compromiso realista con fechas de pase

Pedido: $ARGUMENTS (por defecto `planificar` del proximo sprint)

## Paso 1 — Propuesta (agente `planificador`)
- **planificar {N}**: capacidad (config o velocidad, la menor), candidatos por prioridad + lo que
  viene del sprint anterior, filtro de preparacion (sin HU, sin entrega, muy grande, sin estimar,
  bloqueado), objetivo del sprint, fechas del ciclo y riesgos.
- **replanificar**: intercambio explicito (entra X, sale Y) y ajuste de fechas.
- **fechas**: solo fechas de pase del sprint en curso (respetando pases en lote).
- **riesgos**: solo deteccion (solo lectura).
`--capacidad` fuerza la capacidad para esta vez (se anota en el json del sprint).

## Paso 2 — Plan y aprobacion
Mostrar la propuesta (formato del planificador) y lo que se escribira en el tracker. **Esperar el OK.**
Si el PO cambia algo, se ajusta y se vuelve a mostrar.

## Paso 3 — Escribir
Con el OK: asignar sprint/iteracion (y fechas si hay campos), guardar
`.po-team/sprints/{sprint}.json`. Si hubo items "sin HU", ofrecer `/po-team:refinar` para ellos.

## Paso 4 — Entrega
Resumen de 4 lineas + sugerencia: `/po-team:tablero` para ver el sprint en el dashboard.

## Reglas
- Nunca mas puntos que la capacidad sin decision explicita; fechas en el orden del ciclo.
- Nada en el tracker sin OK. `riesgos` y `fechas` sin cambios son solo lectura.
