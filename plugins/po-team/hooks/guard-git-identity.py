#!/usr/bin/env python3
"""guardia: no se crean commits con una identidad de git generica o inventada (PreToolUse: Bash).

Incidente que lo motiva: en septiembre-octubre de 2026 se subieron ~430 commits firmados por
`test <test@local>` (sesiones asistidas por IA con una identidad de relleno) a 14 repos de FAAST;
quitarlos exigio reescribir la historia de ramas de despliegue, tags y releases. Este guardia lo evita en origen.

Que hace: ante un comando que CREA commits o tags anotados (git commit, merge, cherry-pick, revert,
rebase, am, pull, commit-tree, tag -a/-s/-m) calcula la identidad EFECTIVA de autor y de committer
con `git var` (respeta ~/.gitconfig, config del repo, `git -C`, `cd`, `git -c user.*=`, `--author=` y
GIT_AUTHOR_*/GIT_COMMITTER_* puestos en el propio comando). Si es generica o esta sin definir,
DENIEGA y explica como corregirlo. Tambien deniega `git config user.name|user.email <valor generico>`.

Generica = nombre test/tester/root/user/admin/unknown/claude/"your name" o correo test@, root@,
noreply@anthropic.com, @example.*, o cuyo dominio sea local/localhost/localdomain o no tenga punto
(el autodetectado `usuario@equipo.local` que git inventa cuando no hay configuracion).

Excepcion deliberada: la variable de entorno FAAST_PERMITIR_IDENTIDAD_GENERICA=1 en el ENTORNO de
Claude Code (lo decide la persona, no el agente; ponerla dentro del comando no cuenta).
Nunca falla hacia afuera: ante cualquier error inesperado, permite.
"""
import json
import os
import re
import shlex
import subprocess
import sys

CREAN = {"commit", "merge", "cherry-pick", "revert", "rebase", "am", "pull", "commit-tree"}
NOMBRES = {"test", "tester", "root", "user", "admin", "administrator", "unknown", "claude", "your name",
           "you", "nobody", "default", "localhost"}
CORREO_MALO = re.compile(r"^(test|root|user|admin|unknown|nobody|you|your)@|^noreply@anthropic\.com$|@example\.[a-z]+$", re.I)
DOMINIO_LOCAL = re.compile(r"(^|\.)(local|localhost|localdomain)$", re.I)
ASIGNA = re.compile(r"^(GIT_(AUTHOR|COMMITTER)_(NAME|EMAIL))=(.*)$")


def deny(motivo):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": "deny",
                                             "permissionDecisionReason": motivo}}))
    sys.exit(0)


def generica(nombre, correo):
    n, c = (nombre or "").strip().strip("\"'"), (correo or "").strip().strip("\"'<>")
    if not n or not c:
        return "sin definir"
    if n.lower() in NOMBRES:
        return f"nombre generico '{n}'"
    if CORREO_MALO.search(c):
        return f"correo generico '{c}'"
    dom = c.split("@", 1)[1] if "@" in c else ""
    if "@" not in c or not dom or "." not in dom or DOMINIO_LOCAL.search(dom):
        return f"correo local o invalido '{c}'"
    return None


def quitar_heredocs(cmd):
    return re.sub(r"<<-?\s*['\"]?(\w+)['\"]?.*?\n\s*\1\b", " ", cmd, flags=re.S)


def segmentos(cmd):
    return [s for s in re.split(r"&&|\|\||;|\n|\|", quitar_heredocs(cmd)) if s.strip()]


