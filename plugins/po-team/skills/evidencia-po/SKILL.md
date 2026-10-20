---
name: evidencia-po
description: Evidencia del equipo del Product Owner (po-team) - como se capturan pantallas con el Playwright MCP (resaltar, verificar, capturar, viewport declarado), el video a tamaño real con capitulos (navegador limpio, size = viewport, traza despues del video, normalizar_video.py → MP4 + portada) para reproducir y revalidar, el par antes/despues, nombres y carpetas por ticket, redaccion de secretos y datos personales en texto e imagenes, y la entrega EMBEBIDA en el ticket por la rama huerfana `evidence` del repo configurado (subida desde un worktree aparte, nunca en ramas de trabajo) con `![](…/raw/evidence/…)` + link blob de respaldo, o attachment + <img> en Azure DevOps. Cargala al validar, al documentar con capturas, al armar manuales o al comentar un ticket con evidencia.
---

# Evidencia del PO (po-team)

Una captura sin contexto no prueba nada. La evidencia del PO es liviana (una captura por criterio
o por paso) pero **concluyente**: dice que mirar, afirma el resultado y se ve dentro del ticket.
Si el plugin dev-team esta instalado, su skill `visual-evidence` aplica como referencia ampliada;
esta skill es autosuficiente (trae su propio `scripts/normalizar_video.py`).

## Captura (Playwright MCP del plugin)
1. Viewport declarado: `browser_resize` 1280x720 (375x812 si el criterio es movil).
2. Llegar al punto como usuario (`browser_navigate`, `browser_click`, `browser_fill_form`…).
3. `browser_highlight` sobre el elemento que prueba el criterio o el paso; `browser_annotate` si
   hace falta una nota.
4. Verificacion explicita (`browser_verify_*`) — es la afirmacion que la captura respalda.
5. `browser_take_screenshot` con nombre descriptivo. `browser_hide_highlight` antes del siguiente.
El MCP escribe en `~/.faast-mcp/po-team/` (staging fuera de repos); al terminar se MUEVE todo a la carpeta del
ticket y se vacia el staging.

## Video a tamaño real (reproducir, revalidar, `--video`)
No es obligatorio en una validacion normal; si se graba, se graba bien. Playwright comparte UNA
captura de pantalla por pagina entre la traza y el video, y la fija quien la enciende primero: la
traza la deja en 800 px. Si hubo una traza antes del video (aunque ya se haya detenido), el video
sale chico en la esquina con el resto gris, y pasarle `size` no lo arregla. Secuencia obligatoria:
1. **Navegador limpio**: si en la sesion ya se uso `browser_start_tracing` o
   `browser_start_video`, `browser_close` y volver a entrar. Ante la duda, cerrar.
