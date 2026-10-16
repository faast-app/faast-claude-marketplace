#!/bin/bash
# mesa-servicios — inyecta el protocolo de la Mesa en la SESION PRINCIPAL (SessionStart).
# La logica vive en session_context.py (carpeta .mesa canonica fuera de los repos, exclusion
# local en git, protocolo y pendientes). Nunca falla hacia afuera.
python3 "$(dirname "$0")/session_context.py" 2>/dev/null || true
exit 0
