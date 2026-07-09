# Wiki del proyecto (LLM Wiki — patron Karpathy)

Esta carpeta es la **wiki viva del proyecto**: conocimiento compilado y enlazado que
los agentes leen ANTES que cualquier otra fuente. Obsidian es el visor (abre esta
carpeta como vault → graph view); el tech-writer es el unico que escribe aqui.

## Principios
1. **raw vs wiki:** los handoffs, reportes y evidencia son fuentes CRUDAS e inmutables
   (viven en `.coordination/handoffs/archive/`, `evidence/`). La wiki DESTILA: una
   pagina por tema, siempre actualizada, con citas a la fuente cruda.
2. **Una pagina canonica por tema.** Si dos paginas hablan de lo mismo, se fusionan.
3. **Todo se enlaza** con `[[wikilinks]]`. Una pagina sin links entrantes ni salientes
   es un huerfano (el lint la detecta).
4. **El conocimiento compone:** los agentes leen la pagina (barato) en vez de re-leer
   N handoffs historicos (caro). Cada ingest hace la proxima tarea mas barata.

## Estructura

```
wiki/
├── CLAUDE.md            # este esquema
├── index.md             # portada: mapa del proyecto con links a todo
├── servicios/{servicio}.md    # estado vivo: stack, patron, contratos, BD, HUs
├── hus/HU-{NNN}.md            # narrativa, criterios, estado, [[reportes QA]], PRs
├── bugs/BUG-{NNN}.md          # repro, evidencia, estado, [[fix]]
├── decisiones/ADR-{NNN}-{slug}.md   # decisiones arquitectonicas
├── pases/{release}.md         # que se paso, a donde, scripts, resultado
└── agentes/{agente}.md        # memoria por rol: que hizo, que sabe, pendientes
```

## Frontmatter obligatorio (toda pagina)

```yaml
---
type: servicio | hu | bug | adr | pase | agente | index
status: activo | done | rechazada | reemplazada   # segun type
updated: YYYY-MM-DD
fuentes:                # citas a las fuentes crudas que respaldan la pagina
  - handoffs/archive/back-to-lead-2026-07-09.md
---
```

## Operaciones (las ejecuta el tech-writer via /dev-team:wiki)

- **ingest** — procesar handoffs archivados/nuevos reportes no ingeridos aun:
  actualizar las paginas afectadas, crear las que falten, enlazar, registrar la
  fuente en `fuentes:`. Marcar lo ingerido en `wiki/.ingested.log` (una ruta por linea).
- **query** — responder una pregunta SOLO con la wiki, citando paginas y fuentes.
  Si la wiki no alcanza, decirlo y proponer ingest.
- **lint** — salud de la wiki: `[[links]]` rotos, paginas huerfanas, frontmatter
  invalido, `updated` viejo con fuentes nuevas sin ingerir, duplicados de tema.

## Reglas
- Los agentes que NO son tech-writer leen la wiki, NUNCA la editan
- Ninguna pagina sin frontmatter ni sin al menos 1 `[[wikilink]]`
- La wiki NUNCA contradice al codigo o al tracker: ante drift, gana la realidad
  y se corrige la pagina (o se reporta al Lead)
- Secretos JAMAS en la wiki (ni credenciales, ni API keys de appsettings)
