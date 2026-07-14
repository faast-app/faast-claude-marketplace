---
description: Verifica estado de git antes de commitear (branch correcto, archivos correctos, sin conflictos)
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


Ejecuta verificaciones de git antes de commitear:

1. **Branch:** `git branch --show-current`
   - Si es `main` o `develop` → ERROR: "No debes commitear aqui. Cambia a tu branch asignado."
   - Si es otro → OK, mostrar nombre

2. **Archivos staged:** `git diff --cached --name-only`
   - Verificar que SOLO son archivos de tu area de responsabilidad
   - Si hay archivos de otro agente → ADVERTENCIA con lista

3. **Conflictos:** `git diff --check`
   - Si hay marcadores de conflicto → ERROR: "Resuelve conflictos primero o crea handoff al Lead"

4. **Cambios sin stage:** `git status --short`
   - Si hay archivos modificados no staged → INFO: mostrar lista

5. **Sincronizacion:** `git fetch origin && git status -sb`
   - Si el branch remoto tiene commits nuevos → ADVERTENCIA: "Haz git pull --rebase antes de commitear"

6. **Resumen:**
   - Branch: {nombre} (OK/ERROR)
   - Archivos staged: N (OK/ADVERTENCIA)
   - Conflictos: ninguno/encontrados
   - Sincronizado: si/no
   - Veredicto: LISTO PARA COMMIT / CORREGIR ANTES DE COMMIT
