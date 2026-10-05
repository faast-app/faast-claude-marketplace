-- Flujo: {{dominio}}/{{flujo}} · Paso 3: CAMBIO (idempotente, guardado por clave y valor previo)
-- Base destino: <BASE> · Tipo: 7_update · Fuente: <ID_SOLICITUD> · Autoriza: <AUTORIZA>
-- Idempotencia: el WHERE exige el valor previo; una segunda ejecucion no afecta filas.

UPDATE operaciones
SET estado = '<ESTADO_NUEVO>'
WHERE id = <ID_OPERACION>
  AND estado = '<ESTADO_PREVIO>';
-- Esperado: 1 fila afectada (0 si ya se ejecuto)
