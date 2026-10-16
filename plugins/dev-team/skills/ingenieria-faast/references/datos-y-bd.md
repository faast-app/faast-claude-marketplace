# Datos y base de datos — detalle

Complementa al agente `dba` (que es dueño de las reglas de formato de pases, idempotencia y
comparaciones en solo lectura). Lo de aqui es el oficio: modelado, rendimiento, bloqueos,
migraciones sin downtime y respaldo.

## 1. Modelado para una fintech

- PK en toda tabla; claves naturales de negocio con **UNIQUE** (folio + emisor de factura,
  `operacion_id` + tipo de giro, clave de idempotencia).
- Montos `DECIMAL(18,2)` (o escala 0 para CLP si el modelo lo fija), tasas `DECIMAL(9,6)`,
  moneda `CHAR(3)` ISO 4217. Nunca FLOAT/REAL/MONEY.
- Tiempos en UTC: `DATETIME(3)` (MySQL), `datetime2(3)`/`datetimeoffset` (SQL Server),
  `timestamptz` (Postgres). Fechas de negocio como `DATE`.
- Estados como catalogo o `CHECK` con el set completo y documentado; al agregar un estado, el
  CHECK se extiende **contra los valores reales** de cada ambiente (leccion del ledger: auditar
  todos los CHECK de una pasada antes del primer bootstrap).
- Concurrencia: columna `version INT NOT NULL DEFAULT 0` o `rowversion`.
- Auditoria: `created_at/created_by/updated_at/updated_by` + tabla de historia/auditoria
  append-only para dinero, estados y permisos.
- Borrado logico (`deleted_at`) donde la ley o el negocio exigen trazabilidad; con indices
  filtrados/parciales para que no degrade las consultas.
- PII: columnas identificadas; cifrado a nivel columna o de almacenamiento segun
  clasificacion; vistas o usuarios con enmascaramiento para soporte/reportes.

## 2. Indices y planes de ejecucion

Metodo ante una consulta lenta:
1. **Medir** con datos y volumen reales (o una copia anonimizada): tiempo, filas leidas vs
   devueltas, frecuencia (`pg_stat_statements`, `performance_schema.events_statements_summary_by_digest`
   / `sys.statements_with_runtimes_in_95th_percentile`, Query Store / `sys.dm_exec_query_stats`).
2. **Plan real**: `EXPLAIN ANALYZE` (MySQL 8.0.18+, Postgres con `BUFFERS`), plan real de SQL
   Server (`SET STATISTICS IO, TIME ON` + actual execution plan). Busca scans completos,
   estimaciones muy lejos de lo real, sorts/hash en disco, key lookups masivos.
3. **Diseñar el indice** para el patron: igualdad primero, luego rango, luego orden; prefijo
   izquierdo de indices compuestos; indices **cubrientes** (`INCLUDE` en SQL Server/Postgres)
   para lecturas calientes; selectividad real.
4. **Anti-patrones** que anulan indices: funcion sobre la columna (`DATE(created_at) = ...`,
   usar rangos), conversion implicita (`varchar` vs `nvarchar` en SQL Server, numero vs
   string en MySQL), `LIKE '%x'`, `OR` entre columnas distintas, collation distinta en un JOIN.
5. **Verificar** el plan nuevo y el costo de escritura del indice (cada indice encarece
   INSERT/UPDATE). Revisar duplicados/no usados (`sys.schema_redundant_indexes`,
   `sys.schema_unused_indexes`, `pg_stat_user_indexes.idx_scan = 0`, DMV de uso en SQL Server).
6. SQL Server: cuidado con *parameter sniffing* (planes buenos para un valor y malos para
   otro): `OPTIMIZE FOR`, `RECOMPILE` puntual o Query Store forzando plan, con evidencia. Las
   "missing index" DMVs son sugerencias, no ordenes.

Del lado del codigo (revision que el DBA pide al backend): N+1 (usar `Include`/joins o
proyecciones), `SELECT *`, paginacion sin indice de orden, consultas en bucles, traer
colecciones enteras para contar, `AsNoTracking()` en lecturas de EF.

## 3. Bloqueos y deadlocks

- Transacciones cortas; nada de I/O externo dentro; orden de acceso a tablas consistente.
- Diagnostico: MySQL `SHOW ENGINE INNODB STATUS` (ultimo deadlock),
  `performance_schema.data_locks` / `data_lock_waits`, `sys.innodb_lock_waits`; SQL Server
  `sys.dm_tran_locks`, `sys.dm_os_waiting_tasks`, deadlock graph en el XE `system_health`;
  Postgres `pg_locks` + `pg_stat_activity` (`wait_event`).
- UPDATE/DELETE masivos en **lotes** (1-10k filas) con commit por lote y pausa, por PK o
  rango indexado; nunca un UPDATE de millones en una sola transaccion en horario de operacion.
