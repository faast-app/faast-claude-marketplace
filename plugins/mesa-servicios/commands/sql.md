---
description: El DBA de mesa (CERO ESCRITURA) diagnostica en solo lectura y ARMA scripts idempotentes por la regla global de formato - paquete por solicitud (estado actual, scripts por motor/base/tipo, verificacion, reversa, README) o flujos reutilizables por carpeta (flujos-sql/{dominio}/{flujo}/). Nunca ejecuta un script contra ninguna base; los entrega para que los ejecute el autorizado. Uso - /mesa-servicios:sql {subcomando}
argument-hint: 'consultar {conexion} "{pregunta en negocio}" | script {ID} | flujo crear {dominio}/{flujo} | flujo listar | flujo preparar {dominio}/{flujo} {ID} | validar {ID}'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# SQL: armar scripts sin ejecutarlos

Pedido: $ARGUMENTS

**REGLA DE ESTE COMANDO (dura):** el DBA de mesa tiene **cero escritura**. Solo ejecuta `SELECT`
para diagnosticar; arma INSERT/UPDATE/DELETE idempotentes pero **jamas los corre** contra una
base. La ejecucion es de quien esta autorizado (ambiente de pruebas: su administrador; ambiente
formal: el pase del dev-team y Plataformas). Todo via el agente `dba-mesa` con la skill `flujos-sql`.

## `consultar {conexion} "{pregunta}"` — diagnostico en solo lectura
Traduce una pregunta de negocio ("¿en que estado esta la operacion 10432 de ACME?", "¿cuantas
cesiones vencidas tiene el cliente X?") a `SELECT`s sobre la conexion configurada
(`.mesa/db-access.json`, por nombre; contraseña por variable de entorno). Devuelve el resultado
en lenguaje de negocio, sin datos personales de personas. Si la cuenta tiene permisos de
escritura, lo reporta como riesgo. Nada se escribe.

## `script {ID}` — paquete de scripts para una solicitud
1. Prerequisito: la solicitud tiene cerrado QUE objeto (IDs reales), estado actual → deseado,
   por que, quien autoriza y ambiente (`preguntas.md`). Si falta, volver a `analizar`.
2. **Plan primero**: que se va a tocar, cuantas filas se espera, riesgos, quien ejecutara. OK.
3. `dba-mesa`: diagnostico en lectura (`00-estado-actual.md` con before-image y conteos) →
   scripts por la regla global (`MYSQL/1_base/7_update.sql`…, guards, PK + valor previo) →
   `VERIFICACION.sql` + `REVERSA.sql` + `README.md` en negocio → checklist.
4. Salida: ruta del paquete en `.mesa/solicitudes/{ID}/scripts/`, filas afectadas, riesgos y
   **quien debe ejecutarlo**. Si el pedido se repite, propone dejarlo como flujo.

## `flujo crear {dominio}/{flujo}` — flujo reutilizable
Crea `.mesa/flujos-sql/{dominio}/{flujo}/` desde `templates/flujo-sql/` (README con parametros,
`01-verificar-estado.sql`, `02-respaldo.sql`, `03-{cambio}.sql`, `04-verificar-posterior.sql`,
`05-reversa.sql`) con placeholders `<PARAMETRO>`; el `dba-mesa` lo completa con el conocimiento
del proceso (faast-brain) y el diagnostico en lectura de un caso real. Ejemplo:
`factoring/revertir-operacion`.

## `flujo listar` — flujos disponibles
Tabla: dominio, flujo, para que sirve, parametros, ultima actualizacion.

## `flujo preparar {dominio}/{flujo} {ID}` — aplicar un flujo a un caso
Rellena los parametros con los datos cerrados de la solicitud, verifica en lectura las
precondiciones (`01-verificar-estado.sql` con sus esperados) y deja el paquete listo en
`.mesa/solicitudes/{ID}/scripts/`. El flujo base no se modifica.

## `validar {ID}` — checklist del paquete
Revisa el paquete contra la checklist que audita el release-manager (motor/base/tipo, guards,
PK + valor previo, sin esquemas, UTF-8, verificacion y reversa, README). Validacion estatica;
solo si `config.json` → `sql.sandbox` define una base local desechable en Docker, se puede
correr ahi para sintaxis. Nunca en un ambiente real.

## Reglas
- Cero escritura contra cualquier base, sin excepcion.
- Scripts idempotentes y guardados; verificacion y reversa siempre; regla global de formato.
- Sin credenciales ni datos personales en scripts, README ni chat.
- La ejecucion la hace el autorizado; la Mesa registra en el ticket quien y cuando.
