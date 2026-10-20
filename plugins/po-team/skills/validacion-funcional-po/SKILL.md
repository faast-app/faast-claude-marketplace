---
name: validacion-funcional-po
description: Metodo de VALIDACION FUNCIONAL RAPIDA del Product Owner (po-team) - recorrer solo los criterios de aceptacion de la HU por el camino normal de uso (10-20 minutos por ticket) en Desa, Demo o Preprod con el Playwright MCP, una captura resaltada por criterio con su verificacion, veredicto VB PO u Observado, regla de la primera falla (se reporta en lenguaje de negocio y no se buscan causas ni se debuggea), modo lote (sprint o lista de tickets en serie con tabla cumple/observado por ticket), reproducir antes de registrar un bug (REPRODUCIDO / NO REPRODUCIDO / BLOQUEADO) y revalidar un arreglo con par antes/despues, la clase del ambiente (pruebas vs productivo), formato del informe y del comentario, y la diferencia explicita con la prueba de QA. Cargala al validar uno o varios tickets como PO.
---

# Validacion funcional rapida del PO (po-team)

Es la mirada del dueño del producto: **¿hace lo que pedimos, por el camino normal, en el ambiente
donde lo va a ver el cliente?** No es una prueba de QA. Se hace rapido, sin datos rebuscados ni
casos borde, y sirve para dar el VB PO antes de mostrar al cliente o para levantar una
observacion temprano.

## QA vs validador-po (no se reemplazan)
| | QA (humana / equipo QA de desarrollo) | validador-po |
|---|---|---|
| Objetivo | Asegurar calidad: que funcione en todos los casos | Confirmar que cumple lo pedido por el camino normal |
| Alcance | Criterios + casos borde + regresion + datos limite + permisos | Solo los criterios de aceptacion de la HU |
| Tiempo | Lo que haga falta | ~10-20 minutos por ticket |
| Evidencia | Traza, video, capturas por paso, consola/red, suite automatizada | Una captura resaltada por criterio con su verificacion |
| Ante una falla | Documenta a fondo, reproduce, clasifica | Reporta a la primera falla en lenguaje de negocio y para ese ticket |
| Veredicto | El del proceso de QA (mueve estados de QA) | **VB PO** u **Observado** (etiqueta + comentario; nunca estados de QA) |
| Ambiente tipico | QA | Desa, Demo, Preprod |

## Antes de empezar (2 minutos)
1. Leer la HU del tracker: criterios de aceptacion numerados. Si no tiene criterios Gherkin
   verificables → no se valida: se devuelve al refinador ("HU sin criterios verificables").
2. Ambiente: el pedido o la etapa del ticket (Demo del pais, Preprod del cliente, Desa). URL y
   clase de `ambientes.*` del config; cuenta por NOMBRE de variable de `.po-team/accesos.env`,
   verificada con `scripts/accesos.py` y escrita como NOMBRE en el login (skill `evidencia-po`).
3. Escribir `00-plan.md`: ticket, ambiente, perfil (variable), criterios a recorrer, fecha/hora.

## Recorrido
- Camino normal de uso, como lo haria el usuario del perfil indicado. Un intento por paso.
- Por cada criterio: llegar al punto → `browser_highlight` sobre lo que prueba el criterio →
  verificacion explicita (`browser_verify_text_visible`, `browser_verify_element_visible`,
  `browser_verify_list_visible` o `browser_verify_value`) → `browser_take_screenshot`
  `caN-{resumen}.png`. Viewport 1280x720 declarado.
- Si la verificacion no pasa, o no se puede llegar al punto (login falla, ambiente caido, menu no
  aparece, dato inexistente): **primera falla → se detiene ese ticket**. Captura
  `caN-OBSERVADO-{resumen}.png`, se anota que se esperaba y que se vio, y se termina.
- **Prohibido**: buscar la causa, leer codigo, revisar consola o red para explicar, consultar la
  base, reintentar con otro dato o camino, tocar configuracion. Si algo tienta a explicar, se omite.
- Video: no es obligatorio en una validacion normal (es rapida); se graba con `--video` y SIEMPRE
  en reproducir y revalidar (skill `evidencia-po`, "Video a tamaño real"). Traza solo si se pide.
- **Clase del ambiente**: en `pruebas` las acciones de negocio de prueba son normales; en
  `productivo` se para antes de cada accion que registra algo y se pide autorizacion para esa
  accion (sin ella: "No evaluado — requiere autorizacion en productivo"); sin clase, se pregunta.

