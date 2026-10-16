#!/usr/bin/env python3
"""mesa-servicios — guardia: NADA de la Mesa (.mesa) dentro de un repositorio (PreToolUse).

Bloquea escribir `.mesa/` (solicitudes, evidencia, metricas, accesos) dentro de
un repo git: contamina el repo y llena el historial. La coordinacion vive en la carpeta del
proyecto (ver coord_root.py). Aplica a Write/Edit/MultiEdit/NotebookEdit y a comandos Bash que
escriben (>, >>, tee, touch, mkdir) o que hacen `git add` de esa carpeta. Mover la carpeta
FUERA del repo (mv/cp/rsync) se permite: es la migracion.

Excepcion: las plantillas de los plugins (rutas con /templates/). Nunca falla hacia afuera: ante cualquier error, permite.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coord_root import CARPETA, repo_de, resolve  # noqa: E402

ESCRIBE = re.compile(r"(>>?|\btee\b|\btouch\b|\bmkdir\b|\bgit\s+add\b)")
REF = re.compile(r"(?:(?<=\s)|(?<=^)|(?<=[\"'=(]))((?:[~\w./-]*/)?" + re.escape(CARPETA) + r")(?=/|\s|$|[\"')])")


def exento(path):
    p = path.replace("\\", "/")
    return "/templates/" in p


def deny(motivo):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": "deny",
                                             "permissionDecisionReason": motivo}}))
    sys.exit(0)


def mensaje(base_repo, cwd):
    canon = resolve(cwd)
    destino = canon["path"] if canon["path"] and not canon["en_repo"] else None
    txt = (f"Bloqueado: no se guarda la carpeta de la Mesa (.mesa) dentro del repositorio {base_repo} "
           "(contamina el repo). ")
    if destino:
        txt += f"Usa la ruta ABSOLUTA de la carpeta canonica de la Mesa: {destino}"
    else:
        txt += ("Esta Mesa no tiene su carpeta fuera de los repos. Pide al usuario "
                "la carpeta del proyecto (la que contiene el repo o una dedicada), crea ahi "
                ".mesa/ y registrala en ~/.claude/mesa-servicios.config.json → \"proyectos\": "
                "{\"<ruta del repo>\": \"<carpeta del proyecto>\"}. Si ya existe una .mesa "
                "dentro del repo, MUEVELA (mv) a la carpeta del proyecto; sacarla del historial del "
                "repo es un PR aparte que requiere OK del usuario.")
    return txt


def en_repo_coord(path):
    """Si `path` cae dentro de una .mesa que vive en un repo git, devuelve la raiz del repo."""
    p = os.path.abspath(os.path.expanduser(path))
    partes = p.split(os.sep)
    if CARPETA not in partes:
        return None
    base = os.sep.join(partes[:partes.index(CARPETA)]) or os.sep
    if exento(p):
        return None
    return repo_de(base)


def main():
    payload = json.load(sys.stdin)
    tool = payload.get("tool_name") or ""
    ti = payload.get("tool_input") or {}
    cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        path = ti.get("file_path") or ti.get("notebook_path") or ""
        if path:
            if not os.path.isabs(path):
                path = os.path.join(cwd, path)
            repo = en_repo_coord(path)
            if repo:
                deny(mensaje(repo, cwd))
        return

    if tool == "Bash":
        cmd = ti.get("command") or ""
        if CARPETA not in cmd or not ESCRIBE.search(cmd):
            return
        for segmento in re.split(r"&&|\|\||;|\n", cmd):
            if CARPETA not in segmento or not ESCRIBE.search(segmento):
                continue
            # mover/copiar la carpeta FUERA del repo es la migracion: permitido
            if re.match(r"\s*(mv|cp|rsync)\b", segmento) and not re.search(r">", segmento):
                continue
            for m in REF.finditer(segmento):
                ref = m.group(1)
                path = os.path.expanduser(ref)
                if not os.path.isabs(path):
                    path = os.path.join(cwd, path)
                repo = en_repo_coord(path)
                if repo:
                    deny(mensaje(repo, cwd))


try:
    main()
except SystemExit:
    raise
except Exception:
    pass
sys.exit(0)
