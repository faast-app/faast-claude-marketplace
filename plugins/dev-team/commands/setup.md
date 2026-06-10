---
description: Valida e instala todos los prerequisitos del proyecto - git, gh/az CLI, Docker, SDKs, clientes de BD, Playwright. Configura conexiones de BD y autenticacion del tracker. Ejecutalo si algo falla o antes de empezar.
argument-hint: (opcional) que validar - "db", "tracker", "playwright" o vacio para todo
---

# Setup: Validar e instalar prerequisitos

Alcance solicitado: $ARGUMENTS (vacio = checklist completo)

Invoca al agente `setup` para que ejecute su flujo completo:

1. Detectar sistema operativo
2. Leer `.coordination/config.json` (si existe) para saber que necesita el proyecto
3. Validar segun el alcance:
   - **todo** (default): basicos (git, Docker, Node) + tracker + stack + BD + Playwright
   - **db**: solo cliente CLI del motor + conexion (credenciales → `.coordination/dba-access.json`)
   - **tracker**: solo gh CLI + auth (GitHub) o az CLI + extension devops + auth (Azure)
   - **playwright**: solo Playwright/browsers para el agente QA
4. Mostrar tabla de resultados (OK / Falta / Sin configurar)
5. Ofrecer instalar lo que falta (UNA confirmacion, lista explicita)
6. Re-verificar y guardar estado en `.coordination/setup-status.json`
7. Reportar el OK final o el impacto de lo pendiente

Reglas: nunca instalar sin confirmacion; nunca guardar credenciales en archivos
trackeados por git; siempre re-verificar despues de instalar.
