---
description: El validador-po hace la VALIDACION FUNCIONAL RAPIDA del PO (no reemplaza a QA) - recorre solo los criterios de aceptacion de la HU por el camino normal en Desa, Demo o Preprod con el Playwright MCP, una captura verificada por criterio, y da VB PO u Observado; a la primera falla reporta en lenguaje de negocio sin buscar causas. Acepta un ticket, una lista o un sprint completo en modo lote (tabla cumple/observado con evidencia por ticket). Con tu OK publica la evidencia embebida y la etiqueta en cada ticket. Uso - /po-team:validar {#n | #n #m ... | --lote sprint N} [--ambiente clave]
argument-hint: '{#n | #n #m … | --lote sprint N} [--ambiente {clave del config}] [--publicar]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Validar: VB PO rapido (no es la prueba de QA)

Pedido: $ARGUMENTS

## Paso 0 — Prerequisitos
- Herramientas `browser_*` del Playwright MCP disponibles; si no: `/po-team:setup playwright`.
- Ambiente: `--ambiente` (clave de `ambientes.*`) o, si no viene, el que corresponde a la etapa
  del ticket (Demo del pais / Preprod del cliente); si es ambiguo, preguntar UNA vez.
- Cuenta del perfil por NOMBRE de variable en `.po-team/accesos.env` con valor cargado; si falta,
  avisar que variable completar (sin pedir el valor en el chat).

## Paso 1 — Alcance
- `#n` → un ticket. `#n #m …` → lista (modo lote). `--lote sprint N` → tickets del sprint en la
  etapa validable para ese ambiente (segun el ultimo tablero o el Project).
Mostrar: tickets, criterios a recorrer por ticket, ambiente, perfil, duracion estimada (~10-20 min
por ticket). Si el lote supera ~8 tickets, confirmar antes de empezar. Validar es solo lectura
sobre el tracker: no requiere el OK de escritura para empezar.

## Paso 2 — Validacion (agente `validador-po`)
Invocar al `validador-po` (un solo navegador, en serie). Por ticket: plan, criterios con captura
resaltada y verificada, veredicto **VB PO** u **Observado**; primera falla → se detiene ese ticket
y sigue con el siguiente. Resultado local en `.po-team/tickets/{n}/validacion-…/` y, en lote,
`lote-*.md` + `.json`.

## Paso 3 — Resultado
```
Validacion PO — Demo CO — 16/10
| Ticket | Titulo | Pts | Veredicto | Criterios |
| #123 | Filtrar operaciones por fecha | 3 | ✅ VB PO | 3/3 |
| #130 | Total con IVA en el resumen | 5 | ⚠️ Observado | 1/3 — el total no incluye el IVA |
VB PO: 3 pts · Observados: 5 pts
Nota: validacion funcional rapida del PO; no reemplaza la validacion de QA.
```

## Paso 4 — Publicar (plan + OK)
Proponer: subir capturas a la rama `evidence`, comentar cada ticket con su tabla y capturas
embebidas, etiqueta `vbPO` / `observadoPO`; para observados, que el `refinador` redacte la
observacion (mismo ticket o bug relacionado). Con el OK (o `--publicar` ya confirmado en este
pedido), ejecutar. Luego sugerir `/po-team:tablero` para reflejar los veredictos.

## Reglas
- Solo criterios de aceptacion, camino normal; jamas causas ni debug.
- Nunca estados reservados a QA, nunca cierre de tickets.
- Evidencia embebida por la rama `evidence`; secretos y datos personales redactados.
