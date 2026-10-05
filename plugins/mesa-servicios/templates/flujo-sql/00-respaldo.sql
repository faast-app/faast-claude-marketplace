-- Flujo: {{dominio}}/{{flujo}} · RESPALDO / before-image (solo lectura). Guardar la salida ANTES del cambio.
SELECT * FROM operaciones WHERE id = <ID_OPERACION>;
SELECT * FROM cuotas      WHERE operacion_id = <ID_OPERACION>;
