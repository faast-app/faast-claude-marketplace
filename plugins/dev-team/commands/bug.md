---
description: Reporta un bug con REPRODUCCION OBLIGATORIA - QA replica el problema paso a paso en el ambiente real, con evidencia, y emite un veredicto explicito (REPRODUCIDO / NO REPRODUCIDO / BLOQUEADO) ANTES de que se registre el bug o se hable de la correccion. Uso - /dev-team:bug {descripcion, ID o URL del ticket}
argument-hint: '{descripcion} | {ID o URL} | #12 #15 #21 (lote) | --nuevos | --etiqueta bug --estado Nuevo | --sprint actual  [--ambiente qa|desa|demo] [--paralelo N]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Bug: reproducir primero, registrar despues

Reporte: $ARGUMENTS

**REGLA DE ESTE COMANDO (dura):** ningun bug se registra en el tracker, se triagea ni se
asigna a un dev hasta que el equipo QA lo haya **reproducido y confirmado con evidencia**.
"Me paso una vez" no es un bug registrado: es un reporte pendiente de reproduccion.

## Modo LOTE (varios tickets a la vez)
Si $ARGUMENTS trae **varios IDs/URLs** (`#12 #15 #21`), un **filtro** (`--nuevos` = bugs en
estado inicial sin reproduccion; `--etiqueta bug --estado Nuevo`; `--sprint actual`) o un
**archivo** (`--lista bugs.txt`, un ticket por linea), el flujo es el mismo por ticket, con
estas reglas de lote:
1. **Listar y confirmar** primero: mostrar la tabla de tickets candidatos (ID, titulo,
   ambiente inferido) y esperar el OK del usuario antes de reproducir nada. Maximo 15 por
   lote; si hay mas, proponer cortes.
2. **Un ambiente valido por lote** (Paso 1 se hace UNA vez por ambiente). Tickets que
   requieren otro ambiente van a un sub-lote.
3. **Reproduccion en PARALELO**: la sesion principal / el Lead lanza varias instancias de
   `qa-frontend` y/o `qa-backend`, cada una con UN ticket y su propia carpeta
   `.coordination/evidence/REP-.../` (`--paralelo N`, default 3; nunca dos instancias
   sobre el mismo ticket). Cada instancia aplica los Pasos 0-3 completos y deja su
   `reproduccion.md`. El agente `qa` (QA Lead) consolida.
4. **Consolidado** en `.coordination/evidence/REP-lote-{fecha}/lote.md`:
   ```markdown
   # Lote de reproduccion — {fecha} — ambiente qa (version 2.4.1)
   | Ticket | Titulo | Veredicto | Consistencia | Severidad sugerida | Evidencia |
   |---|---|---|---|---|---|
   | #12 | Registros repetidos al paginar | ✅ REPRODUCIDO | 2/2 | Alta | REP-…-1/ |
   | #15 | Total no cuadra en exportacion | ❌ NO REPRODUCIDO | — | — | REP-…-2/ (funciona: 01-export-ok.png) |
   | #21 | Login lento | ⛔ BLOQUEADO | — | — | sin informe de conformidad de auth |
   Resumen: 1 reproducido · 1 no reproducido · 1 bloqueado
   ```
5. **Paso 4 solo para los REPRODUCIDOS**, en un solo pase del PO (registra/actualiza cada
   ticket con su evidencia embebida) y un solo triaje del Lead (prioriza el lote y presenta
   UN plan con el orden de correccion). Los NO REPRODUCIDOS se comentan en su ticket con lo
   probado y lo que falta; los BLOQUEADOS se agrupan por bloqueo y se escala una vez.
6. La salida al usuario es la tabla consolidada + el plan. Nunca "aprobar" un lote en
   bloque: cada ticket tiene su veredicto propio con su evidencia propia.

## Paso 0 — Entender el reporte (sesion principal, sin agentes)
1. Si $ARGUMENTS es un ID o URL de ticket: leerlo del tracker (`gh issue view` / `az boards
   work-item show`) y extraer pasos, esperado, obtenido, ambiente, usuario, datos.
