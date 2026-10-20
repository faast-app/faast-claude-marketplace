---
description: Si no le dices cual, te pregunta que quieres - tablero generico, tablero Organizacion PO, informe de validaciones del sprint, o crear un backlog nuevo en GitHub. Para los tableros, el seguimiento lee los estados reales del GitHub Project (o Azure DevOps), ubica cada ticket en su etapa del ciclo de pase FaaST, calcula el avance por puntos por sprint, lista los cambios desde la revision anterior y los riesgos, redacta el informe diario o semanal en lenguaje de negocio y regenera el dashboard HTML; si la sesion tiene la herramienta Artifact lo publica o actualiza como artifact. Los tableros son solo lectura sobre el tracker; crear el backlog (GitHub Project con el ciclo FaaST, puntos, sprint y fechas de pase, skill backlog-github - crear, agregar, verificar, espejo) escribe en GitHub y va con plan y OK. Uso - /po-team:tablero [generica|organizacion|validaciones|crear-backlog [agregar|verificar [--corregir]|espejo]] [diario|semanal] [--sprint N] [--publicar] [--sin-html]
argument-hint: '[generica | organizacion | validaciones | crear-backlog [agregar | verificar [--corregir] | espejo]] [diario | semanal] [--sprint N] [--publicar] [--sin-html]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica, SIEMPRE con su nombre completo `po-team:{agente}`
> (dev-team y mesa-servicios tambien tienen un agente `setup`: sin prefijo se puede invocar el
> de otro equipo). Al invocar: ruta ABSOLUTA de `.po-team/`, "Pedido del usuario (textual): ..."
> y, si el usuario aprobo un plan, "Autorizacion del usuario: {plan literal}".

# Tablero: como va cada sprint, en 20 segundos

Pedido: $ARGUMENTS (por defecto el informe configurado en `tablero.informe`, todos los sprints
activos, HTML regenerado)

## Paso 0 — ¿Que tablero?
Si el pedido ya dice cual (`generica`, `organizacion`, `validaciones`, `crear-backlog`, o el
equivalente en palabras: "el de Organizacion PO", "el de validaciones", "armar un backlog"), o trae
`--plantilla {generica|organizacion}` (forma anterior, sigue valiendo), ir directo. Si no, preguntar
UNA vez con opciones (herramienta de preguntas con opciones si la sesion la tiene; si no, lista
numerada), marcando como recomendada la ultima elegida (`tablero.ultimaOpcion`) o, la primera vez,
`tablero.plantilla`:

| # | Opcion | Que entrega | Sigue en |
|---|---|---|---|
| 1 | **Tablero generico** | KPIs, stepper por sprint, chips por etapa, fechas, cambios y riesgos | Paso 1 |
| 2 | **Organizacion PO** | KPIs, cambios desde la revision anterior, tarjeta por sprint con anillo de avance y chips con el estado del tablero, fechas comprometidas y lo que pide atencion | Paso 1 |
| 3 | **Validaciones del sprint** | Pagina con cada ticket validado: casos, evidencia, bloqueos, decisiones y bugs | Paso V |
| 4 | **Crear un backlog en GitHub** | Un GitHub Project con el ciclo FaaST, puntos, sprint y fechas de pase, listo para usar (o completar / verificar uno existente: `crear-backlog agregar`, `crear-backlog verificar`) | Paso B |

Si el config todavia no tiene ningun Project (`tracker.github.projects` vacio o con numero 0), decir
que las opciones 1-3 necesitan un tablero y recomendar la 4. Guardar la eleccion en
`tablero.ultimaOpcion` (escritura local del config, permitida).

Las opciones 1 y 2 son SOLO LECTURA sobre el tracker y escriben unicamente en `.po-team/tablero/`.

## Paso 1 — Datos (agente `po-team:seguimiento`)
Invocar al agente `po-team:seguimiento` con el alcance. Sigue la skill `dashboard-po`: lee cada Project del
config, ubica tickets por sprint y etapa, incorpora veredictos del validador-po y fechas de
`.po-team/sprints/`, calcula avance, compara con el snapshot anterior y guarda el nuevo.

## Paso 2 — Dashboard
Salvo `--sin-html`: regenera el HTML con `tablero-datos.json` embebido, desde la plantilla de la
opcion elegida:

