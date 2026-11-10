---
name: qa-comentario-ticket-detallado
description: El comentario de QA en el ticket es detallado, criterio por criterio, con evidencia embebida.
tags: [qa, entregable]
runs: 3
max_turns: 14
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Invoca al agente `dev-team:qa` con este pedido y devuelveme su respuesta COMPLETA y tal
cual, sin resumirla ni comentarla:

Pedido del usuario (textual): "Escribe el comentario que vas a publicar en el issue de GitHub de la
HU-042 (giro de operacion de factoring) con el resultado de la validacion." Datos que ya tienes:
ambiente qa (clase pruebas); version frontend 2.4.1 y api-operaciones 2.4.0 (fuente /health,
captura 00-version.png); usuario qa.analista del cliente A; operacion OP-QA-001.
- CA-1 girar una operacion aprobada: cumple. Pasos: abrir OP-QA-001, Girar, confirmar. Capturas
  01-ca1-inicial.png, 02-ca1-confirmar.png, 03-ca1-comprobante.png; video ca1.mp4 con portada
  ca1-portada.png.
- CA-2 con monto 0 muestra «El monto debe ser mayor que 0» y no deja continuar: NO cumple; con
  monto 0 deja continuar y registra el giro. Capturas 04-ca2-monto0.png, 05-ca2-registro.png;
  video ca2.mp4 con portada ca2-portada.png; consola ca2-consola.txt sin errores.
- CA-3 un analista de otro cliente no puede girar: cumple (403). Pasos: entrar como qa.analista.b
  (cliente B), abrir OP-QA-001 e intentar Girar. Captura 06-ca3-403.png.
La evidencia ya esta subida a la rama evidence del repo en evidence/HU-042/ (base de enlaces:
https://github.com/acme/portal/raw/evidence/evidence/HU-042/).

No hay proyecto, repositorio ni ambiente disponibles en esta sesion: el agente entrega el texto
del comentario en su respuesta (no intenta publicarlo ni escribir archivos).
