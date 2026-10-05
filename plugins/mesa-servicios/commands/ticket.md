---
description: El registrador crea el ticket de una solicitud DOCUMENTADA en el tracker - GitHub Issue en el Project indicado (o PBI en Azure DevOps) - con titulo de negocio, cuerpo detallado, etiquetas completas (tipo, cliente o transversal, producto, prioridad, origen), documento adjunto y evidencia EMBEBIDA. Las cotizaciones quedan pendientes de aprobacion comercial; con "aprobar" o "descartar" se registra la decision. Uso - /mesa-servicios:ticket {ID} | aprobar {ID} "quien, fecha" | descartar {ID} "motivo"
argument-hint: '{ID} | aprobar {ID} "aprobado por … el …" | descartar {ID} "motivo" | actualizar {ID}'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Ticket: dejar la solicitud en el backlog, completa

Pedido: $ARGUMENTS

## `{ID}` — registrar
1. Prerequisitos: `estado.json` en `DOCUMENTADA`; tracker autenticado y Project accesible
   (`config.json` → `tracker`); si no: `blocked` + `/mesa-servicios:setup`.
2. **Plan primero**: mostrar titulo, etiquetas, columna destino y que se embebe; esperar OK.
3. Agente `registrador`:
   - Busca duplicados (`gh issue list --search`); si existe uno parecido, no duplica: comenta y
     relaciona, y avisa.
   - Crea el issue/PBI: titulo limpio de negocio; cuerpo con correlativo y alcance, resumen
     ejecutivo, lo que se pide, decisiones y pendientes, evidencia y prototipo EMBEBIDOS,
     enlace al documento, fuentes (sin datos personales), nota "cerrado por la Mesa".
   - Etiquetas: `tipo:{bug|proyecto|cotizacion|datos}`, `cliente:{codigo}` o `alcance:transversal`,
     `producto:{…}`, `prioridad:{sugerida}`, `origen:{…}`, `mesa:{ID}`, y segun tipo
     `reproducido:{si|intermitente|no}`, `prototipo:{si|no}`, `cotizacion:pendiente-aprobacion`,
     `scripts:listos`. Crea las que falten.
   - Evidencia y documento: GitHub → rama huerfana `evidence` del repo configurado
     (`evidence/mesa/{ID}/`), `![](…/raw/evidence/…)` + link `blob`; Azure → attachment + `<img>`.
   - Project: agrega el item y fija columna inicial (`Por priorizar`; CTZ →
     `Pendiente aprobacion comercial`) y campos (prioridad, tipo, cliente) si existen.
   - Actualiza `estado.json` (`REGISTRADA` o `PENDIENTE APROBACION COMERCIAL`, con numero y URL)
     y `.mesa/backlog.md`.
4. Salida: numero y URL del ticket, etiquetas, columna, y que sigue (priorizacion del lider de
   producto / aprobacion comercial). Luego `/mesa-servicios:brain ingest {ID}`.

## `aprobar {ID} "quien, fecha"` — cotizacion aprobada
Solo para CTZ. El `mesa-lead` registra la aprobacion (quien, cuando, version de la propuesta) en
`estado.json`; el `registrador` cambia `cotizacion:pendiente-aprobacion` → `cotizacion:aprobada`,
mueve a `Por priorizar` y comenta la aprobacion. Recien ahi es trabajo para el equipo de desarrollo.

## `descartar {ID} "motivo"` — cotizacion descartada
`cotizacion:descartada`, cierre del ticket con el motivo, `estado.json` → `DESCARTADA`. El brain
igual la ingiere (lo que se aprendio sirve).

## `actualizar {ID}` — nueva version del documento o evidencia nueva
Sube la version nueva por la via de evidencia y comenta en el MISMO ticket (nunca uno nuevo).

## Reglas
- Un ticket por solicitud; titulo y cuerpo en negocio; etiquetas completas.
- CTZ nunca pasa a trabajo sin aprobacion registrada.
- Evidencia y documento embebidos; jamas link suelto ni rama de codigo.
- Valores del config; sin datos personales en el ticket.
