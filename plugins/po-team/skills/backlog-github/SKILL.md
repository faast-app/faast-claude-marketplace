---
name: backlog-github
description: Procedimiento del equipo del Product Owner (po-team) para crear o completar de forma idempotente el GitHub Project v2 del backlog con el ciclo de pase FaaST - Status con las opciones del ciclo (No iniciado · En desarrollo · Desarrollo terminado · En QA · Validado por QA · Pase a Demo · En validacion · Observado · Bloqueado · VB cliente, o las del config) FUSIONADAS conservando los ids existentes para que ningun item pierda su estado, campos Puntos, Sprint (iteracion, o seleccion si la API la rechaza, o milestone), Prioridad, Fecha Demo, Fecha Preprod y Fecha VB cliente, repos vinculados, vistas Tablero / Sprint actual / Backlog, epicas con sub-issues e HUs opcionales, espejo local en .po-team/backlog.md y registro en .po-team/config.json. Script autosuficiente project_backlog.py (un spec JSON, plan con --dry-run, reanudable, sin dependencia de dev-team). Cargala para /po-team:tablero crear-backlog (crear, agregar, verificar, espejo).
---

# Backlog en GitHub Project v2 con el ciclo FaaST — po-team

Lo usa el comando `/po-team:tablero crear-backlog` (Paso B). Deja un Project listo para que el
tablero (`/po-team:tablero`), el refinador y el seguimiento trabajen sobre el: Status con las
etapas del ciclo FaaST, puntos, sprint y fechas de pase. Todo sale de UN spec JSON y del script
`scripts/project_backlog.py`, que crea o reutiliza cada pieza sin duplicar ni borrar.

```bash
S="${CLAUDE_PLUGIN_ROOT}/skills/backlog-github/scripts/project_backlog.py"
```

## Cuando usarla
- El PO no tiene Project todavia (`tracker.github.projects` vacio o con `numero: 0`).
- Hay un Project pero le faltan el ciclo, Puntos, Sprint o las fechas de pase (`agregar`).
- Revisar la salud del Project: opciones del ciclo, campos, items sin Status, borradores (`verificar`).
- Cargar en bloque las primeras HUs / epicas ya redactadas (items del spec).
- No aplica con Azure DevOps (`tracker.provider: "azure"`): ahi el backlog vive en Boards.

## Reglas duras
1. **Plan primero, escritura solo con OK.** Siempre `--dry-run` y mostrar el plan; sin un si
   claro del usuario no se escribe en GitHub. Si `gh` no esta autenticado o le falta el scope
   `project`, decirlo y parar: el usuario corre `gh auth refresh -s project` (o `/po-team:setup tracker`).
2. **Nunca se borra ni se renombra un Project.** Si ya existe uno con el mismo nombre exacto,
   `crear` se detiene: preguntar al usuario si se reutiliza (re-ejecutar con `--reutilizar`) o se
   usa otro nombre. Si hay dos con el mismo nombre, el usuario elige.
3. **Status sin perdida de datos.** Las opciones se fusionan pasando el `id` de cada opcion
   existente (`updateProjectV2Field` sin ids recrea las opciones y GitHub BORRA el Status de
   todos los items). Ninguna opcion existente se elimina. Las opciones por defecto se renombran
   conservando su id: Todo → primer estado del ciclo, In Progress → segundo, Done → ultimo (salvo
   que ese nombre ya sea parte del ciclo).
4. **Nunca se modifica la configuracion de una iteracion existente** (reemplazarla puede vaciar
   el sprint de los items). Si faltan sprints, se avisa y se agregan en la interfaz.
5. **Nunca borradores**: cada item es un issue real en el repo de issues (`gh project item-create`
   esta prohibido). Nunca se crean repos.
6. **Lenguaje de negocio** en titulos y cuerpos (skill `redaccion-negocio`). El script avisa si
   detecta jerga tecnica o HUs sin Dado / Cuando / Entonces; el responsable es el PO.
7. **Re-ejecuciones solo llenan vacios**: no pisan el Status que el equipo movio ni los puntos o
   la prioridad que alguien ajusto.
8. **Nada dentro de un repo git**: estado, spec, espejo y config viven en la `.po-team/` canonica
   (resuelta con `hooks/coord_root.py`) o en `~/.po-team/project-state/`.

