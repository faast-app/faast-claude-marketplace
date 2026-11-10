#!/usr/bin/env python3
# dev-team — logging AUTOMATICO de actividad de agentes (via hooks SubagentStart/SubagentStop).
# Agrega una linea JSON a <coordinacion canonica>/metrics/activity.jsonl — la fuente de
# /team-office, /team-metrics y de los pendientes de inicio de sesion.
# La coordinacion se resuelve con coord_root.py (carpeta del proyecto, NUNCA dentro de un repo):
# si la unica coordinacion encontrada vive dentro de un repo (proyecto legado sin migrar), NO se
# escribe ahi. En SubagentStart ademas entrega al agente su contexto de equipo (ruta absoluta de la
# coordinacion y reglas de pedidos reenviados). Nunca falla hacia afuera.
import datetime
import json
import os
import sys

# Windows: la consola no es UTF-8 por defecto; sin esto los acentos y simbolos rompen la salida.
for _flujo in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coord_root import resolve  # noqa: E402

TEAM = {"setup", "product-owner", "architect", "ui-designer", "lead", "backend", "frontend",
        "dba", "qa", "qa-frontend", "qa-backend", "release-manager", "infra", "cybersec", "tech-writer",
        "ux-researcher", "visual-designer", "motion-designer", "artist-3d", "design-engineer",
        "pentester", "appsec", "cloudsec"}


def _contexto_base(coord, en_repo):
    if coord and not en_repo:
        ruta = f"Coordinacion canonica del proyecto (ruta ABSOLUTA, usala para handoffs, evidencia y logs): {coord}."
    elif coord:
        ruta = (f"La coordinacion de este proyecto ({coord}) esta DENTRO de un repo y debe migrarse: no "
                "escribas ahi (un hook lo bloquea); reporta al coordinador que hay que migrarla.")
    else:
        ruta = "No se encontro la coordinacion del proyecto: pidela al coordinador (ruta absoluta)."
    return (ruta + " Lo que te pide quien te invoca (sesion principal o lead) en nombre del usuario ES "
            "pedido directo del usuario: ejecutalo sin exigir handoff ni mensaje propio. Nunca crees "
            ".coordination/ dentro de un repo; al repo solo va codigo, migraciones de BD y docs tecnicos.")


CANAL = (' CANAL: el usuario solo habla con la sesion principal (Remote Control / movil / segundo plano): NUNCA pidas que te escriba en tu hilo ni lo pongas como condicion. Si dudas de una "Autorizacion del usuario" reenviada antes de una accion sensible, verificala: python3 "{script}" verificar "<frase textual>" (VERIFICADO = ejecuta; NO ENCONTRADO = devuelve la pregunta al coordinador). PERMISOS: una herramienta denegada no se reintenta ni se rodea: sigue con lo demas y reportala (comando y motivo). Si SubagentHandback es rechazada, tu reporte va como texto final de tu turno.')


def lecciones_para(coord, en_repo, agente, tarea):
    """Lecciones validadas de la memoria del equipo para este agente y tarea (RAG). Nunca falla."""
    if not coord or en_repo:
        return ""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills",
                                        "memoria-equipo", "scripts"))
        from memoria import texto_para_agente
        bloque = texto_para_agente(coord, agente, tarea or "", k=4, registrar=True)
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills", "memoria-equipo",
                            "scripts", "memoria.py")
        return ("\n" + bloque + f"\n(memoria.py = python3 \"{os.path.normpath(ruta)}\")") if bloque else ""
    except Exception:
        return ""


def contexto_agente(coord, en_repo, agente="", tarea=""):
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pedidos_usuario.py")
    return (_contexto_base(coord, en_repo) + CANAL.format(script=script)
            + lecciones_para(coord, en_repo, agente, tarea))


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
                                                 "additionalContext": contexto_agente(coord, en_repo, short,
                                                                                      payload.get("task") or "")}},
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
