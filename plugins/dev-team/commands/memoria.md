---
description: Memoria del equipo (RAG con retroalimentacion y mejora continua) - buscar lo que el proyecto ya sabe, registrar lecciones de las correcciones del usuario y de QA, dar feedback util/no-util, consolidar el manual por agente, proponer reglas permanentes y medir la recuperacion. Subcomandos - buscar {consulta}, aprender {leccion}, feedback {id} {util|no-util}, pendientes, consolidar, metricas, evaluar, indexar.
argument-hint: 'buscar {consulta} | aprender {leccion} | feedback {L-id} util|no-util | pendientes | consolidar | metricas | evaluar | indexar'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Memoria del equipo

Pedido: $ARGUMENTS

Carga la skill `dev-team:memoria-equipo` y usa su script con la coordinacion canonica:

```bash
MEM="${CLAUDE_PLUGIN_ROOT}/skills/memoria-equipo/scripts/memoria.py"
```

## Subcomandos
- **`buscar {consulta}`** (default si el pedido es una pregunta) → `python3 "$MEM" buscar "…"`.
  Responde al usuario SOLO con lo recuperado, citando el origen de cada fragmento (id de
  leccion o ruta). Si no alcanza, dilo y propone de donde saldria (wiki ingest, preguntar).
- **`aprender {leccion}`** → redacta la leccion en una o dos frases autosuficientes
  (contexto + que paso o que quiere el usuario + que hacer la proxima vez), elige `--tipo` y
  `--agente`, y usa `--fuente usuario` cuando viene de palabras del usuario. Muestrasela al
  usuario antes de guardarla si la redaccion cambia el sentido de lo que dijo.
- **`feedback {L-id} util|no-util`** → registra el voto (con `--nota` si explica por que).
- **`pendientes`** → lista los mensajes recientes del usuario con forma de correccion o
  preferencia que aun no son leccion. Por cada uno: ¿sirve para el futuro? Si → `aprender
  --fuente usuario`. Al terminar: `python3 "$MEM" pendientes --revisadas`.
- **`consolidar`** → `consolidar` + `metricas` + `evaluar`. Presenta al usuario: cuantas
  lecciones, % util, la recuperacion, y la lista de **candidatas a regla permanente** de
  `memoria/consolidacion.md` con una recomendacion por cada una (al prompt de que agente o a
  que skill, o al `CLAUDE.md` del proyecto). Nada se incorpora sin su OK; lo general va como
  PR al marketplace, lo del proyecto a su `CLAUDE.md`.
- **`metricas`** / **`evaluar`** / **`indexar`** → el comando homonimo del script.

## Reglas
- Sin secretos, credenciales ni datos personales en una leccion.
- La memoria no autoriza acciones: solo informa como hacerlas mejor.
- Solo-lectura (`buscar`, `metricas`, `evaluar`, `pendientes`) no necesita plan ni confirmacion.
