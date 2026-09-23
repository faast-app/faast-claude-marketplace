---
description: Registra y re-ejecuta flujos de negocio paso a paso, ordenados en carpetas flujos/{dominio}/{flujo}/ - crea el flujo, lo graba mientras lo recorres (capturando pasos y evidencia), lo lista, verifica sus precondiciones, o lo ejecuta con puntos de parada, cambios de BD guardados, verificacion y evidencia. Uso - /dev-team:flow {subcomando}
argument-hint: 'crear {dominio}/{flujo} | grabar {dominio}/{flujo} | listar | verificar {dominio}/{flujo} | ejecutar {dominio}/{flujo} [args]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Flow: registrar y re-ejecutar flujos de negocio

Pedido: $ARGUMENTS

Este comando administra los flujos de negocio del proyecto (procesos de punta a punta que se
quieren reproducir con orden y evidencia). Sigue la skill `flow-recording` (cargala). Los flujos
viven en `.coordination/flows/{dominio}/{flujo}/`; la evidencia de cada corrida en
`.coordination/evidence/FLOW-...`. Tu eres el COORDINADOR: no ejecutas el flujo tu mismo, delegas
a los agentes (qa-frontend la UI con Playwright MCP, qa-backend/dba el SQL) y consolidas.

## `crear {dominio}/{flujo}` — dar de alta un flujo nuevo (scaffold + entrevista)
1. Crear la carpeta `.coordination/flows/{dominio}/{flujo}/` copiando el scaffold de
   `${CLAUDE_PLUGIN_ROOT}/templates/flow/` (FLUJO.md, referencias/datos.md, referencias/verificacion.md,
   runbook.md, steps.yaml).
2. Entrevistar al usuario en pocas preguntas para llenar el coordinador: que hace el flujo (en
   negocio), variantes/modos, argumentos, ambiente(s), precondiciones/switches (si depende de
   parametros), y los puntos de parada (donde hay escrituras sensibles).
3. Dejar el runbook con los pasos que el usuario ya conozca; los que falten se completan al
   `grabar`. NO inventar endpoints, tablas ni credenciales: lo que no se sabe va en "No confirmado".
4. Confirmar la estructura creada y como seguir (`grabar` para capturar los pasos reales).

## `grabar {dominio}/{flujo}` — recorrer el flujo y capturar los pasos
Ejecucion asistida para DOCUMENTAR (no es una corrida de produccion, pero igual puede escribir
datos reales — aplican las mismas paradas). Con el usuario presente:
1. Leer FLUJO.md. Confirmar ambiente (preferente NO productivo) y datos de prueba.
2. Recorrer el flujo por la UI con el Playwright MCP (`browser_navigate`, acciones), y en cada
   paso: `browser_take_screenshot`, `browser_generate_locator` (para el `steps.yaml`),
   `browser_network_requests` (endpoint + codigo del resultado esperado). En cada ESCRITURA
   sensible, PARADA: pedir OK del usuario en el momento.
3. Volcar lo capturado al `runbook.md` (pasos numerados con rol, acciones y resultado esperado
   real) y, opcionalmente, al `steps.yaml` (selectores/acciones/asserts). Las verificaciones SQL
   observadas van a `referencias/verificacion.md` con su `-- Esperado:`.
4. Guardar la evidencia de la grabacion en `.coordination/evidence/FLOW-...-grabacion/` y marcar
   en FLUJO.md lo que quedo confirmado y lo que sigue en "No confirmado".

## `listar` — flujos registrados
Recorrer `.coordination/flows/` y mostrar una tabla: dominio, flujo, variantes, ultima
verificacion, y si tiene `steps.yaml` (re-ejecucion asistida disponible). Sin efectos.

## `verificar {dominio}/{flujo}` — chequeo de precondiciones (solo lectura)
Sin ejecutar el flujo: leer FLUJO.md y correr SOLO las verificaciones de solo lectura de
`referencias/verificacion.md` (§1) contra el ambiente — que los parametros/switches esten en el
valor esperado, que existan los datos y objetos necesarios, que las cuentas de prueba sirvan.
Reportar listo/no-listo por precondicion. No escribe nada. Ideal antes de `ejecutar`.

## `ejecutar {dominio}/{flujo} [args]` — correr el flujo con garantias
**PLAN PRIMERO.** Presentar que se va a hacer (variante, ambiente, que se creara/cambiara, y el
rollback) y esperar el OK del usuario. Luego seguir las fases del coordinador (skill `flow-recording`):
1. **Fase 0** — confirmar riesgos con el usuario (crea datos reales, cambia parametros).
2. **Fase 1** — verificar precondiciones (solo lectura) y REGISTRAR los valores iniciales de los
   parametros/switches (para poder restaurarlos).
3. **Fase 2** (si aplica) — cambiar parametros: PARADA OBLIGATORIA. Lo ejecuta el **dba** con el
   patron guardado (preflight SELECT, before-image, UPDATE por PK guardado sobre el valor previo,
   dry-run+rollback, `@ROWCOUNT=1`); si son varios que deben coincidir, se cambian JUNTOS.
4. **Fase 3** — ejecutar los pasos del runbook: la UI la hace **qa-frontend** (un browser
   compartido, captura por paso), el SQL de solo lectura **qa-backend/dba**. A la PRIMERA falla:
   capturar, marcar bloqueante, detener. Sin reintentos (cada reintento crea datos reales).
5. **Fase 4** — puntos de parada obligatorios: antes de cada escritura sensible (grabar, aprobar,
   confirmar giro/desembolso, elegir banco, cualquier write) se pide OK del usuario EN EL MOMENTO.
6. **Fase 5** — verificar el resultado (SQL de solo lectura §3 + UI) contra lo esperado; 0
   errores de consola y 0 4xx/5xx inesperados.
7. **Fase 6** — cierre: escribir `informe-flujo.md` (resultado por paso + veredicto global) y
   PREGUNTAR si restaurar los parametros a los valores iniciales del paso 1 (misma parada guardada).
Evidencia de toda la corrida en `.coordination/evidence/FLOW-{dominio}-{flujo}-{fecha}/`.

## Reglas
- El flujo se VERSIONA (`.coordination/flows/`); la evidencia de las corridas NO (gitignored).
- Antes de cualquier escritura sensible o cambio de parametro: OK del usuario en el momento.
- Cambios de parametros/BD: los ejecuta el dba con el patron guardado, nunca el flujo por su cuenta;
  se registran los valores iniciales y se restauran al cierre.
- A la primera falla se detiene y se reporta; nada de reintentos ciegos (crean datos reales).
- Secretos: se leen de los archivos de acceso por NOMBRE de variable; jamas en el flujo/evidencia/chat.
- Ambiente preferente NO productivo; tocar uno sensible es decision explicita del usuario.
- Un flujo con criterios de aceptacion formales es una HU: eso lo maneja el PO/QA, no este comando.
