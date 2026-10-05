---
description: Flujos propios de la Mesa - registrar y re-ejecutar operaciones del dia a dia (buscar operaciones de un cliente, verificar el estado de una cesion, revisar una bandeja, preparar un reporte) en carpetas flujos/{dominio}/{flujo}/, con pasos numerados, verificaciones de solo lectura, evidencia grabada y paradas antes de cualquier accion que escriba; permite ambientes productivos con autorizacion registrada. Uso - /mesa-servicios:flujo {crear|grabar|listar|verificar|ejecutar} {dominio}/{flujo} [args]
argument-hint: 'crear {dominio}/{flujo} | grabar {dominio}/{flujo} | listar | verificar {dominio}/{flujo} | ejecutar {dominio}/{flujo} [cliente=ACME …] [--ambiente pruebas|produccion]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Flujo: lo que la Mesa hace a diario, registrado y repetible

Pedido: $ARGUMENTS

Sigue la skill `flujos-mesa`. Los flujos viven en `.mesa/flujos/{dominio}/{flujo}/`; la evidencia
de cada corrida en `.mesa/evidencia/FLUJO-…/`. Tu coordinas: la UI la ejecuta `qa-negocio`
(grabando todo), las verificaciones `SELECT` el `dba-mesa`; nunca escribes por SQL dentro de un flujo.

## `crear {dominio}/{flujo}` — dar de alta
1. Copiar el scaffold de `templates/flujo/` a `.mesa/flujos/{dominio}/{flujo}/` (FLUJO.md,
   referencias/datos.md, referencias/verificacion.md, runbook.md, steps.yaml).
2. Entrevistar al usuario de mesa en pocas preguntas: que hace el flujo (en negocio), clase
   (consulta / accion), ambiente (pruebas / produccion y que se permite), argumentos, perfiles por
   paso (por nombre de variable), y donde hay pasos que escriben (paradas).
3. Dejar el runbook con lo que ya se conoce; lo que falta se completa al `grabar`. No inventar
   pantallas ni consultas: lo no confirmado va en "No confirmado".

## `grabar {dominio}/{flujo}` — recorrerlo y capturar lo real
Con el usuario de mesa presente, `qa-negocio` recorre el flujo por la UI con el Playwright MCP:
captura por paso, `browser_generate_locator` (para `steps.yaml`), `browser_network_requests`
(resultado esperado real), y vuelca todo al runbook. Las verificaciones de datos observadas van
a `referencias/verificacion.md` como `SELECT` con `-- Esperado:`. En produccion: solo clase
consulta, o accion con parada y autorizacion registrada. Evidencia de la grabacion en
`.mesa/evidencia/FLUJO-…-grabacion/`.

## `listar` — flujos registrados
Tabla: dominio, flujo, clase, ambiente permitido, argumentos, ultima verificacion, si tiene `steps.yaml`.

## `verificar {dominio}/{flujo}` — precondiciones (solo lectura)
Sin ejecutar el flujo: `dba-mesa` corre `referencias/verificacion.md` §1 (solo `SELECT`) y se
comprueba que existan los perfiles y accesos. Reporta listo / no listo por precondicion. No
escribe nada. Ideal antes de `ejecutar`, sobre todo en produccion.

## `ejecutar {dominio}/{flujo} [args] [--ambiente …]` — correrlo con garantias
**PLAN PRIMERO**: mostrar clase, ambiente, argumentos, pasos que escriben (paradas) y que se
grabara; en produccion, pedir y REGISTRAR la autorizacion (quien, cuando, para que caso) en
`00-ANTES.md`. Con el OK:
1. Fase 1 — `dba-mesa` verifica precondiciones (`SELECT`); si algo no cumple, DETENIDO.
2. Fase 2 — `qa-negocio` ejecuta los pasos del runbook en la UI, grabando (traza, video con
   capitulos, capturas resaltadas, consola/red). Antes de CADA paso que escribe: parada y OK
   escrito del usuario de mesa en el momento. Un intento por paso; a la primera falla, detener
   y reportar (sin reintentos: en produccion cada reintento puede crear datos reales).
3. Fase 3 — verificar resultado (`SELECT` §2 + UI).
4. Fase 4 — `informe-flujo.md` (resultado por paso, verificaciones, veredicto COMPLETADO /
   DETENIDO EN PASO N / BLOQUEADO) + `INDEX.md`. Si el flujo alimenta una solicitud, enlazar
   la evidencia desde ella.

## Salida
```
Flujo factoring/buscar-operaciones-cliente — cliente=ACME — produccion (consulta, autorizado por … el …)
COMPLETADO · 4 pasos · 5 capturas, traza, video 40 s · verificaciones: 2/2 OK
Resultado: 12 operaciones vencidas (ver 03-listado.png) · Evidencia: .mesa/evidencia/FLUJO-…/
```

## Reglas
- DBA solo `SELECT` dentro de un flujo; cambios en datos → `/mesa-servicios:sql` (lo ejecuta el autorizado).
- Produccion: autorizacion registrada por corrida; acciones solo las declaradas; parada por escritura.
- Secretos por nombre de variable; datos personales redactados en capturas.
- Flujos versionados; evidencia fuera de git.
