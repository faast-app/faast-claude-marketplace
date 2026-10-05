-- Flujo: {{dominio}}/{{flujo}} · Paso 1: VERIFICAR ESTADO (solo lectura)
-- Fuente: <ID_SOLICITUD> · Autoriza: <AUTORIZA>
-- Si algun resultado no coincide con "Esperado", DETENER y avisar: no ejecutar los pasos siguientes.

SELECT id, estado, fecha, monto
FROM operaciones
WHERE id = <ID_OPERACION>;
-- Esperado: 1 fila, estado = '<ESTADO_PREVIO>'

SELECT COUNT(*) AS dependientes
FROM cuotas
WHERE operacion_id = <ID_OPERACION>;
-- Esperado: <N_CUOTAS>
