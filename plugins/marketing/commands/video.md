---
description: Videos motion cinematograficos de presentacion y propuesta de producto - la pieza MAS importante del equipo - con el lenguaje de un keynote de Apple, un reveal de Ferrari, Bugatti o Pagani o un comercial de perfume, y el producto REAL desglosado parte por parte. Subcomandos - keynote (video con un capitulo por parte), parte {n} (clip de 6-15 s y/o pieza extendida de una parte), clips (un clip por cada parte), teaser (15-30 s de expectativa), redes (9x16 y 1x1 reencuadrados + version muda), preproduccion (concepto, tratamiento, guion, storyboard y animatic), revisar {archivo} (QA cuadro a cuadro de un video existente). Produce con HyperFrames y capturas reales del Playwright MCP; render final solo con aprobacion. Usa el agente director-motion.
argument-hint: 'keynote | parte {P01|n} [--extendida] | clips | teaser | redes | preproduccion | revisar {archivo|carpeta} [--campana CMP-...] [--duracion SEG] [--formatos 16x9,9x16,1x1] [--4k] [--voz] [--muda]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su procedimiento en
> la sesion actual. NUNCA lo corras dentro de un subagente ni lo invoques via Agent/Task. Solo se
> delegan los AGENTES del equipo, y unicamente cuando este procedimiento lo indica.

# Video: el producto revelado parte por parte

Pedido: $ARGUMENTS

El video es lo que el CEO ve primero y lo que se reenvia. Este comando lo trata como una productora:
preproduccion aprobada, material real impecable, HyperFrames, postproduccion fina y QA cuadro a cuadro.
Manual: skill `video-lanzamiento`. Agente: `director-motion`.

## Prerrequisitos (todos los subcomandos de produccion)
1. Campana con **mapa y fichas APROBADOS** (`campanas/{ID}/aprobaciones.md`). Si faltan →
   `/marketing:desglose` primero (explicar por que: sin desglose el video sale generico). Excepcion:
   `revisar`.
2. Guiones del redactor (`copy/guion-keynote.md`, `copy/guion-clips.md`); si faltan, se piden al
   redactor (via director) o el director-motion parte del copy por parte.
3. Herramientas: Node ≥ 22, FFmpeg, HyperFrames (skill `hyperframes` / `npx hyperframes`). Si falta
   HyperFrames: avisar y ofrecer (a) instalarlo con OK del usuario, (b) composicion HTML/GSAP grabada a
   tamaño real, o (c) paquete de preproduccion para productora externa.
4. Ambiente demo (clase `pruebas`, datos ficticios) para grabar recorridos, o prototipos del proyecto.
5. Kit de marca (`.marketing/marca/kit.md`); si no, `marca-faast` con sus pendientes declarados.

## Plan primero (siempre)
Antes de producir, presentar en 6-8 lineas: pieza(s) y formatos, duracion, capitulos/partes en orden,
concepto en una frase, musica (caracter) y voz (si/no), material real disponible por parte (y que
falta), entregables y tiempos. Esperar OK.

## `preproduccion` — concepto → animatic (se aprueba antes de producir)
Invocar `director-motion` con: campana, partes, guiones, formatos, pedido textual. Entrega en
`piezas/video/preproduccion/`: `concepto.md` (1 frase + 3 referencias de lenguaje), `tratamiento.md`
(1 pagina: tono, luz, paleta, ritmo/BPM, musica, tipografia, como se muestra el producto, marca),
`guion/P{NN}.md` (`templates/video/guion-parte.md`), `storyboard/P{NN}.md`
(`templates/video/storyboard-parte.md`: plano por plano con duracion, tipo de plano, camara virtual,
material real, texto, sonido, transicion, blueprint) y `animatic-v{N}.mp4` (render draft en tiempo real
con la musica). Mostrar al usuario concepto + tratamiento + animatic → `approval_requested`.
Los demas subcomandos ejecutan esta fase si no esta aprobada.

## `keynote` — un capitulo por parte
Estructura: apertura emocional (6-12 s) → problema con cifra (15-30 s) → **un capitulo por parte**
(20-40 s c/u: titulo → revelacion → como funciona en pantalla real → resultado con cifra) → prueba y
resultados (15-25 s) → hoja de ruta (8-15 s) → cierre y llamado (6-10 s). Duracion total 2-4 min (o
`--duracion`).
1. Preproduccion aprobada.
2. Captura real (secuencia limpia del Playwright MCP + `normalizar_video.py` en OK por grabacion).
3. Produccion HyperFrames: proyecto en `piezas/video/{proyecto}/`; un capitulo = una sub-composicion;
   catalogo y blueprints antes de escribir movimiento; `lint` → `check`.
