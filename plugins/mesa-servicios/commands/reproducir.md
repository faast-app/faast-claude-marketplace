---
description: El QA de negocio reproduce lo que reporta un cliente en el ambiente real con Playwright MCP grabando todo (traza, video con acciones y capitulos, capturas resaltadas, consola y red) y emite un veredicto explicito - REPRODUCIDO / NO REPRODUCIDO / BLOQUEADO - con un informe en lenguaje de negocio y evidencia lista para el lead o el PO. Solo prueba - jamas causas. Tambien captura "como funciona hoy" para proyectos y cotizaciones. Uso - /mesa-servicios:reproducir {ID} [--ambiente qa|prod] [--hoy]
argument-hint: '{ID} [--ambiente qa|prod] [--hoy  (capturar el estado actual, sin veredicto)]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Reproducir: convertir el relato en un hecho con evidencia

Solicitud: $ARGUMENTS

**REGLA DE ESTE COMANDO:** el QA de negocio **solo prueba y documenta**. No busca causas, no lee
codigo, no toca datos, no reintenta. A la primera falla, reporta.

## Paso 0 — Prerequisitos
- La solicitud debe tener los **pasos exactos** cerrados (`preguntas.md`); si estan incompletos,
  volver a `/mesa-servicios:analizar` antes. No se reproduce adivinando.
- **Ambiente acordado**: por defecto el de pruebas (`config.json` → `ambientes`). Produccion
  solo con autorizacion explicita del cliente y del `mesa-lead`, registrada en `00-ANTES`.
- Cuentas de prueba por nombre de variable (`.mesa/accesos.env`). Tools `browser_*` disponibles;
  si no: `/mesa-servicios:setup`.

## Paso 1 — Plan primero
Mostrar en 4 lineas que se va a hacer (pasos, ambiente, perfil, que se graba) y esperar OK.

## Paso 2 — Reproduccion (agente `qa-negocio`)
Invocar al `qa-negocio`. Aplica la skill `evidencia-reproduccion`: `00-ANTES`, traza desde el
inicio, video con acciones y capitulos, captura resaltada por paso con `browser_verify_*`,
snapshot de accesibilidad, consola y red; un intento por paso; segunda corrida completa solo
si se reprodujo (consistente 2/2 / intermitente 1/2). Con `--hoy`: recorre la pantalla actual
y deja 3-6 capturas con `INDEX.md`, sin veredicto.

## Paso 3 — Veredicto y entrega
`reproduccion.md` con veredicto explicito, tabla de pasos, esperado vs obtenido, verificacion,
observaciones de consola/red (sin interpretar), traza y video; `INDEX.md`. Estado →
`EN REPRODUCCION` → vuelve a `CERRADA` con `reproduccion: {veredicto}`.
- **REPRODUCIDO** → `/mesa-servicios:documento {ID}` (el BUG lleva la evidencia).
- **NO REPRODUCIDO** → se informa al cliente lo probado y lo que falta; no se inventa el bug.
- **BLOQUEADO** → al `mesa-lead` (acceso, ambiente, dato); se reintenta al destrabar.

## Salida
```
Reproduccion {ID} — {titulo}
Veredicto: REPRODUCIDO (consistente 2/2) en pruebas · perfil analista · 1280x720
Pasos: 3 · Evidencia: 4 capturas, traza, video 18 s (2 capitulos) · Consola/red: 1 observacion
Siguiente: /mesa-servicios:documento {ID}
```

## Reglas
- Solo reproducir, documentar, reportar. Jamas causas.
- Evidencia fuera de git; al ticket embebida; secretos y datos personales redactados.
