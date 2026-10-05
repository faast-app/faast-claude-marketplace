-- =====================================================================
-- Base destino : db_fintec            Motor : MySQL
-- Tipo         : 7_update             Fuente: <ID_SOLICITUD> (<MOTIVO>)
-- Autoriza     : <AUTORIZA>           Ejecuta: <ROL_AUTORIZADO> — la Mesa NO ejecuta
-- Idempotencia : el WHERE exige la clave primaria Y el valor previo; una segunda
--                ejecucion no afecta filas. Sin nombres de esquema; valores absolutos.
-- =====================================================================

UPDATE operaciones
   SET estado = '<ESTADO_NUEVO>'
 WHERE id = <ID_OPERACION>
   AND estado = '<ESTADO_PREVIO>';
-- Esperado: 1 fila afectada (0 si ya se ejecuto)
