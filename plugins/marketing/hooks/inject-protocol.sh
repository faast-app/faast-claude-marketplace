#!/bin/bash
# marketing — inyecta el protocolo del equipo de Marketing en la SESION PRINCIPAL (SessionStart).
# La logica vive en session_context.py (carpeta .marketing canonica fuera de los repos, exclusion
# local en git, protocolo, tendencias vencidas y pendientes). Nunca falla hacia afuera.
python3 "$(dirname "$0")/session_context.py" 2>/dev/null || true
exit 0
