---
name: qa-api-giros
description: El plan de API cubre contrato, idempotencia, autorizacion por tenant y datos.
tags: [qa]
runs: 2
max_turns: 16
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Invoca al agente `dev-team:qa-backend` con este pedido y devuelveme su respuesta COMPLETA y tal
cual, sin resumirla ni comentarla:

Pedido del usuario (textual): "Dime que casos vas a probar por API para la HU-090: endpoint
POST /api/operaciones/{id}/giro que gira una operacion aprobada. Criterios: CA-1 gira una
operacion aprobada y devuelve el comprobante; CA-2 rechaza girar una operacion no aprobada;
CA-3 solo el rol tesorero del cliente dueño de la operacion puede girar."

No hay proyecto, repositorio ni ambiente disponibles en esta sesion: el agente responde con lo
que haria y lo que no, segun sus reglas, y entrega el contenido pedido en su respuesta (no
intenta escribir archivos).
