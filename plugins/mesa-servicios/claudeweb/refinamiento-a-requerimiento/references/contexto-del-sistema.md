# Contexto del sistema

El filtro pregunta bien solo si sabe cómo funciona hoy el sistema en la zona del requerimiento y qué se ha hecho antes en ella. Pero conseguir ese contexto no debe crear nuevas iteraciones con desarrollo: el objetivo del skill es reducirlas. Por eso el orden es: lo que ya está escrito, luego quien usa el skill y, solo al final, desarrollo, en un único pedido.

El contexto sirve para:

1. **No preguntar lo que ya está resuelto.** Ni por el sistema ni por decisiones anteriores.
2. **Detectar lo que ya existe.** Algo liberado, configurable, en curso o pedido antes. Cambia la naturaleza del requerimiento, así que se avisa antes de refinar.
3. **Detectar choques.** Con el comportamiento actual, con decisiones previas, con trabajo en curso o con lo que usan otros clientes.
4. **Proponer buenos valores por defecto.** Lo ya decidido en casos parecidos se ofrece como propuesta en las preguntas.
5. **Escribir "lo que no cambia"** y usar los nombres reales de pantallas, estados y parámetros.

## Catálogo de insumos

| Insumo | Qué buscar en él | Cómo cambia el refinamiento |
|---|---|---|
| **AS-IS del módulo** | Flujo actual, estados, reglas vigentes, momento de cálculo, parametrización por tenant, permisos, canales (front, portal, API digital), integraciones | Las preguntas pasan de "¿cómo lo quiere?" a "hoy funciona así, ¿se mantiene o cambia?"; aparecen los choques |
| **Especificaciones y propuestas previas** del módulo | Reglas y decisiones (`D-xx`) ya tomadas, fuera de alcance declarado, deuda registrada | No contradecir decisiones sin decirlo; reutilizar vocabulario y criterios; detectar si el pedido es algo que antes se dejó fuera |
| **Historial de cambios, release notes, último release** | Qué cambió recientemente, qué versión está vigente, si algo parecido ya salió | Evita pedir lo que ya existe; ubica el requerimiento respecto de la versión actual |
| **Historias de usuario y tickets** previos o en curso | Trabajo que se solapa, dependencias, bloqueos | Evita duplicar; declara dependencias en impactos o "Para resolver por desarrollo" |
| **Solicitudes parecidas** de este u otros clientes | Cómo se resolvió, qué se parametrizó | Proponer parametrizar en lugar de hacer a medida; reutilizar decisiones; anticipar conflictos entre tenants |
| **Defectos e incidencias conocidas** | Si lo pedido es en realidad un error del sistema | Puede convertir el requerimiento en una corrección |
| **Manuales y capturas** | Nombres de pantallas, menús y campos que el usuario conoce | Propuesta y preguntas en el idioma del usuario |

No hace falta tenerlos todos: basta con lo que toca el requerimiento. El AS-IS es el más importante cuando se modifica algo existente.

## Dónde buscarlos, en orden

1. **faast-brain**, si está cargado en el Proyecto de Claude: el conocimiento curado del negocio de FaaST (productos, clientes y sus configuraciones, procesos, integraciones, reglas, glosario, decisiones y resumen de solicitudes anteriores). Se lee ANTES de preguntar: lo que el brain ya responde no se pregunta ni al usuario ni al cliente. Cita la página (`[C brain/<pagina>]`).
2. **Ficha de contexto del módulo** (`contexto/<modulo>.md`, en los archivos del Proyecto o del skill). Resume lo que ya se aprendió en requerimientos anteriores y dice dónde está cada insumo.
3. Archivos adjuntos a la conversación o al Proyecto.
4. Conversaciones previas sobre el módulo o el cliente, si la búsqueda de chats está disponible.
5. Conectores de la sesión, en modo lectura: repositorios de código, SharePoint/OneDrive, tracker o proyecto de GitHub, ambiente de pruebas.
6. **Quien usa el skill**: conoce el sistema. Hazle pocas preguntas cerradas sobre el comportamiento actual, con la hipótesis ya formulada ("hoy X funciona así, ¿correcto?"). Lo que confirme es evidencia `[U]`.
7. **Otra área o desarrollo**: solo lo que no salió de 1 a 6 y cambia una regla o el alcance. Va en un único pedido consolidado por destinatario (ver abajo). Las áreas de negocio (contabilidad, riesgo, legal, operaciones) responden lo suyo; desarrollo responde sobre el sistema.

Si el código y la descripción funcional difieren, el código manda. Revisa la fecha de cada insumo y si cubre el producto, país y canal del requerimiento: un AS-IS de Factoring no describe Ordering, y una especificación anterior a un release puede estar superada.

## El pedido a desarrollo u otra área: uno por destinatario y sin detener el trabajo

La misma lógica aplica a cualquier destinatario: desarrollo, contabilidad, riesgo, legal u operaciones.

