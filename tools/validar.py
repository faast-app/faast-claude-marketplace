#!/usr/bin/env python3
"""Validador estructural del marketplace. Es la puerta de calidad del repo (corre en CI).

  python3 tools/validar.py            # sale con 1 si hay errores

Comprueba lo que antes solo se revisaba a mano y se rompia en silencio:
  - marketplace.json y cada plugin.json (nombre, version semver, carpeta existente)
  - frontmatter de agentes, comandos y skills (nombre = archivo, descripcion, modelo permitido)
  - hooks.json: forma exec con node + run.mjs, scripts existentes, sin .sh, guardias con PowerShell
  - .mcp.json sin bash
  - archivos compartidos identicos en los cuatro equipos
  - reglas comunes presentes en todos los agentes
  - version y cantidad de comandos de los manuales = realidad
  - todo .py compila y todo .mjs pasa `node --check`
"""
import glob
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EQUIPOS = {"dev-team": "lead", "mesa-servicios": "mesa-lead", "po-team": "po-lead", "marketing": "director-marketing"}
MODELOS = {"haiku", "sonnet", "opus", "inherit"}
COMPARTIDOS = ["run.mjs", "_python.mjs", "py.mjs", "mcp-playwright.mjs", "doctor.mjs", "pedidos_usuario.py"]
SECCIONES_AGENTE = ["### Como reportas", "### Terminal y sistema operativo",
                    "### El canal con el usuario es el coordinador", "### Si el sistema te deniega una herramienta"]
errores, avisos = [], []


def err(msg):
    errores.append(msg)


def rel(p):
    return os.path.relpath(p, RAIZ)


def leer(p):
    return open(p, encoding="utf-8").read()


def frontmatter(p):
    m = re.match(r"^---\n(.*?)\n---\n", leer(p), re.S)
    if not m:
        err(f"{rel(p)}: sin frontmatter YAML")
        return None
    campos = {}
    for linea in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", linea)
        if mm:
            campos[mm.group(1)] = mm.group(2).strip().strip("'\"")
    return campos


