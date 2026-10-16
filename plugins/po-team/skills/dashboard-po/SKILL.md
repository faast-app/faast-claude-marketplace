---
name: dashboard-po
description: Tablero (dashboard) del Product Owner en po-team - como se leen los estados del GitHub Project (gh project item-list y gh api graphql sobre ProjectV2 con Status, puntos, sprint/iteracion y fechas), como se ubica cada ticket en una etapa del ciclo de pase, la estructura de datos tablero-datos.json, colores por etapa y estado, calculo de avance por puntos por sprint (VB cliente y avance ponderado), deteccion de fechas vencidas y tickets sin movimiento, snapshots para listar cambios de estado desde la revision anterior, el informe diario/semanal en lenguaje de negocio, y como generar el HTML desde la plantilla y publicarlo como artifact si la sesion tiene esa herramienta. Cargala al actualizar el tablero o redactar el informe.
---

# Dashboard del PO (po-team)

El tablero responde en 20 segundos: **¿como va cada sprint, que esta en que etapa, que se atraso
y que cambio desde la ultima vez?** Se genera desde los datos reales del Project, nunca a mano.

## 1. Leer el Project (solo lectura)
Config: `tracker.github.org`, `projects[]` (numero y nombres de campos), `ciclo.etapas`.
Rapido (campos por nombre en minusculas):
```bash
gh project item-list {numero} --owner {org} --format json --limit 1000 > .po-team/tablero/raw-{numero}.json
```
Completo y exacto (paginar con `endCursor` mientras `hasNextPage`):
```bash
gh api graphql -F org="{org}" -F num={numero} -f query='
query($org:String!,$num:Int!,$cursor:String){
  organization(login:$org){ projectV2(number:$num){ title
    items(first:100, after:$cursor){ pageInfo{ hasNextPage endCursor }
      nodes{ id updatedAt
        content{ __typename
          ... on Issue { number title url state createdAt repository{ nameWithOwner }
                         labels(first:30){ nodes{ name } } assignees(first:5){ nodes{ login } } }
          ... on PullRequest { number title url }
          ... on DraftIssue { title } }
        fieldValues(first:40){ nodes{ __typename
          ... on ProjectV2ItemFieldSingleSelectValue { name  field{ ... on ProjectV2FieldCommon { name } } }
          ... on ProjectV2ItemFieldNumberValue       { number field{ ... on ProjectV2FieldCommon { name } } }
          ... on ProjectV2ItemFieldIterationValue    { title startDate duration field{ ... on ProjectV2FieldCommon { name } } }
          ... on ProjectV2ItemFieldDateValue         { date  field{ ... on ProjectV2FieldCommon { name } } }
          ... on ProjectV2ItemFieldTextValue         { text  field{ ... on ProjectV2FieldCommon { name } } } } } } } } } }'
```
Si la org es de usuario, `user(login:)` en vez de `organization(login:)`. Requiere el scope
`read:project` (`gh auth refresh -s read:project`). Azure DevOps: `az boards query --wiql` con
`System.State`, `System.IterationPath`, el campo de puntos y `System.ChangedDate`.

## 2. Ubicar cada ticket
- **Sprint**: valor del campo `campos.sprint` (iteracion: titulo + inicio + duracion) o milestone
  si `sprintVia` = `milestone`. Sin sprint → grupo "Backlog" (se muestra aparte, plegado).
- **Etapa**: regla de la skill `ciclo-pase-faast` (etiquetas > Status; observado; bloqueado;
  "Sin etapa" si no calza — se reporta, no se adivina).
- **Puntos**: campo `campos.puntos`; vacio → 0 y se lista en "sin estimar".
- **veredictoPO**: del ultimo `lote-*.json` o `validacion.md` del ticket (`vb` | `observado` | null).
- **Fechas del sprint**: `.po-team/sprints/{sprint}.json` → `fechas` (y campos de fecha del Project
  si existen).

## 3. Estructura `tablero-datos.json`
```json
{
  "generado": "2026-10-16T12:00:00Z",
  "equipo": "{config.equipo}",
  "fuente": { "org": "{org}", "projects": [{ "numero": 0, "titulo": "" }] },
  "etapas": [ { "clave": "desarrollo", "nombre": "Desarrollo" }, { "clave": "qa", "nombre": "Validacion QA" },
              { "clave": "demo", "nombre": "Pase a Demo" }, { "clave": "validacion", "nombre": "Validacion Demo / Preprod" },
              { "clave": "vb", "nombre": "VB cliente" } ],
  "sprints": [ {
    "nombre": "Sprint 12", "inicio": "2026-10-06", "fin": "2026-10-17",
    "objetivo": "Que el ejecutivo pueda …",
    "fechas": { "demo": "2026-10-20", "preprod": "2026-10-23", "vb": "2026-10-28" },
    "tickets": [ { "numero": 123, "repo": "org/repo", "titulo": "Filtrar operaciones por fecha",
                   "tipo": "hu", "estado": "Validado por QA", "etapa": "qa", "observado": false,
                   "bloqueado": false, "puntos": 3, "veredictoPO": null, "url": "https://…",
                   "cliente": "", "diasEnEstado": 2 } ]
  } ],
  "backlog": [ ],
  "cambios": [ { "numero": 123, "titulo": "…", "de": "Desarrollo Completado", "a": "Validado por QA" } ],
  "riesgos": [ { "nivel": "alto", "texto": "Fecha de pase a Demo vencida (20/10) con 2 tickets aun en QA" } ],
  "sinEtapa": [ ], "sinEstimar": [ ]
}
```
Etiquetas visibles y textos en lenguaje de negocio. Sin datos personales; responsables solo si el
config lo permite (por defecto no se muestran personas).

