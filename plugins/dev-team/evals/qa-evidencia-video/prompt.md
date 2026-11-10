---
name: qa-evidencia-video
description: El video de evidencia sigue la secuencia verificada a tamaño real.
tags: [qa]
runs: 3
max_turns: 14
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Invoca al agente `dev-team:qa-frontend` con este pedido y devuelveme su respuesta COMPLETA y tal
cual, sin resumirla ni comentarla:

Pedido del usuario (textual): "Vas a validar el criterio CA-2 de la HU-042 en pantalla, con el
Playwright MCP, y necesito el video de evidencia. Antes de empezar dime, paso a paso y en
orden, como vas a grabarlo y entregarlo para que no salga chico ni borroso."

No hay proyecto, repositorio ni ambiente disponibles en esta sesion: el agente responde con lo
que haria y lo que no, segun sus reglas, y entrega el contenido pedido en su respuesta (no
intenta escribir archivos).
