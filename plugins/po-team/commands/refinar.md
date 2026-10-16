---
description: El refinador convierte lo que llego de la Mesa de Servicios (un ticket, un documento o un pedido en tus palabras) en Historias de Usuario o bugs en lenguaje de negocio con criterios Gherkin y estimacion Fibonacci, detecta duplicados, divide lo grande y, con tu OK, los crea o actualiza en GitHub Projects o Azure DevOps. Tambien redacta observaciones de validacion y registra el VB del cliente. Uso - /po-team:refinar {#ticket de la Mesa | texto | ruta a documento} [--estimar] [--observacion #n] [--vb-cliente #n]
argument-hint: '{#ticket | texto | ruta} [--estimar] [--observacion #n] [--vb-cliente #n] [--sprint N]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Refinar: de lo que llego a trabajo listo para desarrollo

Pedido: $ARGUMENTS

## Paso 0 — Prerequisitos
`.po-team/config.json` existe y `gh auth status` (o `az account show`) responde; si no,
`/po-team:setup tracker`.

## Paso 1 — Redactar (agente `refinador`)
Invocar al `refinador` con el pedido. Segun la entrada:
- **#ticket de la Mesa**: lee el ticket completo (documento, decisiones, pendientes, evidencia). Si
  tiene pendientes que bloquean, propone las preguntas a la Mesa y NO inventa.
- **Texto o documento**: lo lee completo; maximo 3 preguntas al PO si falta algo critico.
- **--estimar**: solo propone o revisa puntos de items existentes (skill `estimacion-fibonacci`).
- **--observacion #n**: redacta la observacion del ultimo `validacion.md` de ese ticket.
- **--vb-cliente #n**: prepara el registro del VB del cliente (quien por el cliente, cuando, por
  que medio: correo, acta firmada, reunion) como comentario en el ticket + etiqueta
  `tracker.etiquetas.vbCliente` (+ estado de la etapa `vb` si el config lo mapea). Los datos del
  VB los da el PO; no se suponen. Nunca cierra el ticket salvo `tracker.reglas.cerrarIssues`.
Devuelve los items redactados (titulo, cuerpo, etiquetas, puntos con justificacion, Project y
sprint si se pidio), con el test de lectura aplicado y duplicados detectados.

## Paso 2 — Plan y aprobacion
Mostrar el plan: que items se crean o actualizan, en que repo y Project, con que puntos y
etiquetas, y si alguno es "pendiente de informacion". **Esperar el OK.**

## Paso 3 — Escribir en el tracker
Con el OK, el `refinador` crea/actualiza (gh o az), agrega al Project, fija puntos y, si se
pidio, sprint. Actualiza `.po-team/backlog.md`.

## Paso 4 — Entrega
```
Creados: #140 Filtrar operaciones por fecha de vencimiento (3 pts, propuesta) · #141 … (5 pts)
Pendiente de informacion: #131 (Mesa) — 2 preguntas comentadas
Siguiente: /po-team:sprint para incluirlas, o /po-team:documento hu #140
```

## Reglas
- Lenguaje de negocio, titulos limpios, criterios Gherkin verificables por pantalla.
- Nada inventado; nada en el tracker sin OK; sin duplicados; valores del config.
