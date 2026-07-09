---
description: Oficina virtual del equipo en tiempo real (estilo Gather Town) - un mapa 2D en el browser donde ves a cada agente en su escritorio, su estado (trabajando/bloqueado/idle), su tarea actual y los handoffs volando entre escritorios.
argument-hint: "[--port 4321]"
---

Levanta la oficina virtual del equipo (visualizacion en vivo de la actividad).

Argumentos: $ARGUMENTS

## Procedimiento

1. **Verificar prerequisitos:**
   - Node.js >= 18 (`node --version`) — si falta, pedir `/dev-team:setup`
   - Que exista `.coordination/` (si no: el usuario debe correr `/dev-team:onboard`
     o `/dev-team:new-project` primero)
   - Crear `.coordination/metrics/` si no existe (ahi los agentes escriben
     `activity.jsonl`)

2. **Instalar la app localmente (una sola vez):**
   ```bash
   mkdir -p .coordination/office
   cp "${CLAUDE_PLUGIN_ROOT}/templates/team-office/server.mjs" \
      "${CLAUDE_PLUGIN_ROOT}/templates/team-office/office.html" .coordination/office/
   ```
   Si ya existe, NO sobreescribir sin avisar (el usuario pudo personalizarla);
   ofrecer actualizar desde el template.

3. **Levantar el servidor** (en background, no bloquear la sesion):
   ```bash
   node .coordination/office/server.mjs --dir .coordination --port {puerto|4321}
   ```
   Abrir `http://localhost:{puerto}` en el browser del usuario (`open` en macOS).

4. **Explicar al usuario lo que ve:**
   - Cada agente en su sala (Management, Desarrollo, Sala QA, Datos, Ops,
     Ventanilla de Pases, Biblioteca, Diseño, Recepcion)
   - Anillo verde = trabajando (con su tarea actual), rojo = bloqueado,
     gris = idle, ambar = trabajando pero sin señal hace >30 min
   - Sobres ✉️ animados = handoffs nuevos entre agentes
   - Panel lateral: handoffs pendientes + feed de actividad en vivo
   - Fuente de datos: `.coordination/metrics/activity.jsonl` (los agentes
     registran eventos por protocolo) + carpeta `handoffs/` — todo local,
     solo lectura, cero tokens

## Reglas
- El servidor es SOLO LECTURA sobre `.coordination/` — jamas modifica nada
- Si `activity.jsonl` aun no existe, la oficina se ve vacia: es normal en un
  proyecto recien creado; se llena a medida que los agentes trabajan
- Para detenerla: matar el proceso node (informar el PID al levantarla)