| Opcion | Plantilla | Salida |
|---|---|---|
| 1 `generica` | `templates/tablero/tablero.html` | `{tablero.outputDir}/tablero.html` |
| 2 `organizacion` | `templates/tablero/organizacion-po.html` | `{tablero.outputDir}/organizacion-po.html` |

Ambas leen el mismo JSON (skill `dashboard-po` §3): cambiar de plantilla no cambia los datos. Cada
plantilla publica en su propia URL: `tablero.artifactUrl` para la generica y
`tablero.artifactUrls.organizacion` para la otra.
**Publicar** si `--publicar` o si la URL de esa plantilla ya existe y la sesion tiene el tool
`Artifact`: siempre la misma URL (en sesion nueva, leer primero esa URL y publicar sobre ella);
la primera vez se guarda la URL en el config. Sin el tool: se entrega la ruta local.
Publicar no escribe en el tracker; el artifact queda privado hasta que el PO decida compartirlo.

## Paso 3 — Informe
Mostrar el informe (formato de la skill, §9) y guardarlo en `informes/`. Primero lo urgente
(fechas vencidas, observados, bloqueados, sin movimiento), luego avance y cambios.

## Paso 4 — Siguiente accion
Si hay algo accionable, sugerir el comando exacto, sin ejecutarlo:
- observado sin devolver → `/po-team:refinar --observacion #n`
- tickets en Demo sin VB PO → `/po-team:validar --lote sprint N --ambiente {demo}`
- items sin estimar o "Sin etapa" → `/po-team:refinar --estimar` / `/po-team:setup tracker`
- fecha en riesgo → `/po-team:sprint replanificar`

## Paso V — Validaciones del sprint (opcion 3)
1. Preguntar sprint y ambiente si el pedido no los trae (sugerir el sprint activo y el ambiente de su
   etapa). Buscar `.po-team/validaciones/{sprint}-{ambiente}/validacion-datos.json`.
2. **Si existe:** regenerar el HTML y publicarlo exactamente como el Paso 3b de `/po-team:validar`
   (misma URL de `validacion.artifactUrls["{sprint}-{ambiente}"]`). No vuelve a validar nada.
3. **Si no existe:** no hay validaciones guardadas para ese sprint. Ofrecer correr
   `/po-team:validar --lote sprint {N} --ambiente {clave} --artifact` (necesita el navegador y las
   cuentas del ambiente; avisar la duracion, ~10-20 min por ticket) y, con el OK, seguir ese comando.

## Paso B — Crear un backlog en GitHub (opcion 4) — escribe en GitHub: plan + OK
Cargar la skill `backlog-github` (reglas duras, spec, limites de la API). Todo lo hace su script
idempotente; nunca se arman campos ni opciones con comandos `gh` sueltos (reemplazar las opciones
del Status sin sus ids borra el estado de todos los items):

```bash
S="${CLAUDE_PLUGIN_ROOT}/skills/backlog-github/scripts/project_backlog.py"
```

Formas de uso:
- `crear-backlog` — Project nuevo (o reutilizar uno existente si el usuario lo decide).
- `crear-backlog agregar` — completar un Project que ya existe: ciclo, campos, vistas, epicas o HUs que falten.
- `crear-backlog verificar [--corregir]` — revisar la salud del Project (y arreglar lo corregible).
- `crear-backlog espejo` — regenerar `.po-team/backlog.md` (local, sin OK: no toca GitHub).

Con Azure DevOps (`tracker.provider: "azure"`) esta opcion no aplica: decir que el backlog se crea en
Boards y ofrecer `/po-team:setup tracker`. Requiere `gh` con el scope `project` (`gh auth status`; si
falta, el usuario corre `gh auth refresh -s project` o `/po-team:setup tracker`; no se hace auth desde
el agente). Si falta `gh`, se puede igual mostrar el plan con `--dry-run --offline`.

1. **Preguntar UNA vez, todo junto,** solo lo que no este en el config: organizacion
   (`tracker.github.org`), nombre exacto del backlog (sugerir "Backlog {equipo}"), repo donde viven
   las HUs (`repoDefault`) y repos que se vinculan (`repos`), fecha de inicio del primer sprint (un
   lunes), duracion (por defecto 14 dias corridos = 10 habiles de `capacidad.duracionSprintDias`),
   cuantos sprints crear (por defecto 4) y si se agregan los issues abiertos de esos repos. En
   `agregar`, partir del spec guardado (`.po-team/project-state/<nombre>.spec.json` o la clave `spec`
   del estado) y sumar solo lo nuevo.
