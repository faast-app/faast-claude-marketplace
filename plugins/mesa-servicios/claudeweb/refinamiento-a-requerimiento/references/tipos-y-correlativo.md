# Tipos de salida, correlativo y alcance

Todo lo que entra por la Mesa termina en una de cuatro salidas. Decidirla primero evita refinar un
bug como requerimiento, pasar a trabajo una cotización sin aprobar, o tratar un cambio de alcance
como "un detalle".

## Los cuatro tipos

| Tipo | Cuándo | Preguntas que lo delatan | Documentos | Estado final |
|---|---|---|---|---|
| **BUG** | El sistema no hace lo que ya debería según el AS-IS, una especificación o un release | "antes funcionaba", "se duplica", "no deja", "sale mal el total" | `assets/plantilla-bug.md` | Reporte completo con evidencias → QA valida → desarrollo |
| **PRY** | Requerimiento ya aprobado (o interno) que hay que especificar: cambio menor, funcional, reporte o funcionalidad nueva | "necesitamos que…", "agreguen", "cambien", "un reporte de…" | Propuesta + especificación (o ficha única si es menor); `plantilla-proyecto.md` si es un proyecto con fases | `Listo para desarrollo` → issue en el backlog |
| **CTZ** | Lo pedido requiere valorización y aprobación comercial antes de ser trabajo | "cuánto cuesta", "cotícenme", "cuánto demora", un cliente pide algo fuera de contrato | `plantilla-cotizacion.md` (propuesta comercial, valorización en blanco) | `Pendiente de aprobación comercial` → aprobada pasa a PRY; descartada se cierra |
| **CC** | El solicitante cambia algo ya aprobado (propuesta/cotización con visto bueno) o en desarrollo (issue emitido) | "mejor que…", "ahora también…", "cambiemos lo que aprobamos" | `plantilla-control-cambio.md` | Nuevo visto bueno → issue actualizado o issue nuevo referenciando al original |

Reglas de frontera:
- **Bug vs. requerimiento**: si el "esperado" sale del AS-IS, una especificación o un release, es bug;
  si el "esperado" es algo que el sistema nunca prometió, es PRY (o CTZ). Si funciona así por diseño y
  el cliente no lo sabía, es consulta de uso, no bug.
- **PRY vs. CTZ**: si hay que cobrar o aprobar presupuesto, es CTZ. Un PRY interno o ya contratado no
  pasa por cotización.
- **PRY vs. CC**: si ya existe una propuesta aprobada o un issue emitido sobre lo mismo, cualquier
  cambio es CC. Si todavía está en refinamiento (sin visto bueno), es simplemente una nueva decisión `D-xx`.
- **Mixto**: un correo con un bug y un pedido nuevo son dos salidas; se separan desde la Fase 0.

## Correlativo

`TIPO-AÑO-NNN`: `BUG-2026-003`, `PRY-2026-014`, `CTZ-2026-007`, `CC-2026-002`.

- Lo lleva el **Registro de correlativos** del Proyecto de Claude (`assets/registro-correlativos.md`),
  una tabla por tipo y año. Antes de emitir un documento, mira el último número del tipo y toma el
  siguiente; registra la fila (correlativo, título, cliente/alcance, fecha, estado, ticket).
- Si el registro no está en el Proyecto o el usuario no lo tiene a mano, deja `TIPO-2026-___` y pide
  que quien lleva el registro lo complete antes de enviar al cliente o crear el issue.
- Un número **nunca se reutiliza**: si un documento se anula, su número queda anulado en el registro.
- Un CC referencia siempre al PRY/CTZ original (`CC-2026-002 · sobre PRY-2026-014`).
- La CTZ aprobada **conserva su número** y además recibe un PRY cuando pasa a trabajo
  (`PRY-2026-020 · origen CTZ-2026-007`), para que comercial y desarrollo se rastreen entre sí.

## Alcance (obligatorio en portada e issue)

| Alcance | Cuándo | Cómo se escribe |
|---|---|---|
| **Cliente** | Es para un cliente específico (su cotización, su proyecto, un bug que solo él ve por su configuración) | `Cliente: ACME` (código corto del cliente) |
| **Clientes** | Para varios, pero no para todos | `Clientes: ACME, BETA` |
| **Transversal** | Para el producto, lo usen quienes lo usen (un bug que ven todos aunque lo reporte uno; una mejora general) | `Transversal` |

Recordatorio del gobierno de FaaST: aunque el alcance sea transversal, lo nuevo se despliega
desactivado por defecto y se activa por tenant; "transversal" describe a quién le sirve, no que se
active para todos de golpe.

## Etiquetas y campos del issue (ver `references/github.md`)

`tipo:bug | tipo:proyecto | tipo:cotizacion | tipo:control-cambio` · `cliente:{codigo}` o
`alcance:transversal` · `producto:{factoring|confirming|…}` · `prioridad:{critica|alta|media|baja}` ·
`origen:{correo|reunion|ticket|chat}` · `mesa:{correlativo}` · en CTZ `cotizacion:pendiente-aprobacion`
→ `cotizacion:aprobada` o `cotizacion:descartada` · en CC `cc:sobre-{correlativo-original}`.

## Nombres de archivo

- `{Correlativo} - {Tema} - v{N}.md` (y `.docx` / `.pdf` cuando se genere)
- Propuesta: `{Correlativo} - Propuesta - {Cliente} - v{N}` · Cotización: `{Correlativo} - Cotizacion - {Cliente} - v{N}`
- Control de cambio: `{CC} - Control de cambio - {Cliente} - v{N}` · Bug: `{BUG} - {Que falla}`
- Las versiones no se sobreescriben: `v2` lleva "Cambios respecto a v1".
