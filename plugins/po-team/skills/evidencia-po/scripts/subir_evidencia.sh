#!/bin/bash
# po-team — sube evidencia a la rama huerfana de evidencia del repo configurado, SIN tocar ramas
# de trabajo. Usa un worktree hermano del clon ({clon}-evidence) con RUTAS ABSOLUTAS y verifica la
# rama antes de commitear: si el worktree no esta en la rama de evidencia, aborta sin escribir.
#
# Uso:
#   subir_evidencia.sh --clon /ruta/abs/al/clon --rama evidence \
#       --destino "evidence/po/130-total-iva/validacion-demo-co-20261016" \
#       --origen /ruta/abs/.po-team/tickets/130/validacion-demo-co-20261016 \
#       --mensaje "evidence(po): #130 validacion Demo CO"
# Copia del origen solo imagenes, video y .md (png jpg jpeg webp gif mp4 webm md). Imprime al final
# las bases RAW= y BLOB= para armar los enlaces del comentario. Codigos: 0 ok, 1 error de uso o
# verificacion, 2 git fallo (nada a medias queda commiteado en otra rama).
set -u
CLON=""; RAMA="evidence"; DESTINO=""; ORIGEN=""; MENSAJE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --clon) CLON="$2"; shift 2;; --rama) RAMA="$2"; shift 2;;
    --destino) DESTINO="$2"; shift 2;; --origen) ORIGEN="$2"; shift 2;;
    --mensaje) MENSAJE="$2"; shift 2;;
    *) echo "argumento desconocido: $1" >&2; exit 1;;
  esac
done
err() { echo "ERROR: $*" >&2; exit "${2:-1}"; }
[ -n "$CLON" ] && [ -n "$DESTINO" ] && [ -n "$ORIGEN" ] && [ -n "$MENSAJE" ] || err "faltan argumentos (--clon --destino --origen --mensaje)"
case "$DESTINO" in /*|*..*) err "--destino debe ser relativo dentro de la rama y sin '..'";; esac
CLON="$(cd "$CLON" 2>/dev/null && pwd)" || err "no existe el clon"
ORIGEN="$(cd "$ORIGEN" 2>/dev/null && pwd)" || err "no existe el origen"
git -C "$CLON" rev-parse --git-dir >/dev/null 2>&1 || err "$CLON no es un repo git"
DIR="$(dirname "$CLON")/$(basename "$CLON")-evidence"

if [ ! -d "$DIR" ]; then
  git -C "$CLON" fetch -q origin "$RAMA" 2>/dev/null
  if git -C "$CLON" rev-parse -q --verify "refs/remotes/origin/$RAMA" >/dev/null; then
    git -C "$CLON" worktree add -q -B "$RAMA" "$DIR" "origin/$RAMA" || err "no se pudo crear el worktree" 2
  elif git -C "$CLON" rev-parse -q --verify "refs/heads/$RAMA" >/dev/null; then
    git -C "$CLON" worktree add -q "$DIR" "$RAMA" || err "no se pudo crear el worktree" 2
  else
    # la rama no existe en ningun lado: crearla huerfana UNA vez
    git -C "$CLON" worktree add -q --detach "$DIR" || err "no se pudo crear el worktree" 2
    git -C "$DIR" checkout -q --orphan "$RAMA" || err "no se pudo crear la rama huerfana" 2
    git -C "$DIR" rm -rfq . 2>/dev/null
    find "$DIR" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
    printf 'Evidencia del equipo — solo esta rama. Nunca se mergea ni se borra.\n' > "$DIR/README.md"
    git -C "$DIR" add README.md && git -C "$DIR" commit -qm "chore(evidence): rama de evidencia" || err "commit inicial fallo" 2
  fi
fi

ACTUAL="$(git -C "$DIR" branch --show-current)"
[ "$ACTUAL" = "$RAMA" ] || err "el worktree $DIR esta en la rama '$ACTUAL', no en '$RAMA': no se escribe nada"
git -C "$DIR" pull -q --ff-only origin "$RAMA" 2>/dev/null

mkdir -p "$DIR/$DESTINO"
n=0
for f in "$ORIGEN"/*; do
  [ -f "$f" ] || continue
  case "${f##*.}" in png|jpg|jpeg|webp|gif|mp4|webm|md|PNG|JPG|JPEG) cp "$f" "$DIR/$DESTINO/" && n=$((n+1));; esac
done
[ "$n" -gt 0 ] || err "no hay archivos de evidencia en $ORIGEN"
git -C "$DIR" add -- "$DESTINO" || err "git add fallo" 2
[ "$(git -C "$DIR" branch --show-current)" = "$RAMA" ] || err "la rama cambio durante la subida" 2
git -C "$DIR" commit -qm "$MENSAJE" || err "commit fallo (¿sin cambios?)" 2
git -C "$DIR" push -q -u origin "$RAMA" || err "push fallo: el commit quedo local en $DIR (rama $RAMA)" 2

URL="$(git -C "$CLON" remote get-url origin | sed -E 's#^git@github\.com:#https://github.com/#; s#\.git$##')"
echo "OK $n archivo(s) en $RAMA:$DESTINO"
echo "RAW=$URL/raw/$RAMA/$DESTINO"
echo "BLOB=$URL/blob/$RAMA/$DESTINO"
