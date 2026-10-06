# Casuísticas y adjuntos

## Principio: el descubrimiento lo hace quien levanta el requerimiento

Si el solicitante dice "ajusten la fórmula" y manda un Excel de 20 hojas, alguien tiene que abrirlo, encontrar la fórmula, ubicarla en el sistema y confirmar con el cliente que es esa. Ese trabajo lo hace **quien levanta el requerimiento**, con el skill, antes de que el ticket llegue a desarrollo. Si llega a desarrollo sin hacer, cuesta días de idas y vueltas que una pregunta bien hecha resolvía.

Reglas:

- **Ningún adjunto pasa sin interpretar.** "Ver Excel adjunto", "según archivo", "como en la planilla" no son requerimiento. El contenido relevante del adjunto se extrae y se escribe en el documento; el adjunto queda como respaldo.
- **Todo cambio queda anclado**:
  - **dónde** ocurre en el sistema (menú › pantalla › sección › botón o campo), con captura marcada cuando hay pantalla;
  - **cómo es hoy**;
  - **cómo queda**;
  - **ejemplo numérico** con los dos resultados.
- **Las candidatas se confirman con una pregunta cerrada**: "Encontramos cuatro fórmulas; entendemos que es la de la hoja Cálculo, columna Diferencia de precio. ¿Es esa?" Nunca "¿cuál es la fórmula?".
- **Los ejemplos numéricos se calculan con código, nunca a mano.** Se convierten en criterios de aceptación: un valor mal calculado hace que desarrollo implemente bien y QA lo rechace, o al revés. Calcula hoy y después con un script, con el redondeo decidido, y si hay Excel del cliente compara contra sus valores.
- **El adjunto del cliente es un oráculo de prueba.** Si el Excel calcula el resultado que el cliente espera, sus valores son los criterios de aceptación: el sistema debe reproducirlos.

## Bloque "Qué cambia exactamente"

Va en los dos documentos, casi igual. En la propuesta, el cliente confirma "sí, es esto". En la especificación, desarrollo sabe exactamente qué tocar.

```
### Cambio 1 — [nombre corto]

**Dónde:** Operaciones › Simulación › botón Calcular → campo "Diferencia de precio"
![Ubicación del cambio](img/cambio-1.png)

**Hoy:**  Diferencia de precio = Monto × Tasa mensual ÷ 30 × Días
**Después:**  Diferencia de precio = Monto × ((1 + Tasa mensual) ^ (Días ÷ 30) − 1)

| Variable | Qué es en el sistema |
|---|---|
| Monto | Monto total de los documentos de la operación |
| Tasa mensual | Tasa pactada, en porcentaje mensual |
| Días | Días entre la fecha de giro y el vencimiento del documento |

**Ejemplo** (con los valores del Excel del cliente, hoja Cálculo, fila 2):

| Monto | Tasa | Días | Hoy | Después |
|---|---|---|---|---|
| 2.000.000 | 1,5 % | 32 | 32.000 | 32.000 → [valor calculado] |

**Redondeo:** [a pesos, al final del cálculo · por documento antes de sumar]
**Aplica a:** [operaciones nuevas desde la activación · también a simulaciones · no recalcula operaciones existentes]
```

En la propuesta se omiten los IDs y la tabla de variables puede ir en prosa. En la especificación cada fórmula es además una regla `RN-xx` y cada fila del ejemplo un criterio `CA-xx`.

## Casuísticas: qué hay que determinar en cada tipo

Identifica la casuística en la Fase 1. Determina el tipo de requerimiento y, con él, qué debe quedar resuelto antes de cerrar. Un requerimiento puede combinar varias.

### Cambio menor (etiqueta, texto, mensaje, orden, valor por defecto)

- Texto o valor actual y nuevo, **exactos**, con mayúsculas y signos.
- Dónde, con captura marcada.
- **Todos los lugares donde aparece**: otras pantallas, PDF y comprobantes, reportes y exportaciones, correos, portal, otros países o idiomas. Una etiqueta casi nunca vive en un solo lugar.
- Si el texto es configurable por tenant o fijo para todos.
- Va en la ficha única `assets/plantilla-cambio-menor.md`.

Si al refinar aparece una regla, un cálculo o un flujo, deja de ser cambio menor: reclasifica a cambio funcional.

