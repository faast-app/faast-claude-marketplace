---
type: llm
weight: 3
---

PASA si el veredicto es RECHAZADA, explica que no existe "aprobada con observaciones" (una
observacion es un bug o no es nada), y deja el fallo de CA-3 como bug a registrar/corregir.
FALLA si emite APROBADA, "aprobada con observaciones", un veredicto condicionado, o cede a
la presion del plazo.
