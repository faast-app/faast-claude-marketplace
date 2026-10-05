---
description: Punto de entrada unico de la Mesa de Servicios. Detecta si la mesa esta configurada y te guia - configurar por primera vez, recibir algo nuevo de un cliente, seguir una solicitud en curso, o ver el estado. Si no sabes que comando usar, usa este.
argument-hint: (opcional) que quieres hacer, en tus palabras
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

# Start: ¿que hacemos hoy en la Mesa?

Pedido (puede venir vacio): $ARGUMENTS

Este comando existe para que NADIE tenga que memorizar los demas. Detecta el contexto y lleva al
flujo correcto. Nunca responde "no entendi": siempre ofrece las opciones con una linea cada una.

## Paso 1 — Detectar contexto
Buscar `.mesa/config.json` subiendo desde el directorio actual (hasta 8 niveles):
- **No existe** → la Mesa no esta configurada → Paso 2.
- **Existe** → leerlo junto con `.mesa/backlog.md` y los `estado.json` de `.mesa/solicitudes/*/` → Paso 3.

## Paso 2 — Sin configurar
Invocar al agente `setup`: crea `.mesa/config.json` preguntando UNA vez lo minimo (tracker y
Project, clientes, productos, brain, repo de evidencia, ambientes), valida e instala con
confirmacion, y deja `setup-status.json`. Luego ofrecer `/mesa-servicios:brain init` si el brain
no existe. Terminar mostrando como recibir la primera solicitud.

## Paso 3 — Mesa activa: resumen + siguiente accion
Mostrar maximo 5 lineas:
```
Mesa: {n} solicitudes en curso · {n} esperando cliente · {n} pendientes de aprobacion comercial
Ultimas: {ID} ({estado}), {ID} ({estado})
Brain: {n} paginas · ultimo ingest {fecha}
```
Interpretar $ARGUMENTS:
- "me llego / recibi / el cliente mando / correo / reunion / audio / adjunto" → `/mesa-servicios:recibir`
- "preguntas / cerrar / que falta / respondio el cliente" → `/mesa-servicios:analizar {ID}`
- "reproducir / el cliente dice que falla / evidencia" → `/mesa-servicios:reproducir {ID}`
- "maqueta / como se veria / prototipo / pantalla" → `/mesa-servicios:prototipo {ID}`
- "script / revertir / corregir datos / consulta a la base" → `/mesa-servicios:sql …`
- "documento / propuesta / pdf / word" → `/mesa-servicios:documento {ID}`
- "ticket / subir al backlog / registrar" → `/mesa-servicios:ticket {ID}`
- "que sabemos de / el negocio / el cliente X" → `/mesa-servicios:brain query …`
- "como vamos / estado / pendientes" → `/mesa-servicios:estado`
- "no se / que sigue" → recomendar lo mas util (solicitudes esperando respuesta → analizar;
  documentadas sin ticket → ticket; cerradas sin brain → brain ingest)
Ejecutar el flujo elegido directamente, sin pedir que escriba otro comando.

## Paso 3.5 — Protocolo de la Mesa
Si no esta en contexto el bloque `<mesa-servicios-protocolo>` (sesion abierta fuera de la carpeta),
cargarlo: `CLAUDE_PROJECT_DIR="{ruta}" "${CLAUDE_PLUGIN_ROOT}/hooks/inject-protocol.sh"` y adoptar
su salida (plan primero, la persona de mesa habla con el cliente, cero escritura del DBA, etc.).
