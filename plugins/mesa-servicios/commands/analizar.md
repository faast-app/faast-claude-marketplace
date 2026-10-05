---
description: El analista cierra una solicitud preguntando - lee faast-brain para no preguntar lo que el negocio ya sabe, prepara una ronda de preguntas puntuales en lenguaje de negocio (max 7, con opciones) que la persona de mesa lleva al cliente, registra las respuestas, y repite hasta cumplir la checklist del tipo (tope 3 rondas); al cerrar clasifica tipo, alcance (cliente o transversal), producto y prioridad sugerida. Uso - /mesa-servicios:analizar {ID} [--respuestas "..."]
argument-hint: '{ID} | {ID} --respuestas "1: … 2: …" | {ID} --respuestas archivo.md'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Analizar: cerrar el requerimiento preguntando

Solicitud: $ARGUMENTS

## Modo A — preparar una ronda (sin `--respuestas`)
1. Invocar al agente `analista` con el ID. Lee `solicitud.md`, faast-brain (producto, cliente,
   reglas, glosario, casos parecidos), el historial del tracker y, si hay ambiente, la pantalla
   real con Playwright MCP. Separa SABIDO / FALTA / CONTRADICE.
2. Produce la ronda N en `preguntas.md`: lo que ya tenemos claro (solo confirmar) + hasta 7
   preguntas concretas con opciones, de lo estructural a lo fino.
3. **PLAN PRIMERO**: mostrar la ronda a la persona de mesa para su OK antes de "enviarla"; puede
   ajustar o quitar preguntas. Con el OK, estado `ESPERANDO CLIENTE`.
4. Salida: la ronda lista para copiar/pegar al cliente (correo, chat o reunion), en lenguaje de
   negocio, sin codigo.

## Modo B — registrar respuestas (`--respuestas`)
1. Invocar al `analista` con las respuestas (texto o archivo). Las registra tal cual en
   `preguntas.md` y, al lado, lo DECIDIDO o lo PENDIENTE y por que; actualiza SABIDO/FALTA.
2. Aplica la checklist de completitud del tipo:
   - **Cumplida** → Cierre: clasificacion (BUG|PRY|CTZ, alcance cliente/transversal, producto,
     prioridad sugerida con fundamento) y que necesita (reproduccion / prototipo / scripts).
     `estado.json` → `CERRADA`. Siguiente: `/mesa-servicios:reproducir` (BUG),
     `/mesa-servicios:prototipo` (PRY con pantalla, proyecto, CTZ), `/mesa-servicios:sql` (datos),
     o directo `/mesa-servicios:documento`.
   - **No cumplida** → nueva ronda (Modo A). Tope 3 rondas: al tercer intento sin cierre, el
     analista escala al `mesa-lead` con lo que falta y una propuesta (reunion de trabajo o
     decision de alcance).

## Salida
```
{ID} — Ronda {N} lista ({n} preguntas) · Esperando cliente
  o
{ID} — CERRADA · Tipo: PRY · Alcance: Cliente ACME · Producto: Factoring · Prioridad sugerida: alta (frena cierre mensual)
Necesita: prototipo si · reproduccion no · scripts no → siguiente: /mesa-servicios:prototipo {ID}
```

## Reglas
- La persona de mesa habla con el cliente; el equipo prepara y registra.
- Nunca suponer para avanzar; pendientes explicitos.
- Max 7 preguntas por ronda; tope 3 rondas; luego escalar.
