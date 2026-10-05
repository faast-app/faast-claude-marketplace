#!/usr/bin/env python3
# mesa-servicios — bloquea la delegacion anidada de subagentes (PreToolUse: Agent/Task).
# Politica: solo mesa-lead delega (cualquier agente de la Mesa, incluso varias instancias
# del mismo rol; nunca otro mesa-lead). Los demas ejecutan su trabajo directamente;
# unica excepcion: Explore (busqueda barata de solo-lectura). Los comandos
# /mesa-servicios:* corren INLINE, nunca como subagente. Nunca falla hacia afuera.
import json, sys

TEAM = {"mesa-lead","recepcion","analista","qa-negocio","dba-mesa","prototipador",
        "redactor","registrador","curador","setup"}
CHEAP_OK = {"explore"}
SKILLS_NOT_AGENTS = {"start","recibir","analizar","reproducir","prototipo","sql","flujo",
                     "documento","ticket","brain","estado"}   # "setup" tambien es AGENTE

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
    if target in SKILLS_NOT_AGENTS and ("mesa-servicios" in raw.lower() or caller in TEAM):
        deny(f"'{target}' es un COMANDO del plugin, no un agente. Ejecutalo INLINE con el Skill "
             f"tool (/mesa-servicios:{target}); correrlo como subagente recarga todo el contexto.")
    if not payload.get("agent_id") or caller not in TEAM:
        return
    if target in CHEAP_OK:
        return
    if caller == "mesa-lead" and target in TEAM and target != "mesa-lead":
        return
    if caller == "mesa-lead" and target == "mesa-lead":
        deny("Delegacion bloqueada: mesa-lead no lanza otro mesa-lead — tu YA eres el coordinador.")
    if caller == target:
        deny(f"Delegacion bloqueada: '{caller}' intento lanzar otra instancia de si mismo. "
             "Ejecuta el trabajo TU directamente.")
    deny(f"Delegacion bloqueada ('{caller}' → '{target or 'desconocido'}'): solo mesa-lead delega; "
         "los demas ejecutan su trabajo directamente. Si necesitas otro rol, deja un handoff en "
         ".mesa/handoffs/ y termina tu parte. Unica excepcion: Explore.")

try:
    main()
except Exception:
    pass
sys.exit(0)
