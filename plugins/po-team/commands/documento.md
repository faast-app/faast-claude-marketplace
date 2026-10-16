---
description: El documentador genera un documento de NEGOCIO en PDF + DOCX desde la plantilla del plugin y los datos reales del tracker - documento de una HU, especificacion funcional de una epica o conjunto de HUs, acta de aceptacion/entrega (criterios con evidencia y espacio de VB del cliente) o informe de sprint (comprometido vs logrado por etapa del ciclo, fechas y riesgos). Lenguaje 100% funcional; lo tecnico en anexo. Uso - /po-team:documento {hu|especificacion|aceptacion|sprint} {referencia} [--formato pdf|docx|ambos]
argument-hint: 'hu #n | especificacion {#epica | #n #m …} | aceptacion {#n | sprint N} | sprint {N} [--formato pdf|docx|ambos] [--version]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Documento: el entregable de negocio

Pedido: $ARGUMENTS

## Paso 0 — Prerequisitos
- `soffice` disponible; si no: `/po-team:setup documentos`.
- Tipo valido (`hu`, `especificacion`, `aceptacion`, `sprint`); si falta o es ambiguo, ofrecer
  los cuatro con una linea cada uno.
- Para `aceptacion`: idealmente existe VB PO (`validacion.md` o lote) y el veredicto de QA en el
  ticket; si no, se avisa que el acta saldra con criterios "pendientes de validacion".
- Para `sprint`: existe `.po-team/sprints/{N}.json`; se recomienda `/po-team:tablero` reciente.

## Paso 1 — Documento (agente `documentador`)
Invocar al `documentador` con tipo y referencia. Reune datos reales, redacta en negocio
(criterios Gherkin, capturas clave con pie), rellena
`${CLAUDE_PLUGIN_ROOT}/templates/documento/documento-po.html` (o la plantilla del config),
convierte a PDF y DOCX, verifica acentos e imagenes y guarda en `documentos.outputDir`.
`--formato` limita a uno; `--version` genera `v{N+1}` con "Cambios respecto a v{N}".

## Paso 2 — Entrega
```
Acta de aceptacion — Filtrar operaciones por fecha — v1
  .po-team/documentos/Acta de aceptacion - Filtrar operaciones por fecha - v1 - 2026-10-16.pdf (+ .docx)
  Criterios: 3/3 con VB PO (Demo CO, 14/10) · VB cliente: a completar
Siguiente: enviarla al cliente; al recibir el VB, registrarlo con /po-team:refinar --vb-cliente #n
```
Adjuntar el documento al ticket es una escritura: solo con plan + OK.

## Reglas
- Cuerpo de negocio, nada inventado, PDF + DOCX por defecto.
- Autor, equipo y aprobadores del config o del PO en el momento; nunca nombres de memoria.
