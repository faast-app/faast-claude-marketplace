---
description: El planificador arma o ajusta el sprint segun capacidad (puntos o velocidad), propone el orden con un metodo visible y saca lo que no cumple la Definition of Ready (sin HU, con pendientes, sin entrega, demasiado grande), fija las fechas de pase del ciclo FaaST (Demo, Preprod, VB cliente) y detecta riesgos; con tu OK asigna el sprint y las fechas en el Project. Al cerrar, hace la review y la retro desde los datos con acciones con responsable. Uso - /po-team:sprint [planificar N | replanificar | fechas | riesgos | cierre N]
argument-hint: '[planificar {N} | replanificar | fechas | riesgos | cierre {N}] [--capacidad {pts}]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica, SIEMPRE con su nombre completo `po-team:{agente}`
> (dev-team y mesa-servicios tambien tienen un agente `setup`: sin prefijo se puede invocar el
> de otro equipo). Al invocar: ruta ABSOLUTA de `.po-team/`, "Pedido del usuario (textual): ..."
> y, si el usuario aprobo un plan, "Autorizacion del usuario: {plan literal}".

# Sprint: compromiso realista con fechas de pase

Pedido: $ARGUMENTS (por defecto `planificar` del proximo sprint)

## Paso 1 — Propuesta (agente `po-team:planificador`)
- **planificar {N}**: capacidad (config o velocidad, la menor), candidatos por prioridad + lo que
  viene del sprint anterior, filtro de preparacion (sin HU, sin entrega, muy grande, sin estimar,
  bloqueado), objetivo del sprint, fechas del ciclo y riesgos.
- **replanificar**: intercambio explicito (entra X, sale Y) y ajuste de fechas.
- **fechas**: solo fechas de pase del sprint en curso (respetando pases en lote).
- **riesgos**: solo deteccion (solo lectura).
- **cierre {N}**: review (comprometido vs logrado por etapa, objetivo, fechas comprometidas vs
  reales, observados, bloqueos, velocidad) + retro desde los datos con maximo 3 acciones con
  responsable; revisa primero las acciones de la retro anterior. Solo lectura sobre el tracker:
  escribe `.po-team/retros/retro-sprint-{N}.md` y marca el sprint cerrado (no requiere el OK de
  escritura en el tracker; si se muestra antes de guardar).
`--capacidad` fuerza la capacidad para esta vez (se anota en el json del sprint).

## Paso 2 — Plan y aprobacion
Mostrar la propuesta (formato del planificador) y lo que se escribira en el tracker. **Esperar el OK.**
Si el PO cambia algo, se ajusta y se vuelve a mostrar.

## Paso 3 — Escribir
Con el OK: asignar sprint/iteracion (y fechas si hay campos), guardar
`.po-team/sprints/sprint-{N}.json`. Si hubo items "sin HU", ofrecer `/po-team:refinar` para ellos.

## Paso 4 — Entrega
Resumen de 4 lineas + sugerencia: `/po-team:tablero` para ver el sprint en el dashboard.

## Reglas
- Nunca mas puntos que la capacidad sin decision explicita; fechas en el orden del ciclo.
- Solo entra lo que cumple la Definition of Ready; el orden se propone con metodo visible y lo
  decide el PO.
- Nada en el tracker sin OK. `riesgos` y `fechas` sin cambios son solo lectura.
