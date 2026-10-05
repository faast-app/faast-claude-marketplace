-- Flujo: {{dominio}}/{{flujo}} · VERIFICACION PREVIA (solo lectura; NO forma parte del paquete ejecutable)
-- Fuente: <ID_SOLICITUD> · Si algun resultado no coincide con "Esperado", DETENER y avisar.

SELECT id, estado, fecha, monto FROM operaciones WHERE id = <ID_OPERACION>;
-- Esperado: 1 fila, estado = '<ESTADO_PREVIO>'

SELECT COUNT(*) AS dependientes FROM cuotas WHERE operacion_id = <ID_OPERACION>;
-- Esperado: <N_CUOTAS>
