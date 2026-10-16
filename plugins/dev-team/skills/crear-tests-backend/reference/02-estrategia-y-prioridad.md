# 02 — Estrategia por capas y por objetivo

**Fase 2 de `crear-tests-backend`.**

Cinco familias de tests. No son niveles de una pirámide que haya que subir en orden: son
**herramientas distintas para preguntas distintas**, y en un legado sin tests la (a) vale
más que la (b).

---

## 1. Prioridad: el orden es el del riesgo, no el de la pirámide

Cuando hay tiempo para 20 tests y el sistema tiene 500 cosas testeables, este es el orden.

| # | Área | Por qué primero | Qué pasa si se rompe y nadie se entera |
|---|---|---|---|
| **1** | **Autenticación** | Un cambio de librería cambia el mapeo de claims sin fallar el build (`E-JWT-01` de `migrar-dotnet`) | La autorización **se afloja**: alguien entra donde no debía. Es el único fallo que no se nota nunca |
| **2** | **Dinero y cálculos** | Montos, tasas, intereses, mora, asientos contables | Plata mal calculada, y el error viaja a contabilidad antes que a un ticket |
| **3** | **Cifrado** | Cambiar de algoritmo o de derivación de clave deja datos **existentes** ilegibles | Datos en base que no se pueden descifrar. No hay rollback que lo arregle |
| **4** | **Jobs / procesos automáticos** | Corren sin nadie mirando y suelen ser idempotentes "por costumbre" | Correos, asientos o archivos duplicados. Precedente propio: `E-HF-02` |
| **5** | **Fechas, cultura y zona horaria** | Barato de testear, y es la causa nº1 de "verde en local, rojo en CI" y de "el contenedor mueve todo 5 horas" | Registros con la hora corrida, reportes con montos mal formateados |
| **6** | **Contrato de los endpoints consumidos** | Es lo que rompe al front y a los otros micros | Un consumidor deja de encontrar un campo |
| 7 | El resto | — | — |

**Regla práctica:** si en la revisión del plan de tests alguien no puede decir *qué se
rompe y a quién le duele* para un test propuesto, ese test va al final de la lista.

---

## 2. Familia (a) — Tests de caracterización: la red de seguridad

**Qué son:** tests que describen lo que el sistema hace **hoy**, incluidos sus bugs. No
afirman que el comportamiento sea correcto: afirman que es **el mismo**.

**Cuándo se escriben:** antes de migrar de TFM, antes de dockerizar, antes de tocar una
librería de serialización o de auth. Siempre **antes**.

**La regla que los hace valer:** durante el cambio **no se editan**. Si uno se pone rojo,
el cambio movió algo. El test no está "desactualizado".

### 2.1 Contrato OpenAPI (snapshot)

```
GET /swagger/<doc>/swagger.json  →  normalizar  →  archivo .verified.json en el repo
```

- Normalizar: ordenar claves, **quitar `info.version`** (cambia en cada release) y
  cualquier timestamp. Si no se normaliza, el diff es ruido y nadie lo lee.
- Veredicto del diff: la tabla de `migrar-dotnet` `03-plan-de-pruebas` §3 aplica igual.
  Un endpoint que desaparece, un tipo que cambia o un `required` nuevo **bloquean**.
- **No cambiar de generador de OpenAPI mientras exista el snapshot** (`E-SWAG-01`).
- Herramienta: `Verify` (MIT, [V]) o comparación manual contra un archivo. Verify es mejor
  porque el diff queda legible y el archivo `.received.` se genera solo.

### 2.2 Golden-file de respuestas

Para cada endpoint del contrato real: petición fija → respuesta esperada **byte a byte**
(tras normalizar lo que legítimamente varía: ids generados, fechas de emisión).

- Sirve contra el `TestServer` si la app arranca, y contra el ambiente si no.
- Es lo que atrapa un cambio de casing, de formato de fecha o de serializador **sin que
  nadie haya tocado un DTO** (`E-JSON-01`).

### 2.3 Serialización JSON

Un test por cada forma que el componente emite:

| Caso | Qué fija |
|---|---|
| DTO con `null` en un campo | ¿se emite `null` o se omite? |
| Enum | ¿número o string? |
| `decimal` con decimales | ¿cuántos, y con qué separador? |
| `DateTime` con y sin offset | el formato exacto de salida |
| Ciclo de referencia, si existe | que siga comportándose igual |

Si el componente usa Newtonsoft, el test debe demostrar que **sigue** usando Newtonsoft.

### 2.4 Fechas, cultura y zona horaria

El más barato y el que más veces salva. Tres tests mínimos:

