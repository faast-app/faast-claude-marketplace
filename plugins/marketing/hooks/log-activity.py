#!/usr/bin/env python3
# marketing — logging AUTOMATICO de actividad de agentes (via hooks).
# Recibe el payload del hook (SubagentStart/SubagentStop) por stdin y agrega una linea JSON a
# .marketing/metrics/activity.jsonl de la carpeta CANONICA (coord_root.resolve). Si la carpeta
# canonica esta dentro de un repo git, no escribe (la regla es que viva fuera). Nunca falla
# hacia afuera (exit 0).
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coord_root import resolve  # noqa: E402

TEAM = {"director-marketing","investigador-mercado","analista-producto","estratega-comercial",
        "redactor-publicitario","disenador-presentaciones","director-motion","disenador-grafico"}


def carpeta(start):
    if not start:
        return None
    r = resolve(start)
    if not r["path"] or r["en_repo"]:
        return None
    return r["path"]


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    agent = (payload.get("agent_type") or "").strip()
    short = agent.split(":", 1)[-1]
    if short not in TEAM:
        return
    mk = carpeta(payload.get("cwd")) or carpeta(sys.argv[1] if len(sys.argv) > 1 else None)
    if not mk:
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
    metrics = os.path.join(mk, "metrics")
    os.makedirs(metrics, exist_ok=True)
    with open(os.path.join(metrics, "activity.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


try:
    main()
except Exception:
    pass
sys.exit(0)
