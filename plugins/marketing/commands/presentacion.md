---
description: El disenador-presentaciones arma un deck con estetica de lanzamiento (keynote de Apple, presentacion de un hiperdeportivo) siguiendo el desglose aprobado - propuesta comercial (apertura y mercado, una seccion por parte con portada, detalle, como funciona con pantallas reales y resultado, benchmark, hoja de ruta, cierre con la propuesta, anexo de fuentes), benchmark (deck comparativo por parte) o version corta para enviar. Storyboard primero, sistema visual sobre la marca FAAST, capturas reales, y entrega en PowerPoint editable (skill pptx), PDF y/o HTML navegable o Artifact de presentacion, con previews por lamina verificadas. Nunca una plantilla generica.
argument-hint: '[propuesta | benchmark | corta] [--campana CMP-...] [--formato pptx,pdf,html] [--publico ceo|comercial|cliente] [--laminas N]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su procedimiento en
> la sesion actual. NUNCA lo corras dentro de un subagente ni lo invoques via Agent/Task. Solo se
> delegan los AGENTES del equipo, y unicamente cuando este procedimiento lo indica.

# Presentacion: el deck de lanzamiento

Pedido: $ARGUMENTS

Reglas de diseño: skill `presentacion-premium`. Agente: `disenador-presentaciones`.

## Prerrequisitos
Mapa y fichas APROBADOS (si no → `/marketing:desglose`); copy por parte y narrativa (si faltan, el
director los pide al redactor y al estratega); kit de marca; capturas en `desglose/capturas/`.

## Tipos
- **`propuesta`** (por defecto): apertura (1-3) → contexto de mercado (2-4) → **una seccion por parte**
  (3-5 laminas: portada con imagen principal, detalle, como funciona con pantallas reales, resultado)
  → benchmark general (1-2) → hoja de ruta (1) → cierre con la propuesta (1-2) → anexo (fuentes,
  supuestos, origen de pantallas).
- **`benchmark`**: deck comparativo — contexto → una lamina por parte con su matriz y lectura honesta →
  matriz general → metodologia y fuentes.
- **`corta`**: 8-12 laminas autoexplicativas para enviar (una por parte + apertura y cierre).

## Procedimiento
1. **Plan primero**: tipo, formato(s), numero aproximado de laminas, orden de las partes, fecha. OK.
2. Invocar `disenador-presentaciones` (pedido textual + ruta absoluta de la campana).
3. **Storyboard** (`piezas/deck/storyboard.md`: una fila por lamina con bloque, parte, mensaje, imagen,
   texto, fuente) → revision del director-marketing.
4. **Sistema visual** (`piezas/deck/sistema.md`) → construccion (`deck-v{N}.pptx|.pdf|.html`) →
   previews PNG por lamina (`piezas/deck/preview/`).
5. Revision del director (checklist) → al usuario con las previews → aprobacion → `entregables/`.

## Salida
```
Deck {tipo} v{N} — {ID}: {n} laminas ({n} secciones de parte)
Archivos: piezas/deck/deck-v{N}.{pptx|pdf|html} · previews: piezas/deck/preview/
Pendiente: {precios de comercial / supuestos} · Esperando: aprobacion del usuario
```

## Reglas
- Una seccion por parte; ninguna lamina generica ("Nuestra solucion", "Beneficios").
- Una idea por lamina; cuerpo ≥ 24 pt; capturas reales con origen; cifras con nota.
- Marca FAAST; sin logos de terceros como propios; pieza externa sin informacion interna.
- No se entrega sin aprobacion del usuario.
