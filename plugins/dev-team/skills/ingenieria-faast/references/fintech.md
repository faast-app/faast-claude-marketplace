# Reglas fintech — detalle

FAAST opera factoring y confirming en Chile, Peru y Colombia. Un error de redondeo, un giro
duplicado o un RUT en un log no son bugs menores: son perdida de dinero, incumplimiento
regulatorio o filtracion de datos. Estas reglas aplican a codigo NUEVO y a todo lo que la
tarea toque; en codigo legado que hace otra cosa, NO "corrijas" en silencio un calculo que
esta en produccion: reportalo (puede haber conciliaciones que dependen de el).

## 1. Vocabulario minimo del negocio

| Termino | Significado para el codigo |
|---|---|
| Factoring | El cliente (cedente) cede facturas por cobrar; FAAST anticipa un % del monto y cobra al deudor al vencimiento |
| Confirming | El pagador (empresa grande) confirma facturas de sus proveedores; el proveedor puede adelantar el cobro |
| Cedente / proveedor | Quien vende la factura y recibe el anticipo |
| Deudor / pagador | Quien debe pagar la factura al vencimiento |
| Anticipo / % de financiamiento | Porcion del monto que se adelanta |
| Tasa / diferencia de precio / comision | Componentes del costo; se calculan por dias entre giro y vencimiento |
| Giro / desembolso | Transferencia de dinero al cedente/proveedor. **Irreversible en produccion** |
| Excedente | Lo que se devuelve al cedente tras cobrar (monto − anticipo − costos) |
| Mora | Pago despues del vencimiento; genera intereses por dias de atraso |
| Cesion | Registro legal de la transferencia de la factura (en Chile, ante el SII) |

Si una regla de calculo no esta escrita en la HU, la wiki o el codigo existente: **se
pregunta**. Nunca se infiere una formula financiera.

## 2. Dinero

**Tipos:**
| Stack | Tipo | Prohibido |
|---|---|---|
| C# | `decimal` | `double`, `float` |
| Java | `BigDecimal` (con `RoundingMode` explicito; comparar con `compareTo`, no `equals`) | `double` |
| Python | `decimal.Decimal` (construir desde `str`, nunca desde `float`) | `float` |
| JS/TS | montos como **string** en el transporte; calculo con libreria decimal (`decimal.js`, `big.js`, `dinero.js`) o en centavos `bigint` | aritmetica con `number` |
| SQL | `DECIMAL(18,2)` montos en moneda; `DECIMAL(19,4)`/`(9,6)` tasas y factores | `FLOAT`, `REAL`, `MONEY` (SQL Server) en codigo nuevo |
| JSON | string (`"125000.50"`) o numero con decimales fijos acordado en el contrato | numeros que el cliente parsea a float y re-serializa |

**Moneda:** todo monto viaja con su moneda (`{ "monto": "125000", "moneda": "CLP" }`) o la
moneda es inequivoca por contrato y esta documentada. No se suman montos de monedas distintas.

| Moneda | Decimales operativos | Notas |
|---|---|---|
| CLP | 0 | Nunca mostrar ni persistir centavos. Montos grandes: usar `long`/`DECIMAL(18,0)` o `(18,2)` con escala 0 en la practica |
| PEN | 2 | |
| USD | 2 | En PE/CL hay operaciones en USD: la moneda es parte del dato, no del pais |
| COP | 2 (ISO 4217) | En la practica muchas operaciones se manejan sin centavos: la regla la fija el producto; documentala en el codigo |
| UF (CL) | 4 (unidad de fomento) | Unidad indexada; su valor del dia viene de una fuente oficial, nunca hardcodeado. Conversion a CLP redondea a 0 al final |

**Redondeo:**
- Se decide por calculo y se documenta (comentario + test): `MidpointRounding.AwayFromZero`
  (half-up, lo habitual en documentos tributarios) o `ToEven` (bancario). **El default de
  .NET `Math.Round` es ToEven** y el de `BigDecimal.setScale` depende del `RoundingMode`
  que pases: nunca dejes el default implicito.
