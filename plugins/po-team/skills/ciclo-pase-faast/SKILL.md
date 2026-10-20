---
name: ciclo-pase-faast
description: El ciclo de pase FaaST que el equipo del Product Owner (po-team) acompaña por ticket y por sprint - Desarrollo -> Validacion QA -> Pase a Demo (Demo de cada pais) -> Validacion Demo / Preprod de cliente -> VB cliente, con el criterio de entrada y de salida de cada etapa, quien mueve cada estado (desarrollo, QA humana, PO, cliente), los estados reservados a QA, el tratamiento de Observado y Bloqueado, pases en lote, fechas comprometidas, como se mapea cada etapa a los estados y etiquetas del Project segun el config, y que hace el PO en cada paso. Cargala al planificar, al hacer seguimiento, al validar o al decidir que sigue con un ticket.
---

# Ciclo de pase FaaST (po-team)

Cada ticket (HU o bug) y cada sprint recorre cinco etapas. El PO no programa ni prueba como QA:
**acompaña** el ticket, fija fechas, detecta lo que se atrasa, valida rapido lo funcional y
consigue el VB del cliente. Los nombres exactos de estados, ambientes y clientes salen de
`.po-team/config.json` (`ciclo.etapas`, `ambientes`, `clientes`); nada de lo que sigue asume un
valor concreto.

```
 Desarrollo ──► Validacion QA ──► Pase a Demo ──► Validacion Demo / Preprod ──► VB cliente
     ▲                │                 │                    │                       │
     └──── Observado ◄┴─────────────────┴────────────────────┴───────────────────────┘
```

## Las etapas
| # | Etapa (`clave`) | Entra cuando | Sale cuando (criterio de paso) | Quien mueve el estado | Que hace el PO |
|---|---|---|---|---|---|
| 1 | Desarrollo (`desarrollo`) | La HU esta lista (criterios Gherkin, estimada, en el sprint) | El equipo de desarrollo marca el estado de "resuelto" del config (`tracker.reglas.estadoAlResolver`) y lo despliega en el ambiente de QA | Equipo de desarrollo | Responde dudas funcionales; no reescribe la HU dentro del sprint sin avisar |
| 2 | Validacion QA (`qa`) | Desplegado en el ambiente de QA | QA humana deja su veredicto con evidencia y mueve al estado reservado (`tracker.reglas.estadosSoloQA`) | **Solo QA humana** | Puede adelantar una validacion funcional rapida (validador-po) para detectar observaciones temprano, **sin reemplazar a QA ni mover estados de QA** |
| 3 | Pase a Demo (`demo`) | Validado por QA | El pase al Demo correspondiente esta ejecutado (fecha registrada) | Equipo de desarrollo / release | Fija la fecha de pase con el planificador; confirma que entra al lote |
| 4 | Validacion Demo / Preprod (`validacion`) | Desplegado en Demo (y en Preprod del cliente si aplica) | VB PO en el Demo con evidencia; si el cliente tiene Preprod, desplegado y validado ahi | PO (VB PO) | El validador-po recorre los criterios en Demo/Preprod; veredicto VB PO u Observado |
| 5 | VB cliente (`vb`) | VB PO dado y cliente notificado | El cliente da su visto bueno (quien, cuando, por que medio) y se registra; acta de aceptacion si corresponde | PO, con la confirmacion del cliente | Prepara el acta (documentador), registra el VB en el ticket |

## Reglas de estados
- **Estados reservados a QA** (`tracker.reglas.estadosSoloQA`): ningun agente del po-team los
  asigna. El VB PO es otra cosa y se registra con su etiqueta (`tracker.etiquetas.vbPO`) y un
  comentario con evidencia.
- **Cerrar issues**: solo si `tracker.reglas.cerrarIssues` es `true` y el usuario lo confirma.
  Mover a un estado de `tracker.reglas.estadosFinales` (Done, Cerrado) cuenta como cerrar.
  Por defecto, nunca se cierra: el VB cliente se registra con etiqueta/estado y comentario.
- **Observado** (en cualquier etapa): el ticket vuelve a Desarrollo. Si la observacion esta
  dentro del alcance de la HU → comentario en el MISMO ticket con evidencia y el estado
  `ciclo.estadosObservado`; si es otra cosa → bug nuevo relacionado (redactado por el refinador).
  En el tablero el ticket se ve rojo, en la etapa donde se observo.
- **Bloqueado**: falta un ambiente, un acceso, un dato o una decision. Se registra el motivo y el
  responsable de destrabar; el seguimiento lo lista primero.
- **Sin movimiento**: un ticket que no cambia de etapa en `ciclo.diasAlertaSinMovimiento` dias
  habiles se alerta como riesgo.

## Pases en lote
Un ambiente con `paseEnLote: true` (config `ambientes.demo[]`) **no** recibe cada correccion apenas
se termina: se acumulan y se pasan juntas en una fecha. El planificador propone esa fecha de lote
y el seguimiento muestra que tickets esperan el lote. Nunca se pide un pase individual a esos
ambientes.

## Fechas comprometidas (por sprint)
El planificador fija, por sprint: fecha de pase a Demo (por pais si difiere), fecha de Preprod
por cliente (si aplica) y fecha objetivo de VB cliente. Viven en
`.po-team/sprints/sprint-{N}.json` → `fechas` y, si el Project tiene campos de fecha
(`projects[].campos.fechaDemo|fechaPreprod|fechaVB`), tambien ahi. Una fecha pasada con tickets
que no llegaron a esa etapa = **fecha vencida** (riesgo alto en el tablero).

## Como se refleja en el tablero
Cada etapa del config tiene `estados` (opciones del campo Status del Project) y/o `etiquetas`.
Para ubicar un ticket en una etapa:
1. Si tiene una etiqueta de alguna etapa, gana la etapa MAS AVANZADA cuyas etiquetas tenga.
   Por eso las etiquetas del PO son excluyentes y se mantienen limpias: publicar un Observado
   QUITA `vbPO`; publicar un VB PO quita `observadoPO`; `vbPO` solo se pone por validacion en
   Demo/Preprod (nunca por una adelantada en Desa/QA).
2. Si no, la etapa cuyo listado `estados` contiene su Status.
3. Si su Status esta en `ciclo.estadosObservado` **o** tiene la etiqueta
   `tracker.etiquetas.observadoPO` → marca Observado (etapa = donde estaba).
4. Si esta en `ciclo.estadosBloqueado` → marca Bloqueado.
5. Si no calza en nada → "Sin etapa" (se reporta para corregir el mapeo, no se adivina).
El stepper del dashboard (skill `dashboard-po`) muestra las cinco etapas con los puntos que ya
alcanzaron cada una.

## Que NO hace el PO en el ciclo
- No mueve estados de QA, no aprueba en nombre de QA, no reemplaza la prueba formal.
- No ejecuta pases ni scripts (eso es del equipo de desarrollo / release).
- No cierra tickets por su cuenta.
- No promete fechas al cliente que el planificador no valido contra capacidad.
