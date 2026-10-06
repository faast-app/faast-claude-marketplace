# [Tema] — Especificación funcional

**Correlativo:** `PRY-AAAA-NNN` (origen `CTZ-AAAA-NNN` si vino de cotización) · **Alcance:** Cliente [código] | Transversal · **Versión:** v1.0 · **Tipo:** Cambio funcional | Reporte | Funcionalidad nueva
**Estado:** En refinamiento | Pendiente de aprobación | Listo para desarrollo
**Aprobación:** Pendiente | Aprobado por [nombre, cargo, empresa] el AAAA-MM-DD vía [correo / reunión] (propuesta v[X.Y])
**Fecha:** AAAA-MM-DD

> [Párrafo inicial de 2-3 líneas: qué permite el requerimiento, para quién y con qué piezas principales.]

*Requerimiento aprobado por el solicitante. Este documento es el contenido del issue de backlog: a partir de él, desarrollo elabora historias de usuario, diseño, prompts de Claude Design, pruebas y QA.*

| | |
|---|---|
| **Ticket de origen** | [N° de ticket MDS · proyecto de implementación] — levantado por [MDS / Implementaciones] |
| **Issue de backlog** | [Se completa al cerrar el ticket · N° o enlace] |
| **Solicitante** | [Cliente, cotización N° · o área interna] |
| **Aprueba** | [Persona con autoridad para aprobar el alcance, si no es el solicitante] |
| **Urgencia** | [Normal · fecha comprometida AAAA-MM-DD y por qué · qué pasa si no se hace] |
| **Norma** | [Solo si es cambio obligatorio por normativa: norma, referencia, fecha de vigencia, países y clientes a los que aplica] |
| **Negocio** | [Producto(s) y países; lo que queda fuera] |
| **Tenant** | [Solo cliente X · todos · parametrizable por instancia] |
| **AS-IS de referencia** | [Documento o fuente del comportamiento actual, con fecha · "No disponible: supuestos marcados para validar por desarrollo" · "No aplica: funcionalidad nueva"] |
| **Otros insumos** | [Especificaciones previas, release notes, HU o tickets, solicitudes parecidas, defectos conocidos usados · "Ninguno"] |
| **Base** | [Transcripción reunión DD/MM · documento del solicitante · propuesta aprobada · decisiones D-01 a D-NN] |

<!--
Secciones según el tipo (las que no aplican se eliminan, no se dejan vacías):

| Sección | Cambio funcional | Reporte | Funcionalidad nueva |
|---|---|---|---|
| Alcance en una mirada, control de versiones, objetivo y alcance | Sí | Sí | Sí |
| Resumen de la solución | — | — | Sí |
| Qué cambia exactamente | Sí | Si modifica uno existente | — |
| Definición del reporte | — | Sí | Si incluye reportes |
| Actores y permisos | Si cambian | Sí | Sí |
| Flujo funcional | Si cambia | — | Sí |
| Reglas de negocio | Sí | Sí (cálculos de columnas) | Sí |
| Información de negocio | — | — | Sí |
| Pantallas y mensajes | Si cambia una pantalla | — | Sí |
| Casos de borde | Si hay | Si hay | Sí |
| Dónde aplica e impactos | Sí | Si afecta otros lugares | Sí |
| Criterios de aceptación | Sí | Sí | Sí |
| Activación y puesta en marcha | Sí | Si se activa por tenant | Sí |
| Fuera de alcance, trazabilidad, preguntas abiertas | Sí | Sí | Sí |
| Para resolver por desarrollo | Si hay | Si hay | Si hay |

Cambio menor (etiqueta, texto, mensaje, orden, valor por defecto): usar assets/plantilla-cambio-menor.md.
-->

## Alcance en una mirada

Lo que se aprobó y lo que no. Es el contrato: lo que aparezca después es cambio de alcance.

