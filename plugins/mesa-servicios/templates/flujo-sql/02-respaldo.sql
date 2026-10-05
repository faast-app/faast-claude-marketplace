-- Flujo: {{dominio}}/{{flujo}} · Paso 2: RESPALDO (before-image, solo lectura)
-- Guardar la salida completa de estas consultas antes de ejecutar el paso 3.

SELECT * FROM operaciones WHERE id = <ID_OPERACION>;
SELECT * FROM cuotas      WHERE operacion_id = <ID_OPERACION>;
