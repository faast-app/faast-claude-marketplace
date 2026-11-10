#!/usr/bin/env python3
"""permisos_equipo.py — que el equipo no se bloquee por confirmaciones ni por el modo automatico.

Los agentes se frenan cuando una accion rutinaria y segura necesita una confirmacion que
nadie ve (agentes en segundo plano, Remote Control) o cuando el modo automatico la deniega.
Un plugin no puede traer reglas de permisos: viven en la configuracion del proyecto o del
usuario. Este script las PROPONE (y solo las escribe con `aplicar`, tras el OK del usuario):

  proponer [--proyecto DIR]     muestra el plan: reglas allow puntuales de solo lectura y de
                                los scripts del equipo, reglas ask para lo que siempre debe
                                confirmarse, y el texto de entorno para el modo automatico
  aplicar  [--proyecto DIR]     fusiona allow/ask en <proyecto>/.claude/settings.local.json
                                (local, no se commitea). Nunca toca deny ni reglas existentes.
  estado   [--proyecto DIR]     que reglas del plan ya estan y cuales faltan

Criterios: reglas ANGOSTAS (el modo automatico descarta las amplias como Bash(*) o
interpretes con comodin), nada que escriba en un ambiente, y lo irreversible queda en `ask`.
El texto de `autoMode.environment` va en ~/.claude/settings.json (Claude Code lo ignora en
archivos del proyecto): se imprime para que el usuario lo agregue; este script no lo escribe.
"""
import json
import os
import subprocess
import sys

# Windows: la consola no es UTF-8 por defecto; sin esto los acentos y simbolos rompen la salida.
for _flujo in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coord_root import resolve  # noqa: E402

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOLO_LECTURA = [
    "git status *", "git diff *", "git log *", "git show *", "git branch *", "git remote -v",
    "git rev-parse *", "git ls-files *", "git fetch *", "git stash list",
    "ls *", "pwd", "wc *", "file *", "which *", "date *",
    "gh auth status", "gh pr view *", "gh pr list *", "gh pr diff *", "gh pr checks *",
    "gh issue view *", "gh issue list *", "gh run view *", "gh run list *", "gh run watch *",
    "gh project item-list *", "gh project field-list *", "gh project view *", "gh repo view *",
    "az boards work-item show *", "az boards query *",
    "docker ps *", "docker images *", "docker logs *", "docker inspect *", "docker compose ps *",
    "docker compose config *", "docker compose logs *",
    "node --version", "npm --version", "pnpm --version", "dotnet --version", "python3 --version",
    "npm view *", "pnpm list *", "npm ls *",
]
SCRIPTS = [
    "hooks/pedidos_usuario.py", "hooks/permisos_equipo.py",
    "skills/libreria-faast/scripts/kit_libreria.py", "skills/memoria-equipo/scripts/memoria.py",
]
SIEMPRE_CONFIRMAR = [
    "git push *", "git push", "git merge *", "git rebase *", "git reset --hard *", "git clean *",
    "gh pr merge *", "gh pr create *", "gh workflow run *", "gh release create *", "gh issue close *",
    "docker compose down *", "docker compose up *", "docker rm *", "docker system prune *",
    "rm -rf *",
]


def plan():
    allow = [f"Bash({c})" for c in SOLO_LECTURA]
    for rel in SCRIPTS:
        ruta = os.path.join(PLUGIN, rel)
        if os.path.exists(ruta):
            allow.append(f'Bash(python3 "{ruta}" *)')
            allow.append(f"Bash(python3 {ruta} *)")
    ask = [f"Bash({c})" for c in SIEMPRE_CONFIRMAR]
    return allow, ask


def proyecto_dir(argv):
    if "--proyecto" in argv:
        return os.path.abspath(os.path.expanduser(argv[argv.index("--proyecto") + 1]))
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return os.getcwd()