| | |
|---|---|
| **Estrategia** | [Modifica lo existente · Opción nueva que convive con lo actual · Extiende lo existente con un modo o parámetro · Nuevo, sin equivalente actual] |
| **Se construye** | [Cambio 1 · Cambio 2 · …, en una línea cada uno] |
| **Dónde aplica** | [Lugares que cambian: IM-01, IM-02, IM-03] |
| **No cambia** | [Lugares e impactos que se mantienen: IM-04 · …] |
| **Fuera de alcance** | [Lo excluido explícitamente] |
| **Supuestos** | [Supuestos aceptados, o "Ninguno"] |

## Control de versiones

| Fecha | Versión | Cambios |
|---|---|---|
| AAAA-MM-DD | 1.0 | Versión inicial a partir de [insumo]. |

---

## Objetivo y alcance

**Hoy (AS-IS):** cómo funciona actualmente lo que toca el requerimiento, con referencia `[A §x]`, y cuál es el problema.
**Qué se mantiene:** comportamiento actual que no cambia y que alguien podría suponer que cambia.
**Objetivo:** qué debe poder hacerse cuando esté implementado.

**Incluye**
1. …

## Resumen de la solución

Puntos numerados con las piezas funcionales de la solución, cada una con su nombre en negrita:

1. **[Pieza].** Qué hace y por qué.

## Qué cambia exactamente

Un bloque por cambio. Es el núcleo del requerimiento cuando el cambio es puntual (una fórmula, un campo, una columna). Formato completo en `references/casuisticas.md` del skill.

### Cambio 1 — [nombre corto]

**Dónde:** [Menú › Pantalla › sección › botón o campo]
![Cambio 1](img/cambio-1.png)

**Hoy:** [comportamiento o fórmula actual, explícita] `[A §x]`
**Después:** [comportamiento o fórmula nueva, explícita] (RN-01)

| Variable / dato | Qué es en el sistema |
|---|---|

**Ejemplo** (valores del cliente):

| [Entradas] | Hoy | Después |
|---|---|---|

**Redondeo / momento / alcance:** [si aplica]

## Definición del reporte

*Solo tipo Reporte, o funcionalidad nueva que incluye reportes.*

- **Para qué y quién lo usa:** [decisión o tarea que apoya; perfiles]
- **Dónde se genera:** [Menú › opción · programado (periodicidad, hora, destinatarios)]
- **Formato de salida:** [Excel · PDF · CSV · en pantalla]
- **Filtros:** [nombre, tipo, obligatorio, valor por defecto]
- **Orden y agrupación:** […]
- **Volumen esperado:** [filas por ejecución, rango de fechas típico]
- **Destinatarios y datos personales:** [si sale por correo o se exporta: a quién, interno o externo; datos que se omiten o enmascaran]

| # | Columna | Origen del dato (concepto o pantalla del sistema) | Cálculo | Formato |
|---|---|---|---|---|
| 1 | | | — o RN-xx | [moneda, decimales, fecha dd/mm/aaaa] |

**Totales:** [por grupo y general; qué columnas]
**Maqueta o ejemplo:** [modelo del cliente interpretado, o tabla de ejemplo con 2-3 filas]

## Actores y permisos

| Rol | Puede | No puede | Origen |
|---|---|---|---|

## Flujo funcional

### Flujo principal
1. …

### Flujos alternativos y de error
- **FA-1 [nombre]:** en el paso N, si … entonces …

## Reglas de negocio

| ID | Regla | Origen |
|---|---|---|
| RN-01 | [Condición → resultado, con valores concretos] | D-01 · [T mm:ss – Hablante] · [A §x] · [C documento §x] |

## Información de negocio

Datos que el sistema captura, muestra o calcula, en términos funcionales:

| Dato | Dónde se usa | Obligatorio | Validación / formato | Origen del valor |
|---|---|---|---|---|

**Datos existentes:** [aplica solo hacia adelante · qué pasa con lo que ya existe]

## Pantallas y mensajes