- Se redondea **una vez, al final**, a la escala de la moneda. Los intermedios conservan
  precision (tasas diarias, factores).
- Al prorratear (repartir un total en N cuotas/facturas), la suma de las partes debe dar el
  total exacto: asigna el residuo a la ultima parte (o al de mayor monto) y pruebalo.
- Dias para intereses: base 30/360 o actual/365 segun producto — es una regla de negocio,
  no una eleccion tecnica.

## 3. Idempotencia

Toda operacion que mueve dinero o cambia el estado de una operacion financiera puede llegar
dos veces (doble clic, reintento del cliente, reintento del gateway, reentrega de cola,
callback repetido de un banco). Debe producir **un solo efecto**.

Patron estandar (API):
1. El cliente envia `Idempotency-Key: <uuid>` en POST de giros, pagos, desembolsos,
   confirmaciones, cargas de nomina.
2. El servidor guarda `(key, usuario/tenant, hash del request, estado, respuesta)` con
   **restriccion unica** sobre `(tenant, key)`.
3. Primera llegada: procesa y guarda la respuesta. Llegada repetida con mismo hash: devuelve
   la respuesta guardada (mismo status). Mismo key con otro body: `422`/`409` Problem Details.
   En proceso: `409` con `Retry-After`.
4. Expiracion de claves acorde al negocio (24 h – 7 dias), nunca menor que la ventana de
   reintentos.

Ademas, defensa en la BD: clave natural unica (p. ej. `uq_giro_operacion` sobre
`operacion_id` + `tipo`) para que un segundo giro de la misma operacion falle por
constraint aunque el codigo tenga un bug. Consumidores de colas: tabla de mensajes
procesados (inbox) por `message_id`.

## 4. Concurrencia

- **Optimistic locking** por defecto en agregados editables: `rowversion` (SQL Server),
  columna `version` entera (MySQL/Postgres) con `UPDATE ... WHERE id = ? AND version = ?` y
  verificacion de filas afectadas = 1. En EF Core: `[Timestamp]`/`IsRowVersion()` o
  `IsConcurrencyToken()`; capturar `DbUpdateConcurrencyException` → `409 Conflict`.
- En HTTP: `ETag` en GET y `If-Match` en PUT/PATCH de recursos sensibles → `412` si no calza.
- **Transiciones de estado** con guarda en la misma sentencia:
  `UPDATE operacion SET estado='GIRADA' WHERE id=? AND estado='APROBADA'`; 0 filas = otro
  proceso gano → error de negocio, no reintento ciego.
- **Pessimistic locking** (`SELECT ... FOR UPDATE`, `UPDLOCK`) solo en secciones cortas y con
  orden de bloqueo consistente; nunca con una llamada externa dentro.
- Jobs (Hangfire/cron): una sola instancia por storage o lock distribuido; el job es
  idempotente por diseño (puede correr dos veces).

## 5. Transacciones y consistencia

- Una unidad de negocio = una transaccion **corta**. Nada de HTTP, colas o correo dentro de
  una transaccion de BD abierta.
- Efectos externos (evento a otro servicio, correo, llamada a banco) por **outbox**: se
  escribe el mensaje en la misma transaccion que el cambio y un publicador lo envia despues
  (con reintentos e idempotencia en el receptor).
- Entre microservicios no hay transacciones distribuidas: sagas con compensaciones
  explicitas y estados intermedios visibles (`PENDIENTE_GIRO`, `GIRO_RECHAZADO`).
- Nivel de aislamiento: el default del motor salvo razon documentada. En SQL Server
  considerar RCSI (decision del DBA, no del dev).

## 6. Auditoria

En toda operacion sobre dinero, estados de operaciones, limites, tasas, permisos/roles y
datos de clientes:
- **Quien** (id de usuario o de sistema/servicio), **cuando** (UTC), **que** (accion +
  entidad + id), **desde donde** (ip/canal/correlation id), **antes/despues** de los campos
  cambiados.
- Tabla de auditoria append-only (o tablas `_hist`), nunca se actualiza ni se borra desde la
  app. Las columnas `created_at/created_by/updated_at/updated_by` no reemplazan la auditoria.
