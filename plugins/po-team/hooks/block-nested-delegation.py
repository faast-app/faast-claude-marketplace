#!/usr/bin/env python3
# po-team — bloquea la delegacion anidada de subagentes (PreToolUse: Agent/Task).
# Politica: solo la sesion principal y po-lead delegan. po-lead puede invocar cualquier
# agente del equipo po-team (incluso varias instancias del mismo rol sobre tickets
# distintos; nunca otro po-lead). Los demas ejecutan su trabajo directamente; unica
# excepcion: Explore (busqueda barata de solo-lectura). El trabajo para el equipo de
# desarrollo se entrega via tickets de GitHub/Azure, nunca invocando agentes de otro
# plugin. Los comandos /po-team:* corren INLINE, nunca como subagente.
# Nunca falla hacia afuera: ante cualquier error, permite (exit 0 sin output).
import json, sys

PLUGIN = "po-team"
TEAM = {"po-lead","refinador","planificador","seguimiento","validador-po",
        "documentador","manualista","setup"}
CHEAP_OK = {"explore"}
SKILLS_NOT_AGENTS = {"start","refinar","sprint","tablero","validar","documento",
                     "manual","estado"}   # "setup" tambien es AGENTE (legitimo)

def short(name):
    return (name or "").strip().split(":", 1)[-1].lower()

def prefix(name):
    n = (name or "").strip().lower()
    return n.split(":", 1)[0] if ":" in n else ""

def deny(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
          "permissionDecision": "deny", "permissionDecisionReason": reason}}))
    sys.exit(0)

def main():
    payload = json.load(sys.stdin)
    raw_caller = payload.get("agent_type") or ""
    caller = short(raw_caller)
    tool_input = payload.get("tool_input") or {}
    raw = (tool_input.get("subagent_type") or tool_input.get("agentType") or "")
    target = short(raw)

    # el caller es de otro plugin (dev-team:setup, mesa-servicios:setup...) → no es nuestro
    caller_is_ours = caller in TEAM and prefix(raw_caller) in ("", PLUGIN)

    # comandos /po-team:* corridos como subagente → siempre INLINE
    if target in SKILLS_NOT_AGENTS and (prefix(raw) == PLUGIN or caller_is_ours):
        deny(f"'{target}' es un COMANDO del plugin, no un agente. Ejecutalo INLINE con el Skill "
             f"tool (/po-team:{target}); correrlo como subagente recarga todo el contexto.")

    # sesion principal o agente ajeno al equipo → no intervenir
    if not payload.get("agent_id") or not caller_is_ours:
        return
    if target in CHEAP_OK:
        return
    target_is_ours = target in TEAM and prefix(raw) in ("", PLUGIN)
    if caller == "po-lead" and target_is_ours and target != "po-lead":
        return
    if caller == "po-lead" and target == "po-lead":
        deny("Delegacion bloqueada: po-lead no lanza otro po-lead — tu YA eres el coordinador.")
    if caller == "po-lead" and not target_is_ours:
        deny(f"Delegacion bloqueada (po-lead → '{raw or 'desconocido'}'): el equipo del PO solo "
             "delega dentro de po-team. El trabajo para desarrollo se entrega como ticket en el "
             "tracker (GitHub/Azure), no invocando agentes de otro plugin.")
    if caller == target:
        deny(f"Delegacion bloqueada: '{caller}' intento lanzar otra instancia de si mismo. "
             "Ejecuta el trabajo TU directamente.")
    deny(f"Delegacion bloqueada ('{caller}' → '{target or 'desconocido'}'): solo po-lead y la "
         "sesion principal delegan; los demas ejecutan su trabajo directamente. Si necesitas "
         "otro rol, deja un handoff en .po-team/handoffs/ y termina tu parte. Unica excepcion: Explore.")

try:
    main()
except SystemExit:
    raise
except Exception:
    pass
sys.exit(0)