def analizar(seg, cwd):
    """Devuelve None o (subcomando, dir, env_extra, opciones -c, author) si el segmento invoca git."""
    try:
        t = shlex.split(seg, posix=True)
    except ValueError:
        return None
    env, i = {}, 0
    while i < len(t) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t[i]):   # VAR=valor git ...
        m = ASIGNA.match(t[i])
        if m:
            env[m.group(1)] = m.group(4)
        i += 1
    if i >= len(t) or os.path.basename(t[i]) != "git":
        return None
    i += 1
    dirs, cfg = cwd, []
    while i < len(t) and t[i].startswith("-"):
        if t[i] == "-C" and i + 1 < len(t):
            dirs = t[i + 1] if os.path.isabs(t[i + 1]) else os.path.join(dirs, t[i + 1])
            i += 2
        elif t[i] == "-c" and i + 1 < len(t):
            cfg.append(t[i + 1])
            i += 2
        elif t[i] in ("--git-dir", "--work-tree", "--namespace") and i + 1 < len(t):
            i += 2
        else:
            i += 1
    if i >= len(t):
        return None
    sub, resto = t[i], t[i + 1:]
    author = None
    for j, a in enumerate(resto):
        if a.startswith("--author="):
            author = a.split("=", 1)[1]
        elif a == "--author" and j + 1 < len(resto):
            author = resto[j + 1]
    return sub, dirs, env, cfg, author, resto


def ident(kind, dirs, env, cfg):
    e = dict(os.environ)
    e.update(env)
    args = ["git"]
    for c in cfg:
        args += ["-c", c]
    args += ["var", f"GIT_{kind}_IDENT"]
    r = subprocess.run(args, cwd=dirs if os.path.isdir(dirs) else None, env=e, capture_output=True, text=True, timeout=8)
    if r.returncode != 0:
        return None, None
    m = re.match(r"^(.*?)\s*<([^>]*)>", r.stdout.strip())
    return (m.group(1), m.group(2)) if m else (None, None)


def main():
    if os.environ.get("FAAST_PERMITIR_IDENTIDAD_GENERICA") == "1":
        return
    p = json.load(sys.stdin)
    if (p.get("tool_name") or "") != "Bash":
        return
    cmd = (p.get("tool_input") or {}).get("command") or ""
    if "git" not in cmd:
        return
    cwd = p.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    actual = cwd
    for seg in segmentos(cmd):
        m = re.match(r"^\s*cd\s+(\"[^\"]*\"|'[^']*'|\S+)\s*$", seg)
        if m:
            d = os.path.expanduser(m.group(1).strip("\"'"))
            actual = d if os.path.isabs(d) else os.path.normpath(os.path.join(actual, d))
            continue
        a = analizar(seg, actual)
        if not a:
            continue
        sub, dirs, env, cfg, author, resto = a
        # git config user.name|user.email <valor generico>
        if sub == "config":
            vals = [x for x in resto if not x.startswith("-")]
            if len(vals) >= 2 and vals[0] in ("user.name", "user.email"):
                n, c = (vals[1], "x@x.com") if vals[0] == "user.name" else ("x", vals[1])
                mal = generica(n, c)
                if mal:
                    deny(f"Bloqueado: no se configura una identidad de git generica ({vals[0]} = '{vals[1]}'; {mal}). "
                         "Usa la identidad real de la persona o pidesela: `git config --global user.name \"Nombre Apellido\"` y "
                         "`git config --global user.email \"correo@faast.app\"`. Nunca inventes una identidad para poder commitear.")
            continue
        crea = sub in CREAN or (sub == "tag" and any(x in resto for x in ("-a", "-s", "-m", "--annotate", "--sign")))
        if not crea:
            continue
        for kind in ("AUTHOR", "COMMITTER"):
            nombre, correo = ident(kind, dirs, env, cfg)
            if kind == "AUTHOR" and author:
                m2 = re.match(r"^(.*?)\s*<([^>]*)>", author)
                if m2:
                    nombre, correo = m2.group(1), m2.group(2)
            mal = generica(nombre, correo)
            if mal:
                que = "autor" if kind == "AUTHOR" else "committer"
                deny(f"Bloqueado: el {que} del commit seria '{nombre or '(vacio)'} <{correo or '(vacio)'}>' ({mal}). "
                     "No se commitea con una identidad generica (en 2026 ~430 commits salieron como 'test <test@local>' y hubo que "
                     "reescribir la historia de 14 repos). Pide al usuario su nombre y correo reales y configuralos: "
                     "`git config --global user.name \"Nombre Apellido\"` y `git config --global user.email \"correo@faast.app\"`, "
                     "o revisa que el repo no tenga una identidad local que la tape (`git config --local --list | grep user.`). "
                     "No inventes ni pongas valores de relleno.")


try:
    main()
except SystemExit:
    raise
except Exception:
    pass
sys.exit(0)
