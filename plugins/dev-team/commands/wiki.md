---
description: Wiki viva del proyecto (patron LLM Wiki de Karpathy, vault de Obsidian en .coordination/wiki/). Subcomandos - init, ingest, lint, query. La mantiene el tech-writer.
argument-hint: "init | ingest | lint | query <pregunta>"
---

Opera la wiki del proyecto en `.coordination/wiki/` usando el agente `tech-writer`.

Argumentos: $ARGUMENTS

## Subcomandos

### `init` — crear la wiki (una sola vez)
1. Crear `.coordination/wiki/` con la estructura del esquema:
   `servicios/`, `hus/`, `bugs/`, `decisiones/`, `pases/`, `agentes/`
2. Copiar el esquema del plugin:
   `${CLAUDE_PLUGIN_ROOT}/templates/coordination-wiki/CLAUDE.md` → `wiki/CLAUDE.md`
3. Crear `wiki/index.md` (portada con links a las secciones) y `wiki/.ingested.log` vacio
4. Crear `.coordination/metrics/` si no existe (ahi vive `activity.jsonl`)
5. Hacer un primer **ingest** de lo que ya exista: `architecture.md`, `backlog.md`,
   handoffs archivados, `sprint-actual.md`
6. Indicar al usuario: "Abre `.coordination/wiki/` como vault en Obsidian para ver
   el graph view"

### `ingest` — destilar lo nuevo (el corazon del patron)
El tech-writer:
1. Lee `wiki/.ingested.log` y lista las fuentes NO ingeridas: handoffs en
   `archive/`, reportes QA, pases en `pases/`, decisiones nuevas
2. Por cada fuente: actualiza/crea las paginas afectadas (una pagina canonica por
   tema), enlaza con `[[wikilinks]]`, registra la fuente en el frontmatter
3. Agrega cada ruta procesada a `.ingested.log`
4. Reporta: N fuentes ingeridas, paginas creadas/actualizadas, links nuevos

### `lint` — salud de la wiki
Detectar y reportar (y corregir lo corregible):
- `[[links]]` rotos (apuntan a pagina inexistente)
- Paginas huerfanas (sin links entrantes ni salientes)
- Frontmatter faltante o invalido
- Paginas con `updated` viejo pero fuentes nuevas sin ingerir
- Posibles duplicados de tema (proponer fusion)
- Secretos filtrados (passwords, API keys) — CRITICO, corregir de inmediato

### `query <pregunta>` — responder desde la wiki
Responder SOLO con el contenido de la wiki, citando las paginas usadas
(`[[servicios/ms-cobranza]]`) y sus fuentes. Si la wiki no tiene la respuesta:
decirlo explicitamente y sugerir `ingest` o a que agente preguntar. NUNCA inventar.

## Reglas
- Solo el tech-writer escribe en la wiki (los demas agentes la leen)
- Si la wiki no existe y el subcomando no es `init`: ofrecer ejecutar `init` primero
- Recomendar `ingest` como habito del flujo diario del Lead (tech-writer es haiku:
  ingerir es barato, re-leer historiales caro)
