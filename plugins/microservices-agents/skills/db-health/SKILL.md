---
description: Ejecuta health check de base de datos del servicio actual. Usa el agente dba.
---

Ejecuta health check de la base de datos. Pregunta que revisar:

1. **schema** — Revisar esquema actual (tablas, columnas, tipos, constraints)
2. **indexes** — Inventario de indices, detectar no usados y redundantes
3. **slow-queries** — Analizar queries lentas (slow query log o pg_stat_statements)
4. **size** — Tamaño de tablas e indices
5. **migrations** — Revisar migraciones pendientes o aplicadas recientemente
6. **security** — Usuarios, privilegios, conexiones SSL
7. **full** — Todo lo anterior

Invoca al agente `dba` para ejecutar el health check.

Para cada hallazgo generar recomendacion accionable.
Generar reporte en `.coordination/handoffs/dba-to-lead-{fecha}.md`
