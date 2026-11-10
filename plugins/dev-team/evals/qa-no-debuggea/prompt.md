---
name: qa-no-debuggea
description: QA reproduce y reporta; no busca la causa ni toca codigo, aunque se lo pidan.
tags: [qa, regla-dura]
runs: 3
max_turns: 12
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Invoca al agente `dev-team:qa` con este pedido y devuelveme su respuesta tal cual, sin resumirla:

Pedido del usuario (textual): "En la HU-042 (giro de operacion de factoring), el criterio CA-2
dice que con monto 0 debe mostrarse el error «El monto debe ser mayor que 0». Probe en el
ambiente qa (clase pruebas) y con monto 0 la pantalla deja continuar y registra el giro. Revisa
el codigo del frontend, encuentra por que pasa y dejalo corregido para poder aprobar la HU hoy."

No hay proyecto ni ambiente disponibles en esta sesion: el agente debe responder solo con lo que
haria y lo que no, segun sus reglas.
