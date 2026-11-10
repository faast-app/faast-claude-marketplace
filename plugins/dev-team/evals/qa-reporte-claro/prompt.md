---
name: qa-reporte-claro
description: El reporte pone el resultado primero y las preguntas aparte, pocas y con opciones.
tags: [qa]
runs: 2
max_turns: 14
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Invoca al agente `dev-team:qa` con este pedido y devuelveme su respuesta COMPLETA y tal
cual, sin resumirla ni comentarla:

Pedido del usuario (textual): "Resumeme como quedo la validacion de la HU-060 (alta de
proveedor)." Contexto que ya tienes: 5 criterios; CA-1 a CA-4 cumplen con evidencia; CA-5
(correo de bienvenida al proveedor) no se pudo probar porque el ambiente qa no envia correos.
No sabes si el usuario prefiere probar CA-5 en otro ambiente o marcarlo como prueba manual.
Escribe el reporte que el coordinador le mostrara al usuario.

No hay proyecto, repositorio ni ambiente disponibles en esta sesion: el agente responde con lo
que haria y lo que no, segun sus reglas, y entrega el contenido pedido en su respuesta (no
intenta escribir archivos).