- **Uno por destinatario y por requerimiento.** Reúne en un mensaje todo lo que falta, tanto los insumos como las preguntas sobre el sistema actual. Un segundo pedido solo se justifica si la respuesta abre algo nuevo y bloqueante.
- **Solo lo que cambia el requerimiento.** Si la respuesta no cambia una regla ni el alcance, no se pregunta: va como `PT-xx` para que desarrollo lo resuelva en el diseño.
- **Con hipótesis.** Cada pregunta trae lo que se cree y pide confirmar o corregir, para que responder tome minutos.
- **En paralelo.** Mientras desarrollo responde, el refinamiento con el solicitante sigue. Solo esperan las reglas que dependen de la respuesta.
- **Lo que llega se guarda.** La respuesta alimenta la ficha del módulo para no volver a preguntarlo.

Plantilla:

```
Asunto: Consulta única — [módulo], requerimiento [nombre] de [cliente]

Estamos refinando un requerimiento de [cliente] que toca [módulo]: [necesidad en una línea].
Necesitamos confirmar lo siguiente; con lo que exista alcanza, no hace falta preparar nada nuevo.

Sobre cómo funciona hoy (confirmar o corregir):
1. Entendemos que [hipótesis]. ¿Correcto?
2. …

Insumos, si existen:
3. [AS-IS / especificación previa / release / tickets abiertos / solicitud parecida] de [tema].

Solo esperamos esto para cerrar: [reglas que dependen de la respuesta].
```

Si quien usa el skill tiene Claude Code sobre los repositorios, ofrece en su lugar un prompt para levantar el AS-IS desde el código, con citas `archivo:línea`. Así no hace falta consultar a nadie.

## Cuando aparece algo que ya existe

Si el contexto muestra que lo pedido ya existe, ya se liberó, se puede resolver configurando o está en curso, **detente y avísalo** antes de refinar, con la evidencia y las opciones:

- Ya existe o es configuración → responder al solicitante cómo usarlo; puede no requerir desarrollo.
- Existe parcialmente → refinar solo la diferencia.
- Está en curso → coordinar con ese trabajo; el requerimiento puede sumarse como ajuste.
- Es un defecto → derivar como corrección.

## Confidencialidad entre clientes

Las solicitudes, valores y configuraciones de otros clientes sirven como contexto interno: valores por defecto, decisión de parametrizar, detección de conflictos. **Nunca aparecen en la propuesta de otro cliente** ni se mencionan al solicitante. En la especificación para desarrollo pueden citarse como antecedente.

## Sin contexto

Si no se consigue o el usuario decide seguir sin él:

- Continúa con el refinamiento.
- Cada supuesto sobre el comportamiento actual que afecte una regla se pregunta primero a quien usa el skill y, si no lo sabe, va al pedido consolidado a desarrollo. Al solicitante no se le pregunta cómo funciona el sistema.
- La especificación declara en el encabezado "AS-IS de referencia: No disponible" y lista en "Otros insumos" lo que sí se usó. Desarrollo debe validar los supuestos marcados antes de diseñar.

## Ficha de contexto por módulo

La ficha (`assets/plantilla-ficha-contexto.md`) es lo que hace que las consultas a desarrollo desaparezcan con el tiempo. Al cerrar cada requerimiento:

- Agrega el comportamiento actual que se confirmó, indicando quién lo confirmó.
- Registra dónde están los insumos que se encontraron.
- Suma las decisiones reutilizables.
- Mueve a "confirmado" los huecos que se respondieron y anota los que siguen abiertos.

Nunca incluyas en la ficha información confidencial de un cliente. La ficha se entrega aparte, como mantenimiento; el usuario la guarda donde viven las fichas (archivos del proyecto, carpeta compartida o la carpeta `contexto/` del skill).

## El ciclo de aprendizaje

Las fichas y los aprendizajes generales hacen que cada refinamiento sea más exacto que el anterior:

1. **Antes de preguntar** se leen la ficha del módulo y los aprendizajes generales. Sus preguntas aprendidas se hacen siempre.
2. **Durante el refinamiento** se confirma comportamiento actual, con el usuario o con desarrollo.
3. **Al cerrar**, lo confirmado va a la ficha.
4. **Después de la entrega**, cada consulta de desarrollo se clasifica (Fase 7). Si era contexto faltante, va a la ficha; si era una pregunta no hecha, va a preguntas aprendidas; si era ambigüedad, va a redacción.
5. **Promoción**: lo que se repite entre módulos pasa al checklist del skill.
6. **faast-brain**: al cerrar un caso, propone al usuario el texto para alimentar el brain (un producto o cliente nuevo, una regla descubierta, un término, una decisión, el resumen del caso con su correlativo), en lenguaje de negocio, sin secretos ni datos personales. Quien cura el brain decide si lo incorpora.

El indicador del ciclo son las consultas de desarrollo después de la entrega. Si un módulo sigue generando consultas por la misma causa, la ficha está incompleta en ese punto.
