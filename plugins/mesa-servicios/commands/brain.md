---
description: El conocimiento del negocio (repo faast-brain) que hace que la Mesa pregunte menos y mejor. Subcomandos - init (crea el repo con la estructura de negocio y lo siembra con productos y clientes), ingest {ID} (destila lo aprendido de una solicitud cerrada), query "{pregunta}" (responde solo desde el brain, citando), lint (salud del brain). Lo mantiene el curador, unico que escribe. Uso - /mesa-servicios:brain {subcomando}
argument-hint: 'init [--remoto faast-app/faast-brain] | ingest {ID|--pendientes} | query "{pregunta}" | lint'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Brain: el conocimiento del negocio

Pedido: $ARGUMENTS

Todo via el agente `curador` con la skill `faast-brain`. Ruta en `config.json` → `brain.path`.

## `init [--remoto …]` — crear faast-brain
1. Si `brain.path` no existe: `git init` (o `git clone` del remoto si ya existe en la organizacion).
2. Copiar el scaffold de `templates/faast-brain/`: `README.md`, `CLAUDE.md` (esquema y reglas),
   `index.md`, `glosario.md`, carpetas `productos/ clientes/ procesos/ integraciones/ reglas/
   decisiones/ solicitudes/`, `.gitignore`, `.ingested.log`.
3. Sembrar con el usuario (UNA pregunta): productos y clientes (o tomarlos de `config.json`); una
   pagina esqueleto por cada uno con `estado: en-revision`.
4. Primer commit; con `--remoto`, `gh repo create {org}/faast-brain --private` + push.
5. Salida: ruta, paginas creadas, y recordatorio: "el brain empieza casi vacio; cada solicitud
   cerrada lo alimenta con `ingest`".

## `ingest {ID}` | `ingest --pendientes` — destilar lo aprendido
Para cada solicitud cerrada no ingerida (`.ingested.log`): el curador lee `solicitud.md`,
`preguntas.md`, `documento/`, `prototipo/NOTAS.md`, `evidencia/reproduccion.md`, `scripts/README.md`
y crea o actualiza SOLO lo reutilizable: `clientes/`, `productos/`, `procesos/`, `reglas/`,
`glosario.md`, `decisiones/`, y el resumen `solicitudes/{ID}.md` (que se pidio, que se decidio,
que se aprendio, la pregunta que mas costo). Frontmatter con fuentes; enlaces; commit
`brain: ingest {ID}`. Salida: paginas tocadas.

## `query "{pregunta}"` — preguntarle al negocio
Responde SOLO desde el brain, citando paginas y fuentes ("segun clientes/acme.md, fuente
reunion 2026-03-11…"). Si no alcanza, lo dice y propone que ingerir o a quien preguntar; no
inventa. Lo usa el analista antes de cada ronda.

## `lint` — salud del brain
Enlaces rotos, paginas huerfanas, frontmatter invalido, `en-revision` viejas, duplicados de
tema, contradicciones (gana la fuente mas reciente), y **secretos o datos personales** que se
hayan colado (se eliminan y se avisa). Reporta y corrige lo que no requiere decision.

## Reglas
- Solo el curador escribe; los demas leen.
- Sin secretos, sin datos personales de personas, sin codigo; lenguaje de negocio.
- Toda afirmacion con fuente; una pagina canonica por tema.
