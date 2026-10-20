---
description: El manualista crea el manual de usuario de un flujo en dos versiones a partir de un recorrido real con el Playwright MCP - version QA (precondiciones, ambiente, datos de prueba, pasos numerados con resultado esperado) y version para cualquier persona (lenguaje simple, capturas anotadas con marcadores) - en HTML + PDF (+ DOCX). Por defecto ambas versiones. Uso - /po-team:manual {flujo} [--version qa|general|ambas] [--ambiente clave] [--perfil VARIABLE] [--hu #n]
argument-hint: '{flujo en tus palabras} [--version qa|general|ambas] [--ambiente clave] [--perfil VARIABLE] [--hu #n …] [--solo-pdf]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Manual: el mismo flujo para QA y para cualquier persona

Pedido: $ARGUMENTS (version por defecto: `ambas`)

## Paso 0 — Prerequisitos
- Herramientas `browser_*` disponibles y `soffice`; si no: `/po-team:setup playwright` /
  `/po-team:setup documentos`.
- Flujo definido (que se hace, de donde a donde), ambiente (clave de `ambientes.*`) y perfil (por
  NOMBRE de variable). Lo que falte se pregunta UNA vez. HUs relacionadas (`--hu`) recomendadas
  para los resultados esperados de la version QA.

## Paso 1 — Plan corto
Mostrar: flujo, ambiente (con su clase), perfil, versiones, pasos estimados y donde quedara.
Generar el manual no escribe en el tracker. Acciones que registran algo en el ambiente (aprobar,
cursar, enviar): en un ambiente de **pruebas** son normales y se recorren sin pedir OK por paso;
en uno **productivo** el manualista se detiene antes de cada una y pide autorizacion por accion
(lo ideal es documentar en un ambiente de pruebas); sin clase declarada, se pregunta UNA vez.
Si ya existe una version anterior con `steps.yaml`, se propone **repetir ese recorrido** (mismos
pasos, ver que cambio en pantalla) y generar `v{N+1}` con "Cambios respecto a v{N}".

## Paso 2 — Manual (agente `manualista`)
Invocar al `manualista`: un recorrido real con capturas y `recorrido.md`; redaccion de la(s)
version(es) desde `templates/manual/manual-qa.html` y `templates/manual/manual-general.html`;
conversion a PDF (+ DOCX salvo `--solo-pdf`); guardado en `manuales.outputDir/{flujo}/`.
Si el flujo falla a mitad: se informa en lenguaje de negocio y el manual queda en borrador.

## Paso 3 — Entrega
```
Manual "Aprobar una operacion como Jefe Comercial" — v1 — Demo CO
  QA:      …/Aprobar una operacion - Manual QA - v1.pdf (+ .html, .docx) — 9 pasos
  General: …/Aprobar una operacion - Manual de usuario - v1.pdf (+ .html, .docx) — 9 capturas anotadas
Pendientes: resultado esperado del paso 7 no esta en ninguna HU (confirmar con el PO)
```

## Reglas
- Ambas versiones del mismo recorrido; nada descrito sin verlo; nada inventado.
- Sin credenciales ni datos personales; version general sin jerga.
