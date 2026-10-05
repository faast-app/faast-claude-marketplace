---
description: El redactor convierte una solicitud CERRADA en el documento ejecutivo estandarizado (BUG / PRY / CTZ) con correlativo TIPO-ANO-NNN y alcance (cliente o transversal), en lenguaje de negocio, con el prototipo y la evidencia incrustados, en PDF + DOCX; para cotizaciones (siempre) y proyectos (si se pide) genera ademas la PROPUESTA para el cliente. Uso - /mesa-servicios:documento {ID} [--propuesta] [--formato pdf|docx|ambos]
argument-hint: '{ID} [--propuesta] [--formato pdf|docx|ambos] [--version]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Documento: el entregable que cierra la solicitud

Solicitud: $ARGUMENTS

## Paso 0 — Prerequisitos
- `estado.json` en `CERRADA` (checklist del tipo cumplida). Si hay pendientes aceptados, van al
  documento como pendientes; si no esta cerrada, volver a `analizar`.
- Si es BUG: existe `evidencia/reproduccion.md` (veredicto). Si es PRY con pantalla / CTZ y se
  decidio prototipo: `prototipo/` validado. Si lleva scripts: `scripts/README.md`.
- LibreOffice disponible (`soffice`); si no: `/mesa-servicios:setup`.

## Paso 1 — Redaccion (agente `redactor`)
1. Asigna el **correlativo** (`.mesa/correlativos.json`, atomico, nunca reutilizado) y el
   **alcance** (`Cliente: X` / `Clientes: A, B` / `Transversal`); renombra la carpeta
   `SOL-…` → `{TIPO}-{AÑO}-{NNN}`.
2. Rellena `templates/documento/documento-mesa.html` (o la del proyecto): portada, resumen
   ejecutivo, secciones del tipo, pendientes, anexo. Incrusta capturas del prototipo y las
   capturas clave de la evidencia con pie de foto. Sin codigo; test de lectura.
3. **Propuesta** (`templates/documento/propuesta.html`): obligatoria en CTZ; en PRY con
   `--propuesta`. Valorizacion en blanco para comercial.
4. Convierte: `soffice --headless --convert-to pdf|docx`. Verifica acentos e imagenes.
5. Guarda en `.mesa/solicitudes/{ID}/documento/`:
   `{ID} - {Titulo} - v{N}.pdf/.docx` (+ `{ID} - Propuesta - {Cliente} - v{N}.pdf/.docx`).
   `estado.json` → `DOCUMENTADA`.

## Paso 2 — Entrega
```
{ID} — {titulo} · Alcance: Cliente ACME · v1
Documento: …/documento/PRY-2026-014 - Filtro de operaciones vencidas - v1.pdf (+ .docx)
Propuesta: …/documento/PRY-2026-014 - Propuesta - ACME - v1.pdf (+ .docx)   [si aplica]
Pendientes en el documento: 1 (confirmar perfil que aprueba)
Siguiente: /mesa-servicios:ticket {ID}
```
Versiones: `--version` genera `v{N+1}` con "Cambios respecto a v{N}" en el anexo; nunca se
sobreescribe una version entregada.

## Reglas
- Nada inventado; pendientes explicitos; lenguaje de negocio; PDF + DOCX.
- Correlativo unico; alcance siempre; valorizacion de comercial, no de la Mesa.
- Datos personales de personas: nunca.
