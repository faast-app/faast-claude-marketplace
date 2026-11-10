#!/usr/bin/env python3
"""po-team — sube evidencia a la rama huerfana de evidencia del repo configurado, SIN tocar ramas
de trabajo. Usa un worktree hermano del clon ({clon}-evidence) con RUTAS ABSOLUTAS y verifica la
rama antes de commitear: si el worktree no esta en la rama de evidencia, aborta sin escribir.
Sin bash: funciona igual en Windows, macOS y Linux.

Uso:
  subir_evidencia.py --clon /ruta/abs/al/clon --rama evidence \
      --destino "evidence/po/130-total-iva/validacion-demo-co-20261016" \
      --origen /ruta/abs/.po-team/tickets/130/validacion-demo-co-20261016 \
      --mensaje "evidence(po): #130 validacion Demo CO"
Copia del origen solo imagenes, video y .md (png jpg jpeg webp gif mp4 webm md). Imprime al final
las bases RAW= y BLOB= para armar los enlaces del comentario. Codigos: 0 ok, 1 error de uso o
verificacion, 2 git fallo (nada a medias queda commiteado en otra rama).
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

for _flujo in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

EXTENSIONES = {"png", "jpg", "jpeg", "webp", "gif", "mp4", "webm", "md"}


def err(msg, codigo=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(codigo)


def git(directorio, *args, check=False):
    r = subprocess.run(["git", "-C", directorio, *args], capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        return None
    return r


def ok(directorio, *args):
    return git(directorio, *args).returncode == 0


def main():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("--clon", required=True)
    p.add_argument("--rama", default="evidence")
    p.add_argument("--destino", required=True)
    p.add_argument("--origen", required=True)
    p.add_argument("--mensaje", required=True)
    a = p.parse_args()

    destino = a.destino.replace("\\", "/")
    if destino.startswith("/") or re.match(r"^[A-Za-z]:", destino) or ".." in destino.split("/"):
        err("--destino debe ser relativo dentro de la rama y sin '..'")
    clon = os.path.abspath(os.path.expanduser(a.clon))
    origen = os.path.abspath(os.path.expanduser(a.origen))
    if not os.path.isdir(clon):
        err("no existe el clon")
    if not os.path.isdir(origen):
        err("no existe el origen")
    if not ok(clon, "rev-parse", "--git-dir"):
        err(f"{clon} no es un repo git")
    wt = os.path.join(os.path.dirname(clon), os.path.basename(clon) + "-evidence")

    if not os.path.isdir(wt):
        git(clon, "fetch", "-q", "origin", a.rama)
        if ok(clon, "rev-parse", "-q", "--verify", f"refs/remotes/origin/{a.rama}"):
            if not ok(clon, "worktree", "add", "-q", "-B", a.rama, wt, f"origin/{a.rama}"):
                err("no se pudo crear el worktree", 2)
        elif ok(clon, "rev-parse", "-q", "--verify", f"refs/heads/{a.rama}"):
            if not ok(clon, "worktree", "add", "-q", wt, a.rama):
                err("no se pudo crear el worktree", 2)
        else:  # la rama no existe en ningun lado: crearla huerfana UNA vez
            if not ok(clon, "worktree", "add", "-q", "--detach", wt):
                err("no se pudo crear el worktree", 2)
            if not ok(wt, "checkout", "-q", "--orphan", a.rama):
                err("no se pudo crear la rama huerfana", 2)
            git(wt, "rm", "-rfq", ".")
            for nombre in os.listdir(wt):
                if nombre == ".git":
                    continue
                ruta = os.path.join(wt, nombre)
                shutil.rmtree(ruta) if os.path.isdir(ruta) else os.remove(ruta)
            with open(os.path.join(wt, "README.md"), "w", encoding="utf-8") as f:
                f.write("Evidencia del equipo — solo esta rama. Nunca se mergea ni se borra.\n")
            if not (ok(wt, "add", "README.md") and ok(wt, "commit", "-qm", "chore(evidence): rama de evidencia")):
                err("commit inicial fallo", 2)

    actual = git(wt, "branch", "--show-current").stdout.strip()
    if actual != a.rama:
        err(f"el worktree {wt} esta en la rama '{actual}', no en '{a.rama}': no se escribe nada")
    git(wt, "pull", "-q", "--ff-only", "origin", a.rama)

    carpeta = os.path.join(wt, *destino.split("/"))
    os.makedirs(carpeta, exist_ok=True)
    n = 0
    for nombre in sorted(os.listdir(origen)):
        ruta = os.path.join(origen, nombre)
        if os.path.isfile(ruta) and nombre.rsplit(".", 1)[-1].lower() in EXTENSIONES:
            shutil.copy2(ruta, carpeta)
            n += 1
    if n == 0:
        err(f"no hay archivos de evidencia en {origen}")
    if not ok(wt, "add", "--", destino):
        err("git add fallo", 2)
    if git(wt, "branch", "--show-current").stdout.strip() != a.rama:
        err("la rama cambio durante la subida", 2)
    if not ok(wt, "commit", "-qm", a.mensaje):
        err("commit fallo (¿sin cambios?)", 2)
    if not ok(wt, "push", "-q", "-u", "origin", a.rama):
        err(f"push fallo: el commit quedo local en {wt} (rama {a.rama})", 2)

    url = git(clon, "remote", "get-url", "origin").stdout.strip()
    url = re.sub(r"\.git$", "", re.sub(r"^git@github\.com:", "https://github.com/", url))
    print(f"OK {n} archivo(s) en {a.rama}:{destino}")
    print(f"RAW={url}/raw/{a.rama}/{destino}")
    print(f"BLOB={url}/blob/{a.rama}/{destino}")


if __name__ == "__main__":
    main()