- Gap locks en MySQL (REPEATABLE READ) ante rangos sin indice: indexar el filtro.
- SQL Server: RCSI (`READ_COMMITTED_SNAPSHOT ON`) reduce bloqueos lector/escritor; es una
  decision del DBA con prueba de tempdb, no un cambio casual.
- El deadlock se reintenta en la app solo si la operacion es idempotente.

## 4. Migraciones seguras (expand / contract, sin downtime)

Regla: **la version N de la app y la N+1 deben funcionar con el mismo esquema** durante el
despliegue. Por eso un cambio incompatible se parte en pasos:

| Paso | Ejemplo: renombrar `monto` → `monto_bruto` |
|---|---|
| 1. Expand | `ADD COLUMN monto_bruto DECIMAL(18,2) NULL` (aditivo, sin default costoso) |
| 2. Dual write | La app escribe en ambas columnas; lee de la vieja |
| 3. Backfill | `UPDATE` por lotes `monto_bruto = monto WHERE monto_bruto IS NULL` |
| 4. Switch read | La app lee la nueva; verificacion de igualdad por conteo |
| 5. Contract | En un release posterior: dejar de escribir la vieja, luego `DROP` (con respaldo) |

- `NOT NULL` nuevo: agregar nullable → backfill → constraint. Un `ADD COLUMN ... NOT NULL
  DEFAULT x` puede reescribir la tabla en motores/versiones viejos.
- Online DDL: MySQL 8 `ALGORITHM=INSTANT` (agregar columnas) o `INPLACE, LOCK=NONE`;
  tablas muy grandes con `gh-ost`/`pt-online-schema-change`. Postgres `CREATE INDEX
  CONCURRENTLY`, `ADD CONSTRAINT ... NOT VALID` + `VALIDATE`. SQL Server `ONLINE = ON`
  (Enterprise) o ventana acordada.
- Cada migracion: reversible (script de reversa o paso de contract postergado), probada sobre
  un volumen realista, con su tiempo estimado y sus locks conocidos.
- **Dos mundos** (ver `dba.md`): las migraciones del repo siguen la convencion del runner; lo
  que viaja en un pase va en el formato global por tipo.

## 5. Respaldo y recuperacion

- Objetivos explicitos por BD: **RPO** (cuanto dato se puede perder) y **RTO** (cuanto tarda
  volver). Los define el negocio; el DBA los hace cumplir.
- Backups completos + logs/binlogs para recuperacion a un punto en el tiempo (PITR); en RDS,
  snapshots automaticos + retencion configurada.
- **Un backup no probado no existe:** restore periodico a un ambiente aislado, con
  verificacion (conteos, checksums, una consulta de negocio) y tiempo medido.
- Antes de un cambio riesgoso en un ambiente real (pase con UPDATE/DELETE masivo,
  migracion destructiva): respaldo de las tablas afectadas o snapshot, y el script de reversa.
- Respaldos cifrados, con acceso restringido; nunca se copian a maquinas personales.

## 6. Accesos

- Un usuario de BD por servicio, con privilegios minimos sobre su esquema. Nada de `root`/`sa`
  en aplicaciones.
- Usuarios de solo lectura para analisis, comparaciones y soporte (el DBA trabaja con ellos
  cuando no necesita escribir).
- Credenciales fuera de git (`dba-access.json` en la coordinacion, gitignored; variables de
  entorno en los servicios). En CLI, preferir `--defaults-extra-file` (MySQL), `PGPASSFILE`/
  `PGPASSWORD` en el entorno o `sqlcmd` con variable, para no dejar la clave en el historial.

## 7. Consultas de diagnostico (SQL Server)

```sql
SET STATISTICS IO, TIME ON;  -- + plan real de ejecucion
-- Top consultas por tiempo promedio
SELECT TOP 20 qs.total_elapsed_time/qs.execution_count AS avg_us, qs.execution_count,
       SUBSTRING(st.text,1,200) AS query
FROM sys.dm_exec_query_stats qs CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
ORDER BY avg_us DESC;
-- Uso de indices (seeks/scans vs updates: candidatos a no usados)
SELECT OBJECT_NAME(s.object_id) AS tabla, i.name, s.user_seeks, s.user_scans, s.user_updates
FROM sys.dm_db_index_usage_stats s
JOIN sys.indexes i ON i.object_id = s.object_id AND i.index_id = s.index_id
WHERE s.database_id = DB_ID();
-- Quien bloquea a quien
SELECT r.session_id, r.blocking_session_id, r.wait_type, r.wait_time, t.text
FROM sys.dm_exec_requests r CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.blocking_session_id <> 0;
```
MySQL adicional: `sys.statements_with_runtimes_in_95th_percentile`, `sys.innodb_lock_waits`.
