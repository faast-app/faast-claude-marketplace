#!/bin/bash
# dev-team — wrapper del logging automatico de actividad (hooks Subagent*).
# El stdin (payload JSON del hook) pasa directo al python. Salida SIEMPRE 0:
# un fallo de logging jamas debe romper al agente.
python3 "$(dirname "$0")/log-activity.py" "$CLAUDE_PROJECT_DIR" 2>/dev/null || true
exit 0