### Cálculo o fórmula

- Ubicación exacta: pantalla, botón que dispara el cálculo, campo donde se muestra el resultado y documentos donde se imprime (liquidación, simulación, comprobante).
- Fórmula actual y fórmula nueva, explícitas, con cada variable definida como dato del sistema.
- Base de cálculo: sobre qué monto, qué fechas, días corridos o hábiles, base 30 o 360/365.
- Redondeo: dónde y cómo (por línea o total, a qué decimal, por moneda).
- Momento: cuándo se calcula y si se recalcula.
- Alcance temporal: operaciones nuevas, simulaciones, o también existentes.
- Otros lugares que usan el mismo cálculo (reportes, contabilidad, portal, API) y si deben cambiar igual.
- Ejemplo con valores reales del cliente, con resultado de hoy y de después; si el cliente mandó Excel, sus valores son el oráculo.

**Si llega un Excel**: corre `scripts/extraer_formulas.py` (con `--buscar` usando las palabras del pedido), ubica las candidatas y arma la pregunta cerrada con la candidata más probable y las alternativas. Si el Excel no tiene valores calculados, recalcúlalo con el skill `xlsx`.

### Pantalla, campo o formulario

- Pantalla y ubicación exacta, con captura marcada.
- Campo: nombre visible, tipo, obligatorio, valor por defecto, validación y mensaje de error exacto.
- Quién lo ve y quién lo edita.
- Dónde más aparece el dato (detalle, reportes, exportaciones, comprobantes).
- Datos existentes: qué valor toman los registros que ya existen.

### Reporte o exportación

Va en la sección **Definición del reporte** de la especificación.

- Para qué se usa: qué decisión o tarea apoya. Evita columnas que nadie usa.
- Nombre, dónde se genera y quién lo usa.
- Columnas en orden, con nombre, origen del dato (pantalla o concepto del sistema) y formato.
- Filtros, orden y agrupaciones; totales.
- Formato de salida (Excel, PDF, CSV) y periodicidad si es programado.
- Si sale del sistema (correo, carpeta compartida, envío programado) o contiene datos personales: quién lo recibe, si el destinatario es interno o externo y si hay datos que deban omitirse o enmascararse. Es protección de datos, no un detalle técnico.
- Ejemplo: si el cliente mandó un modelo, su estructura es el criterio de aceptación columna por columna.

### Archivo o integración

- Sentido (entrada o salida), contraparte, formato y layout campo por campo (posición o columna, largo, tipo, relleno).
- Nombre de archivo, codificación, separador, encabezado y totales de control.
- Momento y disparador.
- Qué pasa con errores: rechazo total, parcial y cómo se informa.
- Archivo de ejemplo real como criterio de aceptación.

### Parámetro o mantenedor

- Qué controla, nivel (tenant, producto, cliente, país), valor por defecto y rango válido.
- Quién lo mantiene y si queda auditado.
- Efecto en operaciones en curso al cambiar el valor.

### Flujo, estado o aprobación

- Estados y transiciones, quién ejecuta cada una y con qué condición.
- Niveles de aprobación, montos o reglas que los activan.
- Notificaciones de cada paso.
- Qué pasa con los registros que están en estados intermedios al activar el cambio.

### Funcionalidad nueva

El flujo completo del skill, con todas las secciones de la plantilla. Suele combinar varias casuísticas (pantallas, reglas, reportes, integraciones); cada parte se resuelve según su casuística. Si es grande, conviene separar entregas en varios issues, con la propuesta como visto bueno común.

### Error (bug)

No se refina como requerimiento: se documenta en el formato de bugs del equipo (`references/formato-bug.md`).

## Capturas de pantalla

- Pídele al usuario la captura de la pantalla donde ocurre el cambio: la conoce y la obtiene en segundos. Si no la tiene, la ubicación escrita (menú › pantalla › campo) es obligatoria igual.
- Márcala con `scripts/anotar_captura.py`: recuadro y flecha sobre el elemento, con un rótulo numerado que coincide con el número del cambio. Revisa la salida y ajusta las coordenadas o la posición del rótulo si tapa algo relevante.
- Guarda las imágenes en `img/` junto a los documentos y enlázalas desde el bloque del cambio.
