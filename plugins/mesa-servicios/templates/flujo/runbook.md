# Runbook: {{titulo del flujo}}

> Pasos exactos. Cada paso dice rol, pantalla, acciones y resultado esperado. Credenciales por
> nombre de variable, nunca aqui. "Escribe algo: si" = PARADA con OK del usuario de mesa.

## Pre-requisitos
- Ambiente: {{pruebas|produccion}} · Perfil: {{VAR_USUARIO}} · Precondiciones verificadas (FLUJO.md)

## Pasos
### Paso 1: {{rol}} ({{VAR_USUARIO}})
1. Menu {{Modulo → Pantalla}}.
2. {{accion: filtrar por cliente = <cliente>, rango <desde>…}}
**Resultado esperado:** {{lo que se ve: listado, columnas, totales}}
**Escribe algo:** no

### Paso 2: …
**Escribe algo:** si → PARADA (OK del usuario de mesa en el momento)

## Tiempos y trampas
| Momento | Accion | Tiempo tipico | Ojo con |
|---------|--------|---------------|---------|

## Fuentes
- {{grabacion FLUJO-…-grabacion, fecha}}
