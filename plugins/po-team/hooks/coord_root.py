#!/usr/bin/env python3
"""po-team — resuelve la carpeta del equipo del Product Owner (.po-team) CANONICA de un proyecto.

Regla del equipo: `.po-team/` vive en la CARPETA DEL PROYECTO (o del PO), NUNCA dentro de un
repositorio git (contamina el repo con tickets, evidencia, tableros, documentos y metricas).

Orden de resolucion (desde una ruta de inicio, normalmente el cwd o CLAUDE_PROJECT_DIR):
  1. Registro del usuario `~/.claude/po-team.config.json` → "proyectos":
     { "<ruta de un repo o carpeta>": "<carpeta que contiene .po-team>" }
     La clave que sea prefijo mas largo de la ruta de inicio gana. Asi un repo que vive
     fuera de la carpeta del proyecto no necesita ningun archivo dentro del repo.
  2. Puntero legado `.po-team-root` (una linea con la ruta a la carpeta del proyecto).
  3. Subir directorios buscando `.po-team/` con config.json, prefiriendo una que NO
     este dentro de un repo git. Una que este dentro de un repo se devuelve marcada
     `en_repo=True` (proyecto legado que hay que migrar).
  4. Ultimo recurso: una `.po-team/` sin config.json (desvio).

Uso como modulo: resolve(start) -> dict(path, en_repo, origen, desvio)
Uso por CLI:     python3 coord_root.py [ruta]  → imprime JSON (o nada si no hay proyecto).
Nunca lanza excepciones hacia afuera.
"""
import json
import os
import sys

CARPETA = ".po-team"
REGISTRO = os.path.expanduser("~/.claude/po-team.config.json")
PROFUNDIDAD = 12


def repo_de(path):
    """Devuelve la raiz del repo git que contiene `path` (o None)."""
    try:
        d = os.path.abspath(path)
        if os.path.isfile(d):
            d = os.path.dirname(d)
        for _ in range(64):
            if os.path.exists(os.path.join(d, ".git")):
                return d
            parent = os.path.dirname(d)
            if parent == d:
                return None
            d = parent
    except Exception:
        return None
    return None


def _registro():
    try:
        with open(REGISTRO, encoding="utf-8") as f:
            data = json.load(f)
        p = data.get("proyectos") or {}
        return {os.path.abspath(os.path.expanduser(k)): os.path.abspath(os.path.expanduser(v))
                for k, v in p.items() if isinstance(k, str) and isinstance(v, str)}
    except Exception:
        return {}


def _dentro(path, base):
    path, base = os.path.abspath(path), os.path.abspath(base)
    return path == base or path.startswith(base.rstrip(os.sep) + os.sep)


def resolve(start):
    res = {"path": None, "en_repo": False, "origen": None, "desvio": None}
    if not start:
        return res
    try:
        start = os.path.abspath(os.path.expanduser(start))
        # 1. registro del usuario
        mejor = None
        for clave, destino in _registro().items():
            if _dentro(start, clave) and (mejor is None or len(clave) > len(mejor[0])):
                mejor = (clave, destino)
        if mejor:
            c = os.path.join(mejor[1], CARPETA)
            if os.path.isdir(c):
                res.update(path=c, en_repo=repo_de(mejor[1]) is not None, origen="registro")
                return res
        # 2 y 3. puntero legado y subida de directorios
        d, en_repo_cand, bare = start, None, None
        for _ in range(PROFUNDIDAD):
            ptr = os.path.join(d, ".po-team-root")
            if os.path.isfile(ptr):
                try:
                    t = open(ptr, encoding="utf-8").readline().strip()
                    if t:
                        t = t if os.path.isabs(t) else os.path.join(d, t)
                        c = os.path.join(os.path.abspath(t), CARPETA)
                        if os.path.isdir(c):
                            res.update(path=c, en_repo=repo_de(t) is not None, origen="puntero")
                            return res
                except Exception:
                    pass
            c = os.path.join(d, CARPETA)
            if os.path.isdir(c):
                if os.path.isfile(os.path.join(c, "config.json")):
                    if repo_de(d) is None:
                        res.update(path=c, en_repo=False, origen="carpeta-proyecto")
                        if bare and bare != c:
                            res["desvio"] = bare
                        return res
                    if en_repo_cand is None:
                        en_repo_cand = c
                elif bare is None:
                    bare = c
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
        if en_repo_cand:
            res.update(path=en_repo_cand, en_repo=True, origen="dentro-de-repo")
            if bare and bare != en_repo_cand:
                res["desvio"] = bare
            return res
        if bare:
            res.update(path=bare, en_repo=repo_de(bare) is not None, origen="sin-config")
    except Exception:
        pass
    return res


if __name__ == "__main__":
    r = resolve(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
    if r["path"]:
        print(json.dumps(r, ensure_ascii=False))