## De donde salen los datos
`.po-team/config.json` da los valores por defecto: `tracker.github.org`, `repoDefault` (repo de
issues), `repos` (se vinculan), `ciclo.etapas[].estados` + `estadosObservado` + `estadosBloqueado`
(opciones del Status; si aun tienen `{{...}}` se usa el ciclo FaaST por defecto),
`capacidad.duracionSprintDias` (habiles → dias corridos: 10 → 14) y `estimacion.escala`. Lo que
falte se pregunta **una sola vez** al usuario y va al spec.

## El spec
Ejemplo completo en `assets/spec-ejemplo.json`; formato exacto en el docstring del script
(`python3 "$S" --help`). Solo `project` es obligatorio si el config ya tiene org y repo.

| Clave | Que es | Defecto |
|---|---|---|
| `org`, `repo`, `repos` | Owner, repo de issues, repos a vincular | config `tracker.github` |
| `project`, `alias` | Nombre EXACTO del Project y su alias en el config | alias `backlog` si es el primero |
| `project_label` | Etiqueta de los issues que crea el script (sirve para reutilizarlos) | nombre del Project sin acentos |
| `status_opciones` | Lista de nombres o `{nombre,color,descripcion}` | ciclo del config o el FaaST |
| `etapas` | `{clave_etapa: [estados], observado: [...], bloqueado: [...]}` solo si `status_opciones` es propia | — |
| `campos` | Nombres de `puntos`, `sprint`, `prioridad`, `fechaDemo`, `fechaPreprod`, `fechaVB` (`""` desactiva) | Puntos, Sprint, Prioridad, Fecha Demo, Fecha Preprod, Fecha VB cliente |
| `sprint` | `via` (`iteration` / `select` / `milestone`), `inicio` (lunes), `duracion_dias`, `cantidad` | iteration, proximo lunes, 14, 4 |
| `vistas` | Crear Tablero / Sprint actual / Backlog | `true` |
| `agregar_abiertos` | Agregar al Project los issues abiertos de los repos vinculados | `false` |
| `epicas[]` | `nombre`, `descripcion` → issue "Épica: X" con sub-issues | — |
| `items[]` | `titulo`, `body`, `tipo` (Historia/Bug/Tarea), `epica`, `estado`, `prio`, `puntos`, `sprint` (1 o "Sprint 1"), `fechaDemo/fechaPreprod/fechaVB`, `etiquetas` | estado = primero del ciclo |

Guardar el spec fuera de todo repo: `.po-team/project-state/<nombre>.spec.json`. El archivo de
estado (`<nombre>.json`) guarda ademas una copia bajo `spec`, util para `agregar`.

## Flujo: plan → OK → ejecutar
```bash
python3 "$S" crear SPEC --dry-run --offline   # plan sin red (spec recien redactado)
python3 "$S" crear SPEC --dry-run             # plan con lecturas reales de GitHub
python3 "$S" crear SPEC                       # ejecutar, SOLO con el OK del usuario
python3 "$S" crear SPEC --reutilizar          # el Project ya existe y el usuario dijo usarlo
python3 "$S" agregar SPEC [--dry-run]         # completar uno existente (falla si no existe)
python3 "$S" verificar SPEC [--corregir]      # revisar / arreglar (corregir escribe: pedir OK)
python3 "$S" espejo SPEC [--dry-run]          # regenerar .po-team/backlog.md
```
Opciones: `--po-team DIR` (fija la carpeta), `--estado RUTA`, `--sin-espejo` (no toca backlog.md ni
config), `--masivo` (permite agregar mas de 200 issues abiertos, con confirmacion aparte),
`--pausa S`.

Que hace `crear` / `agregar`, en orden (cada paso reutiliza lo existente):
1. Project (lo crea si no existe) y vincula cada repo de `repos`.
2. Status: fusion de opciones del ciclo conservando ids. Prioridad: seleccion Alta/Media/Baja.
3. Puntos (NUMBER), Fecha Demo / Fecha Preprod / Fecha VB cliente (DATE). Si existe un campo
   con ese nombre pero de otro tipo, se avisa y no se toca.
4. Sprint: campo ITERATION con `iterationConfiguration {startDate, duration, iterations[{title,
   startDate, duration}]}` (Sprint 1..N). Si GitHub lo rechaza → seleccion simple Sprint 1..N y
   aviso (`sprintVia: select`). Con `via: milestone` crea milestones "Sprint N" en el repo de issues.
5. Etiquetas (la del backlog y por tipo: `tracker.etiquetas.hu`, `bug`, `tarea`, `epica`),
   epicas, items (issue → sub-issue de su epica → item del Project → valores solo si estan vacios).
