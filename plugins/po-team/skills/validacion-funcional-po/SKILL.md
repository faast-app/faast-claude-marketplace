---
name: validacion-funcional-po
description: Metodo de VALIDACION FUNCIONAL RAPIDA del Product Owner (po-team) - recorrer solo los criterios de aceptacion de la HU por el camino normal de uso (10-20 minutos por ticket) en Desa, Demo o Preprod con el Playwright MCP, una captura resaltada por criterio con su verificacion, veredicto VB PO u Observado, regla de la primera falla (se reporta en lenguaje de negocio y no se buscan causas ni se debuggea), modo lote (sprint o lista de tickets en serie con tabla cumple/observado por ticket), formato del informe y del comentario, y la diferencia explicita con la prueba de QA. Cargala al validar uno o varios tickets como PO.
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
2. Ambiente: el pedido o la etapa del ticket (Demo del pais, Preprod del cliente, Desa). URL de
   `ambientes.*` del config; cuenta por NOMBRE de variable de `.po-team/accesos.env`.
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
- Trazas y video NO son obligatorios (es rapido); se activan solo si el pedido lo indica.

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

## Publicar el resultado (solo con el plan aprobado)
Con el OK del usuario: subir las capturas a la rama `evidence` (skill `evidencia-po`), comentar en
el ticket con la tabla y las capturas embebidas, y poner la etiqueta `tracker.etiquetas.vbPO` u
`observadoPO`. Nunca mover a estados de QA; nunca cerrar.
