#!/usr/bin/env python3
# mesa-servicios — logging AUTOMATICO de actividad de agentes (via hooks).
# Recibe el payload del hook (SubagentStart/SubagentStop) por stdin y agrega una
# linea JSON a .mesa/metrics/activity.jsonl. Nunca falla hacia afuera (exit 0).
import json, os, sys, datetime

TEAM = {"mesa-lead","recepcion","analista","qa-negocio","dba-mesa","prototipador",
        "redactor","registrador","curador","setup"}

def find_mesa(start):
    # .mesa canonica = la que tiene config.json; se sube hasta 8 niveles.
    if not start:
        return None
    d = os.path.abspath(start)
    bare = None
    for _ in range(8):
        c = os.path.join(d, ".mesa")
        if os.path.isdir(c):
            if os.path.isfile(os.path.join(c, "config.json")):
                return c
            if bare is None:
                bare = c
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return bare

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    agent = (payload.get("agent_type") or "").strip()
    short = agent.split(":", 1)[-1]
    if short not in TEAM:
        return
    mesa = find_mesa(payload.get("cwd")) or find_mesa(sys.argv[1] if len(sys.argv) > 1 else None)
    if not mesa:
        return
    ev = payload.get("hook_event_name")
    if ev == "SubagentStart":
        event, task = "task_start", (payload.get("task") or "")[:60]
        detail = (payload.get("task") or "")[:120]
    elif ev == "SubagentStop":
        reason = payload.get("stop_reason") or "completed"
        event, task = ("blocked" if reason == "error" else "task_end"), ""
        detail = (payload.get("result") or payload.get("last_assistant_message") or reason)[:120]
    else:
        return
    line = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "agent": short, "event": event, "task": task,
            "detail": detail.replace("\n", " "), "src": "hook", "agent_id": payload.get("agent_id") or ""}
    metrics = os.path.join(mesa, "metrics")
    os.makedirs(metrics, exist_ok=True)
    with open(os.path.join(metrics, "activity.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")

try:
    main()
except Exception:
    pass
sys.exit(0)
