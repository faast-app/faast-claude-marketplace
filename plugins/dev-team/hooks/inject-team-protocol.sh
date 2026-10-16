#!/bin/bash
# dev-team — inyecta el protocolo de orquestacion del equipo en la SESION PRINCIPAL.
# SessionStart hook: lo que se imprime se agrega como contexto de la sesion.
# La logica vive en session_context.py (resolucion de la coordinacion canonica fuera de
# los repos, exclusion local en git, protocolo y pendientes). Nunca falla hacia afuera.
python3 "$(dirname "$0")/session_context.py" 2>/dev/null || true
exit 0