2. `browser_resize` al viewport declarado (1280x720; 375x812 movil).
3. `browser_start_video` con `size` **igual al viewport** (`{"width":1280,"height":720}`).
4. `browser_video_show_actions` (los clics y tecleos se ven en el video).
5. Traza solo si se pidio, y **siempre despues** del video (`browser_start_tracing`).
6. Un `browser_video_chapter` por criterio o paso, con nombre de negocio ("Criterio 2 — total con
   IVA"). No cambiar el viewport a mitad de grabacion.
7. Al terminar: `browser_stop_tracing` (si hubo) y `browser_stop_video`.
8. Un video por sesion de navegador; para otro, volver al paso 1.
Verificacion y entrega de cada video, antes de darlo por bueno:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/evidencia-po/scripts/normalizar_video.py" {carpeta}/video.webm
```
`OK` → deja `video.mp4` (se abre en QuickTime, Teams, el navegador y GitHub) y
`video-portada.png`. `REPARADO` (codigo 2) → salio con relleno gris: el `.mp4` lo recorta y
escala, pero la nitidez perdida no vuelve; si el video es la prueba principal de un bug o de un
arreglo, se **regraba** con la secuencia. Requiere `ffmpeg`/`ffprobe` (`/po-team:setup
playwright`); sin ellos se entrega el `.webm` y se avisa. El `.webm` original no se toca. Al
ticket va la **portada embebida con link al `.mp4`**.

## Par antes/despues (revalidar)
Carpeta NUEVA `…-revalidacion/` con numeracion propia (nunca se pisa la original). Mismos pasos,
perfil y datos equivalentes. Para el paso que fallaba: la captura original (obtenido incorrecto) y
la nueva (esperado correcto), ambas resaltadas y con su `browser_verify_*`, lado a lado en el
comentario. La verificacion que antes fallaba y ahora pasa ES la prueba del arreglo.

## Carpetas y nombres
```
.po-team/tickets/{numero}/
├── validacion-{ambiente}-{YYYYMMDD}/   00-plan.md · caN-{resumen}.png · caN-OBSERVADO-*.png · validacion.md
│                                       [video.webm · video.mp4 · video-portada.png]
├── validacion-{ambiente}-{YYYYMMDD}-revalidacion/   misma estructura + antes-despues por criterio
├── reproduccion-{ambiente}-{YYYYMMDD}/ reproduccion.md · NN-{paso}.png · video.* (siempre)
└── capturas/                           capturas para documentos (NN-{resumen}.png)
.po-team/manuales/{flujo}/capturas/     NN-{paso}.png (manualista)
```
Prefijo numerico por orden; un `INDEX.md` corto si la carpeta tiene mas de 3 archivos.
Todo vive en la carpeta canonica `.po-team/` (fuera de los repos; un hook bloquea crearla dentro de uno).

## Redaccion de secretos y datos personales (antes de entregar)
- Nunca en texto: contraseñas, tokens, valores de `accesos.env`, cookies, URLs con credenciales.
  Las cuentas se nombran por variable (`PO_DEMO_EJECUTIVO`), jamas por su valor.
- En imagenes: RUT/NIT/DNI, nombres de personas reales, correos, telefonos, numeros de cuenta.
  Opciones: usar datos de prueba; o antes de capturar, ocultar con `browser_evaluate` aplicando
  un estilo de difuminado al elemento (`filter: blur(6px)`); o recortar. Revisar cada imagen.
- Nombres de clientes (empresas) se permiten si el ticket ya es de ese cliente.

## Entrega embebida en el ticket (regla dura)
**GitHub** — rama huerfana `evidence` (config `evidencia.repo`, `evidencia.rama`,
`evidencia.carpeta`), unica y permanente, nunca se mergea ni se borra, subida desde un worktree
aparte para no tocar ramas de trabajo:
```bash
REPO={evidencia.repo}; DIR=../$(basename $REPO)-evidence
git -C {clon-local-del-repo} worktree add "$DIR" {evidencia.rama} 2>/dev/null || true
# si la rama no existe: crearla huerfana UNA vez
#   git -C {clon} worktree add --detach "$DIR" && cd "$DIR" && git checkout --orphan {rama} \
#     && git rm -rf -q . ; echo "Evidencia — solo esta rama" > README.md && git add . \
#     && git commit -q -m "chore(evidence): rama de evidencia" && git push -u origin {rama}
mkdir -p "$DIR/{evidencia.carpeta}/{numero}-{slug}/{validacion-o-tema}"
cp {carpeta-local}/*.png "$DIR/{evidencia.carpeta}/{numero}-{slug}/{validacion-o-tema}/"
(cd "$DIR" && git add . && git commit -q -m "evidence(po): #{numero} {tema}" && git push -q)
```
Si no hay clon local del repo de evidencia: `gh repo clone {evidencia.repo}` a una carpeta de
trabajo del PO (fuera de cualquier repo de producto) y usarla solo para esto.
En el comentario del issue, cada imagen embebida y su respaldo:
```markdown
![CA1 — listado filtrado por fecha](https://github.com/{org}/{repo}/raw/{rama}/{carpeta}/{numero}-{slug}/{tema}/ca1-listado.png)
[ver archivo](https://github.com/{org}/{repo}/blob/{rama}/{carpeta}/{numero}-{slug}/{tema}/ca1-listado.png)
```
**Azure DevOps** — attachment via `az devops invoke --area wit --resource attachments` y cada
imagen `<img src="{url}">` dentro del HTML del comentario/descripcion, mas relacion AttachedFile.

## Reglas
- Jamas un link suelto como unica evidencia; jamas evidencia en una rama de codigo o de pruebas.
- Siempre ambiente, fecha/hora y perfil junto a la evidencia.
- Repos privados: el link `blob` de respaldo debajo de cada imagen (el embed puede no renderizar
  sin sesion).
- La evidencia no se edita para "que se vea mejor": se recorta o difumina solo para proteger datos.
