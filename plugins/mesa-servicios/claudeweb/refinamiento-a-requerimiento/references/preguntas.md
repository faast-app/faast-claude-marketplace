# Cómo formular las rondas de preguntas

El objetivo es cerrar vacíos con el menor esfuerzo posible para quien responde, que muchas veces responde por dictado de voz. Una buena pregunta se contesta con "sí", "no" o "la B".

## Formato de cada pregunta

```
**PR-04 · Reglas de negocio · Bloqueante · Para: Solicitante**
¿El monto del adelanto se descuenta del cupo del cliente al solicitarlo o al aprobarlo?
→ Por qué importa: define si dos solicitudes simultáneas pueden superar el cupo.
→ Propuesta: al solicitarlo (reserva), y se libera si se rechaza.
   A) Al solicitar (propuesta)  B) Al aprobar  C) Otro
```

Elementos:
- **ID estable** `PR-xx`. No se reutiliza.
- **Tema** (alcance, actores, flujo, reglas, datos, estados, integraciones, contabilidad, borde, no funcional).
- **Severidad**: `Bloqueante` (cambia alcance, reglas o impactos) o `Detalle`.
- **Destinatario**, en este orden de preferencia:
  - `Usuario`: quien usa el skill; responde en la conversación sobre cómo funciona hoy el sistema.
  - `Solicitante`: qué quiere el negocio.
  - `Otra área`: contabilidad, riesgo, legal, operaciones u otra área del cliente o de FaaST, para lo que les compete (por ejemplo, los asientos contables). Va en un pedido consolidado a esa área.
  - `Desarrollo`: solo lo que nadie más sabe y cambia una regla o el alcance; va al pedido consolidado.

  Al solicitante nunca se le pregunta cómo funciona el sistema.
- **Pregunta cerrada** cuando se pueda. Si es abierta, que sea específica.
- **Por qué importa**: una línea, qué se rompe o cambia.
- **Propuesta por defecto**: tu recomendación fundamentada en el insumo y en prácticas comunes del dominio. Marca cuál es.

## Presentación de una ronda

```
### Ronda 2 — 6 preguntas (3 bloqueantes)
Cerradas: 9 · Abiertas: 6

#### Para el solicitante
**Reglas de negocio**
PR-10 …
PR-11 …
**Casos de borde**
PR-12 …

#### Para ti (sistema actual)
PR-13 Entendemos que hoy … ¿Correcto?

#### Para contabilidad (va en un pedido a esa área)
PR-14 Proponemos que el asiento de otorgamiento cambie así: … ¿Correcto?

#### Para desarrollo (va al pedido consolidado, no bloquea lo demás)
PR-15 …

Puedes responder en bloque, por ejemplo: "PR10 sí, PR11 la B, PR12 decide tú".
```

## Qué preguntar y qué no

Pregunta cuando:
- La transcripción tiene dos posturas y no se ve cuál ganó.
- El insumo dice "según corresponda", "lo de siempre", "como ahora" sin decir qué es eso.
- Un caso de borde probable no tiene comportamiento definido.
- Falta país, producto, moneda o tenant y eso cambia la regla.
- El usuario final propuso un "cómo" y no está claro si es requisito o sugerencia.

No preguntes cuando:
- El insumo ya lo responde (cita la evidencia y sigue).
- Es una decisión técnica: va a "Para resolver por desarrollo" (`PT-xx`), no al solicitante.
- La respuesta no cambia ninguna regla, dato, flujo ni criterio de aceptación.

## Preguntas de encuadre

Algunas preguntas cambian la forma de todo el requerimiento. Se hacen **primero y solas**, en una ronda corta de 1 a 3 preguntas, antes de la ronda completa:

- **¿Modificar lo existente o crear algo nuevo?** (opción nueva que convive, o extender con un modo o parámetro)
- ¿Los datos o documentos ya existen en el sistema, o el requerimiento también los crea?
- ¿Es un requerimiento o son varios que se pueden entregar por separado?

Ejemplo real: un pedido de carga masiva de Venta de Cartera con condiciones por documento. Hoy las condiciones son por cotización.

```
PR-01 · Encuadre · Bloqueante · Para: Solicitante
Hoy Venta de Cartera ya tiene carga por Excel, pero las condiciones (tasa, comisión, gastos)
son las mismas para toda la cotización. Lo que piden trae condiciones distintas por documento.
¿Cómo lo quieren?
→ Por qué importa: si se modifica la opción actual, cambia para todos los que la usan y hay
  que ajustar simulación, nómina y contabilidad; si es una opción nueva, lo actual queda igual.
→ Propuesta: B, porque el pedido dice "no se deben perder las funcionalidades actuales,
  solo agregar la carga masiva".
   A) Modificar la opción actual  B) Nueva opción de carga masiva que convive con la actual (propuesta)
   C) Extender la opción actual con un modo "condiciones por documento"
```

Con la respuesta, recién se arma la ronda completa. Los choques que dependían de modificar lo actual se descartan, y las preguntas pasan a ser sobre las reglas de la opción nueva.

## Preguntas apoyadas en el AS-IS

Cuando el AS-IS describe el comportamiento actual, la pregunta al solicitante no es "¿cómo quiere que funcione?", sino "¿se mantiene o cambia?":

```
**PR-05 · Reglas de negocio · Bloqueante · Para: Solicitante**
Hoy los gastos se calculan una sola vez al pasar al paso de gastos, y si después se agregan
documentos no se recalculan [A §5]. Con tramos, la operación podría cambiar de tramo.
¿Se mantiene el cálculo único?
→ Por qué importa: define si hay recálculo automático.
→ Propuesta: mantener el cálculo único y que el ejecutivo ajuste a mano.
   A) Mantener (propuesta)  B) Recalcular hasta el envío a aprobación
```

Cuando el pedido choca con algo que otros clientes usan o con una parametrización por tenant, dilo en la pregunta: el solicitante debe saber que su cambio se activará solo para él.

## Contradicciones en transcripciones

Muestra ambas posturas con su evidencia y pide la decisión:

```
**PR-07 · Flujo · Bloqueante**
En la reunión hay dos posturas sobre quién aprueba:
- [T 12:40 – Ana] "lo aprueba el jefe comercial"
- [T 31:05 – Pedro] "debería pasar por riesgo"
¿Cuál quedó?  A) Comercial  B) Riesgo  C) Ambos en secuencia  D) Depende del monto (indica umbral)
```

## Mensaje para pendientes externos

Cuando la respuesta depende de otra persona o área, ofrece un mensaje listo para enviar: contexto en 2 líneas, preguntas numeradas con las mismas `PR-xx`, opciones propuestas y para qué fecha se necesita la respuesta (si el usuario la indicó). Mantener los mismos IDs permite reincorporar la respuesta sin reinterpretarla.

## Validación previa de la especificación

Con las preguntas cerradas y antes de escribir los documentos, presenta lo que **tuviste que decidir tú** para completar el documento (no lo que es transcripción de decisiones). Formato:

```
Para validar la especificación te separo lo que tuve que decidir yo:

**Comportamiento en ejecución**
1. **Solape de tramos.** Puse: se aplica el primero por orden de "desde".
   Alternativa: no proponer el gasto. Recomiendo la primera; el preview lo advierte igual.
2. …

**Pantallas**
3. …
```

Cada punto confirmado o corregido pasa a `D-xx`.
