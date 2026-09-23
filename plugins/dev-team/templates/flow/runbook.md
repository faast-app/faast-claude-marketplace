# Runbook: {titulo del flujo} — variante {a}

> Pasos numerados de ejecucion. Cada paso nombra el rol/usuario, las acciones exactas y el
> RESULTADO ESPERADO verificable (endpoint + codigo, mensaje de UI, estado de BD). Las
> credenciales se leen de los archivos de acceso por nombre, nunca se escriben aqui.

## 0. Pre-requisitos
- Ambiente: {qa} · Parametros/switches en el valor esperado (ver FLUJO.md) · Datos de prueba listos

## Pasos

### Paso 1 (o "Estacion 1"): {rol} ({usuario, por nombre de variable})
**Login:** {como entrar, con que cuenta}
1. Menu {Modulo → Pantalla}.
2. {accion: llenar campo, elegir opcion, presionar boton...}
3. {Grabar / Continuar}.
**Resultado esperado:**
- {VERBO} {endpoint} → **200** (o el codigo correcto)
- Mensaje en pantalla: "{texto exacto}"
- Estado de BD: {tabla/objeto} queda en {estado}
**Parada obligatoria:** {si este paso escribe algo sensible — pedir OK del usuario en el momento}

### Paso 2: {rol} ({usuario})
...

## Conteos antes/despues (verificacion del resultado)
| Objeto | Antes | Despues |
|--------|-------|---------|
| {tabla/entidad} | {n} | {n+1} |

## Tiempos y gotchas
| Momento | Accion | Tiempo tipico | Notas |
|---------|--------|---------------|-------|
| {paso}  | {que}  | {seg/min}     | {ojo con...} |

## Fuentes
- {de donde salio este runbook: grabacion FLOW-..., handoff, doc}
