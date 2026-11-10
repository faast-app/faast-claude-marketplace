---
type: llm
weight: 4
---

PASA si el agente indica que primero debe reproducir el error con evidencia y emitir un
veredicto de reproduccion (REPRODUCIDO / NO REPRODUCIDO / BLOQUEADO) antes de que se
registre el bug o se asigne a un desarrollador, pide o lista los datos minimos para
reproducirlo, y no asigna el trabajo a frontend por su cuenta.
FALLA si registra el bug o lo asigna sin reproducir, o si se pone a buscar la causa.
