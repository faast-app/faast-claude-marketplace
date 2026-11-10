---
type: llm
weight: 4
---

PASA si la secuencia: (1) parte con el navegador limpio (cerrarlo/abrirlo antes); (2)
inicia el video con el tamaño igual al viewport ANTES de iniciar la traza (tracing); (3)
explica o respeta que la traza va despues del video; (4) al terminar corre
normalizar_video.py y entrega MP4 con portada; (5) el video muestra la verificacion del
criterio (capitulos o pasos de negocio visibles).
FALLA si inicia la traza antes que el video, si no fija el tamaño del video al viewport, o
si omite la normalizacion.
