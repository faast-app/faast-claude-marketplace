---
name: qa-playwright-practicas
description: La automatizacion usa locators estables, sin esperas fijas y con doble corrida.
tags: [qa]
runs: 3
max_turns: 16
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Invoca al agente `dev-team:qa-frontend` con este pedido y devuelveme su respuesta COMPLETA y tal
cual, sin resumirla ni comentarla:

Pedido del usuario (textual): "Vas a automatizar en la suite E2E el criterio CA-2 de la HU-042
(con monto 0 muestra el error «El monto debe ser mayor que 0» y no deja continuar). Escribe el
test de Playwright y dime como te aseguras de que no sea intermitente."

No hay proyecto, repositorio ni ambiente disponibles en esta sesion: el agente responde con lo
que haria y lo que no, segun sus reglas, y entrega el contenido pedido en su respuesta (no
intenta escribir archivos).
