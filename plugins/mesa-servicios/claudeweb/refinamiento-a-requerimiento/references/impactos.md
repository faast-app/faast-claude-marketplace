# Dónde aplica e impactos

Dos preguntas de analista que el filtro siempre resuelve antes de cerrar:

1. **¿Dónde vive lo que cambia?** Todos los lugares del sistema donde se calcula, se muestra, se imprime, se exporta o se envía. Se cambia la fórmula en el botón Calcular, pero también estaba en el botón Recalcular de otra pantalla y en el PDF de liquidación. Si eso no queda escrito, desarrollo cambia uno, QA encuentra los otros y vuelve el ticket.
2. **¿Qué más se ve afectado?** Contabilidad, cobranza, cupos, reportes, integraciones. Cada impacto debe quedar **enumerado y concreto**: qué cambia, dónde y cómo.

## 1. Inventario de puntos de aplicación

Para cada cosa que cambia (una fórmula, un campo, una regla, un estado), arma el inventario de lugares donde existe. Fuentes:

- AS-IS y ficha de contexto del módulo.
- Quien usa el skill, que conoce el sistema: es la fuente principal.
- Desarrollo, en el pedido consolidado, si nadie más lo sabe. Desarrollo puede buscar en el código dónde se usa el cálculo.

Recorre estas categorías:

| Categoría | Ejemplos |
|---|---|
| Pantallas y botones | Simulación (botón Calcular), alta de operación (paso de condiciones), detalle de operación (botón Recalcular), modificación de operación |
| Documentos generados | PDF de liquidación, simulación, comprobante, carta de cesión, contrato, notificación al deudor |
| Reportes y exportaciones | Reportes operativos, exportaciones a Excel, reportes regulatorios |
| Contabilidad | Asientos que usan el valor (ver sección 2) |
| Otros módulos | Cupos, cobranza, desembolso, gastos, mora, prórrogas |
| Canales | Portal de clientes o autoatención, API digital, carga masiva |
| Procesos automáticos | Cierres diarios, devengos, procesos batch nocturnos, recálculos |
| Integraciones | Archivos o servicios hacia bancos, entes tributarios, registros, sistemas del cliente |
| Notificaciones | Correos o mensajes que muestran el valor |

Resultado: la **matriz "Dónde aplica"**, con una fila por lugar y la decisión para cada uno:

| ID | Lugar | Tipo | ¿Cambia? | Detalle | Origen |
|---|---|---|---|---|---|
| IM-01 | Simulación › botón Calcular | Pantalla | Sí | Usa la fórmula nueva | D-02 |
| IM-02 | Detalle de operación › botón Recalcular | Pantalla | Sí | Usa la fórmula nueva | D-02 |
| IM-03 | PDF de liquidación | Documento | Sí | Imprime el valor nuevo; el texto de la fórmula impresa cambia a "…" | D-03 |
| IM-04 | Reporte de cartera | Reporte | No | Muestra el valor ya calculado; no recalcula | [U] |
| IM-05 | Portal de autoatención | Canal | No | Fuera de alcance | D-04 |

Si la estrategia es una **opción nueva que convive**, la funcionalidad actual va como fila propia con "No cambia" ("Venta de Cartera › carga por Excel actual · No cambia · las condiciones siguen siendo por cotización"). Es lo que más tranquiliza al cliente y lo que evita que desarrollo la toque.

Cada fila es una decisión explícita. **"No cambia" también se decide y se escribe**, porque evita que desarrollo lo cambie por las dudas o que el cliente lo reclame después.

**La pregunta al solicitante es cerrada y con la lista:**

```
PR-06 · Alcance · Bloqueante · Para: Solicitante
Esta fórmula hoy se usa en estos lugares. ¿En cuáles debe cambiar?
  1. Simulación, botón Calcular
  2. Detalle de la operación, botón Recalcular
  3. PDF de liquidación
  4. Reporte de cartera
  5. Portal de autoatención
→ Propuesta: 1, 2 y 3 cambian; 4 muestra lo ya calculado; 5 queda fuera.
```

## 2. Impactos por área: qué tiene que quedar escrito

Un impacto está bien escrito cuando desarrollo puede implementarlo sin preguntar. Por área:

### Contabilidad

