# Mesa de Servicios

Equipo de 10 agentes IA que recibe **todo lo que llega del cliente** — tickets, reportes de
bugs, cotizaciones, proyectos, pedidos de datos — desde **cualquier fuente** (correo,
documento, transcripcion de Teams/Meet, audio o video, chat, relato), y lo convierte en un
requerimiento **cerrado, documentado y registrado** en el backlog, listo para que el equipo de
desarrollo lo priorice sin volver a preguntarle nada al cliente.

Cubre la parte izquierda del flujo FAAST (solicitud del cliente → mesa → refinamiento →
backlog de GitHub). El plugin **dev-team** toma desde ahi (lider de producto → PO → desarrollo).

## Instalacion

```bash
/plugin marketplace add faast-app/faast-claude-marketplace
/plugin install mesa-servicios@faast-marketplace
```

## Uso

```bash
/mesa-servicios:start
```
Eso es todo: detecta si la Mesa esta configurada y te guia. La primera vez corre el `setup`
(credenciales y herramientas, con una confirmacion) y crea el repo de conocimiento `faast-brain`.

## El flujo
1. **Recibir** (`/mesa-servicios:recibir`) — cualquier fuente; audio y video se transcriben en la
   maquina; queda el registro normalizado: que se entendio, que falta, que se contradice.
2. **Analizar** (`/mesa-servicios:analizar`) — el analista lee `faast-brain` para no preguntar lo que
   el negocio ya sabe, y prepara rondas cortas de preguntas en lenguaje de negocio (max 7, tope 3)
   que la persona de mesa lleva al cliente, hasta cerrar el requerimiento y clasificarlo.
3. **Reproducir** (`/mesa-servicios:reproducir`) — para bugs: el QA de negocio reproduce en el
   ambiente real grabando todo (traza, video con acciones y capitulos, capturas resaltadas,
   consola y red) y emite veredicto. **Solo prueba, jamas causas.**
4. **Prototipo** (`/mesa-servicios:prototipo`) — para funcionalidad nueva con pantalla, proyecto
   o cotizacion: maqueta tipo wireframe navegable para que el cliente VEA la idea.
5. **SQL** (`/mesa-servicios:sql`) — para pedidos de datos: el DBA de mesa diagnostica en solo
   lectura y ARMA scripts idempotentes y flujos reutilizables. **Cero escritura: nunca ejecuta.**
6. **Documento** (`/mesa-servicios:documento`) — el documento ejecutivo estandarizado (BUG / PRY /
   CTZ) con correlativo `TIPO-AÑO-NNN` y alcance (cliente o transversal), en PDF + Word; y la
   **Propuesta** para el cliente en cotizaciones.
7. **Ticket** (`/mesa-servicios:ticket`) — issue en el Project de GitHub (o PBI en Azure) con
   etiquetas completas, documento y evidencia embebida. Las cotizaciones esperan aprobacion
   comercial antes de ser trabajo.
8. **Brain** (`/mesa-servicios:brain`) — el curador destila lo aprendido a `faast-brain` para que
   la proxima solicitud se cierre con menos preguntas.

## El equipo
| Agente | Rol |
|---|---|
| **mesa-lead** | Coordina la Mesa, decide que sigue, escala; unico que delega |
| **recepcion** | Recibe de cualquier fuente, transcribe, normaliza sin inventar |
| **analista** | El que pregunta: cierra el requerimiento con rondas puntuales y lo clasifica |
| **qa-negocio** | Reproduce con Playwright MCP grabando todo; veredicto con evidencia; nunca causas |
| **dba-mesa** | Diagnostica en lectura y arma scripts/flujos idempotentes; cero escritura |
| **prototipador** | Maquetas wireframe navegables para validar la idea |
| **redactor** | Documento estandar (PDF + DOCX) y Propuesta para el cliente |
| **registrador** | Ticket con etiquetas en el Project, documento y evidencia embebida |
| **curador** | Mantiene `faast-brain`; unico que escribe en el |
| **setup** | Credenciales y herramientas (gh/az, Whisper, LibreOffice, Playwright, BD solo lectura) |

Todos corren en `sonnet` por defecto; se sube por agente en `.mesa/config.json` → `team.models`.

## Principios
- **Nada se inventa**: lo que el cliente no respondio queda como pendiente explicito.
- **Lenguaje de negocio** en preguntas, documentos y tickets; cero codigo.
- **Correlativo + alcance**: `BUG-2026-003 · Transversal`, `CTZ-2026-007 · Cliente ACME`.
- **QA solo prueba**; **DBA solo arma** (cero escritura); **la persona de mesa habla con el cliente**.
- **Evidencia embebida** en el ticket, nunca link suelto; secretos y datos personales, jamas.
- **Una cotizacion no es trabajo** hasta su aprobacion comercial.
- Estado y memoria en `.mesa/` (separado de `.coordination/` del dev-team: pueden convivir).