2. Si es texto libre: estructurarlo en **pasos como usuario**, **resultado esperado**,
   **resultado obtenido**, **ambiente** (`--ambiente` o `urls.*` del config; por defecto
   qa si existe, si no desa), **datos/usuario** necesarios.
3. Si falta algo indispensable para intentar la reproduccion (URL, credencial, dato que
   debe existir): preguntarlo AHORA, una sola vez, todo junto. No adivinar.
4. Asignar ID temporal `REP-{fecha}-{n}` y crear `.coordination/evidence/REP-.../`.

## Paso 1 — Regla de oro (QA no reproduce sin ambiente valido)
Verificar el **informe de conformidad** del ambiente (que version esta desplegada, health
OK) o, en desa, que el stack COMPLETO este levantado (no `npm run dev`). Si no se cumple:
veredicto **BLOQUEADO** (motivo: sin informe / stack incompleto), `blocked` en el log,
avisar al Lead y terminar. Nunca reproducir sobre un ambiente del que no se sabe que
version corre: el veredicto seria invalido.

## Paso 2 — Reproduccion (agente qa; reparte a qa-frontend / qa-backend si aplica)
Invocar al agente `qa` con el reporte estructurado. QA (o su especialista) ejecuta los
pasos EXACTOS, una sola vez, como usuario:
- Frontend: Playwright MCP del plugin — `browser_navigate`, acciones, `browser_take_screenshot`
  en CADA paso (`00-`, `01-`...), `browser_start_tracing`/`browser_start_video` desde el
  inicio, `browser_console_messages` y `browser_network_requests` guardados como `.txt`,
  y `browser_verify_*` para afirmar lo obtenido (ej. "el registro X aparece en ambas
  paginas"). Viewport declarado.
- Backend/API: request exacto reproducible (curl copy-paste) + response completa
  capturada + comparacion con el contrato (`openapi.yml`).
- Registrar version desplegada, ambiente, usuario/rol, datos usados, fecha/hora.
- **LEY:** si algo falla ANTES de llegar al punto del bug (login, servicio caido, dato que
  no existe) → **BLOQUEADO**, evidencia de ese primer intento, reporte inmediato. Sin
  reintentos, sin workarounds, sin debug.
- **Determinismo:** si el bug se reproduce, repetir el recorrido UNA segunda vez para
  clasificarlo como *consistente* (2/2) o *intermitente* (1/2). Un intermitente igual es
  REPRODUCIDO, pero se anota la tasa.

## Paso 3 — Veredicto de reproduccion (obligatorio, explicito)
QA escribe `.coordination/evidence/REP-.../reproduccion.md` con UNO de estos veredictos:

```markdown
# Reproduccion REP-2026-09-11-1 — {titulo corto del problema}
**Veredicto:** ✅ REPRODUCIDO (consistente 2/2) | ✅ REPRODUCIDO (intermitente 1/2) | ❌ NO REPRODUCIDO | ⛔ BLOQUEADO
**Ambiente:** qa · **Version:** frontend 2.4.1 / api 2.4.0 (informe de conformidad {fecha}) · **Usuario/rol:** analista
**Viewport:** 1280x720

## Pasos exactos
| # | Accion | Resultado | Captura |
|---|---|---|---|
| 0 | Ingresar como analista y abrir Cobranzas | Listado pagina 1 con 20 registros | 00-listado-p1.png |
| 1 | Clic en "Siguiente" | Pagina 2 muestra 5 registros que ya estaban en pagina 1 | 01-p2-repetidos.png |

**Esperado:** registros distintos en cada pagina · **Obtenido:** 5 repetidos (IDs 1042, 1043, 1050, 1051, 1052)
**Verificacion:** `browser_verify_list_visible` → los 5 IDs presentes en p1 y p2 → CONFIRMADO
**Consola:** 0 errores · **Red:** GET /api/cobranzas?page=2 → 200 (ver 02-network.txt)
**Trace:** rep.trace.zip · **Clip:** rep.webm (18 s)
**Severidad sugerida:** Alta (afecta a todos los usuarios del listado) — la decide el Lead
```

- **REPRODUCIDO** → continuar al Paso 4.
- **NO REPRODUCIDO** → NO se registra bug. Se informa al usuario que se intento, con los
  pasos exactos, el ambiente/version y la evidencia de que funciono correctamente, y se
  le pide lo que falta para volver a intentar (otro usuario, otro dato, otro ambiente,
  hora exacta, navegador). Si el usuario insiste en registrarlo igual, se crea con
  etiqueta/estado **"No reproducible — requiere informacion"**, nunca como bug confirmado.
- **BLOQUEADO** → se reporta el bloqueo al Lead (que lo destrabe quien corresponda:
  infra/dev) y se reintenta la reproduccion cuando el ambiente este listo.

## Paso 4 — Registrar (solo con REPRODUCIDO)
1. **product-owner** crea el bug en el tracker en lenguaje de negocio (titulo limpio,
   pasos como usuario, esperado vs obtenido, impacto, severidad sugerida) con la
   **evidencia EMBEBIDA** segun la regla dura (GitHub: rama `evidence` +
   `![](raw)`; Azure: attachment + `<img>`), incluyendo la tabla de reproduccion y la
   version/ambiente. Renombrar la carpeta `REP-...` → `BUG-{id}` (o `{issue}-slug` en la
   rama `evidence`).
2. QA registra el evento `verdict` (`task` = BUG-id, `detail` = `REPRODUCIDO consistente|intermitente`).
3. **Lead** hace triaje (componente, severidad, prioridad) y presenta el **plan de
   correccion** (PLAN PRIMERO) → el usuario aprueba → `fix/{bug-id}-...`.
4. QA deja anotado el **test de regresion** que escribira en rojo antes del fix
   (mismos pasos exactos de la reproduccion → `tests/bug-{id}.spec.ts`).

## Salida al usuario en lote
```
Lote de reproduccion — 3 tickets — ambiente qa, version 2.4.1
✅ #12 Registros repetidos al paginar      REPRODUCIDO (siempre)   → registrado con evidencia, severidad Alta
❌ #15 Total no cuadra en exportacion       NO REPRODUCIDO          → comentado en el ticket; falta: archivo de ejemplo y filtro usado
⛔ #21 Login lento                          BLOQUEADO               → sin informe de conformidad de auth; escalado a infra
Siguiente paso: el Lead te presenta el plan de correccion para #12.
```

## Salida al usuario (siempre, en lenguaje claro)
```
Reproduccion del problema "{titulo}"
Veredicto: REPRODUCIDO (consistente) en qa, version 2.4.1
Pasos: 2 · Evidencia: 3 capturas, trace, clip de 18 s · Consola/red: limpias
→ Bug registrado: #1234 (con la evidencia dentro) · Severidad sugerida: Alta
Siguiente paso: el Lead te presenta el plan de correccion para tu OK.
```
o
```
Veredicto: NO REPRODUCIDO en qa (version 2.4.1) siguiendo estos pasos: ...
Lo que si vimos: pagina 2 muestra 20 registros distintos (captura 01-p2-ok.png)
Para volver a intentar necesito: usuario con el que ocurrio, fecha/hora aproximada, filtro aplicado.
No se registro ningun bug.
```

## Reglas
- Sin reproduccion confirmada no hay bug, triaje ni asignacion. Sin excepcion por urgencia:
  un incidente urgente se reproduce igual (es lo mas rapido para acotarlo).
- QA no debuggea ni propone causa: reproduce, documenta y reporta. La causa es del dev.
- Toda la evidencia vive en `.coordination/evidence/` y sube al tracker EMBEBIDA; jamas en
  una rama de codigo.
- Un solo intento por paso salvo la segunda corrida de determinismo; nada de "probar 5
  veces a ver si sale".
- Si el reporte llega por otro camino (`/start`, chat, `/refine`), se redirige a este flujo.
