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
exit 0