## 4. Calculos
- **Puntos del sprint** = Σ puntos de sus tickets.
- **Avance por etapa** (stepper): para cada etapa e, puntos de tickets cuya etapa ≥ e (los
  observados cuentan en la etapa donde estan, no mas alla).
- **% VB cliente** = puntos en etapa `vb` / puntos del sprint.
- **Avance ponderado** = Σ (puntos × (indice etapa + 1) / n etapas) / puntos del sprint (con las
  5 etapas: Desarrollo vale 20%, QA 40%, Demo 60%, Validacion 80%, VB 100%) — una sola cifra
  que sube a medida que los tickets avanzan; se explica asi en el informe.
- **Fecha vencida**: hoy > fecha de una etapa y hay tickets del sprint antes de esa etapa.
- **Sin movimiento**: `diasEnEstado` ≥ `ciclo.diasAlertaSinMovimiento` (con snapshots: dias desde
  que cambio de estado; sin historial: `updatedAt` del item como aproximacion, indicandolo).
- **Velocidad** (para el planificador): puntos que llegaron a la etapa `qa` o mas por sprint
  cerrado, promedio de los ultimos `capacidad.sprintsVelocidad`.

## 5. Colores por etapa y estado
| Estado | Token | Uso |
|---|---|---|
| Desarrollo | `--c-desarrollo` (azul) | chip y paso del stepper |
| Validacion QA | `--c-qa` (violeta) | |
| Pase a Demo | `--c-demo` (ambar) | |
| Validacion Demo/Preprod | `--c-validacion` (turquesa) | |
| VB cliente | `--c-vb` (verde) | |
| Observado | `--c-observado` (rojo) | chip con borde y icono ⚠ |
| Bloqueado | `--c-bloqueado` (gris oscuro) | chip con icono ⛔ |
El color nunca es la unica señal: cada chip lleva el nombre de la etapa en su `title` y los
observados/bloqueados un icono. Modo claro y oscuro definidos en la plantilla.

## 6. Snapshots y cambios desde la revision anterior
Cada actualizacion guarda `.po-team/tablero/snapshots/{YYYYMMDD-HHmm}.json` con
`{numero: {estado, etapa, puntos, sprint}}`. "Cambios" = diferencia con el snapshot anterior
(cambio de estado, de etapa, de puntos, de sprint, tickets nuevos o que salieron). Se conservan
los ultimos 60 snapshots.

## 7. Generar el HTML
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/templates/tablero/generar_tablero.py" \
  "{tablero.outputDir}/tablero-datos.json" "{tablero.outputDir}/tablero.html"
```
El script valida el JSON, quita la marca de ejemplo, escapa `</` y reemplaza el bloque de datos
(script con `id="datos"`) de la plantilla `templates/tablero/tablero.html`. La plantilla renderiza
todo sola, sin librerias externas, en modo claro y oscuro y en pantallas de telefono.
`templates/tablero/datos-ejemplo.json` muestra un tablero completo de referencia.

## 8. Publicar como artifact (si la sesion tiene el tool `Artifact`)
- Primera vez: publicar `{tablero.outputDir}/tablero.html` con `icon: "chart"` y descripcion de
  una frase; guardar la URL devuelta en `tablero.artifactUrl` del config.
- Siguientes veces en la misma sesion: publicar el MISMO archivo (misma ruta) para actualizar la
  misma URL. En una sesion nueva: `action: "read"` sobre `tablero.artifactUrl` y luego publicar
  con `url` = esa URL.
- Sin el tool: entregar la ruta local del HTML (se abre en el navegador).
- El tablero es privado por defecto; compartirlo es decision del PO.

## 9. Informe diario / semanal (texto, lenguaje de negocio)
```
Tablero {equipo} — {fecha} ({diario|semanal})
Sprint 12 (06/10–17/10): 34 pts · VB cliente 9 pts (26%) · avance ponderado 58%
  Desarrollo 8 · QA 11 · Demo 6 · Validacion 0 · VB 9   | observados 1 · bloqueados 0
Cambios desde {revision anterior}:
  - #123 Filtrar operaciones por fecha: Desarrollo Completado → Validado por QA
  - #130 Total con IVA: observado por el PO en Demo CO (el total no suma el IVA)
Atencion:
  - ALTO: pase a Demo comprometido para el 20/10 y 2 tickets (8 pts) siguen en QA
  - #118 lleva 7 dias sin moverse en Desarrollo
Proximos hitos: Demo 20/10 · Preprod {cliente} 23/10 · VB cliente 28/10
```
El semanal agrega: puntos que avanzaron en la semana por etapa, VB obtenidos y riesgos nuevos.