def leer_settings(ruta):
    try:
        return json.load(open(ruta, encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"ERROR: {ruta} no es JSON valido ({e}). Corrigelo a mano; no se toca.", file=sys.stderr)
        sys.exit(2)


def entorno(dir_proyecto):
    """Prosa para autoMode.environment a partir de los ambientes declarados del proyecto."""
    r = resolve(dir_proyecto)
    lineas = ["$defaults"]
    if not r.get("path") or r.get("en_repo"):
        return lineas, None
    try:
        cfg = json.load(open(os.path.join(r["path"], "config.json"), encoding="utf-8"))
    except Exception:
        return lineas, r["path"]
    nombre = (cfg.get("project") or cfg.get("proyecto") or {})
    nombre = nombre.get("name") if isinstance(nombre, dict) else nombre
    amb = cfg.get("ambientes") or {}
    pruebas = sorted(k for k, v in amb.items() if isinstance(v, dict) and v.get("clase") == "pruebas")
    prod = sorted(k for k, v in amb.items() if isinstance(v, dict) and v.get("clase") == "productivo")
    lineas.append(f"La carpeta {r['path']} es la coordinacion del equipo de desarrollo"
                  f"{' del proyecto ' + str(nombre) if nombre else ''}: los agentes leen y escriben ahi "
                  "handoffs, evidencia, metricas y memoria como parte normal del trabajo.")
    if pruebas:
        lineas.append("Ambientes de PRUEBAS de este proyecto: " + ", ".join(pruebas) + ". En ellos las "
                      "acciones de negocio de prueba (giros, pagos, aprobaciones, desembolsos) y las "
                      "consultas de solo lectura a sus bases de datos son trabajo rutinario del equipo.")
    if prod:
        lineas.append("Ambientes PRODUCTIVOS de este proyecto: " + ", ".join(prod) + ". Cualquier "
                      "escritura, despliegue o cambio de datos en ellos requiere autorizacion explicita "
                      "del usuario para esa accion.")
    return lineas, r["path"]


def cmd_proponer(argv):
    d = proyecto_dir(argv)
    allow, ask = plan()
    ruta = os.path.join(d, ".claude", "settings.local.json")
    actual = leer_settings(ruta).get("permissions") or {}
    faltan_allow = [r for r in allow if r not in (actual.get("allow") or [])]
    faltan_ask = [r for r in ask if r not in (actual.get("ask") or [])]
    print(f"PLAN DE PERMISOS para {d}\n")
    print(f"1) {ruta} → permissions.allow (+{len(faltan_allow)} reglas de solo lectura y scripts del equipo)")
    for r in faltan_allow:
        print(f"   + {r}")
    print(f"\n2) mismo archivo → permissions.ask (+{len(faltan_ask)}; siempre confirman, tambien en modo automatico)")
    for r in faltan_ask:
        print(f"   + {r}")
    env, coord = entorno(d)
    print("\n3) Modo automatico — agregar a ~/.claude/settings.json (lo hace el usuario; este script no lo escribe):")
    print(json.dumps({"autoMode": {"environment": env}}, ensure_ascii=False, indent=2))
    if not coord:
        print("   (sin coordinacion del proyecto fuera de un repo: el texto no incluye ambientes)")
    print("\nNo se cambio nada. Con el OK del usuario: permisos_equipo.py aplicar"
          + (f" --proyecto \"{d}\"" if "--proyecto" in argv else ""))


def cmd_aplicar(argv):
    d = proyecto_dir(argv)
    allow, ask = plan()
    ruta = os.path.join(d, ".claude", "settings.local.json")
    cfg = leer_settings(ruta)
    perm = cfg.setdefault("permissions", {})
    deny = set(perm.get("deny") or [])
    sumadas = {"allow": 0, "ask": 0}
    for clave, reglas in (("allow", allow), ("ask", ask)):
        lista = perm.setdefault(clave, [])
        for r in reglas:
            if r not in lista and r not in deny:
                lista.append(r)
                sumadas[clave] += 1
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
        f.write("\n")
    try:  # el archivo es local: que no entre a git
        r = subprocess.run(["git", "-C", d, "rev-parse", "--git-path", "info/exclude"],
                           capture_output=True, text=True, timeout=5)
        exc = r.stdout.strip()
        if r.returncode == 0 and exc:
            exc = exc if os.path.isabs(exc) else os.path.join(d, exc)
            actual = open(exc, encoding="utf-8").read() if os.path.exists(exc) else ""
            if ".claude/settings.local.json" not in actual:
                os.makedirs(os.path.dirname(exc), exist_ok=True)
                with open(exc, "a", encoding="utf-8") as f:
                    f.write(("\n" if actual and not actual.endswith("\n") else "") + ".claude/settings.local.json\n")
    except Exception:
        pass
    print(f"{ruta}: +{sumadas['allow']} allow, +{sumadas['ask']} ask (deny y reglas existentes intactos).")
    print("Rige desde la proxima accion; en una sesion abierta puede requerir /permissions o reiniciarla.")


def cmd_estado(argv):
    d = proyecto_dir(argv)
    allow, ask = plan()
    perm = leer_settings(os.path.join(d, ".claude", "settings.local.json")).get("permissions") or {}
    ya = sum(1 for r in allow if r in (perm.get("allow") or []))
    ya_ask = sum(1 for r in ask if r in (perm.get("ask") or []))
    print(f"{d}: allow {ya}/{len(allow)} · ask {ya_ask}/{len(ask)} del plan del equipo")
    sys.exit(0 if ya == len(allow) and ya_ask == len(ask) else 1)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "proponer"
    {"proponer": cmd_proponer, "aplicar": cmd_aplicar, "estado": cmd_estado}.get(cmd, cmd_proponer)(sys.argv)
