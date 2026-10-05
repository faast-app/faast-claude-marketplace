-- Flujo: {{dominio}}/{{flujo}} · Paso 4: VERIFICAR POSTERIOR (solo lectura)

SELECT id, estado FROM operaciones WHERE id = <ID_OPERACION>;
-- Esperado: estado = '<ESTADO_NUEVO>'
