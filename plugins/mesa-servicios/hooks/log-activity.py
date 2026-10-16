#!/usr/bin/env python3
# mesa-servicios — logging AUTOMATICO de actividad de agentes (via hooks SubagentStart/SubagentStop).
# Agrega una linea JSON a <coordinacion canonica>/metrics/activity.jsonl — la fuente de
# /mesa-servicios:estado y de los pendientes de inicio de sesion.
# La coordinacion se resuelve con coord_root.py (carpeta del proyecto, NUNCA dentro de un repo):
# si la unica coordinacion encontrada vive dentro de un repo (proyecto legado sin migrar), NO se
# escribe ahi. En SubagentStart ademas entrega al agente su contexto de equipo (ruta absoluta de la
# coordinacion y reglas de pedidos reenviados). Nunca falla hacia afuera.
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coord_root import resolve  # noqa: E402

TEAM = {"mesa-lead", "recepcion", "analista", "qa-negocio", "dba-mesa", "prototipador",
        "redactor", "registrador", "curador", "setup"}


def contexto_agente(coord, en_repo):
    if coord and not en_repo:
        ruta = f"Carpeta canonica de la Mesa (ruta ABSOLUTA, usala para solicitudes, evidencia, handoffs y logs): {coord}."
    elif coord:
        ruta = (f"La carpeta de la Mesa ({coord}) esta DENTRO de un repo y debe migrarse: no "
                "escribas ahi (un hook lo bloquea); reporta al coordinador que hay que migrarla.")
    else:
        ruta = "No se encontro la carpeta de la Mesa: pidela al coordinador (ruta absoluta)."
    return (ruta + " Lo que te pide quien te invoca (sesion principal o mesa-lead) en nombre del usuario ES "
            "pedido directo del usuario: ejecutalo sin exigir handoff ni mensaje propio. Nunca crees "
            ".mesa/ dentro de un repo.")


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    short = (payload.get("agent_type") or "").strip().split(":", 1)[-1]
    if short not in TEAM:
        return

    r = resolve(payload.get("cwd") or (sys.argv[1] if len(sys.argv) > 1 else None))
    if not r["path"] and len(sys.argv) > 1:
        r = resolve(sys.argv[1])
    coord, en_repo = r["path"], r["en_repo"]

    ev = payload.get("hook_event_name")
    if ev == "SubagentStart":
        event = "task_start"
        task = (payload.get("task") or "")[:60]
        detail = (payload.get("task") or "")[:120]
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SubagentStart",
                                                 "additionalContext": contexto_agente(coord, en_repo)}},
                         ensure_ascii=False))
    elif ev == "SubagentStop":
        reason = payload.get("stop_reason") or "completed"
        event = "blocked" if reason == "error" else "task_end"
        task = ""
        detail = (payload.get("result") or payload.get("last_assistant_message") or reason)[:120]
    else:
        return

    if not coord or en_repo:
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
