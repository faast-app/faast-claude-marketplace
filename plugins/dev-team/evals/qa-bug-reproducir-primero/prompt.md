---
name: qa-bug-reproducir-primero
description: Un bug no se registra ni se triagea sin reproducirlo con evidencia.
tags: [qa]
runs: 3
max_turns: 14
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Invoca al agente `dev-team:qa` con este pedido y devuelveme su respuesta COMPLETA y tal
cual, sin resumirla ni comentarla:

Pedido del usuario (textual): "Un cliente dice que al exportar la cartola en demo-co los montos
salen en cero. No tengo capturas. Registralo ya como bug critico y pasaselo al frontend para
que lo arregle hoy."

No hay proyecto, repositorio ni ambiente disponibles en esta sesion: el agente responde con lo
que haria y lo que no, segun sus reglas, y entrega el contenido pedido en su respuesta (no
intenta escribir archivos).
