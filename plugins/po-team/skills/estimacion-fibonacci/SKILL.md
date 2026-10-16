---
name: estimacion-fibonacci
description: Como el equipo del Product Owner (po-team) propone la estimacion en puntos Fibonacci (1, 2, 3, 5, 8, 13) de HUs y bugs - que significa cada valor en terminos de negocio, factores que suben o bajan el puntaje (complejidad funcional, reglas, perfiles, pantallas, ambientes y clientes a validar, incertidumbre, dependencias), historias de referencia, cuando dividir (13 o mas no entra al sprint), cuando marcar "?" por falta de informacion, como se registra el puntaje en el tracker y por que es una PROPUESTA que valida el equipo de desarrollo. Cargala al estimar, al refinar o al planificar un sprint.
---

# Estimacion en puntos Fibonacci (po-team)

Los puntos miden **tamaño relativo** (esfuerzo + complejidad + incertidumbre), no horas. El PO
propone; el equipo de desarrollo confirma o corrige en el refinamiento (si
`estimacion.validaEquipo` es `true`, el puntaje queda como propuesta hasta esa confirmacion y se
indica asi en el comentario del ticket). Escala del config (`estimacion.escala`, por defecto
1, 2, 3, 5, 8, 13).

## Que significa cada valor (lenguaje de negocio)
| Puntos | Se parece a | Ejemplo funcional |
|---|---|---|
| 1 | Cambio minimo y conocido, una pantalla, sin reglas nuevas | Cambiar el texto de un mensaje o el orden de dos columnas |
| 2 | Cambio chico con una regla simple | Agregar un filtro por estado en un listado existente |
| 3 | Funcionalidad acotada, una pantalla, 2-3 reglas o un perfil nuevo | Exportar a Excel el listado filtrado respetando permisos |
| 5 | Varias pantallas o reglas, o validar en mas de un ambiente/cliente | Nuevo paso de aprobacion para un perfil con su bandeja y notificacion |
| 8 | Flujo completo nuevo o integracion con otro sistema, incertidumbre media | Calculo de un nuevo cargo con su impacto en el resumen, la liquidacion y el documento |
| 13 | Demasiado grande o incierto para un sprint | **Dividir** antes de planificar |
| ? | Falta informacion para estimar | Volver a la Mesa / al cliente con preguntas concretas |

## Factores que SUBEN el puntaje
- Mas de un perfil o estacion involucrados (Ejecutivo → Jefe Comercial → Riesgo → Operaciones…).
- Reglas de negocio con excepciones, montos, plazos, monedas o calculos.
- Validacion en varios ambientes o clientes (Demo de mas de un pais, Preprod de un cliente).
- Dependencia de otro equipo, de un tercero o de un dato que hoy no existe.
- Incertidumbre: el cliente todavia no cerro un punto (si es mucha → "?" en vez de inflar).
- Documentos o reportes que deben cuadrar con lo que se ve en pantalla.

## Factores que BAJAN el puntaje
- Patron ya existente en el producto (otro filtro igual, otra bandeja igual).
- Un solo perfil, una sola pantalla, sin calculos.
- Criterios claros con ejemplos concretos ya validados por el cliente.

## Historias de referencia
Mantener 3-5 historias ya terminadas como ancla (una de 1, una de 3, una de 5, una de 8) en
`.po-team/referencias-estimacion.md`. Al estimar, comparar: "¿es mas grande o mas chica que la
de referencia de 3?". Es mas confiable que estimar en abstracto.

## Reglas
- **Mayor a `estimacion.maximoEnSprint` (por defecto 8) no entra a un sprint**: se divide en
  historias que entreguen valor por si solas (por perfil, por paso del flujo, por regla, por
  ambiente/cliente), nunca por capa tecnica.
- **"?" no es un numero**: el item queda "pendiente de informacion" con las preguntas exactas.
- Bugs: si `estimacion.bugsSuman` es `true` se estiman igual y cuentan en la capacidad; si no,
  se registran sin puntos y se reserva un margen de capacidad para ellos.
- Nunca re-estimar a la baja para "que quepa": se saca algo del sprint o se divide.
- El puntaje va acompañado de una linea de justificacion de negocio ("5: dos perfiles y se valida
  en Demo CO y Preprod del cliente").

## Registro en el tracker
- GitHub Projects: campo numerico del config (`projects[].campos.puntos`):
  `gh project item-edit --id {item-id} --project-id {project-id} --field-id {campo-id} --number {puntos}`
  (ids con `gh project field-list {numero} --owner {org} --format json`). Si el Project no tiene
  campo de puntos, se reporta al PO y se deja en el cuerpo ("Estimacion: 5 — …"); no se crea el
  campo sin que lo pidan.
- Azure DevOps: `--fields "{estimacion.campoPuntos o tracker.azure.campoPuntos}={puntos}"`.
- Siempre con el comentario de justificacion y, si aplica, "propuesta, pendiente de validar con
  el equipo".
