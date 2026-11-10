---
name: qa-plan-por-riesgo
description: El plan clasifica por riesgo y aplica tecnicas formales y borde fintech.
tags: [qa]
runs: 3
max_turns: 16
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Invoca al agente `dev-team:qa` con este pedido y devuelveme su respuesta COMPLETA y tal
cual, sin resumirla ni comentarla:

Pedido del usuario (textual): "Arma el plan de pruebas de la HU-077: calculo de interes por mora
en operaciones de factoring vencidas. Criterios: CA-1 desde el dia siguiente al vencimiento se
cobra interes diario con la tasa del contrato; CA-2 el interes se muestra en la moneda de la
operacion (CLP, PEN o COP) con el redondeo de esa moneda; CA-3 un analista ve solo las
operaciones de su cliente; CA-4 el interes acumulado aparece en el detalle de la operacion."

No hay proyecto, repositorio ni ambiente disponibles en esta sesion: el agente responde con lo
que haria y lo que no, segun sus reglas, y entrega el contenido pedido en su respuesta (no
intenta escribir archivos).
