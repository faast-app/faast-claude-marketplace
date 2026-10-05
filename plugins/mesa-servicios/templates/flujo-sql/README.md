# Flujo: {{dominio}} / {{flujo}}

> Flujo de scripts REUTILIZABLE de la Mesa de Servicios. La Mesa lo ARMA y lo PREPARA para un
> caso; **nunca lo ejecuta**. Lo ejecuta quien esta autorizado (ambiente de pruebas: su
> administrador; ambiente formal: el pase del dev-team y Plataformas).
>
> **Regla global de formato (la misma que audita el release-manager):** el paquete ejecutable
> vive en `MOTOR/N_base/N_tipo.sql` — carpetas por motor (`MYSQL/`, `SQL/`, `POSTGRES/`) y base
> numerada en orden de ejecucion, archivos por tipo con prefijo numerico (`1_createTable.sql`,
> `2_alterTable_add.sql`, `3_alterTable_modify.sql`, `4_views.sql`, `5_insertInto.sql`,
> `6_procedures.sql`, `7_update.sql`, `8_delete.sql`), un archivo por tipo, nada suelto.
> Las verificaciones (solo `SELECT`) quedan FUERA del paquete ejecutable, con prefijo `00-`.
> La reversa es OTRO paquete en el mismo formato, en `reversa/`.

## Estructura
```
{{flujo}}/
├── README.md                              este archivo
├── 00-verificacion-previa.sql             SELECTs de precondicion (-- Esperado:) — NO se ejecuta como cambio
├── 00-respaldo.sql                        SELECTs de before-image — guardar la salida antes del cambio
├── MYSQL/1_db_fintec/7_update.sql         el cambio (regla global, idempotente, por clave y valor previo)
├── MYSQL/1_db_fintec/5_insertInto.sql     (si aplica: inserts con WHERE NOT EXISTS)
├── 00-verificacion-posterior.sql          SELECTs de resultado (-- Esperado:)
└── reversa/MYSQL/1_db_fintec/7_update.sql deshacer, mismo formato, mismo rigor
```

## Para que sirve
{{que resuelve, en negocio — ej. "revertir una operacion de factoring girada por error"}}

## Cuando aplica / cuando NO aplica
- Aplica: {{condiciones}}
- NO aplica: {{casos en que hay que escalar o es otro problema}}

## Parametros
| Parametro | Que es | Ejemplo (ficticio) |
|---|---|---|
| `<ID_OPERACION>` | numero de la operacion | 10432 |
| `<MOTIVO>` | motivo (va en la cabecera de cada script) | solicitud BUG-2026-003 |

## Orden (quien ejecuta lo sigue tal cual)
1. `00-verificacion-previa.sql` (solo lectura) — si algun `-- Esperado:` no se cumple, DETENER y avisar.
2. `00-respaldo.sql` (solo lectura) — guardar la salida.
3. Paquete `MYSQL/1_db_fintec/` en orden de tipo (`5_` antes que `7_`, etc.).
4. `00-verificacion-posterior.sql` (solo lectura).
5. `reversa/` SOLO si hay que deshacer.

## Riesgos y quien autoriza
- Riesgos: {{que puede pasar si se ejecuta mal}}
- Autoriza: {{rol}} · Ejecuta: {{rol autorizado}} · La Mesa NO ejecuta.
