-- =====================================================================
-- REVERSA del flujo {{dominio}}/{{flujo}} — mismo formato y rigor que el cambio
-- Base destino : db_fintec            Motor : MySQL
-- Tipo         : 7_update             Fuente: <ID_SOLICITUD> (reversa)
-- Idempotencia : por clave primaria Y valor previo (el estado nuevo); valores absolutos.
-- =====================================================================

UPDATE operaciones
   SET estado = '<ESTADO_PREVIO>'
 WHERE id = <ID_OPERACION>
   AND estado = '<ESTADO_NUEVO>';
-- Esperado: 1 fila afectada (0 si ya se revirtio)
