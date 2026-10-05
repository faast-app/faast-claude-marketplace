---
name: flujos-sql
description: Como el DBA de mesa arma scripts y flujos de scripts SIN ejecutar escrituras - regla global de formato (carpetas por motor y base, archivos numerados por tipo, idempotencia total con guards, UPDATE/DELETE por clave primaria y valor previo, sin esquemas calificados, FKs por clave natural, UTF-8), el paquete por solicitud (estado actual, scripts, verificacion, reversa, README), los flujos reutilizables parametrizados en flujos-sql/{dominio}/{flujo}/ (verificar, respaldo, cambio, verificar posterior, reversa), el diagnostico en solo lectura, la checklist que audita el release-manager, y quien ejecuta (nunca la Mesa). Cargala al armar un script, un flujo o un paquete de datos.
---

# Flujos de scripts — armar sin ejecutar (DBA de mesa)

La Mesa resuelve muchos pedidos con datos, pero **jamas ejecuta escrituras**: arma scripts
correctos, seguros e idempotentes, los empaqueta con su verificacion y su reversa, y los
entrega a quien esta autorizado a ejecutarlos (Plataformas, el DBA titular, o el canal de pase
del dev-team). La conexion del DBA de mesa es de solo lectura y sirve para diagnosticar y para
que el script apunte exactamente a lo correcto.

## Principios
1. **Cero escritura.** Solo `SELECT`/`SHOW`/`DESCRIBE`/`EXPLAIN` contra bases reales. Ni "en una
   transaccion que deshago", ni "en pruebas", ni "para validar". La validacion es estatica o en
   una base local desechable (`config.json` → `sql.sandbox`), nunca en un ambiente real.
2. **Diagnosticar antes de armar.** Confirmar que el objeto existe, su estado actual, que depende
   de el y cuantas filas tocaria el cambio. Eso es el before-image (`00-estado-actual.md`).
3. **Idempotente y guardado.** Un script se puede correr dos veces sin daño: INSERT con guard,
   UPDATE/DELETE por clave primaria **y** por el valor previo esperado, ALTER con guard.
4. **Todo cambio viene con su verificacion y su reversa.** Sin reversa no hay paquete.
5. **La misma regla de formato que audita el release-manager del dev-team.** Si el paquete va a
   un ambiente formal, entra al pase y se audita como cualquier otro; un paquete que no cumple
   se rechaza.

## Regla global de formato
```
{paquete}/
├── MYSQL/1_db_fintec/5_insertInto.sql · 7_update.sql · 8_delete.sql
├── SQL/1_db_interface/7_update.sql
└── (solo los motores/bases/tipos que apliquen)
```
- Carpetas por **MOTOR** (`MYSQL/`, `SQL/`, `POSTGRES/`) y por **BASE numerada** en orden de
  ejecucion (`1_db_fintec/`, `2_db_dicom/`). Nunca scripts sueltos en la raiz; nunca carpetas por
  ticket o fecha.
- Archivos por **TIPO** con prefijo numerico, un archivo por tipo: `1_createTable.sql`,
  `2_alterTable_add.sql`, `3_alterTable_modify.sql`, `4_views.sql`, `5_insertInto.sql`,
  `6_procedures.sql`, `7_update.sql`, `8_delete.sql`.
- **Cabecera** en cada archivo: base destino, tipo, fuente (`-- Fuente: PRY-2026-014`), nota de
  idempotencia, quien autoriza.
- `CREATE TABLE IF NOT EXISTS`; sin `AUTO_INCREMENT=N`; ALTERs con guard por `information_schema`
  + `PREPARE`/`EXECUTE`.
- Cada `INSERT` con `WHERE NOT EXISTS` (conteo de INSERTs = conteo de guards); sin multi-row
  `VALUES` sin guard; CERO `ON DUPLICATE KEY UPDATE` / `REPLACE INTO`.
- `UPDATE`/`DELETE` con `WHERE` por clave primaria **y** valor previo (`AND estado = 'APROBADA'`),
  valores absolutos, nunca relativos ("+1") ni masivos sin lista explicita de claves.
- Sin nombres de esquema/base calificando tablas; FKs a catalogos externos por clave natural
  (`SELECT id FROM catalogo WHERE codigo = 'X'`), no por id literal.