2. **Generar el spec** (formato en la skill; ejemplo en
   `${CLAUDE_PLUGIN_ROOT}/skills/backlog-github/assets/spec-ejemplo.json`) y guardarlo fuera de todo
   repo en `.po-team/project-state/<nombre>.spec.json`. El Status sale de `ciclo.etapas[].estados` +
   `estadosObservado` + `estadosBloqueado`; si el config aun tiene `{{...}}`, el ciclo FaaST por
   defecto (No iniciado · En desarrollo · Desarrollo terminado · En QA · Validado por QA · Pase a Demo ·
   En validacion · Observado · Bloqueado · VB cliente). HUs o epicas en el spec solo si el usuario las
   trae ya redactadas en lenguaje de negocio (si no, despues con `/po-team:refinar`).
3. **Plan en modo prueba**: `python3 "$S" crear SPEC --dry-run` (`agregar SPEC --dry-run` en
   `agregar`; `--offline` si aun no hay acceso a GitHub). Mostrar al usuario: Project a crear o
   reutilizar, repos a vincular, opciones del Status (renombres conservando id, opciones nuevas,
   opciones que se conservan), campos Puntos / Sprint / Prioridad / fechas, sprints con sus fechas,
   vistas, items y advertencias. Si avisa jerga tecnica o HUs sin Dado / Cuando / Entonces, corregir el
   spec y volver a mostrar el plan.
   - **Si el plan dice `[REUTILIZAR] Project` en `crear`**: ya existe uno con ese nombre. Preguntar si
     se usa ese (se ejecuta con `--reutilizar`; solo se completa, nada se borra) o se elige otro nombre.
     Nunca se borra ni se renombra un Project existente.
4. **Esperar el OK explicito** ("¿Lo creo en GitHub?"). Sin un si claro, no se escribe nada. Si el plan
   muestra mas de 200 issues abiertos por agregar, pedir una confirmacion aparte (`--masivo`).
5. **Ejecutar**: `python3 "$S" crear SPEC` (o `--reutilizar` / `agregar SPEC`). Si se corta (rate limit,
   red), re-ejecutar el mismo comando: reanuda sin duplicar. Si la API rechaza el campo de iteracion,
   el script crea Sprint como seleccion simple y lo avisa.
6. **Registro** (lo hace el script, escritura atomica local que conserva el resto del config):
   `tracker.github.projects[]` (alias, numero, titulo, campos `estado`, `puntos`, `sprint`, `prioridad`,
   `fechaDemo`, `fechaPreprod`, `fechaVB`), `projectDefault`, `sprintVia` (`iteration` / `select` /
   `milestone`), `ciclo.etapas[].estados` con los nombres reales de las opciones y el espejo
   `.po-team/backlog.md`. Confirmarlo leyendo el config.
7. **Entregar**: enlace al Project, que se creo y que se reutilizo, `sprintVia`, avisos del script y lo
   que queda a mano: la API crea las vistas **Tablero**, **Sprint actual** (filtro `sprint:@current`) y
   **Backlog** (filtro `no:sprint`), pero el agrupamiento y el orden de cada vista se fijan en la
   interfaz (confirmar que el Tablero usa Status como columnas); con Sprint de seleccion, el filtro del
   sprint en curso tambien es manual; los workflows del Project se configuran en la interfaz. Sugerir
   `/po-team:refinar` para cargar las primeras HUs y luego `/po-team:tablero` (opcion 1 o 2).

`verificar`: `python3 "$S" verificar SPEC` (solo lectura) y mostrar los hallazgos; con el OK del usuario,
`python3 "$S" verificar SPEC --corregir` (agrega opciones o campos faltantes, convierte borradores en
issues, llena Status vacios, enlaza sub-issues; nunca borra ni pisa valores). Sin spec guardado, armar
uno minimo con `project` (org y repo salen del config).

## Reglas
- Datos reales; lo que falta se muestra como faltante, nunca se estima a ojo.
- Lenguaje de negocio; sin datos personales.
- Tableros y validaciones: solo lectura sobre el tracker. Crear el backlog: solo con plan aprobado.
