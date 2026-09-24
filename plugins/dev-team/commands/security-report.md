---
description: Genera el informe profesional de seguridad (PDF + HTML) de un pentest o auditoria, con resumen ejecutivo, hallazgos por severidad, evidencia embebida (imagenes de las pruebas), CVSS y remediacion. Uso - /dev-team:security-report PENTEST-{id}
argument-hint: 'PENTEST-{id}  (o la carpeta de evidencia a consolidar)'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Informe de seguridad (PDF con evidencia)

Encargo: $ARGUMENTS

Produce el informe formal de la prueba/auditoria `PENTEST-{id}` a partir de la evidencia y
los hallazgos consolidados por el Cybersec Lead. El entregable es un documento presentable a
gerencia y auditoria: PDF + HTML (fuente de verdad), con las imagenes de las pruebas
EMBEBIDAS. Lo arma el agente **cybersec** (con apoyo del **tech-writer** para la redaccion).

## Paso 1 — Reunir insumos
De `.coordination/evidence/PENTEST-{id}/`:
- `roe.md` (alcance y autorizacion) · `threat-model.md`
- Handoffs de hallazgos (`pentester/appsec/cloudsec-to-cybersec-*`) y la consolidacion del Lead
- Evidencia por hallazgo (`{area}/{id}/` con capturas numeradas, responses, salidas)
Si falta la consolidacion del Cybersec Lead, generarla primero (Paso 4 de `/dev-team:pentest`).

## Paso 2 — Armar el informe desde la plantilla
Partir SIEMPRE de `${CLAUDE_PLUGIN_ROOT}/templates/pentest/informe-pentest.html` (autocontenido,
imprime a PDF). Rellenar sus secciones:
1. **Portada**: proyecto, alcance, ambiente, fecha, clasificacion ("Confidencial")
2. **Resumen ejecutivo** (para gerencia, sin jerga): postura general, riesgos clave en lenguaje
   de negocio, y un grafico/tabla de conteo por severidad
3. **Alcance y RoE**: que entro, que quedo fuera, quien autorizo, cuando
4. **Metodologia**: PTES / OWASP (WSTG, Top 10 2021, API Top 10 2023), herramientas
5. **Resumen de hallazgos**: tabla ID / titulo / clase OWASP / CVSS / severidad / estado
6. **Detalle por hallazgo**: descripcion, impacto de negocio, ubicacion, PoC, **evidencia
   embebida** (las imagenes de la prueba, con pie de foto), vector CVSS, remediacion con ejemplo
7. **Estado de reprueba** (retest): CERRADO / ABIERTO por hallazgo
8. **Plan de remediacion**: prioridad y SLA (Critico inmediato / Alto 24-72h / Medio sprint / Bajo backlog)
9. **Anexos**: comandos, referencias

**Embeber las imagenes** (no linkearlas): copiar las capturas relevantes junto al HTML (o
incrustarlas en base64) para que el PDF sea autosuficiente. Redactar SIEMPRE secretos, tokens
y PII real en el texto y en las imagenes (`Bearer ***`, `rut: ***`).

## Paso 3 — Convertir a PDF
```bash
# opcion A (ya disponible para pases): LibreOffice headless
soffice --headless --convert-to pdf --outdir "{carpeta}" informe-pentest.html
# opcion B: Chromium headless (si esta), respeta mejor el CSS de impresion
# (usar el navegador del Playwright MCP para imprimir a PDF si soffice no rinde)
```
Verificar que el PDF abre, las imagenes se ven y no quedo ningun secreto sin redactar.

## Paso 4 — Entregar
- Guardar en `.coordination/evidence/PENTEST-{id}/informe/`:
  `Informe de Seguridad - {Proyecto} - {fecha}.pdf` + `.html` + imagenes embebidas
- Si el usuario quiere el informe en el tracker: subirlo por la via de evidencia EMBEBIDA
  (rama `evidence` en GitHub / attachment en Azure) y enlazarlo desde el item de resumen
- Handoff al Lead con: ruta del informe, conteo por severidad, top 3 riesgos y estado de reprueba

## Salida al usuario
```
Informe de seguridad PENTEST-{id} listo
PDF: evidence/PENTEST-{id}/informe/Informe de Seguridad - {Proyecto} - {fecha}.pdf
Hallazgos: 1 Critico · 2 Altos · 3 Medios · 1 Bajo · Reprueba: 4 cerrados / 3 abiertos
Sin secretos ni PII en el documento (redactados).
```

## Reglas
- El informe se DERIVA de la evidencia real; no se inventan hallazgos ni severidades
- Secretos y PII SIEMPRE redactados, tambien en las imagenes
- El PDF debe ser autosuficiente (imagenes embebidas), presentable a gerencia
- No se entrega un informe con hallazgos sin PoC/evidencia
