# Reglas de redacción

Escribe para alguien que no estuvo en la reunión y que hará exactamente lo que el texto dice. Ese lector es tanto un desarrollador nuevo como un agente de Claude Code.

## Términos vagos prohibidos

Si aparece uno de estos términos, reemplázalo por un valor, una condición o una referencia concreta. Si no sabes el valor, es una pregunta abierta.

| Evitar | Reemplazar por |
|---|---|
| rápido, ágil, eficiente, en tiempo real | tiempo concreto ("en menos de 3 segundos") o eliminar |
| fácil, intuitivo, amigable | el comportamiento concreto de la interfaz |
| adecuado, apropiado, correcto, válido (sin definir) | la condición exacta |
| según corresponda, cuando aplique, si es necesario | la condición que determina cuándo aplica |
| etc., entre otros, y similares | la lista completa o "solo los siguientes:" |
| normalmente, generalmente, habitualmente | la regla y sus excepciones |
| lo de siempre, como ahora, igual que antes | la descripción del comportamiento actual |
| debería, podría | "debe" (obligatorio) o mover a fuera de alcance |
| algunos, varios, muchos | la cantidad o el criterio |
| TBD, por definir, [completar] | pregunta abierta en la sección correspondiente |

El script `validar_requerimiento.py` detecta estos términos como advertencia y los marcadores tipo TBD como error.

## Lenguaje según el documento

- **Propuesta funcional** (solicitante): lenguaje de su negocio, con los nombres de pantallas y menús que ya conoce y ejemplos de su operación. Evita: tabla, columna, base de datos, endpoint, API, backend, frontend, gateway, micro, repositorio, query, flag, deploy, null, parámetro técnico, y cualquier ID interno (RN, D, CA, PR). No menciones módulos, patrones ni proyectos internos que el lector no conoce.
- **Cotización y control de cambio** (cliente, y comercial): mismo lenguaje que la propuesta. La cotización describe alcance, entregables, supuestos, exclusiones y plazos estimados; **la valorización la completa comercial**, el skill nunca pone precios ni esfuerzos. El control de cambio compara "lo aprobado decía / ahora se pide" con palabras del cliente y mide el impacto en alcance, plazo y costo sin tecnicismos.
- **Reporte de bug** (QA y desarrollo): hechos observables — pasos exactos, resultado, esperado con su fuente, evidencia. Sin hipótesis de causa ni soluciones: el bug describe lo que pasa, no por qué.
- **Especificación funcional** (issue de backlog, equipo de desarrollo): lenguaje funcional, de usuario; no necesita términos técnicos. Debe ser **precisa**: reglas con valores, bordes decididos, pantallas con datos, acciones y textos exactos de mensajes, y criterios verificables. No incluye diseño técnico (modelo de datos, DDL, endpoints, clases, repos, tareas, historias): eso lo produce desarrollo. Si el insumo trae un dato técnico relevante (una restricción, un módulo que no se toca), va como restricción o en "Para resolver por desarrollo".

## Reglas de negocio

- Una regla por fila. Si una fila tiene "y además", probablemente son dos.
- Forma sugerida: **condición → resultado**. "Si el cliente está bloqueado para el producto, el sistema rechaza la solicitud con el mensaje X."
- Valores concretos con unidad y moneda.
- Fuente obligatoria: `[T mm:ss – Hablante]` (transcripción), `[R §…]` (documento del solicitante), `[A §…]` (AS-IS), `[C <documento> §…]` (otro insumo de contexto: especificación previa, release, HU, solicitud parecida), `[U]` (confirmado por quien usa el skill) o `D-xx` (decisión). Una regla que solo describe el comportamiento actual que se mantiene lleva `[A §…]`.

## Criterios de aceptación (CA-xx en la especificación)

- Un criterio por fila, verificable sin interpretar: situación con valores concretos → resultado observable (estado, monto, mensaje, registro).
- No "el sistema funciona correctamente" ni repetir la regla con otras palabras: un criterio es un caso.
- Columna **Ref.** con la regla `RN-xx` que verifica. Toda RN tiene al menos un CA; el validador lo comprueba.
- Al menos un criterio negativo por regla de validación, y uno por cada caso de borde relevante.
- Si una regla tiene variantes (límites, países, monedas), un criterio por variante relevante.

## IDs

| Prefijo | Qué es | Dónde se define |
|---|---|---|
| `RN-xx` | Regla de negocio | Reglas de negocio de la especificación |
| `CA-xx` | Criterio de aceptación | Criterios de aceptación de la especificación |
| `D-xx` | Decisión | Trazabilidad de decisiones |
| `PR-xx` | Pregunta de refinamiento | Preguntas abiertas |
| `PT-xx` | Punto técnico para desarrollo | Para resolver por desarrollo |
| `IM-xx` | Lugar donde aplica o impacto | Dónde aplica e impactos |

La propuesta funcional, la cotización y el control de cambio no llevan IDs internos; solo el **correlativo** `TIPO-AÑO-NNN` y el alcance en portada (ver `tipos-y-correlativo.md`). Los IDs no se renumeran entre versiones; si algo se elimina, su ID queda sin uso.
