#!/bin/bash
# po-team — inyecta el protocolo del equipo del PO en la SESION PRINCIPAL (SessionStart).
# La logica vive en session_context.py (carpeta .po-team canonica fuera de los repos, exclusion
# local en git, protocolo, avisos de mantenimiento y pendientes). Nunca falla hacia afuera.
python3 "$(dirname "$0")/session_context.py" 2>/dev/null || true
exit 0