- Sin charset/collation hardcodeado (excepcion marcada `-- charset-exception: <motivo>`); UTF-8
  sin mojibake (grep de `Ã`, `Â`, `�`), acentos y eñes intactos.
- Vistas `CREATE OR REPLACE VIEW` sin DEFINER; procedures con `DROP … IF EXISTS`.

## Paquete por solicitud (`.mesa/solicitudes/{ID}/scripts/`)
```
00-estado-actual.md     before-image: SELECTs de diagnostico con su resultado (sin datos personales), conteos, dependencias
MYSQL/… · SQL/…         los scripts por motor/base/tipo (regla global)
VERIFICACION.sql        SELECTs antes/despues con "-- Esperado:" por cada cambio
REVERSA.sql             deshacer cada cambio, tambien guardado e idempotente
README.md               en negocio: que hace, sobre que (IDs), cuantas filas, riesgos, orden de ejecucion, quien autoriza, QUIEN EJECUTA, como se verifica despues
```

## Flujos reutilizables (`.mesa/flujos-sql/{dominio}/{flujo}/`)
Cuando un pedido se repite, se deja parametrizado para que la proxima vez sea rellenar y entregar:
```
flujos-sql/factoring/revertir-operacion/
├── README.md                 para que sirve · cuando aplica · parametros (<ID_OPERACION>, <MOTIVO>) · riesgos · quien autoriza · quien ejecuta · casos en que NO aplica
├── 01-verificar-estado.sql   precondiciones (-- Esperado: estado = 'GIRADA', 1 fila)
├── 02-respaldo.sql           before-image de todo lo que se tocara
├── 03-revertir.sql           el cambio (segun regla: 7_update / 8_delete), guardado por PK + valor previo
├── 04-verificar-posterior.sql
└── 05-reversa.sql            deshacer (guardado)
```
- Parametros como placeholders explicitos `<NOMBRE>`; nunca valores de un caso pegados en el flujo.
- `/mesa-servicios:sql flujo preparar {dominio}/{flujo} {ID}` rellena los parametros para un caso
  y deja el paquete en la solicitud; el flujo base no se modifica.
- Un flujo se versiona con la Mesa (`.mesa/flujos-sql/` si se versiona); los paquetes de casos
  concretos viven en cada solicitud.

## Diagnostico en solo lectura (lo que SI se ejecuta)
```sql
-- existencia y estado
SELECT id, estado, fecha, monto FROM operaciones WHERE id = <ID_OPERACION>;        -- Esperado: 1 fila
-- dependencias (que apunta a ella)
SELECT COUNT(*) FROM cuotas WHERE operacion_id = <ID_OPERACION>;
SELECT COUNT(*) FROM giros  WHERE operacion_id = <ID_OPERACION>;
-- cuantas filas tocaria el cambio (debe coincidir con lo que el cliente espera)
SELECT COUNT(*) FROM operaciones WHERE id = <ID_OPERACION> AND estado = 'GIRADA';  -- Esperado: 1
```
Si el conteo no coincide con lo esperado (el cliente cree que esta en un estado y no lo esta),
se reporta: puede ser otro problema; nunca se "fuerza" el script.

## Checklist de entrega (lo que audita el release-manager)
- [ ] Carpetas por motor y base numerada; archivos por tipo con prefijo; nada suelto
- [ ] Cabecera por archivo con fuente y autorizacion
- [ ] INSERTs = guards; cero `ON DUPLICATE`/`REPLACE`; UPDATE/DELETE por PK + valor previo
- [ ] Sin esquemas calificados; FKs por clave natural; UTF-8 sin mojibake
- [ ] `VERIFICACION.sql` con esperados y `REVERSA.sql` presentes
- [ ] `README.md` en negocio con filas afectadas, riesgos, quien autoriza y quien ejecuta
- [ ] Before-image en `00-estado-actual.md` sin datos personales
- [ ] Ninguna escritura ejecutada por la Mesa; validacion estatica o sandbox local

## Quien ejecuta
Nunca la Mesa. Ambiente de pruebas: quien administre ese ambiente, con el paquete y el README.
Ambiente formal (certificacion, puente, demo, preprod, produccion): el paquete entra al pase del
dev-team (`/dev-team:pase`), el release-manager lo audita y Plataformas lo ejecuta. La Mesa
registra en el ticket quien ejecuto y cuando, y verifica despues en solo lectura.