## Veredicto
- **VB PO**: todos los criterios verificados con su captura.
- **Observado**: al menos un criterio no se cumple o no se pudo verificar. Se indica cual,
  que se esperaba, que se vio, y si fue bloqueo de ambiente/acceso (en ese caso: "Observado —
  bloqueado por ambiente", para no culpar a la funcionalidad).

## Informe por ticket (`.po-team/tickets/{numero}/validacion-{ambiente}-{fecha}/validacion.md`)
```markdown
# Validacion PO — #{numero} {titulo}
**Veredicto:** ✅ VB PO | ⚠️ Observado | ⛔ Observado — bloqueado por ambiente
**Ambiente:** {nombre} · **Fecha/hora:** {ts} · **Perfil:** {rol} · **Duracion:** {min} min

| Criterio | Resultado | Captura |
|---|---|---|
| 1. Dado… cuando… entonces… | Cumple | ca1-listado-filtrado.png |
| 2. … | Observado: el total no incluye el IVA | ca2-OBSERVADO-total.png |
| 3. … | No evaluado (se detuvo en el criterio 2) | — |

**Observacion (lenguaje de negocio):** {que ve el usuario, que esperaba}
**Siguiente paso sugerido:** comentar en el ticket y devolver a desarrollo | dar VB PO y avisar al cliente
```
Nota final fija: "Validacion funcional rapida del PO; no reemplaza la validacion de QA."

## Reproducir y revalidar
| | Reproducir | Revalidar |
|---|---|---|
| Para que | Confirmar un reporte ANTES de registrar el bug | Confirmar el arreglo de un bug u observado |
| Recorrido | Los pasos del reporte, como usuario, + una segunda corrida limpia | El MISMO recorrido original, mismos pasos y perfil |
| Carpeta | `reproduccion-{ambiente}-{fecha}/` | `validacion-{ambiente}-{fecha}-revalidacion/` (nueva, numeracion propia) |
| Evidencia | Video desde el inicio + captura resaltada en el punto del problema | Video + par antes/despues por criterio |
| Veredicto | REPRODUCIDO consistente / intermitente (n de m) · NO REPRODUCIDO · BLOQUEADO | Corregido · Corregido con observaciones · Sigue fallando |
| Siguiente | REPRODUCIDO → el refinador registra el bug | El refinador comenta en el MISMO issue y se pregunta si cerrar |
`reproduccion.md`: reporte original (citado), ambiente/fecha/perfil/version, tabla paso · accion ·
esperado · visto · captura, veredicto y la nota "reproduccion funcional; no es diagnostico". Un
NO REPRODUCIDO muestra lo que SI se vio; nunca se fuerza el fallo con otros datos.

## Modo lote
Entrada: `--lote sprint {N}` (todos los tickets del sprint en la etapa validable) o una lista de
numeros. Se recorren **en serie** (un solo navegador), cada uno con su carpeta e informe. Un
ticket observado no detiene el lote: se pasa al siguiente. Al final, `lote-{fecha}.md`:
```markdown
# Validacion PO en lote — {sprint o lista} — {ambiente} — {fecha}
| Ticket | Titulo | Puntos | Veredicto | Criterios | Evidencia |
|---|---|---|---|---|---|
| #123 | Filtrar operaciones por fecha | 3 | ✅ VB PO | 3/3 | tickets/123/validacion-…/ |
| #130 | Total con IVA en el resumen | 5 | ⚠️ Observado | 1/3 | tickets/130/validacion-…/ |
**Resumen:** {n} VB PO ({puntos}) · {n} observados ({puntos}) · {n} bloqueados
```
Ademas deja `lote-{fecha}.json` (`[{numero, veredicto, criteriosOk, criteriosTotal, ambiente,
fecha, carpeta}]`) que el seguimiento usa como insumo del dashboard (`veredictoPO` por ticket).

## Informe como artifact (`/po-team:validar --artifact`)
Plantilla `templates/validacion/validacion.html`: el informe de validaciones de un sprint en un
ambiente. Muestra un resumen por estado, los bloqueos del ambiente, las decisiones del PO, una fila
por ticket (descripcion de negocio, criterios, casos de prueba, evidencia y siguiente paso) y al
final los bugs, separados entre los del alcance y los de fuera. Datos en
`.po-team/validaciones/{sprint}-{ambiente}/validacion-datos.json`; `templates/validacion/datos-ejemplo.json`
es un ejemplo completo.
```json
{ "titulo": "Validaciones Sprint 12", "producto": "…", "sprint": "Sprint 12", "ambiente": "Demo CO",
  "fecha": "2026-10-16", "repoUrl": "https://github.com/{org}/{repo}/issues/",
  "tituloDecisiones": "Decisiones del PO", "columnaTicket": "Ticket", "notaBugs": "(opcional)",
  "grupos": [ { "id": "val", "nombre": "A validar en Demo CO", "descripcion": "…",
    "items": [ { "numero": 123, "titulo": "…", "url": "(opcional; si falta, repoUrl + numero)",
      "estado": "ok|warn|alert|block|pend|na|pr|wait", "etiqueta": "Cumple", "nota": "…", "siguiente": "…",
      "descripcion": { "trata": "…", "validar": "…", "criterios": ["…"], "duda": "(opcional)" },
      "casos": [ { "caso": "C1", "que": "…", "estado": "ok", "resultado": "…", "falta": "—",
                   "fuente": { "tipo": "observado|inferido", "fuente": "…", "pasos": ["…"] } } ],
      "evidencia": [ { "archivo": "img/123-c1.jpg", "original": "(opcional, version grande)", "leyenda": "C1 · …" } ],
      "links": [ { "texto": "…", "url": "…" } ] } ] } ],
  "bloqueos": [ { "titulo": "…", "detalle": "…" } ], "decisiones": ["…"],
  "bugs": [ { "titulo": "…", "ticket": "#123 C2", "alcance": "en|fuera", "detalle": "…", "url": "(opcional)" } ] }
```
Estados: `ok` Cumple (= VB PO) · `alert` No cumple (= Observado) · `warn` A revisar · `block`
Bloqueado · `pend` En validacion · `wait` Espera confirmacion · `pr` En PR · `na` No aplica.
Reglas: lenguaje de negocio; un caso por criterio; los videos (`.webm`/`.mp4`) salen con
reproductor; en `archivo` va la captura liviana (JPG de ~1400 px) y en `original` la PNG; sin datos
personales ni secretos. Al publicar, cada archivo de `evidencia` va en `files` del Artifact con su
misma ruta relativa.

## Publicar el resultado (solo con el plan aprobado)
Con el OK del usuario: subir las capturas a la rama `evidence` (skill `evidencia-po`), comentar en
el ticket con la tabla y las capturas embebidas, y poner la etiqueta `tracker.etiquetas.vbPO` u
`observadoPO`. Nunca mover a estados de QA; nunca cerrar.
