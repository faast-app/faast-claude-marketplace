#!/usr/bin/env python3
# dev-team — logging AUTOMATICO de actividad de agentes (via hooks).
# Recibe el payload del hook (SubagentStart/SubagentStop) por stdin y agrega una
# linea JSON a .coordination/metrics/activity.jsonl — la fuente de /team-office
# y /team-metrics. Nunca falla hacia afuera (cualquier error sale con codigo 0).
import json, os, sys, datetime

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return

    agent = (payload.get("agent_type") or "").strip()
    if not agent:
        return
    TEAM = {"setup","product-owner","architect","ui-designer","lead","backend","frontend",
            "dba","qa","qa-frontend","qa-backend","release-manager","infra","cybersec","tech-writer"}
    short = agent.split(":", 1)[-1]
    if short not in TEAM:
        return

    def find_coord(start):
        if not start:
            return None
        d = os.path.abspath(start)
        for _ in range(8):
            c = os.path.join(d, ".coordination")
            if os.path.isdir(c):
                return c
            parent = os.path.dirname(d)
            if parent == d:
                return None
            d = parent
        return None

    coord = find_coord(payload.get("cwd")) or find_coord(sys.argv[1] if len(sys.argv) > 1 else None)
    if not coord:
        return

    ev = payload.get("hook_event_name")
    if ev == "SubagentStart":
        event = "task_start"
        task = (payload.get("task") or "")[:60]
        detail = (payload.get("task") or "")[:120]
    elif ev == "SubagentStop":
        reason = payload.get("stop_reason") or "completed"
        event = "blocked" if reason == "error" else "task_end"
        task = ""
        detail = (payload.get("result") or payload.get("last_assistant_message") or reason)[:120]
    else:
        return

    line = {
        "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agent": short,
        "event": event,
        "task": task,
        "detail": detail.replace("\n", " "),
        "src": "hook",
        "agent_id": payload.get("agent_id") or "",
    }
    metrics = os.path.join(coord, "metrics")
    os.makedirs(metrics, exist_ok=True)
    with open(os.path.join(metrics, "activity.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")

try:
    main()
except Exception:
    pass
sys.exit(0)
