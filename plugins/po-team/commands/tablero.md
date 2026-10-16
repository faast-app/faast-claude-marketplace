---
description: Si no le dices cual, te pregunta que quieres - tablero generico, tablero Organizacion PO, informe de validaciones del sprint, o crear un backlog nuevo en GitHub. Para los tableros, el seguimiento lee los estados reales del GitHub Project (o Azure DevOps), ubica cada ticket en su etapa del ciclo de pase FaaST, calcula el avance por puntos por sprint, lista los cambios desde la revision anterior y los riesgos, redacta el informe diario o semanal en lenguaje de negocio y regenera el dashboard HTML; si la sesion tiene la herramienta Artifact lo publica o actualiza como artifact. Los tableros son solo lectura sobre el tracker; crear el backlog (GitHub Project con el ciclo FaaST, puntos, sprint y fechas de pase) escribe en GitHub y va con plan y OK. Uso - /po-team:tablero [generica|organizacion|validaciones|crear-backlog] [diario|semanal] [--sprint N] [--publicar] [--sin-html]
argument-hint: '[generica | organizacion | validaciones | crear-backlog] [diario | semanal] [--sprint N] [--publicar] [--sin-html]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual. NUNCA lo corras dentro de un subagente ni lo
> invoques via Agent/Task. Solo se delegan los AGENTES del equipo, y unicamente
> cuando este procedimiento lo indica.

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
| 4 | **Crear un backlog en GitHub** | Un GitHub Project nuevo con el ciclo FaaST, puntos, sprint y fechas de pase, listo para usar | Paso B |

Si el config todavia no tiene ningun Project (`tracker.github.projects` vacio o con numero 0), decir
que las opciones 1-3 necesitan un tablero y recomendar la 4. Guardar la eleccion en
`tablero.ultimaOpcion` (escritura local del config, permitida).

Las opciones 1 y 2 son SOLO LECTURA sobre el tracker y escriben unicamente en `.po-team/tablero/`.

## Paso 1 — Datos (agente `seguimiento`)
Invocar al `seguimiento` con el alcance. Sigue la skill `dashboard-po`: lee cada Project del
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
Requiere `gh` con el scope `project` (si falta: `gh auth refresh -s project`, o `/po-team:setup tracker`).
Con Azure DevOps esta opcion no aplica: decir que el backlog se crea en Boards y ofrecer
`/po-team:setup tracker` para conectarlo.

1. **Preguntar UNA vez** lo que no este en el config: organizacion (`tracker.github.org`), nombre del
   backlog (sugerir "Backlog {equipo}"), repos que se vinculan (`tracker.github.repos`), duracion
   del sprint (por defecto 2 semanas; la iteracion de GitHub se mide en dias corridos, asi que 10 dias
   habiles de `capacidad.duracionSprintDias` = 14) y fecha de inicio del primer sprint (un lunes), y si se agregan los issues abiertos de esos repos.
2. **Plan** (mostrar y esperar el OK; nada se crea antes):
   - Project nuevo `{nombre}` en `{org}`: `gh project create --owner {org} --title "{nombre}" --format json`.
   - Campo **Status** con las opciones del ciclo, en orden: los estados de `ciclo.etapas[].estados`,
     `ciclo.estadosObservado` y `ciclo.estadosBloqueado` del config; si el config aun tiene los
     valores de ejemplo, proponer: No iniciado · En desarrollo · Desarrollo terminado · En QA ·
     Validado por QA · Pase a Demo · En validacion · Observado · Bloqueado · VB cliente. Se cambian
     las opciones del Status que trae el Project con `gh api graphql` (mutacion
     `updateProjectV2Field` con `singleSelectOptions`, cada opcion con nombre, color y una
     descripcion corta de negocio).
   - Campo **Puntos** (numero): `gh project field-create {n} --owner {org} --name Puntos --data-type NUMBER`.
   - Campo **Sprint** (iteracion de `{duracion}` dias corridos desde `{inicio}`): `gh api graphql`
     mutacion `createProjectV2Field` con `dataType: ITERATION` e `iterationConfiguration {startDate, duration}`; si la cuenta no lo permite, campo de seleccion
     "Sprint" con Sprint 1..4 y avisarlo.
   - Campos de fecha **Fecha Demo**, **Fecha Preprod**, **Fecha VB cliente**
     (`--data-type DATE`).
   - Vincular los repos: `gh project link {n} --owner {org} --repo {org}/{repo}`.
   - Opcional, si lo pidio: agregar los issues abiertos con `gh project item-add` (decir cuantos son
     antes; mas de ~200 pedir confirmacion aparte). Sus estados quedan en el primero del ciclo
     hasta que alguien los mueva.
3. **Ejecutar** en ese orden; si un paso falla, detenerse, decir que quedo creado y que no, sin
   reintentar a ciegas.
4. **Guardar en el config** (escritura local): el Project en `tracker.github.projects` (alias,
   numero, titulo, campos `estado: Status`, `puntos: Puntos`, `sprint: Sprint`, `fechaDemo`,
   `fechaPreprod`, `fechaVB`), `projectDefault`, `sprintVia: iteration` y el mapeo
   `ciclo.etapas[].estados` con los nombres reales de las opciones creadas.
5. **Entregar**: enlace al Project y lo que falta a mano (GitHub no permite crear vistas por API):
   crear la vista **Tablero** agrupada por Status y, si se quiere, una vista **Sprint actual**
   filtrada por la iteracion en curso. Sugerir `/po-team:refinar` para cargar las primeras HUs y
   luego `/po-team:tablero` (opcion 1 o 2).

Nunca se borra ni renombra un Project existente; si ya hay uno con el mismo nombre en la org,
avisar y preguntar si se usa ese (solo se registra en el config) o se crea otro con otro nombre.

## Reglas
- Datos reales; lo que falta se muestra como faltante, nunca se estima a ojo.
- Lenguaje de negocio; sin datos personales.
- Tableros y validaciones: solo lectura sobre el tracker. Crear el backlog: solo con plan aprobado.
