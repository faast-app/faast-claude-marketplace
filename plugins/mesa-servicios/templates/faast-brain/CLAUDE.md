# faast-brain — el conocimiento del negocio (esquema para agentes)

Este repo es lo que el equipo SABE del negocio de FAAST: productos, clientes, procesos,
integraciones, reglas, vocabulario y decisiones. Lo lee la Mesa de Servicios antes de
preguntarle algo a un cliente, para preguntar poco y bien. **Solo el curador escribe aqui**;
el resto lee.

## Estructura
```
index.md                   portada: mapa del negocio con enlaces a todo
productos/{producto}.md    que es, para quien, flujos clave, estados, terminos propios, limites
clientes/{codigo}.md       quien es, productos que usa, particularidades, contactos por ROL
procesos/{proceso}.md      como opera el negocio de punta a punta
integraciones/{sistema}.md con quien se conversa y para que (bancos, burós, SII, pasarelas), en negocio
reglas/{tema}.md           reglas duras: plazos, montos, aprobaciones, excepciones
glosario.md                el vocabulario del negocio, en palabras del cliente
decisiones/{NNN}-{slug}.md decisiones de negocio y por que
solicitudes/{ID}.md        resumen destilado de cada solicitud cerrada (que se pidio, decidio, aprendio)
.ingested.log              IDs de solicitudes ya ingeridas (uno por linea)
```

## Frontmatter obligatorio (toda pagina)
```yaml
---
tipo: producto | cliente | proceso | integracion | regla | decision | solicitud | glosario | index
estado: vigente | en-revision | obsoleto
actualizado: YYYY-MM-DD
fuentes:
  - solicitudes/PRY-2026-014.md
  - reunion 2026-03-11 con cliente ACME (transcripcion)
---
```

## Reglas
1. **Toda afirmacion con fuente.** Lo asumido se marca como supuesto no confirmado.
2. **Una pagina canonica por tema**; duplicados se fusionan; alias en el glosario.
3. **Todo se enlaza** con `[[wikilinks]]`; una pagina sin enlaces es huerfana (el lint la detecta).
4. **Lenguaje de negocio.** Sin codigo, tablas, servicios ni endpoints (eso vive en los repos de producto).
5. **Jamas secretos** (credenciales, tokens, cadenas de conexion, claves).
6. **Jamas datos personales de personas** (RUT, telefonos, correos personales, datos bancarios):
   se habla de la empresa cliente y de roles.
7. **Gana la realidad**: ante contradiccion entre el brain y lo que el cliente confirma, se corrige
   la pagina citando la nueva fuente y se anota el cambio.
8. **Se destila, no se copia**: resumenes cortos con la fuente citada, no documentos completos.

## Operaciones (las ejecuta el curador via /mesa-servicios:brain)
- **init**: crear esta estructura y sembrar productos y clientes como esqueletos `en-revision`.
- **ingest {ID}**: destilar una solicitud cerrada en las paginas que aporte (cliente, producto,
  proceso, regla, glosario, decision, resumen de la solicitud). Registrar en `.ingested.log`.
- **query**: responder SOLO desde el brain, citando paginas y fuentes; si no alcanza, decirlo.
- **lint**: enlaces rotos, huerfanas, frontmatter invalido, `en-revision` viejas, duplicados,
  contradicciones, secretos o datos personales colados.

## Como se lee antes de preguntar (para el analista)
1. Identificar producto y cliente (o transversal).
2. Leer solo lo que aplica: `productos/`, `clientes/`, `procesos/`, `reglas/`, `glosario.md`,
   y `solicitudes/` por casos parecidos.
3. Separar lo SABIDO (se confirma en una frase) de lo que FALTA (se pregunta).