1. **Formateo de monto** con la cultura que el componente usa de verdad.
2. **Parseo de una fecha desde un request** en el formato que mandan los clientes.
3. **Un `DateTime` serializado**, para fijar el formato de salida.

Y uno que no es sobre el código sino sobre el entorno: **correr la suite con
`TZ=America/Santiago` y con `TZ=UTC` y comparar**. Si el resultado cambia, el componente
tiene una dependencia del reloj del host que el contenedor va a exponer (`E-TZ-01`).

### 2.5 JWT: emisión y validación

| Test | Qué fija |
|---|---|
| Token emitido con una clave conocida → cadena esperada (o claims esperados) | El algoritmo, los claims y sus nombres |
| **Token de oro**: un token emitido con el runtime viejo, guardado como constante, debe validar | Que la migración no rompió la validación de los tokens **ya emitidos y en manos de los usuarios** |
| Token firmado con otra clave → rechazado | Que la validación de firma sigue viva |
| Token expirado → rechazado | Que el `ClockSkew` no cambió |
| Arranque sin clave de firma | Que aborta (y si hoy no aborta, el test lo documenta) |

> El **token de oro** es el test más importante de una migración de auth. Es el único que
> demuestra que los usuarios logueados no se van a caer en el cutover.

### 2.6 Cifrado: vectores

Para cada función de cifrado: **texto conocido → cifrado esperado (constante)** y
**cifrado conocido → texto esperado**. El segundo es el que importa: prueba que los datos
que ya están en la base se van a poder leer después.

Si el algoritmo está obsoleto (`RijndaelManaged`, `Rfc2898DeriveBytes` con SHA-1), el test
**no lo arregla**: lo congela y se lo pasa a cybersec con evidencia.

### 2.7 SQL generado por EF

Para las consultas LINQ complejas (`GroupBy`, `Include` filtrado, `Skip/Take`,
`string.Contains`): snapshot de `ToQueryString()`. Es un test **sin base de datos** que
atrapa `E-EF-02`, el error que "no falla, miente".

---

## 3. Familia (b) — Unitarios de lógica de negocio

**Qué entra:** cálculos, validaciones, transformaciones, reglas. Lo que tiene un
resultado que alguien puede discutir.

**Qué no entra:** verificar que un método llamó a otro método. Un test que solo verifica
interacciones con dobles se rompe con cada refactor y no detecta ningún bug de negocio.

**Casos que valen por diez:**

- Los bordes numéricos: 0, negativo, el máximo, el redondeo del medio centavo.
- Los bordes de fecha: fin de mes, año bisiesto, feriado si el negocio lo usa.
- La entrada sucia: `null`, cadena vacía, espacios, tilde, `ñ`.
- El caso que ya produjo un ticket. **Todo bug arreglado deja un test**, sin excepción.

**Dobles:** solo para las fronteras (repositorio, servicio HTTP, reloj). Nunca para
tipos propios del dominio: se construyen de verdad.

---

## 4. Familia (c) — Integración

### 4.1 `WebApplicationFactory` (`Microsoft.AspNetCore.Mvc.Testing`)

Levanta la app completa en memoria, con su DI, su pipeline y su middleware. Es la forma
de probar **lo que el consumidor ve**: status, headers, cuerpo, autorización.

La factory base de esta skill (`templates/FaastWebApplicationFactory.cs`):

- inyecta la configuración **por variables de entorno** (`Seccion__Clave`), que es la
  regla de la casa y además la única forma de probar que esa regla se cumple;
- reemplaza los `DbContext` por los del contenedor de test;
- desactiva la telemetría y cualquier salida a internet;
- fija cultura y zona horaria de forma explícita, para que el test valga lo mismo en la
  máquina de cada uno y en el runner.

### 4.2 Testcontainers (MySQL y SQL Server)

**Cuándo sí:** el repo tiene migraciones de EF o un dump de estructura. Entonces el
fixture levanta el motor real, aplica el esquema y los tests corren contra el proveedor
verdadero — que es lo único que valida traducción de LINQ, tipos y colaciones.

**Cuándo no:** si el esquema no sale del repo, el contenedor arranca vacío y el test
prueba nada. Ahí se va a la familia (d).

**Costos reales, para decirlos de entrada:**

| Punto | Realidad |
|---|---|
| Requiere Docker en la máquina y en el runner | Si el runner de CI no tiene Docker, esta familia **no corre en CI**. Se declara como gap |
| La imagen de SQL Server pesa ~1.5 GB y tarda decenas de segundos en estar lista [G] | Un `IClassFixture` por suite, **jamás un contenedor por test** |
| Licencia de la imagen de SQL Server | Es de Microsoft, con sus términos de uso de imagen de desarrollo. **Revisar antes de meterlo en CI** [G] |
| Limpieza entre tests | `Respawn`, o transacción con rollback, o base nueva por clase. Sin esto, el orden de los tests decide el resultado |

