# [Tema]

**Propuesta funcional para aprobación · [Cliente] · `PRY-AAAA-NNN`** (origen `CTZ-AAAA-NNN` si vino de cotización)
FaaST · [fecha en palabras] · Versión 1.0 · **Alcance:** Cliente [código] | Transversal

---

## 1. Para qué es este documento

[Cliente] solicitó [necesidad en una línea]. Este documento describe lo que entendimos de la solicitud, cómo funcionará la solución en el sistema y qué necesitamos de [Cliente] para ponerla en marcha.

Con la aprobación de este documento pasamos a la etapa de diseño de pantallas y desarrollo. Cualquier ajuste posterior a lo aquí descrito se tratará como un cambio de alcance.

**En resumen**

| | |
| --- | --- |
| **Lo que haremos** | [en una línea por cambio] |
| **Lo que pasa con lo actual** | [Se mantiene igual y lo nuevo se agrega como una opción aparte · Cambia así: …] |
| **Dónde lo verá** | [pantallas, documentos y reportes que cambian] |
| **Lo que no cambia** | [lo que se mantiene igual] |
| **Lo que no incluye** | [exclusiones] |

## 2. Lo que entendimos

### La solicitud

[La solicitud tal como la planteó el cliente, con su tabla o referencia si la entregó.]

### Las precisiones que [Cliente] nos entregó

| Tema | Definición |
| --- | --- |
| | |

## 3. Cómo funcionará

### 3.1 Qué cambia exactamente

[Un bloque por cambio. En un cambio puntual, este es el corazón del documento.]

**Cambio 1 — [nombre corto]**

**Dónde:** [Menú › Pantalla › botón o campo, con los nombres que usted ve en el sistema]
![Cambio 1](img/cambio-1.png)

**Hoy:** [cómo funciona o cómo se calcula, escrito completo]
**Después:** [cómo funcionará o cómo se calculará, escrito completo]

**Ejemplo** con sus valores:

| [Datos] | Hoy | Después |
| --- | --- | --- |

**Dónde se verá el cambio:**

| Lugar | ¿Cambia? |
| --- | --- |
| [Simulación, botón Calcular] | Sí |
| [PDF de liquidación] | Sí |
| [Reporte de cartera] | No: muestra lo ya calculado |

**Otros efectos:** [en lenguaje de negocio: contabilidad, cobranza, cupos, reportes; por ejemplo "el ingreso por diferencia de precio se registra con el nuevo monto desde la activación"]

[Para un reporte: en lugar del bloque anterior, la maqueta del reporte con sus columnas y dos o tres filas de ejemplo con datos de su operación, los filtros, dónde se genera y quién lo recibe.]

### 3.2 [Lo que se mantiene y lo que se agrega]

[Qué no cambia de lo que el usuario ya conoce y qué es lo nuevo.]

### 3.3 [Cómo se configura / cómo se usa]

[Pasos en el lenguaje del usuario, con los nombres de pantallas y menús que ya conoce.]

### 3.4 [Cómo se aplica en la operación]

**Ejemplo.** [Caso con valores reales del cliente, en tabla, con el resultado que verá.]

[Una o dos variantes del ejemplo en una línea.]

**Lo que no cambia.** [Comportamiento actual que se mantiene y que alguien podría suponer que cambia.]

**Si [caso de borde].** [Qué pasa, en lenguaje de negocio.]

### 3.5 Quién puede hacer qué

| Acción | Permiso |
| --- | --- |

### 3.6 Trazabilidad de los cambios

[Qué queda registrado y dónde se consulta, si aplica.]

## 4. Lo que queda fuera de esta solicitud

- …

## 5. Lo que necesitamos de [Cliente]

1. **Aprobación de este documento.**
2. **Revisión del diseño de pantallas**, que enviaremos después de la aprobación (si aplica).
3. **Al momento de la puesta en marcha**, configuración en el sistema (la realiza [Cliente] con apoyo de FaaST):
   - …

## 6. Cómo sigue

| Etapa | Responsable |
| --- | --- |
| Aprobación de esta propuesta | [Cliente] |
| Diseño de pantallas y validación con [Cliente] | FaaST → [Cliente] |
| Desarrollo y pruebas internas | FaaST |
| Pruebas en ambiente de [Cliente] | [Cliente] con apoyo de FaaST |
| Configuración inicial y salida a producción | [Cliente] con apoyo de FaaST |

---

*Documento de definición funcional. La solución no altera el comportamiento de los clientes de FaaST que no la activen.*
