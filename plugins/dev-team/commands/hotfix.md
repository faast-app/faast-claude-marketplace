---
description: Correccion urgente de un incidente en produccion/ambiente sensible - flujo rapido pero con los gates INTACTOS (reproducir, plan, fix, revalidacion con evidencia antes/despues, seguridad si aplica, merge del Lead, informe de conformidad y pase). Rapido no es saltarse controles. Uso - /dev-team:hotfix {descripcion o ticket} [--ambiente]
argument-hint: '{descripcion, ID o URL del incidente} [--ambiente prod|preprod|...]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Hotfix: correccion urgente con gates intactos

Incidente: $ARGUMENTS

Para un problema urgente en un ambiente sensible. La urgencia comprime los TIEMPOS, nunca los
CONTROLES: un hotfix mal hecho a las apuradas causa el segundo incidente. Regla dura: **rapido no
es saltarse gates.**

## Paso 1 — Acotar y reproducir (rapido, con evidencia)
Un incidente urgente se reproduce IGUAL — es lo mas rapido para acotarlo. Via `/dev-team:bug`:
QA reproduce con evidencia (skill `visual-evidence`: captura resaltada + traza + red/consola) y
emite veredicto. Si es un incidente productivo confirmado y observable, basta la evidencia del
estado actual; si no se puede reproducir, no se sabe que se corrige → acotar primero, no adivinar.
Registrar la severidad y a quien afecta.

## Paso 2 — Plan primero (breve, pero explicito)
El Lead presenta un plan corto y espera OK: causa probable (del dev, no de QA), que se cambia,
en que componente/rama (`hotfix/{id}-{desc}` desde la base que corresponda), el riesgo, y el
**rollback** (como se revierte si empeora). Para prod, decir explicitamente el impacto.

## Paso 3 — Fix acotado (un solo cambio)
El dev responsable implementa el MINIMO necesario para el incidente — nada de mejoras "de paso".
Un hotfix toca lo justo. Si aparece deuda relacionada, se registra como item aparte, no se mete aqui.

## Paso 4 — Gates intactos (comprimidos, no omitidos)
- **QA revalida** con la skill `visual-evidence`: mismos pasos del incidente, tanda `-revalidacion`,
  par antes/despues + `browser_verify_*` que ahora pasa, consola/red limpias, veredicto APTO.
  Sin informe de conformidad de la version del fix, QA no valida (regla de oro; tambien en urgencia).
- **cybersec** si el incidente o el fix tocan auth, pagos, datos personales o superficie publica
  (gate del Cybersec Lead; no se omite por urgencia).
- **Solo el Lead mergea** (a la rama que corresponda), con los gates verdes. `git diff` solo del fix.

## Paso 5 — Desplegar y confirmar
- Desplegar por el camino del ambiente (`/dev-team:deploy` para operar; **el pase formal a
  cert/puente/demo/preprod/prod va por `/dev-team:pase`** con release-manager — la urgencia no
  exime el pase, se prioriza).
- Quien desplego emite el **informe de conformidad** (version exacta, ambiente, health). QA hace
  un smoke de confirmacion en el ambiente real con evidencia.

## Paso 6 — Cierre y aprendizaje
- El PO comenta el item con lo corregido (negocio) y la evidencia antes/despues embebida; el cierre
  lo confirma el usuario.
- Anotar el incidente para la **retro** (`/dev-team:retro`): que lo causo y que accion evita que se
  repita. Un hotfix sin aprendizaje es medio trabajo.

## Reglas
- Rapido nunca es saltarse gates: QA revalida con evidencia, cybersec si es sensible, el Lead mergea.
- El fix es minimo y acotado al incidente; la deuda relacionada va como item aparte.
- Siempre hay rollback definido antes de tocar el ambiente.
- El pase a un ambiente formal va por `/dev-team:pase`, aunque sea urgente (se prioriza, no se omite).
- La evidencia (antes/despues) se entrega embebida en el item; secretos/PII redactados.
