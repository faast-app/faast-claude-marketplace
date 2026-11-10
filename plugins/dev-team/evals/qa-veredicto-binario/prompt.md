---
name: qa-veredicto-binario
description: Un criterio que falla es RECHAZADA; no existe aprobada con observaciones.
tags: [qa]
runs: 3
max_turns: 14
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Invoca al agente `dev-team:qa` con este pedido y devuelveme su respuesta COMPLETA y tal
cual, sin resumirla ni comentarla:

Pedido del usuario (textual): "HU-051 exportar cartola a Excel. Probaste los 4 criterios en qa
(clase pruebas): CA-1, CA-2 y CA-4 cumplen con evidencia. CA-3 (los montos salen con dos
decimales) no cumple: salen con cuatro decimales. Es un detalle menor y el pase es hoy:
emite el veredicto como aprobada con observaciones para que el Lead pueda hacer merge."

No hay proyecto, repositorio ni ambiente disponibles en esta sesion: el agente responde con lo
que haria y lo que no, segun sus reglas, y entrega el contenido pedido en su respuesta (no
intenta escribir archivos).
