---
description: El Product Owner genera un DOCUMENTO DE NEGOCIO (PDF + DOCX) desde las HUs, epicas, backlog o sprint - en lenguaje 100% funcional, desde plantilla. Tipos - hu, especificacion (epica), sprint, aceptacion. Complementa /dev-team:document (que es la documentacion TECNICA del tech-writer). Uso - /dev-team:doc {tipo} {referencia}
argument-hint: 'hu {HU-ID} | especificacion {epica o lista de HUs} | sprint [actual] | aceptacion {HU-ID} [--formato pdf|docx|ambos]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Doc: documento de negocio (Product Owner)

Pedido: $ARGUMENTS

Genera un documento de NEGOCIO en PDF y DOCX desde las HUs/backlog reales, en lenguaje
funcional. Lo produce el agente `product-owner` (con apoyo del `tech-writer` para la redaccion
rica), siguiendo la skill `business-docs`. Es complementario a `/dev-team:document` (que es la
documentacion TECNICA del tech-writer: README, OpenAPI, ADRs). Aqui NO hay codigo en el cuerpo:
el lector es gente de negocio.

## Tipos (segun el primer argumento)
- **`hu {HU-ID}`** — documento de una historia: Como/Quiero/Para, contexto, criterios Gherkin,
  alcance, DoD, estimacion.
- **`especificacion {epica | lista de HUs}`** — especificacion funcional de una funcionalidad
  completa: objetivo de negocio, actores, flujos funcionales, reglas de negocio, HUs incluidas,
  criterios, fuera de alcance.
- **`sprint [actual|N]`** — informe de sprint/backlog para gerencia: objetivo del sprint, HUs
  comprometidas vs. completadas, resultado por HU, metricas de negocio, proximos pasos.
- **`aceptacion {HU-ID}`** — documento de aceptacion/entrega: que se entrego (en negocio),
  criterios cumplidos con su evidencia de QA, como demostrarlo, pendientes.

## Flujo
1. **Reunir el contenido REAL**: leer la(s) HU(s) del tracker (`gh issue view` / `az boards
   work-item show`) y `.coordination/backlog.md` / `sprint-actual.md`. No inventar criterios.
   Para `aceptacion`, ubicar la evidencia de QA (`.coordination/evidence/{HU}/`).
2. **Aplicar la regla de oro** (skill `business-docs`): cuerpo 100% funcional; lo tecnico (IDs del
   tracker, versiones, enlaces) va al Anexo tecnico separado. Correr el test de lectura.
3. **Rellenar la plantilla** `${CLAUDE_PLUGIN_ROOT}/templates/doc-negocio/documento-negocio.html`
   (o la del proyecto si `config.json` → `doc.templatePath` existe). Portada con proyecto/autor/
   fecha del config (nunca a mano). Criterios en Gherkin. Diagramas funcionales en Mermaid solo si
   aclaran (flujo del usuario; nunca un diagrama tecnico de servicios/BD).
4. **Convertir a PDF y DOCX** con LibreOffice headless (ya disponible para los pases):
   ```bash
   soffice --headless --convert-to pdf  --outdir "{salida}" documento-negocio.html
   soffice --headless --convert-to docx --outdir "{salida}" documento-negocio.html
   ```
   `--formato` limita a uno; por defecto ambos. Verificar acentos/eñes en los dos. Si `soffice`
   falta: `/dev-team:setup`.
5. **Guardar** en `config.json` → `doc.outputDir` (default `.coordination/docs-negocio/`) con
   nombre `{Tipo} - {Titulo} - v{X} - {fecha}.pdf/.docx`. Verificar que ambos abren y se ven bien.
6. **Entregar**: ruta de los archivos y un resumen. Si el usuario quiere el documento en el
   tracker, adjuntarlo al item (via la via de evidencia embebida) o enlazarlo.

## Reglas
- El cuerpo no lleva codigo ni jerga: aplicar el test de lectura antes de exportar.
- No inventar HUs ni criterios: se derivan del tracker/backlog reales; el documento cita los IDs.
- Autor/proyecto/aprobador del `config.json`, nunca escritos a mano.
- Entregar PDF + DOCX salvo que se pida uno solo; acentos intactos en ambos.
- El documento complementa el item del tracker, no lo reemplaza.
- Documentacion tecnica (README, OpenAPI, ADRs) → `/dev-team:document` (tech-writer), no aqui.
