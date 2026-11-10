---
type: llm
weight: 4
---

PASA si los casos incluyen: (1) doble envio / idempotencia del giro (reintento con la misma
clave no gira dos veces) o concurrencia; (2) autorizacion por objeto y por cliente: un
tesorero de OTRO cliente no puede girar la operacion, y un rol sin permiso tampoco;
(3) codigos de estado y cuerpo de error exactos para los rechazos; (4) el barrido de
contrato con Schemathesis; (5) la verificacion de consistencia de datos con SQL de solo
lectura o equivalente.
FALLA si omite la idempotencia/doble envio o la autorizacion por cliente.