4. Postproduccion: montaje al beat, color sobre el entorno, tipografia cinetica, sound design, mezcla,
   -14 LUFS, subtitulos.
5. `npx hyperframes preview --background` → director → usuario (3 decisiones concretas).
6. Render con aprobacion: 1920x1080 (y 3840x2160 con `--4k` o si es para sala), version muda, poster,
   `.srt`/`.vtt`, `CAPITULOS.md`, `LICENCIAS.md`.
7. QA: `qa_video.py` por archivo + revision de fotogramas por capitulo → `QA-keynote-v{N}.md`.
Con muchas partes, el director-marketing puede lanzar varias instancias de `director-motion` sobre
capitulos distintos; una arma el `index.html` del keynote.

## `parte {n}` — una parte suelta
Clip de 6-15 s de la parte `P{NN}` (gancho 0-2 s → revelacion → cifra con nota → marca y llamado),
reutilizando la sub-composicion de su capitulo si existe. `--extendida`: ademas la pieza de 30-45 s
(el capitulo autonomo). Formatos segun `--formatos` (16:9 por defecto; 9:16 y 1:1 reencuadrados).

## `clips` — un clip por cada parte
Lo mismo que `parte` para todas las partes del mapa aprobado, con una sola musica/identidad sonora
coherente entre clips. Nombres `clip-P{NN}-{slug}-{formato}-v{N}.mp4` + poster por clip.

## `teaser` — expectativa (15-30 s)
Solo macros de 3-5 partes con luz que recorre, sin explicar; ritmo creciente; cierre de marca con
fecha o llamado. 16:9 y 9:16.

## `redes` — derivados para redes
Por cada pieza aprobada: 9:16 (1080x1920) y 1:1 (1080x1080) **reencuadrados** (composicion propia, no
recorte), subtitulos quemados, zona segura (9:16: 250 px libres arriba y abajo), version muda
autosuficiente, posters. Verificar limites vigentes de cada plataforma (con fuente y fecha).

## `revisar {archivo|carpeta}` — QA cuadro a cuadro de un video existente
1. `python3 "${CLAUDE_PLUGIN_ROOT}/skills/video-lanzamiento/scripts/qa_video.py" {ruta} --spec {WxH}
   [--duracion S] [--fps N] [--muda]` → mediciones (codec, resolucion, fps, duracion, bitrate,
   loudness, true peak, negros, congelados) + 12 fotogramas + hoja de contactos.
2. Si son grabaciones del Playwright MCP (`.webm`):
   `python3 "${CLAUDE_PLUGIN_ROOT}/skills/video-lanzamiento/scripts/normalizar_video.py" {ruta}`.
3. Revisar los fotogramas con `templates/video/checklist-qa-video.md`: producto real nitido y a tamaño
   completo, nada de slideshow, textos legibles el tiempo minimo, marca, licencias, confidencialidad.
4. Informe `QA-{pieza}-v{N}.md` con veredicto APTO / NO APTO y correcciones por capitulo y segundo.
Solo lectura sobre el video original (nunca se modifica).

## Especificaciones de entrega (resumen; hoja completa en `templates/video/especificacion-entrega.md`)
| Formato | Resolucion | fps | Codec | Video | Audio |
|---|---|---|---|---|---|
| Keynote master | 3840x2160 | 30 | H.264 High yuv420p | 35-50 Mbps | AAC 48 kHz, -14 LUFS, TP ≤ -1 dBTP |
| Keynote / clips 16:9 | 1920x1080 | 30 | H.264 High yuv420p | 8-16 Mbps | idem |
| 9:16 / 1:1 | 1080x1920 / 1080x1080 | 30 | H.264 | 6-10 Mbps | idem + subtitulos quemados |
| Version muda | = original | 30 | H.264 | = | sin audio, subtitulos quemados |

## Salida
```
Video {pieza} v{N} — {CMP-...}
Entregas: piezas/video/entregas/{archivos}
Capitulos: CAPITULOS.md · Licencias: LICENCIAS.md · QA: QA-{pieza}-v{N}.md ({APTO|NO APTO})
Esperando: {aprobacion de preproduccion | de preview | de render final}
```

## Reglas duras
- Nada de slideshow animado ni transiciones de plantilla; un capitulo por parte; una parte por clip.
- Producto REAL (demo o prototipo rotulado), nitido y a tamaño completo; grabaciones en OK.
- Cifras con nota; hoja de ruta dicha como hoja de ruta.
- Musica, SFX, voz, fuentes y LUT con licencia registrada; nada copiado de los referentes.
- Render final y entrega solo con aprobacion del usuario. Proyecto dentro de `.marketing/`, nunca en un repo.
