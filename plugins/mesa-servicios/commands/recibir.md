---
description: Recibe algo nuevo de un cliente desde cualquier fuente - correo, documento, transcripcion de Teams/Meet, audio o video (se transcribe en la maquina), chat o relato - lo conserva como evidencia y produce el registro normalizado de la solicitud (que se entendio, que falta, que se contradice). Usa el agente recepcion. Uso - /mesa-servicios:recibir {archivos, texto pegado o descripcion} [--cliente CODIGO]
argument-hint: '{rutas de archivos | texto pegado | "me llamo el cliente y..."} [--cliente ACME] [--tipo bug|proyecto|cotizacion]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Recibir: entra algo nuevo del cliente

Material: $ARGUMENTS

## Paso 1 — Reunir las fuentes (sesion principal)
- Archivos: rutas a correos (`.eml`/`.md`), documentos (`.docx .pdf .xlsx .pptx`), transcripciones,
  audio/video (`.mp4 .m4a .mp3 .wav .webm`).
- Texto pegado: correo, chat, acta, o el relato de la persona de mesa.
- Si hay conector de correo/Teams configurado (`config.json` → `fuentes.conectores`), se puede
  indicar "el correo de ACME del lunes" y la recepcion lo trae.
- `--cliente` si ya se sabe; si no, la recepcion lo infiere de las fuentes o lo marca "por confirmar".
Si no llega NINGUNA fuente, pedirla; no se crea una solicitud vacia.

## Paso 2 — Recepcion (agente `recepcion`)
Invocar al agente `recepcion` con las fuentes. Produce `.mesa/solicitudes/SOL-{fecha}-{n}/` con
`fuentes/` (originales intactos; audio/video transcritos localmente con ffmpeg + Whisper),
`solicitud.md` (lo entendido, ejemplos, lo que falta, contradicciones, restricciones, material
faltante), `estado.json` (`RECIBIDA`). Si una fuente trae varios pedidos de naturaleza distinta,
propone varias solicitudes.

## Paso 3 — Resumen y siguiente paso
Mostrar en 5 lineas: ID provisional, cliente, tipo preliminar, las 3 cosas mas importantes que
faltan, y material faltante. Luego: `/mesa-servicios:analizar {ID}` para cerrar con preguntas.
Si falta Whisper/ffmpeg/pandoc: `blocked` y `/mesa-servicios:setup`.

## Reglas
- Fuente original inmutable; nada se inventa; lo que falta se marca.
- Audio/video nunca salen de la maquina; archivos pesados fuera de git.
- Datos personales de personas no se copian al registro.
