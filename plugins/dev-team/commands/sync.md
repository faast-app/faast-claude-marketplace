---
description: Sincroniza el trabajo del equipo con el tracker del proyecto (GitHub Issues/Projects o Azure DevOps Boards). Trae items nuevos, actualiza estados, crea PRs y comenta progreso.
argument-hint: Accion - "pull" (traer del tracker), "push" (subir avances) o "full" (ambos, default)
---

# Sync: Sincronizar con el tracker del proyecto

Accion solicitada: $ARGUMENTS (default: full)

## Paso 0: Detectar el tracker
Leer `.coordination/config.json` → `tracker.provider`:
- `"github"` → usar comandos `gh` (seccion GitHub)
- `"azure"` → usar comandos `az boards` (seccion Azure DevOps)
- Si no existe config o la autenticacion falla → sugerir `/dev-team:setup`

---

## GitHub (Issues + Projects V2)

### PULL — Traer cambios del tracker al backlog local
1. Por cada repo del proyecto (leer `repos.md` o config):
   ```bash
   gh issue list --repo {org}/{repo} --state open --json number,title,labels,assignees,state,body,updatedAt --limit 100
   gh project item-list {project-number} --owner {org} --format json
   ```
2. Detectar: issues nuevos → agregar a backlog.md; cerrados → marcar completados;
   cambios de estado en el Project → actualizar; comentarios nuevos → resumir
3. Actualizar `.coordination/backlog.md` y mostrar resumen (N nuevos / actualizados / cerrados)

### PUSH — Subir el trabajo de los agentes
**Agente toma un ticket:**
```bash
gh project item-edit --project-id {id} --id {item-id} --field-id {status} --single-select-option-id {in-progress}
gh issue comment {n} --repo {org}/{repo} --body "🤖 Agente {nombre} tomo este ticket. Branch: feature/{id}-{desc}"
```
**Agente termina (QA aprobo):**
```bash
gh pr create --repo {org}/{repo} --base develop --head feature/{id}-{desc} \
  --title "feat: {descripcion} (closes #{n})" \
  --body "## Resumen\n{...}\n\nCloses #{n}\n\n## QA\nVeredicto: APROBADA — criterios {lista}\n\n🤖 Implementado por agente {nombre}"
# Mover a "In Review" + comentar
```
**Lead mergea:**
```bash
gh pr merge {pr} --repo {org}/{repo} --squash
gh issue close {n} --repo {org}/{repo} --reason completed   # verificar aunque el closes# lo haga
# Mover a "Done" + comentar ✅
```
**Bloqueo:** `gh issue edit {n} --add-label "blocked"` + comentario ⚠️ con motivo y dependencia.

**Deteccion del Project:** `gh project list --owner {org}` y matchear por nombre
(preguntar si hay ambiguedad). Field IDs: `gh project field-list {n} --owner {org}`.

---

## Azure DevOps (Boards)

### PULL — Traer cambios del tracker al backlog local
```bash
az boards query --wiql "SELECT [System.Id],[System.Title],[System.State],[System.WorkItemType],[Microsoft.VSTS.Common.Priority] FROM WorkItems WHERE [System.TeamProject]='{proyecto}' AND [System.State] <> 'Closed' AND [System.State] <> 'Done' ORDER BY [Microsoft.VSTS.Common.Priority]" --output json
```
Detectar nuevos/actualizados/cerrados igual que en GitHub → actualizar `.coordination/backlog.md`.

### PUSH — Subir el trabajo de los agentes
**Agente toma un work item:**
```bash
az boards work-item update --id {id} --state "Active" \
  --discussion "🤖 Agente {nombre} tomo este item. Branch: feature/{id}-{desc}"
```
**Agente termina (QA aprobo):**
```bash
# El PR se crea en el repo (GitHub o Azure Repos segun donde viva el codigo).
# Si el codigo esta en GitHub: usar gh pr create e incluir "AB#{id}" en el titulo/body
#   → Azure Boards linkea automaticamente el work item (requiere la integracion Azure Boards-GitHub)
# Si el codigo esta en Azure Repos:
az repos pr create --repository {repo} --source-branch feature/{id}-{desc} --target-branch develop \
  --title "feat: {descripcion}" --description "Resumen... QA: APROBADA" --work-items {id}
az boards work-item update --id {id} --state "Resolved"
```
**Lead mergea:**
```bash
az repos pr update --id {pr-id} --status completed --merge-commit-message "feat: {desc}"
az boards work-item update --id {id} --state "Closed" --discussion "✅ Completado y mergeado. PR !{pr-id}"
```
**Bloqueo:**
```bash
az boards work-item update --id {id} --fields "System.Tags=blocked" \
  --discussion "⚠️ Bloqueado: {motivo}. Dependencia: #{otro-id}"
```

---

## Modo FULL
1. PULL primero (traer cambios del tracker)
2. PUSH despues (subir avances de los agentes)
3. Resumen consolidado en un solo mensaje

## Reglas (ambos trackers)
- SIEMPRE verificar autenticacion antes de empezar (`gh auth status` / `az account show`)
- Comentarios de agentes con 🤖, confirmaciones del Lead con ✅, bloqueos con ⚠️
- NUNCA cerrar un item sin que el PR este mergeado
- NUNCA mover a Done sin confirmacion del Lead
- NUNCA crear PR de una HU que QA no haya aprobado (gate del Lead)
