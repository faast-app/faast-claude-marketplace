---
description: El seguimiento lee los estados reales del GitHub Project (o Azure DevOps), ubica cada ticket en su etapa del ciclo de pase FaaST, calcula el avance por puntos por sprint, lista los cambios desde la revision anterior y los riesgos, redacta el informe diario o semanal en lenguaje de negocio y regenera el dashboard HTML; si la sesion tiene la herramienta Artifact lo publica o actualiza como artifact. Solo lectura sobre el tracker. Uso - /po-team:tablero [diario|semanal] [--sprint N] [--publicar] [--sin-html]
argument-hint: '[diario | semanal] [--sprint N] [--publicar] [--sin-html]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Tablero: como va cada sprint, en 20 segundos

Pedido: $ARGUMENTS (por defecto el informe configurado en `tablero.informe`, todos los sprints
activos, HTML regenerado)

SOLO LECTURA sobre el tracker. Escribe unicamente en `.po-team/tablero/`.

## Paso 1 — Datos (agente `seguimiento`)
Invocar al `seguimiento` con el alcance. Sigue la skill `dashboard-po`: lee cada Project del
config, ubica tickets por sprint y etapa, incorpora veredictos del validador-po y fechas de
`.po-team/sprints/`, calcula avance, compara con el snapshot anterior y guarda el nuevo.

## Paso 2 — Dashboard
Salvo `--sin-html`: regenera `{tablero.outputDir}/tablero.html` desde
`${CLAUDE_PLUGIN_ROOT}/templates/tablero/tablero.html` con `tablero-datos.json` embebido.
**Publicar** si `--publicar` o si `tablero.artifactUrl` ya existe y la sesion tiene el tool
`Artifact`: siempre la misma URL (en sesion nueva, leer primero esa URL y publicar sobre ella);
la primera vez se guarda la URL en el config. Sin el tool: se entrega la ruta local.
Publicar no escribe en el tracker; el artifact queda privado hasta que el PO decida compartirlo.

## Paso 3 — Informe
Mostrar el informe (formato de la skill, §9) y guardarlo en `informes/`. Primero lo urgente
(fechas vencidas, observados, bloqueados, sin movimiento), luego avance y cambios.

## Paso 4 — Siguiente accion
Si hay algo accionable, sugerir el comando exacto, sin ejecutarlo:
- observado sin devolver → `/po-team:refinar --observacion #n`
- tickets en Demo sin VB PO → `/po-team:validar --lote sprint N --ambiente {demo}`
- items sin estimar o "Sin etapa" → `/po-team:refinar --estimar` / `/po-team:setup tracker`
- fecha en riesgo → `/po-team:sprint replanificar`

## Reglas
- Datos reales; lo que falta se muestra como faltante, nunca se estima a ojo.
- Lenguaje de negocio; sin datos personales.
