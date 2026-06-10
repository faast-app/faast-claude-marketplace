---
description: Punto de entrada unico del equipo. Detecta si hay proyecto configurado y te guia - crear proyecto nuevo, heredar uno existente, o continuar trabajando. Si no sabes que comando usar, usa este.
argument-hint: (opcional) que quieres hacer, en tus palabras
---

# Start: ¿Que hacemos hoy?

Pedido del usuario (puede venir vacio): $ARGUMENTS

Este comando existe para que NADIE tenga que memorizar los demas comandos.
Detecta el contexto y guia al usuario al flujo correcto.

## Paso 1: Detectar contexto

Buscar `.coordination/config.json` en el directorio actual y en el padre:
- **No existe** → no hay proyecto configurado → Paso 2
- **Existe** → proyecto activo → Paso 3

## Paso 2: Sin proyecto — ofrecer 2 caminos

Preguntar al usuario (con AskUserQuestion si esta disponible):

> ¿Que quieres hacer?
> 1. **Crear un proyecto nuevo** desde una idea o documento de requerimientos
>    → ejecutar el flujo de `/dev-team:new-project`
> 2. **Heredar un proyecto existente** (repos en GitHub/Azure o carpeta local)
>    → ejecutar el flujo de `/dev-team:onboard`

En AMBOS casos, lo primero que hace el flujo elegido es invocar al agente `setup`
para validar/instalar prerequisitos. El usuario no necesita saberlo: simplemente
funciona.

## Paso 3: Proyecto activo — resumen + siguiente accion

1. Leer `.coordination/config.json`, `backlog.md`, `sprint-actual.md` y handoffs pendientes
2. Mostrar un resumen de 5 lineas maximo:
   ```
   Proyecto: {nombre} ({topologia}, tracker: {github|azure})
   Sprint: {n} tareas en curso, {n} bloqueadas
   Handoffs sin procesar: {n}
   Ultimo sync con tracker: {fecha}
   ```
3. Interpretar $ARGUMENTS si el usuario pidio algo especifico:
   - "quiero una nueva funcionalidad / HU / feature" → flujo de `/dev-team:refine` (PO)
   - "hay un bug" / "esto falla" → triaje del Lead (`/dev-team:assign-task` tras registrar el bug)
   - "probar / validar / testear" → agente QA (`/dev-team:e2e` o `/dev-team:test-plan`)
   - "documentar" → tech-writer (`/dev-team:document`)
   - "deploy / publicar" → `/dev-team:deploy-check`
   - "no se / que sigue" → recomendar la accion mas util segun el estado
     (handoffs pendientes → /inbox; HUs sin asignar → /assign-task; nada pendiente → /sync pull)
4. Ejecutar el flujo elegido directamente — no pedir al usuario que escriba otro comando

## Regla
Este comando NUNCA falla con "no entendi": siempre ofrece las opciones disponibles
con una explicacion de una linea cada una.
