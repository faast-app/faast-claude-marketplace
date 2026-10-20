#!/usr/bin/env python3
# po-team — logging AUTOMATICO de actividad de agentes (via hooks).
# Recibe el payload del hook (SubagentStart/SubagentStop) por stdin y agrega una
# linea JSON a .po-team/metrics/activity.jsonl de la carpeta CANONICA (coord_root.resolve).
# Si la carpeta canonica esta dentro de un repo git, no escribe (la regla es que viva
# fuera). Nunca falla hacia afuera (exit 0).
import json, os, sys, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coord_root import resolve  # noqa: E402

PLUGIN = "po-team"
TEAM = {"po-lead","refinador","planificador","seguimiento","validador-po",
        "documentador","manualista","setup"}

def contexto_agente(po, en_repo):
    if po and not en_repo:
        ruta = (f"Carpeta canonica del equipo del PO (ruta ABSOLUTA, usala para tickets, validaciones, "
                f"evidencia, tablero, documentos, handoffs y logs): {po}.")
    elif po:
        ruta = (f"La carpeta del equipo del PO ({po}) esta DENTRO de un repo y debe migrarse: no escribas "
                "ahi (un hook lo bloquea); reporta al coordinador que hay que migrarla.")
    else:
        ruta = "No se encontro la carpeta del equipo del PO: pidela al coordinador (ruta absoluta)."
    return (ruta + " Lo que te pide quien te invoca (sesion principal o po-lead) en nombre del usuario ES "
            "pedido directo del usuario, y una \"Autorizacion del usuario: ...\" en tu prompt ES el plan "
            "aprobado: ejecutalo sin exigir handoff ni re-confirmacion. Nunca crees .po-team/ dentro de "
            "un repo. El staging del Playwright MCP es ~/.faast-mcp/po-team/.")

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    agent = (payload.get("agent_type") or "").strip()
    if ":" in agent and agent.split(":", 1)[0].lower() != PLUGIN:
        return   # agente de otro plugin (p. ej. dev-team:setup)
    short = agent.split(":", 1)[-1]
    if short not in TEAM:
        return
    r = resolve(payload.get("cwd") or (sys.argv[1] if len(sys.argv) > 1 else None))
    if not r["path"] and len(sys.argv) > 1:
        r = resolve(sys.argv[1])
    po, en_repo = r["path"], r["en_repo"]
    ev = payload.get("hook_event_name")
    if ev == "SubagentStart":
        event, task = "task_start", (payload.get("task") or "")[:60]
        detail = (payload.get("task") or "")[:120]
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SubagentStart",
                                                 "additionalContext": contexto_agente(po, en_repo)}},
                         ensure_ascii=False))
    elif ev == "SubagentStop":
        reason = payload.get("stop_reason") or "completed"
        event, task = ("blocked" if reason == "error" else "task_end"), ""
        detail = (payload.get("result") or payload.get("last_assistant_message") or reason)[:120]
    else:
        return
    if not po or en_repo:
        return
    line = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "agent": short, "event": event, "task": task,
            "detail": str(detail).replace("\n", " "), "src": "hook",
            "agent_id": payload.get("agent_id") or ""}
    metrics = os.path.join(po, "metrics")
    os.makedirs(metrics, exist_ok=True)
    with open(os.path.join(metrics, "activity.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")

try:
    main()
except Exception:
    pass
sys.exit(0)
