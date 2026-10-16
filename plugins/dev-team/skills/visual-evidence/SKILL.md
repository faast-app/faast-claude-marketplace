---
name: visual-evidence
description: Captura, ANALISIS y ENTREGA de evidencia visual de alta fidelidad para dev-team (QA, bugs, flujos, pentest) con las mejores herramientas del Playwright MCP - la traza navegable de Playwright como herramienta de analisis (snapshots de DOM por accion, red, consola, timeline), el video con acciones superpuestas y capitulos por paso grabado a TAMAÑO REAL (navegador limpio, video con size igual al viewport y traza despues del video; verificacion con normalizar_video.py que detecta el relleno gris, repara y entrega MP4 + portada), capturas resaltadas y anotadas, snapshot de accesibilidad como evidencia inspeccionable, sidecars de consola y red, verificacion explicita como ancla, evidencia de correccion con par antes/despues al revalidar un fix, entrega concluyente (INDEX de analisis, embebido en el tracker, fotogramas clave, version citada, secretos redactados), y como analizar el material cruzando video + traza + red + consola. Cargala al reproducir un bug, validar una HU, verificar que algo se corrigio, ejecutar un flujo, documentar una prueba de seguridad o entregar evidencia.
---

# Evidencia visual: captura y analisis de alta fidelidad (dev-team)

El objetivo no es "grabar mas", es que la evidencia PRUEBE algo y sea ANALIZABLE. Una foto sin
contexto o un video que hay que mirar entero adivinando no sirven. Estas son las mejores
herramientas del Playwright MCP del plugin y como usarlas para que cada pieza de evidencia diga
exactamente que paso, donde y por que. Aplica a QA (validar HUs, reproducir bugs), a los flujos
y al pentest. NO reemplaza el video ni las capturas: los hace de mayor calidad y mas faciles de
analizar.

## Las tres capas de evidencia (siempre las tres en un flujo relevante)
1. **Traza navegable** (`browser_start_tracing` → `browser_stop_tracing` → `.zip`): la
   herramienta de ANALISIS por excelencia. Guarda, por cada accion, el snapshot del DOM
   (antes/despues), la red, la consola, el codigo y una linea de tiempo. Se abre con
   `npx playwright show-trace archivo.zip` y permite inspeccionar el estado exacto en el que algo
   fallo — mucho mas que mirar pixeles. Se enciende al inicio, **inmediatamente DESPUES del video**
   (ver "Video a tamaño real").
2. **Video con acciones y capitulos** (`browser_start_video`, `browser_video_show_actions`,
   `browser_video_chapter`, `browser_stop_video`): el video se mira completo (asi se entiende el
   flujo), pero se hace analizable — las acciones (clic, tipeo) se SUPERPONEN en la imagen y cada
   paso queda marcado como capitulo. Analizas viendo QUE hizo el usuario en cada momento, no
   adivinando. `browser_video_hide_actions` si se necesita una toma limpia para el usuario final.
   Se graba SIEMPRE a tamaño real con la secuencia de la seccion siguiente.
3. **Capturas ancladas a una afirmacion**: cada captura clave se toma DESPUES de resaltar el
   elemento bajo prueba (`browser_highlight`) y, si hace falta explicar, anotarlo
   (`browser_annotate`), y va acompañada de la verificacion explicita que cierra el criterio
   (`browser_verify_*`). Una captura prueba algo solo si señala QUE mirar y afirma el resultado.

## Video a tamaño real (regla dura, verificada)
**El problema.** Playwright usa UNA sola captura de pantalla por pagina, compartida por la traza y
el video, y el tamaño lo fija quien la enciende primero. La traza la enciende sin tamaño, asi que
queda reducida a 800 px (800x500 para un viewport de 1440x900). Si la traza arranco antes que el
video, o si hubo cualquier traza antes en la misma sesion del navegador (aunque ya se haya
detenido), el video sale con la pantalla chica en la esquina superior izquierda y el resto gris:
el archivo "mide" 1440x900 pero no se lee. Pasarle `size` al video NO lo arregla en ese caso.

**La secuencia obligatoria** (probada: con ella el video ocupa el cuadro completo):
1. **Navegador limpio.** Si en esta sesion ya se uso `browser_start_tracing` o `browser_start_video`,
   `browser_close` antes de empezar (y volver a entrar al ambiente). Ante la duda, cerrar.
2. `browser_resize` al viewport declarado (1280x720 escritorio; 375x812 movil).
3. `browser_start_video` con `size` **igual al viewport exacto** (`{"width":1280,"height":720}`).
   Nunca sin `size` (saldria a 800 px) ni con un tamaño distinto.
4. `browser_video_show_actions`.
5. `browser_start_tracing` — **siempre despues del video**, nunca antes.
6. Los pasos, con `browser_video_chapter` por paso. No cambiar el viewport a mitad de grabacion:
   la toma movil es otro video, en otro navegador limpio.
