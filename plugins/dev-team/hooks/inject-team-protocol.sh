#!/bin/bash
# dev-team — inyecta el protocolo de orquestacion del equipo en la SESION PRINCIPAL.
# SessionStart hook: lo que este script imprime se agrega como contexto de la sesion.
# Solo actua si el proyecto usa dev-team (existe .coordination/ hacia arriba).
d="${CLAUDE_PROJECT_DIR:-$PWD}"
found=""; bare=""
for _ in 1 2 3 4 5 6 7 8; do
  # puntero explicito de repos fuera del paraguas
  if [ -f "$d/.coordination-root" ]; then
    t=$(head -1 "$d/.coordination-root" | tr -d '[:space:]')
    case "$t" in /*) : ;; *) t="$d/$t" ;; esac
    if [ -d "$t/.coordination" ]; then found="$t/.coordination"; break; fi
  fi
  if [ -d "$d/.coordination" ]; then
    if [ -f "$d/.coordination/config.json" ]; then found="$d/.coordination"; break; fi
    [ -z "$bare" ] && bare="$d/.coordination"
  fi
  parent=$(dirname "$d"); [ "$parent" = "$d" ] && break; d="$parent"
done
STRAY=""
if [ -n "$found" ] && [ -n "$bare" ] && [ "$bare" != "$found" ]; then STRAY="$bare"; fi
if [ -z "$found" ]; then found="$bare"; fi
[ -z "$found" ] && exit 0

# ── auto-migracion de proyectos viejos (idempotente, fail-silent) ──────────
# solo sobre la coordinacion CANONICA (con config.json) — jamas engordar un desvio
[ -f "$found/config.json" ] && mkdir -p "$found/wiki" "$found/metrics" "$found/evidence" "$found/pases" \
         "$found/handoffs/archive" "$found/test-plans" 2>/dev/null
if [ -f "$found/config.json" ] && [ ! -f "$found/wiki/CLAUDE.md" ] && [ -f "$CLAUDE_PLUGIN_ROOT/templates/coordination-wiki/CLAUDE.md" ]; then
  cp "$CLAUDE_PLUGIN_ROOT/templates/coordination-wiki/CLAUDE.md" "$found/wiki/CLAUDE.md" 2>/dev/null
fi
if [ -f "$found/config.json" ] && [ ! -f "$found/wiki/index.md" ]; then
  printf '# Wiki del proyecto\n\nPortada pendiente de primer ingest: corre /dev-team:wiki ingest\n' \
    > "$found/wiki/index.md" 2>/dev/null
fi
[ -f "$found/config.json" ] && { [ -f "$found/wiki/.ingested.log" ] || : > "$found/wiki/.ingested.log" 2>/dev/null; }

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

# .coordination sin config.json = desvio probable de la canonica
if [ ! -f "$found/config.json" ]; then
  GAPS="ATENCION: esta .coordination ($found) NO tiene config.json — es probablemente un DESVIO de la coordinacion canonica del proyecto (que suele vivir en la carpeta paraguas). Pregunta al usuario donde esta la canonica; luego, con su OK: (1) crea en la raiz de este repo un archivo .coordination-root con UNA linea (ruta relativa o absoluta a la carpeta paraguas), (2) agregalo al .gitignore del repo, (3) fusiona el contenido util de este desvio en la canonica y eliminalo."
  WIKI_EMPTY=""
fi

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
if [ -n "$GAPS" ] || [ -n "$WIKI_EMPTY" ] || [ -n "$STRAY" ]; then
  echo "<dev-team-mantenimiento>"
  [ -n "$STRAY" ] && echo "DESVIO DETECTADO: existe una .coordination duplicada SIN config.json en $STRAY (la canonica es $found). Es un desvio conocido: propone al usuario fusionar su contenido en la canonica, eliminarla, y crear en esa carpeta un archivo .coordination-root (una linea: ruta a la carpeta paraguas, agregalo al .gitignore del repo) para que hooks y agentes resuelvan siempre la canonica. NO lo hagas sin su OK."
  [ -n "$GAPS" ] && echo "Config incompleto (faltan: $GAPS) — completa cada clave CON el usuario la primera vez que un flujo la necesite (una sola pregunta, luego persistela en .coordination/config.json)."
  [ -n "$WIKI_EMPTY" ] && echo "La wiki de este proyecto esta vacia (proyecto anterior a la wiki). En el primer momento oportuno de esta sesion, menciona al usuario UNA VEZ que puede poblarla con /dev-team:wiki ingest (destila el historial existente) — no lo ejecutes sin su OK ni insistas."
  echo "</dev-team-mantenimiento>"
fi
exit 0
