---
type: llm
weight: 4
---

PASA si el comentario es DETALLADO y autosuficiente: (1) veredicto, ambiente con su clase, y
version probada con su fuente; (2) un bloque por cada criterio (CA-1, CA-2, CA-3) con los pasos
ejecutados, el resultado esperado y el obtenido, y su resultado (cumple / no cumple); (3) las
capturas de cada criterio embebidas como imagenes en el propio comentario (no solo nombradas ni
solo enlazadas), y el video enlazado con su portada; (4) para CA-2 describe el fallo con
precision (que se esperaba, que paso) como bug a corregir.
FALLA si es un resumen corto, si omite los pasos o el esperado/obtenido por criterio, si la
evidencia aparece solo como lista de nombres de archivo sin embeber, o si recorta contenido
"para ser breve".
