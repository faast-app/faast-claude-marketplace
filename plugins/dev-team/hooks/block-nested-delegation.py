#!/usr/bin/env python3
# dev-team — bloquea la delegacion anidada de subagentes (PreToolUse: Agent/Task).
# Problema que resuelve: un backend lanzando 3 backends anidados duplica contexto
# y quema tokens sin dividir trabajo real.
# Politica:
#   - Sesion principal (sin agent_id): puede delegar libremente          → allow
#   - Caller que no es del equipo dev-team: no lo policiamos             → allow
#   - lead: UNICO que delega — cualquier agente del equipo, incluso
#     VARIAS instancias del mismo rol (2 backend en HUs distintas);
#     NUNCA otro lead                                                    → allow
#   - Cualquier dev-team agent → Explore (busqueda barata solo-lectura)  → allow
#   - Todo lo demas desde un subagente dev-team (qa incluido: sus
#     especialistas los invoca el lead/sesion principal)                 → DENY
# Nunca falla hacia afuera: ante cualquier error, permite (exit 0 sin output).
import json, sys

TEAM = {"setup","product-owner","architect","ui-designer","lead","backend","frontend",
        "dba","qa","qa-frontend","qa-backend","release-manager","infra","cybersec","tech-writer"}
CHEAP_OK = {"explore"}  # agentes de busqueda solo-lectura, baratos: permitidos

def short(name):
    return (name or "").strip().split(":", 1)[-1].lower()

def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)

def main():
    payload = json.load(sys.stdin)
    caller = short(payload.get("agent_type"))
    # sesion principal o agente ajeno al equipo → no intervenir
    if not payload.get("agent_id") or caller not in TEAM:
        return
    tool_input = payload.get("tool_input") or {}
    target = short(tool_input.get("subagent_type") or tool_input.get("agentType") or "")

    if target in CHEAP_OK:
        return
    if caller == "lead" and target in TEAM and target != "lead":
        return
    if caller == "lead" and target == "lead":
        deny("Delegacion bloqueada: el lead no lanza otro lead — tu YA eres el "
             "coordinador. Ejecuta la coordinacion directamente.")

    if caller == target:
        deny(f"Delegacion bloqueada: '{caller}' intento lanzar otra instancia de si mismo. "
             "Ejecuta el trabajo TU directamente — una instancia anidada duplica todo el "
             "contexto y quema tokens sin dividir trabajo real.")
    deny(f"Delegacion bloqueada ('{caller}' → '{target or 'desconocido'}'): solo el lead "
         "delega en el equipo; los demas agentes ejecutan su trabajo directamente. Si "
         "necesitas a otro rol, crea un handoff en .coordination/handoffs/ y termina tu "
         "parte. Unica excepcion: el agente Explore (busqueda de solo-lectura).")

try:
    main()
except Exception:
    pass
sys.exit(0)
