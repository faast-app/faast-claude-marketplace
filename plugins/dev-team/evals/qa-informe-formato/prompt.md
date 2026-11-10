---
name: qa-informe-formato
description: El informe consolidado trae veredicto, ambiente y clase, version, riesgo y trazabilidad.
tags: [qa]
runs: 2
max_turns: 14
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Invoca al agente `dev-team:qa` con este pedido y devuelveme su respuesta COMPLETA y tal
cual, sin resumirla ni comentarla:

Pedido del usuario (textual): "Escribe el encabezado y la matriz del informe de QA consolidado
de la HU-042 (giro de operacion de factoring) con estos datos: ambiente qa, clase pruebas;
version frontend 2.4.1 y api-operaciones 2.4.0 tomadas de /health; riesgo alto por ser dinero;
CA-1 cumple (caso C01, test hu-042.spec.ts), CA-2 no cumple (caso C03: con monto 0 deja
continuar), CA-3 cumple (caso C05); fecha 16/10/2026 15:40 hora de Santiago."

No hay proyecto, repositorio ni ambiente disponibles en esta sesion: el agente responde con lo
que haria y lo que no, segun sus reglas, y entrega el contenido pedido en su respuesta (no
intenta escribir archivos).
