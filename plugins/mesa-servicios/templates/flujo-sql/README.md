# Flujo: {{dominio}} / {{flujo}}

> Flujo de scripts REUTILIZABLE de la Mesa de Servicios. La Mesa lo ARMA y lo PREPARA para un
> caso; **nunca lo ejecuta**. Lo ejecuta quien esta autorizado (ambiente de pruebas: su
> administrador; ambiente formal: el pase del dev-team y Plataformas).

## Para que sirve
{{que resuelve, en negocio — ej. "revertir una operacion de factoring que fue girada por error"}}

## Cuando aplica / cuando NO aplica
- Aplica: {{condiciones}}
- NO aplica: {{casos en que hay que escalar o es otro problema}}

## Parametros
| Parametro | Que es | Ejemplo (ficticio) |
|---|---|---|
| `<ID_OPERACION>` | numero de la operacion | 10432 |
| `<MOTIVO>` | motivo del cambio (va en la cabecera) | solicitud BUG-2026-003 |

## Orden de ejecucion (quien ejecuta lo sigue tal cual)
1. `01-verificar-estado.sql` — precondiciones; si algun `-- Esperado:` no se cumple, DETENER y avisar.
2. `02-respaldo.sql` — before-image; guardar la salida.
3. `03-{{cambio}}.sql` — el cambio (idempotente, por clave y valor previo).
4. `04-verificar-posterior.sql` — confirmar el resultado.
5. `05-reversa.sql` — SOLO si hay que deshacer.

## Riesgos y quien autoriza
- Riesgos: {{que puede pasar si se ejecuta mal}}
- Autoriza: {{rol del cliente / interno}} · Ejecuta: {{rol autorizado}}