- La auditoria no guarda secretos y enmascara PII que no sea necesaria para el proposito.
- Un fallo al auditar una operacion de dinero es un fallo de la operacion (misma transaccion).

## 7. Fechas, horas y zonas

- Almacenamiento y transporte en **UTC** (`DateTimeOffset`/`datetime2`/`timestamptz`/ISO 8601
  con `Z`). Zona del pais solo para reglas y presentacion.
- Zonas IANA: Chile `America/Santiago` (tiene horario de verano, cambia dos veces al año;
  Magallanes `America/Punta_Arenas` no), Peru `America/Lima` (UTC−5 fijo), Colombia
  `America/Bogota` (UTC−5 fijo). En Windows/.NET usar `TimeZoneInfo.FindSystemTimeZoneById`
  con IDs IANA (soportado en .NET 6+ con ICU) — verifica la imagen (ICU presente,
  `InvariantGlobalization`).
- **Fecha de negocio** (vencimiento, fecha de giro, fecha de emision) es una fecha sin hora
  (`DateOnly`, `LocalDate`, `date`, `DATE`). No la representes como medianoche UTC: en
  America/* se corre un dia al mostrarla.
- "Hoy" depende del pais: el corte de dia para giros se calcula en la zona del pais.
- Reloj inyectable (`TimeProvider` en .NET 8+, `Clock` en Java, `freezegun`/inyeccion en
  Python, fake timers en JS): sin el, no hay tests deterministas de vencimientos.
- **Dias habiles y feriados** por pais (y feriados regionales en Chile): de una tabla o
  servicio mantenido, nunca hardcodeados en el codigo. Un vencimiento en feriado se mueve
  segun la regla del producto (siguiente habil normalmente).
- Cultura: parseo y formato con cultura explicita (`CultureInfo.InvariantCulture` para
  datos, `es-CL`/`es-PE`/`es-CO` solo para presentacion). Un `decimal.Parse("1.000")` con
  cultura del servidor es un bug de un orden de magnitud.

## 8. Datos personales y secretos

**Identificadores por pais (validacion de formato; la verdad la da la fuente oficial):**
| Pais | Documento | Formato | Validacion |
|---|---|---|---|
| CL | RUT/RUN | `12.345.678-5` (cuerpo + DV) | DV modulo 11 (`0-9` o `K`); normalizar sin puntos y con guion; DV en mayuscula |
| PE | DNI | 8 digitos | longitud/numerico |
| PE | RUC | 11 digitos (10/15/17/20…) | digito verificador modulo 11 |
| CO | NIT | 9-10 digitos + DV | DV con pesos primos (algoritmo DIAN) |
| CO | CC | 6-10 digitos | longitud/numerico |

**Reglas:**
- Minimo necesario: no pidas ni guardes datos que el proceso no usa.
- **Nunca en logs ni en mensajes de error**: documentos completos, cuentas bancarias,
  correos, telefonos, montos asociados a una persona, tokens, claves, cookies, cabeceras
  `Authorization`. Enmascara (`12.***.***-5`, `****1234`) o usa ids internos.
- Configura la redaccion en el logger (destructuring policies en Serilog, `redact` en Pino,
  processors en structlog) en vez de confiar en cada `log` individual.
- Fixtures y seeds con datos **sinteticos** (RUT validos generados, nombres ficticios).
  Datos de produccion bajan a QA solo anonimizados y con autorizacion.
- Secretos solo por variables de entorno / secret store; jamas en el repo, en
  `appsettings.json` con valores, en la imagen ni en el historial de git. Si un secreto se
  commiteo: se rota, no basta con borrarlo.
- Exportaciones (Excel/CSV/PDF) con datos de clientes: solo por endpoints autorizados y
  auditados.

## 9. Ambientes

La clase de cada ambiente (`config.json` → `ambientes`: `pruebas` | `productivo`) decide
cuanta ceremonia lleva una accion de negocio. En pruebas, girar, pagar o aprobar es una
accion de prueba normal. En productivo, toda accion sensible requiere autorizacion explicita
del usuario. El codigo nunca decide el ambiente por el hostname: lo recibe por configuracion.
