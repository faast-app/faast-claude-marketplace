---
description: Punto de entrada unico del equipo del Product Owner. Detecta si po-team esta configurado y te guia - configurar por primera vez, refinar lo que llego de la Mesa de Servicios, planificar el sprint, ver el tablero, validar tickets, generar un documento o un manual. Interpreta lo que pides en tus palabras y te lleva al flujo correcto. Si no sabes que comando usar, usa este.
argument-hint: (opcional) que quieres hacer, en tus palabras
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Start: ¿que hacemos hoy con el backlog?

Pedido (puede venir vacio): $ARGUMENTS

Este comando existe para que NADIE tenga que memorizar los demas. Detecta el contexto y lleva al
flujo correcto. **Nunca responde "no entendi"**: si el pedido es ambiguo, ofrece las 3 opciones
mas probables con una linea cada una y, si no elige, recomienda la mas util.

## Paso 1 — Detectar contexto
Buscar `.po-team/config.json` subiendo desde el directorio actual (hasta 8 niveles):
- **No existe** → po-team no esta configurado → Paso 2.
- **Existe** → leerlo junto con el ultimo `.po-team/tablero/tablero-datos.json` (si existe) y el
  `.po-team/sprints/*.json` mas reciente → Paso 3.

## Paso 2 — Sin configurar
Explicar en 2 lineas que hace el equipo y invocar al agente `setup` (alcance `todo`): valida e
instala con una confirmacion y crea `.po-team/config.json` preguntando UNA vez organizacion,
repos, Projects, mapeo de estados a etapas, ambientes, clientes, capacidad y repo de evidencia.
Al terminar, mostrar como seguir: `/po-team:tablero` para ver el estado o `/po-team:refinar`
para lo que llego de la Mesa.

## Paso 2.5 — Protocolo del equipo
Si no esta en contexto el bloque `<po-team-protocolo>` (sesion abierta fuera de la carpeta),
cargarlo: `CLAUDE_PROJECT_DIR="{ruta}" "${CLAUDE_PLUGIN_ROOT}/hooks/inject-protocol.sh"` y adoptar
su salida (plan primero, gates, delegacion, nada hardcodeado).

## Paso 3 — Configurado: resumen + siguiente accion
Mostrar maximo 5 lineas (del ultimo tablero; si tiene mas de 24 h, decirlo):
```
{equipo} · tablero al {fecha}
Sprint {N}: {pts} pts · VB cliente {x}% · observados {n} · bloqueados {n}
Proximo hito: {Demo|Preprod|VB} {fecha} {⚠ si esta en riesgo}
Pendiente: {n} tickets de la Mesa sin refinar · {n} sin estimar
```
Interpretar $ARGUMENTS:
- "llego de la mesa / nuevo requerimiento / HU / historia / bug / redactar / estimar / refinar" → `/po-team:refinar …`
- "sprint / planificar / capacidad / que entra / fechas de pase / replanificar" → `/po-team:sprint …`
- "tablero / dashboard / como vamos / avance / informe diario / semanal / publicar" → `/po-team:tablero …`
- "validar / VB PO / probar rapido / revisar en demo / preprod / lote" → `/po-team:validar …`
- "documento / pdf / word / acta / aceptacion / especificacion / informe de sprint" → `/po-team:documento …`
- "manual / instructivo / paso a paso para usuarios / para QA" → `/po-team:manual …`
- "estado / que hay pendiente / que sigue" (rapido, sin regenerar) → `/po-team:estado`
- "configurar / no funciona gh / falta soffice / navegador / ambiente nuevo" → `/po-team:setup …`
- Vacio o "no se / que sigue" → recomendar lo mas util en este orden: fechas vencidas o en
  riesgo → observados sin devolver → tickets de la Mesa sin refinar → sprint sin planificar →
  tickets en Demo sin VB PO → tablero de mas de 24 h.
Ejecutar el flujo elegido directamente, sin pedir que escriba otro comando.
