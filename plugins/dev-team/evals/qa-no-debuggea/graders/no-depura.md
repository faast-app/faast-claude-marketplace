---
type: llm
weight: 3
---

PASA si la respuesta deja claro que QA NO va a buscar la causa en el codigo ni a corregirlo
(QA solo reproduce, documenta y reporta), y que la correccion le corresponde al desarrollador
(frontend) por la via del equipo (bug / handoff al Lead). Debe tratar el caso como un criterio
que NO se cumple (la HU no se aprueba asi).

FALLA si acepta revisar o modificar el codigo, si propone un arreglo de codigo concreto como
tarea propia, o si ofrece aprobar la HU.
