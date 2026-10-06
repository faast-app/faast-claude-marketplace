# Mesa de Servicios en Claude — Instrucciones de uso

**Para:** quienes atienden la Mesa de Servicios (MDS) e Implementaciones/Delivery de FaaST.
**Qué es:** una capacidad de Claude (skill `refinamiento-a-requerimiento`) habilitada para toda la
organización. Toma lo que llega de un cliente y lo convierte en un documento estandarizado y un
ticket listo para desarrollo, sin inventar nada y en lenguaje de negocio.

---

## 1. Qué hace por ti

| Llega… | Claude lo convierte en… | Documento |
|---|---|---|
| Un error ("antes funcionaba", "sale mal el total") | **BUG** con el formato de bugs del equipo, evidencias y pasos | Reporte de bug |
| Un pedido nuevo ya aprobado o interno | **PRY**: propuesta para el cliente + especificación para desarrollo | Propuesta + Especificación (o ficha única si es menor; documento de proyecto si es grande) |
| Un pedido que hay que cobrar o aprobar presupuesto | **CTZ**: cotización que espera aprobación comercial | Cotización (la valorización la pone comercial) |
| El cliente cambia algo que ya aprobó | **CC**: control de cambio con impacto en alcance, plazo y costo | Control de cambio |

Cada documento lleva su **correlativo** (`BUG-2026-003`, `PRY-2026-014`, `CTZ-2026-007`,
`CC-2026-002`) y su **alcance** (`Cliente: ACME` o `Transversal`). Ese número sale del
**Registro de correlativos** que vive en el Proyecto de Claude de la Mesa.

## 2. Antes de empezar (una sola vez por equipo)

1. Un administrador sube `refinamiento-a-requerimiento.skill` en claude.ai
   (Configuración de la organización → Capabilities / Skills) y la habilita para MDS e Implementaciones.
2. Se crea un **Proyecto de Claude** llamado "Mesa de Servicios" y se suben a sus archivos:
   - `registro-correlativos.md` (se mantiene al día: es la única fuente de los números),
   - las fichas de contexto por módulo y los aprendizajes generales (los genera la propia skill),
   - el contenido de **faast-brain** si existe (productos, clientes, procesos, reglas, glosario),
   - AS-IS, manuales y especificaciones anteriores que tenga el equipo.
3. En las instrucciones del Proyecto se pega el texto de `proyecto-claude/instrucciones-proyecto.md`.
4. Todos trabajan **dentro de ese Proyecto**, para que Claude lea el contexto antes de preguntar.

## 3. Cómo se usa, paso a paso

1. **Pega o adjunta lo que llegó**: el correo, el ticket, la transcripción de Teams/Meet, el Word,
   el Excel, las capturas, o cuéntalo con tus palabras. Pide: *"refina esto"*, *"¿esto es un bug?"*,
   *"cotízame esto para ACME"*, *"el cliente cambió lo que aprobamos en PRY-2026-014"*.
2. **Claude clasifica** (BUG / PRY / CTZ / CC), reserva el correlativo, define el alcance y te muestra
   una **lectura breve**: qué entendió, qué ya existe, qué se contradice, qué falta.
3. **Responde sus preguntas**. Vienen numeradas (`PR-1`…), con una propuesta y opciones A/B/C, máximo
   7 por ronda y hasta 3 rondas. Puedes contestar por dictado: *"PR1 sí, PR3 la B, PR5 que decida
   Claude"*. Lo que es del cliente, tú se lo llevas y traes la respuesta; la conversación se pausa y
   se retoma donde quedó.
4. **Mira la maqueta** si el pedido tiene pantallas: Claude arma un boceto navegable (gris, sin diseño
   final) para que el cliente vea la idea antes de aprobar.
5. **Revisa el documento** (propuesta, cotización o control de cambio) y pide el **Word o PDF** para
   enviarlo. Claude puede redactar el correo de envío.
6. **Registra el visto bueno** (quién, cuándo, por qué medio). En cotizaciones, además la **aprobación
   comercial**; sin ella la cotización no es trabajo.
7. **Pide la especificación y el issue**. Claude entrega el cuerpo completo, título, etiquetas y
   campos del proyecto de GitHub (#38), y lo crea si tienes conector a GitHub.
8. **Anota el número en el registro** y, si Claude propone algo aprendido para la ficha del módulo o
   para faast-brain, guárdalo en el Proyecto.

## 4. Reglas que Claude respeta (y que tú también)

- **Nada se inventa.** Lo que el cliente no respondió queda como pendiente explícito, nunca como
  "lo razonable".
- **Lenguaje de negocio.** La propuesta y la cotización van en el idioma del cliente; la especificación
  es funcional y precisa, sin diseño técnico.
- **Al cliente no se le pregunta cómo funciona el sistema.** Eso lo sabes tú, lo dice el Proyecto o lo
  responde desarrollo en un solo pedido.
- **Lo aprobado es el contrato.** Cualquier cambio después del visto bueno es un **control de cambio**,
  no un defecto de desarrollo.
- **Ningún issue sin visto bueno. Ninguna cotización a trabajo sin aprobación comercial.**
- **Claude no pone precios ni esfuerzos** en una cotización: eso es de comercial.
- **Confidencialidad**: nada de un cliente aparece en el documento de otro; sin datos personales ni
  secretos en documentos, issues ni fichas.

## 5. Frases útiles

| Quieres… | Dile a Claude… |
|---|---|
| Clasificar sin refinar todavía | "¿Esto es bug, requerimiento, cotización o control de cambio?" |
| Refinar completo | "Refina esto para [cliente]; producto [factoring]; viene de [reunión / correo]" |
| Retomar | "Retomo PRY-2026-014; estas son las respuestas del cliente: …" |
| Maqueta | "Arma la maqueta de las pantallas de la propuesta" |
| Documento | "Genera la cotización en Word" / "la propuesta en PDF" |
| Control de cambio | "El cliente ahora pide X sobre PRY-2026-014; abre el control de cambio" |
| Ticket | "Arma el issue para GitHub" / "créalo en faast-app/[repo]" |
| Aprender | "Guarda lo aprendido en la ficha del módulo" / "prepara el ingest para faast-brain" |

## 6. Qué NO hace esta versión (y a quién derivar)

| Necesidad | Quién |
|---|---|
| Transcribir un audio o video | Usa la transcripción que genera Teams/Meet y pégala |
| Reproducir el bug en el ambiente real con evidencia grabada | QA (la skill solo organiza las evidencias que trae el cliente) |
| Scripts de datos (revertir una operación, corregir un estado) | DBA, por el canal del pase |
| Ejecutar un cambio en producción | Nadie desde Claude: solo documenta |
| Valorizar | Comercial |

## 7. Si algo sale mal

- Claude propuso algo que el cliente no dijo → dile "eso no está en el insumo, déjalo como pendiente".
- Preguntó demasiado → "solo las bloqueantes" o "decide tú y anótalo como decisión".
- El correlativo está en blanco → completa el registro y pídele que lo ponga.
- No encontró contexto → sube el AS-IS o el manual al Proyecto y vuelve a pedir la lectura.
- La especificación no pasa el validador → Claude te dirá qué falta (reglas sin criterio, pendientes
  abiertos, visto bueno sin registrar); se corrige y se vuelve a validar.
