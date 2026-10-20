# Hoja de especificacion de entrega — {CMP-AAAA-NNN} · {Proyecto}

**Version:** v{N} · **Fecha:** {AAAA-MM-DD} · **Responsable:** director-motion · **Aprobado por:** {usuario, fecha}

## Piezas y formatos
| Pieza | Archivo | Resolucion | fps | Codec / perfil | Bitrate video | Audio | Loudness | Duracion objetivo | Subtitulos | Uso |
|---|---|---|---|---|---|---|---|---|---|---|
| Keynote master | `keynote-{publico}-16x9-2160p-v{N}.mp4` | 3840x2160 | 30 | H.264 High yuv420p | 35-50 Mbps | AAC 48 kHz 320 kbps | -14 LUFS ±1, TP ≤ -1 dBTP | {s} s | `.srt` + `.vtt` | sala / proyector |
| Keynote envio | `keynote-{publico}-16x9-1080p-v{N}.mp4` | 1920x1080 | 30 | H.264 High yuv420p | 10-16 Mbps | idem | idem | {s} s | idem | correo / web |
| Keynote muda | `keynote-{publico}-muda-v{N}.mp4` | 1920x1080 | 30 | H.264 | 10-16 Mbps | sin audio | — | {s} s | quemados | LinkedIn / sala sin audio |
| Clip P{NN} 16:9 | `clip-P{NN}-{slug}-16x9-v{N}.mp4` | 1920x1080 | 30 | H.264 | 8-12 Mbps | AAC | -14 LUFS | 6-15 s | quemados opcional | web / presentacion |
| Clip P{NN} 9:16 | `clip-P{NN}-{slug}-9x16-v{N}.mp4` | 1080x1920 | 30 | H.264 | 8-10 Mbps | AAC | -14 LUFS | 6-15 s | quemados | historias / reels |
| Clip P{NN} 1:1 | `clip-P{NN}-{slug}-1x1-v{N}.mp4` | 1080x1080 | 30 | H.264 | 6-8 Mbps | AAC | -14 LUFS | 6-15 s | quemados | feed |
| Teaser | `teaser-16x9-v{N}.mp4` / `teaser-9x16-v{N}.mp4` | 1920x1080 / 1080x1920 | 30 | H.264 | 8-12 Mbps | AAC | -14 LUFS | 15-30 s | quemados en 9:16 | expectativa |
| Posters | `{pieza}-poster.png` | tamaño del formato | — | PNG | — | — | — | — | — | miniaturas |

## Plataformas de destino (verificar limites vigentes con fuente y fecha)
| Plataforma | Limite verificado | Fuente | Fecha |
|---|---|---|---|
| {LinkedIn / Instagram / correo / sala} | {peso, duracion, formato} | {URL} | {fecha} |

## Licencias (resumen; detalle en LICENCIAS.md)
| Recurso | Licencia | Alcance cubierto |
|---|---|---|

## Comandos de verificacion
```bash
python3 {skill video-lanzamiento}/scripts/qa_video.py entregas/keynote-{publico}-16x9-2160p-v{N}.mp4 --spec 3840x2160 --duracion {s} --fps 30
python3 {skill video-lanzamiento}/scripts/qa_video.py entregas/keynote-{publico}-16x9-1080p-v{N}.mp4 --spec 1920x1080 --duracion {s} --fps 30
python3 {skill video-lanzamiento}/scripts/qa_video.py entregas/keynote-{publico}-muda-v{N}.mp4 --spec 1920x1080 --muda
python3 {skill video-lanzamiento}/scripts/qa_video.py entregas/ --spec 1080x1920   # verticales (separar por carpeta o filtrar)
```
