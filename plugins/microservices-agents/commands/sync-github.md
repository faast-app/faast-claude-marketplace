---
description: Sincroniza el estado entre el trabajo de los agentes y GitHub Issues/Projects. Actualiza estados de issues, crea PRs, comenta progreso.
argument-hint: Accion (ej. "pull" para traer cambios, "push" para actualizar GitHub, "full" para ambos)
---

# Sync GitHub: Sincronizar estado con GitHub Issues y Projects

Accion solicitada: $ARGUMENTS (default: full)

## Modo PULL — Traer cambios de GitHub al backlog local

1. **Obtener issues actualizados:**
   Leer repos.md para saber que repos tiene el proyecto.
   Por cada repo:
   ```bash
   gh issue list --repo {org}/{repo} --state open --json number,title,labels,assignees,state,body,updatedAt --limit 100
   ```

2. **Obtener estado del Project:**
   ```bash
   gh project item-list {project-number} --owner {org} --format json
   ```

3. **Detectar cambios:**
   - Issues nuevos que no estan en backlog.md → agregar
   - Issues cerrados que estan como pendientes → marcar completados
   - Issues que cambiaron de estado en el Project → actualizar
   - Issues con nuevos comentarios → mostrar resumen

4. **Actualizar .coordination/backlog.md** con los cambios detectados

5. **Mostrar resumen:**
   - N issues nuevos agregados
   - N issues actualizados
   - N issues cerrados

## Modo PUSH — Actualizar GitHub desde el trabajo de los agentes

### Cuando un agente TOMA un ticket:
```bash
# Mover issue a "In Progress" en el Project
gh project item-edit --project-id {id} --id {item-id} --field-id {status-field-id} --single-select-option-id {in-progress-id}

# Asignar el agente (como comentario, ya que los agentes no son GitHub users)
gh issue comment {number} --repo {org}/{repo} --body "🤖 **Agente {nombre}** ha tomado este ticket.
Branch: \`feature/{id}-{descripcion}\`
Inicio: $(date +%Y-%m-%d)"
```

### Cuando un agente TERMINA un ticket:
```bash
# Crear PR linkeado al issue
gh pr create --repo {org}/{repo} \
  --title "feat: {descripcion} (closes #{number})" \
  --body "## Resumen
{resumen del trabajo realizado}

## Issue
Closes #{number}

## Cambios
{lista de archivos modificados}

## Testing
{como se probo}

🤖 Implementado por agente {nombre}" \
  --base develop \
  --head feature/{id}-{descripcion}

# Mover issue a "In Review" en el Project
gh project item-edit --project-id {id} --id {item-id} --field-id {status-field-id} --single-select-option-id {in-review-id}

# Comentar en el issue
gh issue comment {number} --repo {org}/{repo} --body "🤖 **Agente {nombre}** ha completado este ticket.
PR: #{pr-number}
Esperando review y merge del Lead."
```

### Cuando el Lead hace MERGE:
```bash
# Merge el PR
gh pr merge {pr-number} --repo {org}/{repo} --squash

# El issue se cierra automaticamente por "closes #{number}" en el PR
# Pero verificar:
gh issue close {number} --repo {org}/{repo} --reason completed

# Mover a "Done" en el Project
gh project item-edit --project-id {id} --id {item-id} --field-id {status-field-id} --single-select-option-id {done-id}

# Comentar cierre
gh issue comment {number} --repo {org}/{repo} --body "✅ Ticket completado y mergeado a develop.
PR: #{pr-number}
Merge por: Lead"
```

### Cuando hay un BLOQUEO:
```bash
# Agregar label de bloqueado
gh issue edit {number} --repo {org}/{repo} --add-label "blocked"

# Comentar el motivo
gh issue comment {number} --repo {org}/{repo} --body "⚠️ **Bloqueado**: {motivo}
Dependencia: #{otro-issue}
Agente bloqueado: {nombre}
Se requiere: {que se necesita para desbloquear}"
```

## Modo FULL — Pull + Push

1. Ejecutar PULL primero (traer cambios de GitHub)
2. Ejecutar PUSH despues (subir cambios de los agentes a GitHub)
3. Mostrar resumen consolidado

## Deteccion automatica del Project

Para encontrar el GitHub Project del repositorio:
```bash
# Listar projects de la org
gh project list --owner {org} --format json

# Buscar el que matchee con el nombre del proyecto
# Si hay ambiguedad, preguntar al usuario cual es
```

Para obtener los field IDs del Project (necesarios para mover items):
```bash
gh project field-list {project-number} --owner {org} --format json
```

## Notas importantes
- SIEMPRE verificar que `gh` esta autenticado: `gh auth status`
- SIEMPRE usar `--repo {org}/{repo}` explicito (no asumir el repo actual)
- Los comentarios de los agentes usan emoji de robot 🤖 para identificarlos
- El Lead usa ✅ para confirmar completado
- Los bloqueos usan ⚠️
- NUNCA cerrar un issue sin que el PR este mergeado
- NUNCA mover a Done sin confirmacion del Lead
