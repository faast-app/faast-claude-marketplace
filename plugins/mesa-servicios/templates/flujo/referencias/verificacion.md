# Verificacion — {{dominio}}/{{flujo}}  (SOLO SELECT; las corre el dba-mesa)

## 1. Precondiciones
```sql
SELECT COUNT(*) FROM clientes WHERE codigo = '<CLIENTE>' AND activo = 1;
-- Esperado: 1
```

## 2. Resultado (despues de ejecutar el flujo)
```sql
SELECT COUNT(*) FROM operaciones WHERE cliente = '<CLIENTE>' AND estado = '<ESTADO>';
-- Esperado: coincide con lo que muestra la pantalla
```