def validar_manifiestos():
    mk = json.load(open(os.path.join(RAIZ, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
    nombres = set()
    for pl in mk.get("plugins", []):
        nombres.add(pl["name"])
        carpeta = os.path.normpath(os.path.join(RAIZ, pl.get("source", "")))
        if not os.path.isdir(carpeta):
            err(f"marketplace.json: la carpeta de {pl['name']} no existe ({pl.get('source')})")
            continue
        pj = os.path.join(carpeta, ".claude-plugin", "plugin.json")
        if not os.path.exists(pj):
            err(f"{rel(carpeta)}: falta .claude-plugin/plugin.json")
            continue
        d = json.load(open(pj, encoding="utf-8"))
        if d.get("name") != pl["name"]:
            err(f"{rel(pj)}: name '{d.get('name')}' no coincide con marketplace.json '{pl['name']}'")
        if "version" in d and not re.match(r"^\d+\.\d+\.\d+$", d["version"]):
            err(f"{rel(pj)}: version '{d['version']}' no es X.Y.Z")
    for carpeta in glob.glob(os.path.join(RAIZ, "plugins", "*")):
        if os.path.isdir(carpeta) and os.path.basename(carpeta) not in nombres:
            err(f"{rel(carpeta)}: no esta registrado en marketplace.json")


def validar_markdown():
    for p in glob.glob(os.path.join(RAIZ, "plugins", "*", "agents", "*.md")):
        fm = frontmatter(p)
        if fm is None:
            continue
        nombre = os.path.basename(p)[:-3]
        if fm.get("name") != nombre:
            err(f"{rel(p)}: name '{fm.get('name')}' debe ser '{nombre}'")
        if not fm.get("description"):
            err(f"{rel(p)}: sin description")
        if "model" in fm and fm["model"] not in MODELOS:
            err(f"{rel(p)}: model '{fm['model']}' no permitido (nunca fable)")
        plugin = p.split(os.sep)[-3]
        if plugin in EQUIPOS:
            texto = leer(p)
            if nombre != EQUIPOS[plugin] and "disallowedTools" not in texto.split("\n---\n", 1)[0]:
                err(f"{rel(p)}: solo {EQUIPOS[plugin]} delega; falta disallowedTools: Agent")
            for sec in SECCIONES_AGENTE:
                if sec not in texto:
                    err(f"{rel(p)}: falta la seccion comun «{sec}»")
    for p in glob.glob(os.path.join(RAIZ, "plugins", "*", "commands", "*.md")):
        fm = frontmatter(p)
        if fm is not None and not fm.get("description"):
            err(f"{rel(p)}: sin description")
    for p in glob.glob(os.path.join(RAIZ, "plugins", "*", "skills", "*", "SKILL.md")):
        fm = frontmatter(p)
        if fm is None:
            continue
        carpeta = os.path.basename(os.path.dirname(p))
        if fm.get("name") != carpeta:
            err(f"{rel(p)}: name '{fm.get('name')}' debe ser '{carpeta}'")
        if not fm.get("description"):
            err(f"{rel(p)}: sin description")


def validar_hooks():
    for plugin in EQUIPOS:
        base = os.path.join(RAIZ, "plugins", plugin, "hooks")
        h = json.load(open(os.path.join(base, "hooks.json"), encoding="utf-8"))
        for evento, grupos in h.get("hooks", {}).items():
            for g in grupos:
                matcher = g.get("matcher", "")
                if re.search(r"(^|\|)Bash(\||$)", matcher) and "PowerShell" not in matcher:
                    err(f"{plugin}/hooks.json [{evento}]: el matcher con Bash debe incluir PowerShell")
                for x in g.get("hooks", []):
                    args = x.get("args") or []
                    if x.get("command") != "node" or not args or not args[0].endswith("/hooks/run.mjs"):
                        err(f"{plugin}/hooks.json [{evento}]: usa la forma exec: node + run.mjs (sin shell)")
                        continue
                    if len(args) < 2 or not os.path.exists(os.path.join(base, args[1])):
                        err(f"{plugin}/hooks.json [{evento}]: el script '{args[1] if len(args) > 1 else ''}' no existe")
        mcp = os.path.join(RAIZ, "plugins", plugin, ".mcp.json")
        if os.path.exists(mcp):
            for nombre, srv in json.load(open(mcp, encoding="utf-8")).items():
                if srv.get("command") in ("bash", "sh", "npx"):
                    err(f"{plugin}/.mcp.json [{nombre}]: lanzalo con node (no funciona en Windows con '{srv.get('command')}')")
    for sh in glob.glob(os.path.join(RAIZ, "plugins", "**", "*.sh"), recursive=True):
        if f"{os.sep}templates{os.sep}" not in sh:
            err(f"{rel(sh)}: script de bash fuera de templates (no corre en Windows)")


def validar_compartidos():
    for nombre in COMPARTIDOS:
        contenidos = {}
        for plugin in EQUIPOS:
            p = os.path.join(RAIZ, "plugins", plugin, "hooks", nombre)
            if not os.path.exists(p):
                err(f"{plugin}/hooks/{nombre}: falta (debe existir en los cuatro equipos)")
            else:
                contenidos[plugin] = leer(p)
        if len(set(contenidos.values())) > 1:
            err(f"hooks/{nombre}: difiere entre equipos; debe ser identico ({', '.join(contenidos)})")


def validar_manuales():
    guia = leer(os.path.join(RAIZ, "GUIDE.md"))
    for plugin in EQUIPOS:
        base = os.path.join(RAIZ, "plugins", plugin)
        version = json.load(open(os.path.join(base, ".claude-plugin", "plugin.json"), encoding="utf-8"))["version"]
        menor = ".".join(version.split(".")[:2])
        comandos = len(glob.glob(os.path.join(base, "commands", "*.md")))
        agentes = len(glob.glob(os.path.join(base, "agents", "*.md")))
        manual = leer(os.path.join(base, "GUIDE.md"))
        m = re.search(r"\*\*Version del plugin:\*\*\s*([\d.x]+).*?\*\*Integrantes del equipo:\*\*\s*(\d+).*?\*\*Comandos:\*\*\s*(\d+)", manual)
        if not m:
            err(f"{plugin}/GUIDE.md: no encuentro el encabezado de version/integrantes/comandos")
        else:
            if not m.group(1).startswith(menor):
                err(f"{plugin}/GUIDE.md: dice version {m.group(1)}, plugin.json dice {version}")
            if int(m.group(2)) != agentes:
                err(f"{plugin}/GUIDE.md: dice {m.group(2)} integrantes, hay {agentes} agentes")
            if int(m.group(3)) != comandos:
                err(f"{plugin}/GUIDE.md: dice {m.group(3)} comandos, hay {comandos}")
        fila = re.search(r"\(`" + re.escape(plugin) + r"`\)\s*\|\s*([\d.]+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", guia)
        if not fila:
            err(f"GUIDE.md: falta la fila de {plugin} en la tabla de equipos")
        elif (fila.group(1), int(fila.group(2)), int(fila.group(3))) != (version, agentes, comandos):
            err(f"GUIDE.md: la fila de {plugin} dice {fila.group(1)}/{fila.group(2)}/{fila.group(3)}; "
                f"lo real es {version}/{agentes}/{comandos}")
        if not os.path.exists(os.path.join(base, "GUIDE.pdf")):
            err(f"{plugin}: falta GUIDE.pdf")


def validar_codigo():
    for p in glob.glob(os.path.join(RAIZ, "**", "*.py"), recursive=True):
        if f"{os.sep}.git{os.sep}" in p:
            continue
        try:
            compile(leer(p), p, "exec")
        except SyntaxError as e:
            err(f"{rel(p)}: no compila: linea {e.lineno}: {e.msg}")
    for p in glob.glob(os.path.join(RAIZ, "plugins", "*", "hooks", "*.mjs")) + glob.glob(os.path.join(RAIZ, "docs", "**", "*.mjs"), recursive=True):
        r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
        if r.returncode != 0:
            err(f"{rel(p)}: {r.stderr.strip().splitlines()[0] if r.stderr.strip() else 'node --check fallo'}")
    for p in glob.glob(os.path.join(RAIZ, "plugins", "**", "*.json"), recursive=True) + [os.path.join(RAIZ, ".claude-plugin", "marketplace.json")]:
        try:
            json.load(open(p, encoding="utf-8"))
        except Exception as e:
            err(f"{rel(p)}: JSON invalido: {e}")


def main():
    for paso in (validar_manifiestos, validar_markdown, validar_hooks, validar_compartidos, validar_manuales, validar_codigo):
        try:
            paso()
        except Exception as e:  # un validador roto tambien es un error
            err(f"{paso.__name__}: {type(e).__name__}: {e}")
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"ERROR: {e}")
    print(f"\nVALIDACION: {'PASA' if not errores else 'FALLA'} ({len(errores)} error(es))")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
