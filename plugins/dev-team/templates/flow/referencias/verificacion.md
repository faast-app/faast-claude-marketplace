# Verificacion — {dominio}/{flujo}

> SQL agrupado en tres bloques. Cada query lleva su `-- Esperado:`. Placeholders para nombres que
> cambian entre ambientes (`<TABLA>`, `<ID>`). NUNCA hosts ni credenciales reales aqui: las
> conexiones se referencian por nombre; el DBA las resuelve desde el archivo de acceso.

## 1. Solo lectura — estado antes / precondiciones (lo corre qa-backend/dba)
```sql
-- Parametro/switch: valor actual
SELECT <col> FROM <tabla_parametros> WHERE <clave> = <valor>;
-- Esperado: {valor esperado por la variante en curso}

-- Existencia de datos necesarios
SELECT COUNT(*) FROM <tabla> WHERE <condicion>;
-- Esperado: >= 1
```

## 2. Cambio guardado — SOLO lo ejecuta el DBA (nunca el flujo por su cuenta)
```sql
-- preflight: leer el valor actual (before-image)
SELECT <col> FROM <tabla_parametros> WHERE <clave_primaria> = <pk>;
-- Esperado: {valor inicial que se registra para restaurar despues}

-- cambio guardado sobre el valor previo, dry-run con rollback
BEGIN TRAN;                       -- (o BEGIN; en el motor correspondiente)
UPDATE <tabla_parametros> SET <col> = <nuevo>
 WHERE <clave_primaria> = <pk> AND <col> = <valor_previo>;
-- verificar que afecto exactamente 1 fila (@@ROWCOUNT = 1) antes de confirmar
-- ROLLBACK;   -- dry-run; cambiar a COMMIT solo tras la parada obligatoria y OK del usuario
```

## 3. Estado posterior — tras la accion clave (solo lectura)
```sql
SELECT <col> FROM <tabla_resultado> WHERE <id> = <ID>;
-- Esperado: {estado final del objeto tras el flujo}
```

## 4. Objetos que deben existir
```sql
SELECT COUNT(*) FROM <tabla> WHERE <id> = <ID>;
-- Esperado: 1 (la operacion/registro quedo creado)
```
