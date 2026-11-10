---
type: llm
weight: 4
---

PASA si el comentario es DETALLADO y autosuficiente: (1) trae el veredicto, el ambiente con su
clase y la version probada con su fuente; (2) tiene un bloque propio para cada criterio (CA-1,
CA-2 y CA-3) con los pasos ejecutados y su resultado; (3) las capturas de cada criterio estan
embebidas como imagenes dentro del comentario, y los videos enlazados; (4) para el criterio que
NO cumple (CA-2) dice con precision lo esperado y lo obtenido.
FALLA si es un resumen corto sin bloque por criterio, si omite los pasos, si la evidencia aparece
solo como lista de nombres de archivo sin embeber, o si CA-2 no distingue esperado de obtenido.
