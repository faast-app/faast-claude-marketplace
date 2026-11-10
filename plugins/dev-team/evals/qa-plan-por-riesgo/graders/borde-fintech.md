---
type: llm
weight: 3
---

PASA si el plan incluye casos de borde propios de una fintech para esta HU: el limite de
fecha (dia del vencimiento vs dia siguiente), el redondeo distinto por moneda (CLP sin
decimales frente a PEN/COP), la separacion por cliente/tenant (un analista no ve
operaciones de otro cliente) y al menos uno de: feriados o dias habiles por pais, tasa 0 o
monto 0, cambio de mes o año.
FALLA si faltan el limite de fecha, el redondeo por moneda o la separacion por cliente.