7. Al terminar: `browser_stop_tracing` y luego `browser_stop_video`.
8. **Un video por sesion de navegador.** Para otra toma, preferir capitulos dentro del mismo video;
   si hace falta un segundo archivo, volver al paso 1.

**Verificacion y entrega (cada video, antes de darlo por bueno):**
```bash
python3 <carpeta-de-esta-skill>/scripts/normalizar_video.py .coordination/evidence/{ID}/video.webm
```
- `OK` → deja junto al original `video.mp4` (H.264: se abre en QuickTime, Teams, el navegador y
  GitHub; el `.webm` no se abre en QuickTime) y `video-portada.png` (cuadro central).
- `REPARADO` → la grabacion salio con relleno gris. El `.mp4` recorta la pantalla real y la escala
  al cuadro completo, pero la nitidez perdida NO se recupera: la captura tuvo un tercio de los
  pixeles y el texto chico se ve borroso. Se anota en `INDEX.md` ("video reparado, escalado desde
  800x500") y, si el video es la prueba principal de un bug o de un fix, se **regraba** con la
  secuencia correcta. Codigo de salida 2 = hubo relleno.
- **Calidad esperada** (medida): grabado con la secuencia correcta, cada cuadro quieto es
  practicamente identico a una captura de pantalla (texto de 13 px legible, tambien al desplazar).
  Subir la densidad de pixeles (`deviceScaleFactor` 2) NO mejora el video: Playwright lo entrega
  siempre en pixeles CSS del viewport. Para un detalle mas fino se usa una captura
  (`browser_take_screenshot`) del momento, no un video mas grande.
- `--verificar` solo revisa, sin escribir archivos. Acepta una carpeta para revisar todos los `.webm`.
- El `.webm` original no se toca (evidencia cruda inmutable). Al tracker va la **portada embebida
  con link al `.mp4`**; en documentos, la portada o los fotogramas clave con el link al video.

## Captura de pantalla de alta fidelidad (al reproducir, probar o dar evidencia)
- **Resaltar antes de capturar**: `browser_highlight` sobre el elemento del criterio (el registro,
  el mensaje, el boton) y `browser_annotate` para una flecha/nota si el punto no es obvio. La foto
  debe dirigir la mirada, no dejarla al azar.
- **Par contexto + detalle**: una captura de pagina completa (contexto) y una del elemento
  (detalle) cuando el criterio esta en un componente pequeño.
- **Viewport y escala declarados**: 1280x720 escritorio; 375x812 movil (`browser_resize`) cuando el
  criterio es responsive. Anota el viewport en el nombre/informe. Escala de pixel consistente para
  que la comparacion visual sea valida.
- **Triple por criterio**: inicial (estado previo) / accion / resultado — numeradas `NN-`. El
  resultado se captura EN EL MOMENTO del `browser_verify_*`, no despues.
- **Estados de UI**: capturar los 4 (loading, error, empty, success) cuando aplican; no solo el feliz.

## Snapshot de accesibilidad = evidencia inspeccionable
`browser_snapshot` captura el arbol de accesibilidad (roles, labels, valores, estado) en texto:
es evidencia que se puede LEER y comparar, no solo mirar. Guardala junto a la captura del criterio
— prueba, por ejemplo, que el mensaje de error existe como texto real (no una imagen), que el
boton tiene nombre accesible, o que el valor de un campo es el esperado. Complementa el pixel con
un estado inspeccionable.

## Sidecars: consola y red (analisis de lo que no se ve)
- `browser_console_messages` → `NN-consola.txt`: 0 errores JS es parte del criterio; un error que
  aparece en el momento de la falla es la pista.
- `browser_network_requests` → `NN-red.txt` (y `browser_network_request` para el detalle de una
  llamada): el codigo de estado y el payload de la request del paso. Correlaciona la accion del
  video con la llamada que la respalda (o que fallo). Redacta secretos/tokens.
- El analisis fuerte sale de CRUZAR las tres capas: el video muestra la accion, la traza muestra el
  DOM y la red en ese instante, y los sidecars confirman el error exacto. "Esperado != obtenido" se
  localiza en la accion precisa, con su request y su estado de DOM.

## Verificacion explicita como ancla del analisis
Ninguna captura "prueba" sola: se cierra con `browser_verify_element_visible` /
`browser_verify_text_visible` / `browser_verify_list_visible` / `browser_verify_value` (o
`expect()` en la suite). La verificacion es la afirmacion que la evidencia respalda. Sin ella, la
evidencia es decorativa. `browser_generate_locator` da el localizador estable para el test.

## Evidencia de correccion (revalidacion / retest) — antes vs. despues
Cuando se verifica que un bug se corrigio (o que un hallazgo de seguridad se cerro), la evidencia
tiene que DEMOSTRAR el cambio, no solo decir "ya funciona":
- **Tanda NUEVA, nunca mezclada**: la revalidacion va en una subcarpeta con sufijo `-revalidacion`
  (o `-retest`), con su propia numeracion `00-`, `01-`... Jamas se reusa ni se pisa la numeracion
  del intento fallido original — ambos quedan trazables.
- **Mismos pasos exactos** que la reproduccion original (mismo recorrido, mismo dato, mismo
  usuario/rol, mismo ambiente/version — anotar la version NUEVA desplegada del informe de
  conformidad): asi la comparacion es valida.
- **Par antes/despues explicito**: para el paso donde antes fallaba, poner lado a lado la captura
  del bug original (`obtenido` incorrecto) y la de ahora (`esperado` correcto), ambas resaltadas y
  con su `browser_verify_*`. El video/traza de la revalidacion muestra el recorrido ya sano.
- **Ancla la afirmacion del arreglo**: la verificacion que antes fallaba ahora pasa
  (`browser_verify_text_visible`, `browser_verify_value`, etc.) — esa es la prueba del fix. Consola
  y red limpias en el mismo flujo (0 errores, 0 4xx/5xx inesperados) forman parte de la prueba.
- **Veredicto de revalidacion**: APTO / APTO CON OBSERVACIONES / SIGUE FALLANDO, con el par
  antes/despues y la version que lo corrige. Un "sigue fallando" reabre; QA no cierra por su cuenta.

## Entrega de evidencia (que reciba el que la lee sea concluyente)
La evidencia no esta "entregada" hasta que quien la recibe (PO, Lead, cliente, auditor) la puede
leer y concluir sin reconstruir nada:
- **Nota de analisis (`INDEX.md`)** encabezando la carpeta: 2-4 lineas por archivo que DICEN que
  muestra y donde esta el punto clave, y el veredicto. Es lo que convierte un monton de archivos en
  una historia legible.
- **Embebida en el item del tracker** (nunca link suelto): GitHub → rama `evidence` +
  `![](.../raw/...)` + link `blob` de respaldo; Azure → attachment + `<img>` en el HTML del WI. Los
  fotogramas clave y el par antes/despues van EMBEBIDOS en el issue/comentario, en orden.
- **En documentos** (informe de bug, acta de aceptacion, informe de pentest/flujo): los fotogramas
  clave con pie de foto, y el enlace a la traza/video completos para quien quiera profundizar.
- **Secretos y PII redactados** en el texto y en las imagenes antes de entregar. Verificar que cada
  imagen se ve (repos privados a veces no renderizan el embed sin sesion → el link `blob` de respaldo).
- **Integridad**: la evidencia entregada cita ambiente y version; una entrega sin la version que la
  produjo no es concluyente (no se sabe que se probo).

## Fotogramas clave para el informe (resumir sin perder el video)
Para el informe (bug, HU, pentest, flujo) se extraen 3-6 FOTOGRAMAS representativos del video/traza
y se embeben con pie de foto. No es para saltarse el video: es para que quien lee el informe
entienda el hallazgo de un vistazo y pueda ir al video/traza completos si quiere. Los fotogramas
salen de las capturas numeradas ya tomadas o de cuadros de la grabacion.

## Organizacion y nota de analisis
- Nombres con prefijo numerico por orden y agrupados por criterio/paso (`ca2-01-inicial.png`,
  `ca2-02-accion.png`, `ca2-03-resultado.png`, `ca2.trace.zip`, `ca2.webm`, `ca2-red.txt`,
  `ca2-consola.txt`, `ca2-a11y.txt`).
- Si una carpeta tiene mas de un archivo, un `INDEX.md` corto (2-4 lineas por archivo) que DESCRIBE
  y ANALIZA que muestra cada uno y donde esta el punto clave — es el "analisis" escrito que
  acompaña al material, para que no haya que reconstruirlo mirando todo.
- La evidencia vive en `.coordination/evidence/{ID}/` (gitignored); el MCP escribe en `~/.faast-mcp/dev-team/`
  (staging fuera de los repos) y se mueve a la carpeta del criterio al cerrarlo. Al tracker sube EMBEBIDA. Secretos y
  PII siempre redactados, tambien en las imagenes.

## Checklist de una pieza de evidencia bien hecha
- [ ] Navegador limpio, `browser_resize` al viewport, video con `size` = viewport, traza DESPUES del video
- [ ] Video con acciones superpuestas y un capitulo por paso
- [ ] `normalizar_video.py` en OK (o REPARADO anotado / regrabado) → `.mp4` + portada para entregar
- [ ] Cada criterio: triple de capturas resaltadas + `browser_verify_*` que lo afirma
- [ ] Snapshot de accesibilidad del estado clave (texto inspeccionable)
- [ ] Consola y red guardadas y correlacionadas con la accion
- [ ] Nombres numerados + `INDEX.md` con el analisis escrito
- [ ] Si es revalidacion de un fix: tanda `-revalidacion` nueva, mismos pasos, par antes/despues + verify que ahora pasa, version nueva anotada
- [ ] Entrega: embebida en el item (no link suelto), fotogramas y antes/despues visibles, version/ambiente citados, secretos/PII redactados
