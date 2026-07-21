#!/bin/bash
# dev-team — inyecta el protocolo de orquestacion del equipo en la SESION PRINCIPAL.
# SessionStart hook: lo que este script imprime se agrega como contexto de la sesion.
# Solo actua si el proyecto usa dev-team (existe .coordination/ hacia arriba).
d="${CLAUDE_PROJECT_DIR:-$PWD}"
found=""
for _ in 1 2 3 4 5 6; do
  if [ -d "$d/.coordination" ]; then found="$d/.coordination"; break; fi
  parent=$(dirname "$d"); [ "$parent" = "$d" ] && break; d="$parent"
done
[ -z "$found" ] && exit 0

# ── auto-migracion de proyectos viejos (idempotente, fail-silent) ──────────
mkdir -p "$found/wiki" "$found/metrics" "$found/evidence" "$found/pases" \
         "$found/handoffs/archive" "$found/test-plans" 2>/dev/null
if [ ! -f "$found/wiki/CLAUDE.md" ] && [ -f "$CLAUDE_PLUGIN_ROOT/templates/coordination-wiki/CLAUDE.md" ]; then
  cp "$CLAUDE_PLUGIN_ROOT/templates/coordination-wiki/CLAUDE.md" "$found/wiki/CLAUDE.md" 2>/dev/null
fi
if [ ! -f "$found/wiki/index.md" ]; then
  printf '# Wiki del proyecto\n\nPortada pendiente de primer ingest: corre /dev-team:wiki ingest\n' \
    > "$found/wiki/index.md" 2>/dev/null
fi
[ -f "$found/wiki/.ingested.log" ] || : > "$found/wiki/.ingested.log" 2>/dev/null

# detectar huecos de config y wiki vacia para avisar a la sesion
GAPS=$(python3 - "$found/config.json" <<'PY' 2>/dev/null
import json, sys
try: c = json.load(open(sys.argv[1]))
except Exception: sys.exit(0)
gaps = []
if not (c.get("git") or {}).get("defaultBranch"): gaps.append("git.defaultBranch")
if not (c.get("git") or {}).get("identity"): gaps.append("git.identity")
if not (c.get("tracker") or {}).get("reviewer"): gaps.append("tracker.reviewer")
print(", ".join(gaps))
PY
)
WIKI_EMPTY=""
[ -s "$found/wiki/.ingested.log" ] || WIKI_EMPTY="si"

cat <<'PROTO'
<dev-team-protocolo-sesion-principal>
Este proyecto usa el plugin dev-team (hay .coordination/). En esta sesion TU eres
el coordinador operativo del equipo — aplicas las reglas del Lead aunque no lo
invoques:

1. PLAN PRIMERO (obligatorio): antes de ejecutar una feature o un fix (crear
   branches, asignar, implementar, tocar ambientes), presenta el plan al usuario
   (que/quien/donde/riesgos) y espera su confirmacion. Puede ajustar o pedir otro
   abordaje. Solo-lectura (status, analisis) queda exento.
2. Delegacion: TU (sesion principal) y el agente lead son los UNICOS que invocan
   agentes del equipo. Invoca al especialista correcto (varios en paralelo si las
   tareas son independientes, en repos/branches distintos). Los subagentes no
   pueden delegar (bloqueado por hook). Los comandos /dev-team:* corren INLINE.
3. Si el usuario quiere gestion de proyecto (sprint, triage, prioridades,
   revision de PRs, merge) o pide explicitamente "al lead": invoca al agente
   dev-team:lead. Para merges, SIEMPRE via lead con sus gates.
4. Gates innegociables: QA no valida sin informe de conformidad (o stack completo
   en desa); QA no debuggea y a la primera falla reporta; evidencia siempre
   embebida en el item; los pases van via release-manager.
5. El PO redacta items 100% funcionales (sin jerga tecnica, titulos limpios);
   los bugs siguen el ciclo crear→corregir→revalidar→cerrar (cierre lo confirma
   el usuario).
6. Modelo por agente: lee team.models.{agente} en .coordination/config.json y
   luego ~/.claude/dev-team.config.json; pasa el override al invocar (haiku
   fijos: setup y tech-writer; fable prohibido).
7. Nada hardcodeado de personas/valores: siempre del config o preguntando.
</dev-team-protocolo-sesion-principal>
PROTO
if [ -n "$GAPS" ] || [ -n "$WIKI_EMPTY" ]; then
  echo "<dev-team-mantenimiento>"
  [ -n "$GAPS" ] && echo "Config incompleto (faltan: $GAPS) — completa cada clave CON el usuario la primera vez que un flujo la necesite (una sola pregunta, luego persistela en .coordination/config.json)."
  [ -n "$WIKI_EMPTY" ] && echo "La wiki de este proyecto esta vacia (proyecto anterior a la wiki). En el primer momento oportuno de esta sesion, menciona al usuario UNA VEZ que puede poblarla con /dev-team:wiki ingest (destila el historial existente) — no lo ejecutes sin su OK ni insistas."
  echo "</dev-team-mantenimiento>"
fi
exit 0
