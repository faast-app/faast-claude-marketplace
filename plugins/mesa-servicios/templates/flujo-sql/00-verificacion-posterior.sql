-- Flujo: {{dominio}}/{{flujo}} · VERIFICACION POSTERIOR (solo lectura)
SELECT id, estado FROM operaciones WHERE id = <ID_OPERACION>;
-- Esperado: estado = '<ESTADO_NUEVO>'