Qué ve y qué hace el usuario. Base para el diseño de pantallas (prompts de Claude Design) y para las pruebas.

### [Pantalla o menú: nombre como lo conoce el usuario · existente / nueva]

- **Dónde está:** [menú › opción · pestaña · paso del wizard]
- **Qué ve:** [datos que se muestran, en orden, con formato: moneda, decimales, fechas]
- **Qué puede hacer:** [acciones, botones, filtros; quién puede, según permisos]
- **Mensajes:**

| Situación | Tipo | Texto exacto |
|---|---|---|
| | Error · advertencia · confirmación | "" |

(Si el requerimiento no toca pantallas, escribe "Sin cambios de pantalla" y en qué proceso ocurre el cambio.)

## Casos de borde

| Situación | Comportamiento esperado | Regla |
|---|---|---|
| | | RN-xx |

## Dónde aplica e impactos

Ver `references/impactos.md` del skill. Sin referencias vagas: nada de "lo previamente definido" o "lo que corresponda"; cada impacto se escribe completo.

### Dónde aplica

Todos los lugares donde vive lo que cambia (pantallas, botones, documentos generados, reportes, canales, procesos automáticos, integraciones, notificaciones), con la decisión de cada uno. "No cambia" también se escribe.

| ID | Lugar | Tipo | ¿Cambia? | Detalle | Origen |
|---|---|---|---|---|---|
| IM-01 | [Menú › Pantalla › botón] | Pantalla | Sí | | D-xx |
| IM-02 | [PDF de …] | Documento | Sí | | D-xx |
| IM-03 | [Reporte …] | Reporte | No | [por qué no] | [U] |

### Contabilidad y tributario

Una fila por evento o asiento afectado; si no hay impacto, una línea "Sin impacto contable" con la decisión que lo respalda.

| ID | Evento | Asiento hoy | Asiento después | Qué cambia | Momento |
|---|---|---|---|---|---|

### Otros módulos, reportes e integraciones

| ID | Área | Impacto concreto | Origen |
|---|---|---|---|

### Datos existentes y operaciones en curso

[Qué pasa con lo ya calculado o emitido; desde cuándo rige.]

## Criterios de aceptación

Base para las historias de usuario y las pruebas de QA. Cada criterio es un caso verificable con valores concretos. En **Ref.** va la regla (`RN-xx`) y, cuando corresponde, el lugar o impacto (`IM-xx`) que verifica: cada lugar que cambia y cada impacto necesita al menos un criterio.

| ID | Criterio | Ref. |
|---|---|---|
| CA-01 | [Situación con valores → resultado observable] | RN-01 · IM-01 |

## Activación y puesta en marcha

- La funcionalidad se despliega **desactivada por defecto**; su activación y valores por defecto son **por tenant**. Los tenants que no la activen no ven cambios.
- Configuración inicial que realiza el cliente: …
- Convivencia con el comportamiento actual: …

## Fuera de alcance

- … (con la decisión `D-xx` que lo sacó)

## Para resolver por desarrollo

Dudas técnicas detectadas en el refinamiento. No bloquean el requerimiento; el equipo las resuelve en el diseño.

| # | Punto | Por qué importa |
|---|---|---|
| PT-01 | | |

## Trazabilidad de decisiones

| ID | Decisión | Origen | Fecha |
|---|---|---|---|
| D-01 | | [Quién decidió · respuesta del cliente · delegada y confirmada] | |

## Preguntas abiertas

| ID | Pregunta | Severidad | Dirigida a | Estado |
|---|---|---|---|---|

(Debe quedar "Sin preguntas abiertas." para pasar a aprobación.)

---

*Este documento define qué debe hacer el sistema, bajo qué reglas y qué ve el usuario, y fue aprobado por el solicitante. El diseño técnico, las historias de usuario, los prompts de diseño, el plan de desarrollo y las pruebas los elabora el equipo de desarrollo a partir de él. Cualquier cambio de alcance requiere un nuevo visto bueno.*
