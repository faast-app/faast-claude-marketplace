-- Flujo: {{dominio}}/{{flujo}} · Paso 5: REVERSA (solo si hay que deshacer; idempotente)
-- Base destino: <BASE> · Tipo: 7_update · Fuente: <ID_SOLICITUD>

UPDATE operaciones
SET estado = '<ESTADO_PREVIO>'
WHERE id = <ID_OPERACION>
  AND estado = '<ESTADO_NUEVO>';
-- Esperado: 1 fila afectada (0 si ya se revirtio)
