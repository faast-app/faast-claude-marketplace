# [Tema] — Control de cambio

**`CC-AAAA-NNN` · sobre `PRY-AAAA-NNN` / `CTZ-AAAA-NNN` ([título del original])**
**Cliente:** [código] | Transversal · **Producto:** [...] · **Fecha:** AAAA-MM-DD · **Versión:** 1.0
**Estado del original:** Aprobado sin iniciar | En desarrollo (issue #[n]) | Entregado
**Estado del cambio:** Pendiente de aprobación | Aprobado el AAAA-MM-DD por [quién] | Rechazado

> Se abre un control de cambio cuando el solicitante cambia algo que **ya estaba aprobado** (propuesta
> o cotización con visto bueno) o **ya está en desarrollo** (issue emitido). Lo aprobado es el contrato:
> este documento mide el delta y deja la trazabilidad de que no fue un error de desarrollo.
> Se refina **solo el cambio**, no se reabre todo el requerimiento.

## 1. Qué estaba aprobado

[Resumen en 3-5 líneas de lo aprobado, con la versión y fecha del visto bueno: "Propuesta v1.0 aprobada
el AAAA-MM-DD por [quién]". Citar las secciones del original que se tocan.]

## 2. Qué cambia y por qué

| # | Lo aprobado decía | Ahora se pide | Motivo (en palabras del solicitante) | Evidencia |
|---|---|---|---|---|
| 1 | | | | [T mm:ss] / [R §x] / [U] |

## 3. Impacto del cambio

| Dimensión | Impacto | Detalle |
|---|---|---|
| **Alcance** | Amplía · Reduce · Modifica | [qué entra / qué sale respecto de lo aprobado] |
| **Dónde aplica e impactos** | | [nuevas filas IM-xx o filas que cambian de decisión] |
| **Reglas** | | [RN-xx nuevas o modificadas] |
| **Plazo** | Sin efecto · +[n] días/semanas | [por qué] |
| **Costo / cotización** | Sin efecto · Requiere nueva cotización | [si el original fue CTZ o el cambio es facturable] |
| **Otros clientes / tenants** | Sin efecto · Afecta a … | [convivencia; activación por tenant] |
| **Trabajo ya hecho** | Nada · Se descarta … · Se rehace … | [si ya está en desarrollo] |

## 4. Opciones y recomendación

| Opción | Qué implica | Plazo | Costo | Recomendación |
|---|---|---|---|---|
| A) Aplicar el cambio ahora | | | | |
| B) Entregar lo aprobado y hacer el cambio como requerimiento siguiente | | | | |
| C) No aplicar el cambio | | | | |

## 5. Decisión requerida

- **Quién decide:** [quien tiene autoridad sobre el alcance; y comercial si afecta costo]
- **Qué se necesita:** aprobación escrita de la opción elegida (y nueva cotización si aplica)
- **Decisión:** [opción] · aprobada el AAAA-MM-DD por [quién] vía [medio] → `D-xx`

## 6. Cómo se registra

- **Documentos:** nueva versión de la propuesta/cotización y de la especificación (`v{N+1}`), con
  "Cambios respecto a v{N}" citando este CC.
- **Tracker:** si el issue original no empezó → se actualiza su cuerpo citando `CC-AAAA-NNN`; si ya está
  en desarrollo → **issue nuevo** que referencia al original (`Relacionado con #[n]`), para no mover el
  alcance de lo que se está construyendo. Etiquetas: `tipo:control-cambio`, `cc:sobre-{original}`.
- **Registro de correlativos:** fila del CC con su estado.

---

*Lo aprobado en este control de cambio pasa a ser el nuevo contrato. Un cambio posterior requiere un nuevo CC.*