### 4.3 SQLite in-memory e EF InMemory: qué se puede afirmar con cada uno

| Proveedor | Sirve para | **No** sirve para |
|---|---|---|
| **SQLite in-memory** (`Microsoft.EntityFrameworkCore.Sqlite`) | Probar consultas LINQ reales contra un motor SQL de verdad, transacciones, constraints básicas. Rápido y sin Docker | Tipos específicos del motor (`decimal` se maneja distinto), SQL crudo de T-SQL o MySQL, funciones del motor, colaciones, esquemas/`dbo`. La conexión debe mantenerse **abierta** o la base desaparece |
| **EF InMemory** (`Microsoft.EntityFrameworkCore.InMemory`) | Nada que se parezca a una base. No es relacional: no hay constraints, no hay unicidad, no hay transacciones | **`FromSqlRaw` lanza** [G]. `Include` se comporta distinto. Microsoft mismo desaconseja usarlo para tests de acceso a datos |

**Recomendación:** InMemory **no se usa** en esta flota. Si no se puede levantar el motor
real, es preferible un doble de la interfaz del repositorio (honesto: no prueba SQL) que
un InMemory (deshonesto: parece que prueba SQL y no prueba nada).

### 4.4 HTTP externo: WireMock.Net

Solo tiene sentido si el `HttpClient` se puede redirigir (hay `IHttpClientFactory`, o la
URL base sale de configuración). Con `new HttpClient()` y URL armada adentro del método,
no hay forma de interceptar sin cambiar el código: se anota y se sale.

---

## 5. Familia (d) — Contrato contra un ambiente QA

**Qué es:** una suite que apunta a un ambiente real, hace **solo `GET`**, y compara contra
la línea base. Es el equivalente automatizable de `comparar-respuestas.sh` de `migrar-dotnet`.

**Reglas, todas duras:**

1. **Solo lectura. Solo QA.** Nunca Puente, Demo, preprod ni producción de cliente.
2. **Fuera del CI por defecto.** Se corre a mano o por `workflow_dispatch`. Un test que
   depende de un ambiente ajeno vuelve al CI intermitente y a la gente ciega.
3. **Sin credenciales en el repo.** La URL y el token salen de variables de entorno; si no
   están, los tests se saltan con motivo (`Skip`), no fallan.
4. **Categoría propia** (`Trait("categoria","contrato")`) para poder excluirla de un
   `dotnet test` normal.

**Para qué sirve de verdad:** para lo que no se puede reproducir local —stored procedures,
datos reales, integraciones de terceros—, y para tomar la línea base **antes** de migrar.

---

## 6. Familia (e) — Qué NO se testea

Decirlo explícitamente ahorra semanas.

| No se testea | Por qué |
|---|---|
| DTOs, entidades, contratos: getters y setters | No tienen comportamiento. Suben la cobertura y no detectan nada |
| El mapeo campo por campo de AutoMapper | Se cubre con **un** test: `ConfigurationProvider.AssertConfigurationIsValid()` |
| Textos de Swagger, `SwaggerOperation`, descripciones | Documentación. Cambian por edición, no por bug |
| Librerías de terceros (EF, Newtonsoft, MailKit) | Ya tienen sus tests. Se testea **nuestro uso**, no el paquete |
| Lo que hace un stored procedure por dentro | No está en el repo ni bajo control del componente. Se testea su **contrato**, no su lógica |
| El envío real de un correo, el S3 real, el WhatsApp real | Efectos externos, costo y ruido. Se testea el armado del mensaje |
| `Program.cs` línea por línea | Se cubre entero con un test de arranque de `WebApplicationFactory` |
| Código muerto | **Se borra**, no se testea. Y no en el mismo PR |
| Un porcentaje de cobertura global | Ver `05-ci-cobertura-dod.md` §2 |

---

## 7. Cuánto es suficiente

No hay número. Hay **tres preguntas** que la suite tiene que poder contestar:

1. ¿Si cambio de TFM y todo pasa, puedo afirmar que el contrato no cambió? → familia (a).
2. ¿Si alguien toca un cálculo de plata, el test lo atrapa? → familia (b) sobre lo de §1.
3. ¿Si la autorización se afloja, alguien se entera hoy y no en una auditoría? → §1 nº1.

Una suite de 40 tests que contesta las tres vale más que una de 400 que no contesta
ninguna. Y **una suite que pasa en verde con `dotnet test` sobre un repo sin proyectos de
test no contesta ninguna y además miente** — es el estado actual de `micro-api-back` [V].
