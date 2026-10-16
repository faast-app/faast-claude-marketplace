#!/usr/bin/env python3
# marketing — bloquea la delegacion anidada de subagentes (PreToolUse: Agent/Task).
# Politica: solo director-marketing delega (cualquier agente del equipo, incluso varias
# instancias del mismo rol sobre partes distintas; nunca otro director-marketing). Los demas
# ejecutan su trabajo directamente; unica excepcion: Explore (busqueda barata de solo-lectura).
# Los comandos /marketing:* corren INLINE, nunca como subagente. Nunca falla hacia afuera.
import json, sys

TEAM = {"director-marketing","investigador-mercado","analista-producto","estratega-comercial",
        "redactor-publicitario","disenador-presentaciones","director-motion","disenador-grafico"}
CHEAP_OK = {"explore"}
SKILLS_NOT_AGENTS = {"start","propuesta-comercial","desglose","investigar","presentacion","video",
                     "pieza","tendencias","marca","estado"}
LEAD = "director-marketing"

def short(name):
    return (name or "").strip().split(":", 1)[-1].lower()

def deny(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
          "permissionDecision": "deny", "permissionDecisionReason": reason}}))
    sys.exit(0)

def main():
    payload = json.load(sys.stdin)
    caller = short(payload.get("agent_type"))
    tool_input = payload.get("tool_input") or {}
    raw = (tool_input.get("subagent_type") or tool_input.get("agentType") or "")
    target = short(raw)
    if target in SKILLS_NOT_AGENTS and ("marketing" in raw.lower() or caller in TEAM):
        deny(f"'{target}' es un COMANDO del plugin, no un agente. Ejecutalo INLINE con el Skill "
             f"tool (/marketing:{target}); correrlo como subagente recarga todo el contexto.")
    if not payload.get("agent_id") or caller not in TEAM:
        return
    if target in CHEAP_OK:
        return
    if caller == LEAD and target in TEAM and target != LEAD:
        return
    if caller == LEAD and target == LEAD:
        deny("Delegacion bloqueada: director-marketing no lanza otro director-marketing — tu YA eres el coordinador.")
    if caller == target:
        deny(f"Delegacion bloqueada: '{caller}' intento lanzar otra instancia de si mismo. "
             "Ejecuta el trabajo TU directamente.")
    deny(f"Delegacion bloqueada ('{caller}' → '{target or 'desconocido'}'): solo director-marketing "
         "delega; los demas ejecutan su trabajo directamente. Si necesitas otro rol, deja un handoff en "
         ".marketing/handoffs/ y termina tu parte. Unica excepcion: Explore.")

try:
    main()
except Exception:
    pass
sys.exit(0)