Una fila por asiento o evento contable afectado:

| ID | Evento | Asiento hoy | Asiento después | Qué cambia | Momento |
|---|---|---|---|---|---|
| IM-06 | Otorgamiento de la operación | Debe: Documentos por cobrar · Haber: Diferencia de precio diferida, por el monto de la diferencia de precio | Igual estructura | Cambia el monto: se usa la diferencia de precio con la fórmula nueva | Al otorgar |
| IM-07 | Devengo diario | Devenga linealmente la diferencia de precio | Devengo según la curva de la fórmula nueva | Cambia el cálculo del devengo | Proceso diario |

Además: reversas y anulaciones, operaciones en curso al activar el cambio, diferencias de redondeo entre el monto operativo y el contable, e impacto tributario (IVA, documentos tributarios). Si nadie en el refinamiento conoce el detalle contable, la pregunta va al área contable, con la tabla propuesta para confirmar.

### Otros módulos

- **Cupos:** ¿consume más o menos cupo?, ¿cuándo?
- **Cobranza:** ¿cambia lo que se cobra o cuándo?
- **Desembolso:** ¿cambia el monto a girar?
- **Gastos:** ¿alguno se calcula sobre el valor que cambia?
- **Mora y prórrogas:** ¿usan el mismo cálculo?

Cada impacto lleva el valor o la regla concreta, no "se ve afectado".

### Reportes y regulatorio

Qué reporte, qué columna y qué valor muestra después. Si es regulatorio, a qué ente va y si el cambio altera lo informado.

### Integraciones

Qué archivo o servicio, qué campo y cómo queda. Si la contraparte debe enterarse o adaptarse, quién se lo comunica.

### Datos existentes y operaciones en curso

- ¿Qué pasa con lo ya calculado? ¿Se mantiene o se recalcula?
- ¿Desde cuándo rige: operaciones nuevas, simulaciones nuevas, todo lo no cursado?

### Otros tenants

Confirma que, con la funcionalidad desactivada, el comportamiento para otros clientes es idéntico al actual.

## 3. Referencias vagas: prohibidas

Una referencia vaga obliga a desarrollo a averiguar qué significa, y esa averiguación es una iteración. Prohibidas:

- "lo previamente definido", "lo ya definido", "lo establecido", "lo vigente";
- "según lo acordado", "como se definió", "como se conversó", "lo de siempre", "el procedimiento habitual";
- "según la normativa", "según la política", sin decir cuál ni qué dice;
- "el impacto contable correspondiente", "los asientos que correspondan";
- "en todos los lugares donde aplique", "donde corresponda".

Cada vez que aparezca una en el insumo o en una respuesta:

1. Pregunta **qué es exactamente**: a quien usa el skill primero, y si no lo sabe, en el pedido consolidado a desarrollo o al área que lo definió.
2. Ubica **dónde está definido**: documento, versión y sección, citado como `[C documento §x]`.
3. **Escribe su contenido** en el requerimiento, no solo la cita. La cita es respaldo; el contenido es lo que desarrollo usa.

"Según lo acordado" se convierte en "según D-04: el redondeo es a pesos, al final del cálculo". "El impacto contable previamente definido" se convierte en las filas IM-06 e IM-07 de la tabla de contabilidad.

## 4. Preguntas de analista (repaso antes de cerrar)

Recorre esta lista contra lo que cambia. Si alguna respuesta no está escrita, falta una pregunta:

- ¿Dónde más se calcula, muestra, imprime, exporta o envía esto?
- ¿Quién usa este dato después: otro módulo, un reporte, contabilidad, un cliente externo?
- ¿Qué pasa con lo que ya existe: operaciones, documentos emitidos, saldos?
- ¿Desde cuándo rige y para qué operaciones?
- ¿Qué pasa si se anula, se revierte o se modifica después?
- ¿Cambia algo que el cliente final o el deudor ve?
- ¿Hay otro canal por donde entre lo mismo con otra lógica: portal, API, carga masiva?
- ¿Hay un proceso automático que lo use: devengo, cierre, batch?
- ¿Algún otro cliente usa esto mismo y no debe cambiar?
- ¿Cada referencia del tipo "lo definido" o "lo acordado" está resuelta y escrita?