6. Issues abiertos de los repos (si `agregar_abiertos`), con Status vacio → primer estado.
7. Vistas: Tablero (BOARD), Sprint actual (TABLE, filtro `sprint:@current`), Backlog (TABLE,
   filtro `no:sprint`). La vista por defecto "View 1" se renombra a Tablero.
8. Verificacion final y conteos por Status / Sprint / Tipo / puntos. Solo completa lo que el plan
   mostro (campos del ciclo, issues del spec, sus valores y sub-issues); lo ajeno al spec
   (borradores, items que no estan en el spec) solo se REPORTA para `verificar` (abajo).
9. Espejo `.po-team/backlog.md` y registro en `.po-team/config.json`.

## Que es idempotente
Re-ejecutar el mismo spec no crea nada nuevo (0 escrituras si todo esta): Project por nombre
exacto, campos por nombre, opciones por nombre (sin acentos ni mayusculas), etiquetas,
milestones, epicas e issues por titulo exacto + etiqueta del backlog, sub-issues ya enlazados,
items ya agregados, valores ya llenos y vistas por nombre. Si se corta (rate limit, red), se
re-ejecuta el mismo comando y continua. Reintentos con espera creciente ante errores transitorios;
la creacion de issues no se reintenta a ciegas (antes busca si se creo).

## Registro en `.po-team/config.json` (escritura atomica, conserva todo lo demas)
- `tracker.provider: "github"`; `tracker.github.org`, `repoDefault` (si tenian `{{...}}`) y
  `repos` (se suman los vinculados).
- `tracker.github.projects[]`: se actualiza la entrada del mismo numero o titulo (o la de
  ejemplo) o se agrega: `{alias, numero, titulo, url, campos{estado, puntos, sprint, prioridad,
  fechaDemo, fechaPreprod, fechaVB}}` con los nombres reales (vacio si el campo no quedo).
- `projectDefault` (si no habia uno valido) y `sprintVia` (`iteration` / `select` / `milestone`).
- `ciclo.etapas[].estados`, `estadosObservado`, `estadosBloqueado` con los nombres REALES de las
  opciones; con el ciclo por defecto tambien `tracker.reglas.estadosSoloQA` = Validado por QA y
  `estadoAlResolver` = Desarrollo terminado, solo si tenian `{{...}}`.

## Espejo local
Seccion en `.po-team/backlog.md` entre `<!-- backlog-github:inicio <etiqueta> -->` y
`<!-- backlog-github:fin <etiqueta> -->`; al regenerar solo se reemplaza esa seccion. Tiene el link
al Project, conteo por estado (items y puntos) y la lista por sprint con estado y puntos.

## Verificacion
`verificar` sin `--corregir` es solo lectura y sirve de plan: se muestra al usuario, y con su OK
se corre `verificar --corregir`. Reporta (y con `--corregir` arregla sin borrar ni pisar): opciones del ciclo o campos faltantes,
borradores (se convierten en issues), issues con la etiqueta del backlog fuera del Project, items
sin Status (del spec o, si estan abiertos, el primer estado), valores vacios que el spec trae,
sub-issues faltantes. Antes de declarar un issue "fuera del Project" lo busca desde el propio
issue: el listado de items del Project se indexa con minutos de retraso y un item recien agregado
puede no aparecer ahi (probado contra GitHub real). Solo informa: items con un Status fuera del ciclo ("sin etapa") y cerrados
sin Status (los define el PO).

## Limites de la API y lo que queda manual
- **Vistas**: la API crea vistas, las renombra, fija layout, campos visibles y filtro, pero **no**
  el agrupamiento ni el orden (`groupBy` / `sortBy` son de solo lectura). Queda a mano: confirmar
  que el Tablero usa Status como columnas, agrupar o sumar puntos por Sprint si se quiere.
- Con Sprint de seleccion no existe `@current`: el filtro de "Sprint actual" se pone a mano.
- Agregar sprints a una iteracion existente: en la interfaz (Settings del campo).
- **Workflows** del Project (p. ej. "item agregado → Status") se configuran en la interfaz.
- Sub-issues: REST `POST repos/{repo}/issues/{epica}/sub_issues` con el **id numerico** del issue;
  un issue tiene una sola epica padre (si ya tiene otra, se avisa y no se mueve).
- "Content already exists" al agregar items a ritmo rapido deja items sin valores: la
  verificacion final los re-llena.

## Entrega al usuario
Enlace al Project, que se creo / reutilizo, `sprintVia`, conteos, avisos del script y lo manual
de la seccion anterior. Siguiente paso sugerido: `/po-team:refinar` para cargar HUs y luego
`/po-team:tablero` (opcion 1 o 2).
