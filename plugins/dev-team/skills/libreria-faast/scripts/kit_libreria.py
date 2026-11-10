#!/usr/bin/env python3
"""kit_libreria.py — las propuestas de diseño HEREDAN de la libreria UI de FaaST.

Trae el "kit de propuestas" de la libreria (@faast-app/ui, @faast-app/tokens,
@faast-app/themes) a la carpeta de diseño y verifica que cada HTML entregado use ese kit y
nada inventado. Sin dependencias: solo Python 3 (y `npm` cuando la fuente es el registro).

  obtener   --destino DIR [--version X|latest] [--fuente npm|RUTA_AL_CLON] [--scope @faast-app]
            Copia faast-kit.css, markup.json, catalogo.html, tokens.json, themes.json y los
            logos, y escribe LIBRERIA.json (version, fuente, commit, sha256 de cada archivo).
  verificar HTML [HTML...] --kit DIR [--json]
            Revisa que la propuesta herede de la libreria: hoja del kit enlazada o incrustada,
            cero colores/fuentes literales, cero clases faast-* o variables --faast-* inventadas.
            Sale con 1 si hay errores.
  incrustar HTML --kit DIR [-o SALIDA]
            Reemplaza el <link> al kit por un <style> para entregar UN archivo autocontenido.
  roles     --kit DIR
            Tabla Markdown de los roles semanticos (variable CSS, claro, oscuro) para DESIGN.md.

Nunca escribe dentro de un repositorio de codigo: el destino es la carpeta de diseño de la
coordinacion (o la que indique el coordinador).
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

# Windows: la consola no es UTF-8 por defecto; sin esto los acentos y simbolos rompen la salida.
for _flujo in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PAQUETES = ("tokens", "themes", "ui")
MIN_KIT = (0, 8, 0)
# archivo en el kit -> (paquete, ruta dentro de dist/)
ARCHIVOS = {
    "faast-kit.css": ("ui", "kit/faast-kit.css"),
    "markup.json": ("ui", "kit/markup.json"),
    "catalogo.html": ("ui", "kit/catalogo.html"),
    "tokens.json": ("tokens", "tokens.dtcg.json"),
    "themes.json": ("themes", "themes.dtcg.json"),
    "faast-logo.svg": ("tokens", "brand/faast-logo.svg"),
    "faast-logo-on-dark.svg": ("tokens", "brand/faast-logo-on-dark.svg"),
}
MARCA_KIT = "faast-kit.css (generated, do not edit)"


def fallar(msg, codigo=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(codigo)


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 16), b""):
            h.update(bloque)
    return h.hexdigest()


def version_tupla(v):
    nums = re.findall(r"\d+", v or "")[:3]
    return tuple(int(n) for n in nums) + (0,) * (3 - len(nums))


# ---------------------------------------------------------------- obtener

def _extraer_seguro(tgz, destino):
    """Extrae un tarball de npm rechazando rutas que salgan del destino."""
    base = os.path.realpath(destino)
    with tarfile.open(tgz) as tar:
        for m in tar.getmembers():
            ruta = os.path.realpath(os.path.join(destino, m.name))
            if not (ruta == base or ruta.startswith(base + os.sep)) or m.issym() or m.islnk():
                fallar(f"entrada insegura en {os.path.basename(tgz)}: {m.name}")
        try:
            tar.extractall(destino, filter="data")
        except TypeError:  # Python < 3.12
            tar.extractall(destino)


def _dist_desde_npm(scope, version, tmp):
    if not shutil.which("npm"):
        fallar("no encuentro `npm`. Instala Node o usa --fuente con la ruta a un clon de la libreria.")
    dists = {}
    for p in PAQUETES:
        spec = f"{scope}/{p}@{version}"
        r = subprocess.run(["npm", "pack", spec, "--silent", "--pack-destination", tmp],
                           capture_output=True, text=True, cwd=tmp)
        if r.returncode != 0:
            fallar(f"`npm pack {spec}` fallo: {(r.stderr or r.stdout).strip()[:400]}")
        tgz = os.path.join(tmp, r.stdout.strip().splitlines()[-1])
        dest = os.path.join(tmp, p)
        os.makedirs(dest)
        _extraer_seguro(tgz, dest)
        dists[p] = os.path.join(dest, "package")
    return dists, {"tipo": "npm", "paquetes": f"{scope}/*@{version}"}


def _dist_desde_clon(ruta):
    ruta = os.path.abspath(os.path.expanduser(ruta))
    dists = {p: os.path.join(ruta, "packages", p) for p in PAQUETES}
    faltan = [p for p, d in dists.items() if not os.path.isdir(os.path.join(d, "dist"))]
    if faltan:
        fallar(f"el clon {ruta} no esta compilado (falta dist/ en: {', '.join(faltan)}). "
               "Corre ahi `pnpm install && pnpm run build` y reintenta.")

    def git(*args):
        r = subprocess.run(["git", "-C", ruta, *args], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None

    return dists, {"tipo": "clon", "ruta": ruta, "rama": git("rev-parse", "--abbrev-ref", "HEAD"),
                   "commit": git("rev-parse", "--short", "HEAD"),
                   "sucio": bool(git("status", "--porcelain"))}


def _componer_kit_css(dists):
    """Libreria anterior al kit (< 0.8.0): arma la hoja unica con las hojas publicadas."""
    partes = ["/* faast-kit.css compuesto por kit_libreria.py desde las hojas publicadas "
              "(libreria anterior a 0.8.0: sin fuente Inter incrustada). */"]
    for p, rel in (("tokens", "tokens.css"), ("themes", "themes.css"),
                   ("themes", "base.css"), ("ui", "styles.css")):
        partes.append(open(os.path.join(dists[p], "dist", rel), encoding="utf-8").read())
    return "\n\n".join(partes)


def cmd_obtener(a):
    destino = os.path.abspath(os.path.expanduser(a.destino))
    with tempfile.TemporaryDirectory() as tmp:
        if a.fuente == "npm":
            dists, fuente = _dist_desde_npm(a.scope, a.version, tmp)
        else:
            dists, fuente = _dist_desde_clon(a.fuente)
        version = json.load(open(os.path.join(dists["ui"], "package.json"), encoding="utf-8"))["version"]
        os.makedirs(destino, exist_ok=True)
        copiados, avisos = {}, []
        for nombre, (paq, rel) in ARCHIVOS.items():
            origen = os.path.join(dists[paq], "dist", rel)
            if os.path.exists(origen):
                shutil.copyfile(origen, os.path.join(destino, nombre))
                copiados[nombre] = sha256(os.path.join(destino, nombre))
        if "faast-kit.css" not in copiados:
            with open(os.path.join(destino, "faast-kit.css"), "w", encoding="utf-8") as f:
                f.write(_componer_kit_css(dists))
            copiados["faast-kit.css"] = sha256(os.path.join(destino, "faast-kit.css"))
            avisos.append(f"La libreria {version} es anterior a {'.'.join(map(str, MIN_KIT))}: no trae "
                          "markup.json ni catalogo.html. Use la hoja compuesta y el Storybook como "
                          "referencia de markup, y pida publicar una version con kit.")
        for falta in ("tokens.json", "themes.json"):
            if falta not in copiados and version_tupla(version) >= MIN_KIT:
                avisos.append(f"No se encontro {falta} en la libreria {version}.")
    manifiesto = {
        "libreria": f"{a.scope}/ui", "version": version, "fuente": fuente,
        "obtenido": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "archivos": copiados, "avisos": avisos,
    }
    with open(os.path.join(destino, "LIBRERIA.json"), "w", encoding="utf-8") as f:
        json.dump(manifiesto, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Kit de la libreria {manifiesto['libreria']} {version} en {destino}")
    print("  fuente: " + json.dumps(fuente, ensure_ascii=False))
    for n in copiados:
        print(f"  - {n}")
    for av in avisos:
        print(f"  AVISO: {av}")
    if fuente.get("sucio"):
        print("  AVISO: el clon tiene cambios sin commitear; la propuesta no es reproducible desde un commit.")


# ---------------------------------------------------------------- verificar

RE_STYLE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S | re.I)
RE_LINK = re.compile(r"<link\b[^>]*rel=[\"']?stylesheet[\"']?[^>]*>", re.I)
RE_HREF = re.compile(r"href=[\"']([^\"']+)[\"']", re.I)
RE_ATTR_STYLE = re.compile(r"\sstyle=\"([^\"]*)\"|\sstyle='([^']*)'", re.I)
RE_CLASS = re.compile(r"\sclass=\"([^\"]*)\"|\sclass='([^']*)'", re.I)
RE_COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgb|rgba|hsl|hsla|oklch|oklab|lab|lch|color)\([^)]*\)")
RE_VAR_USO = re.compile(r"var\(\s*(--faast-[a-z0-9-]+)")
RE_VAR_DEF = re.compile(r"(--faast-[a-z0-9-]+)\s*:")
RE_COMENT = re.compile(r"/\*.*?\*/", re.S)
RE_SVG = re.compile(r"<svg\b.*?</svg>", re.S | re.I)
RE_SCRIPT = re.compile(r"<script\b.*?</script>", re.S | re.I)
RE_FONT = re.compile(r"font-family\s*:\s*([^;}\"']+)", re.I)
RE_FONT_PX = re.compile(r"font-size\s*:\s*\d+(?:\.\d+)?px", re.I)
RE_FUENTE_EXT = re.compile(r"fonts\.googleapis\.com|fonts\.gstatic\.com|use\.typekit\.net|@import\s+url", re.I)


def _kit(dir_kit):
    ruta = os.path.join(dir_kit, "faast-kit.css")
    if not os.path.exists(ruta):
        fallar(f"no hay faast-kit.css en {dir_kit}. Corre primero: kit_libreria.py obtener --destino {dir_kit}")
    css = open(ruta, encoding="utf-8").read()
    clases = set(re.findall(r"\.(faast-[A-Za-z0-9_-]+)", css))
    variables = set(RE_VAR_DEF.findall(css))
    # Los componentes emiten clases sin regla propia (modificadores por defecto, ganchos):
    # tambien son de la libreria si aparecen en su markup real.
    try:
        markup = open(os.path.join(dir_kit, "markup.json"), encoding="utf-8").read()
        clases.update(re.findall(r"\b(faast-[A-Za-z0-9_-]+)", markup))
    except FileNotFoundError:
        pass
    manifiesto = {}
    try:
        manifiesto = json.load(open(os.path.join(dir_kit, "LIBRERIA.json"), encoding="utf-8"))
    except Exception:
        pass
    return css, clases, variables, manifiesto


def _linea(texto, pos):
    return texto.count("\n", 0, pos) + 1


def verificar_html(ruta, dir_kit, css_kit, clases_kit, vars_kit):
    html = open(ruta, encoding="utf-8", errors="replace").read()
    errores, avisos = [], []

    def err(codigo, msg):
        errores.append({"codigo": codigo, "detalle": msg})

    def av(codigo, msg):
        avisos.append({"codigo": codigo, "detalle": msg})

    # 1. La hoja del kit esta enlazada o incrustada
    enlazada = any("faast-kit.css" in (RE_HREF.search(l).group(1) if RE_HREF.search(l) else "")
                   for l in RE_LINK.findall(html))
    estilos = RE_STYLE.findall(html)
    incrustada = any(MARCA_KIT in s or "faast-kit.css compuesto" in s for s in estilos)
    if not (enlazada or incrustada):
        err("sin-kit", "la pagina no enlaza ni incrusta faast-kit.css: no hereda de la libreria")
    for l in RE_LINK.findall(html):
        m = RE_HREF.search(l)
        if m and "faast-kit.css" in m.group(1) and not re.match(r"^[a-z]+://", m.group(1)):
            destino = os.path.normpath(os.path.join(os.path.dirname(ruta), m.group(1).split("?")[0]))
            if not os.path.exists(destino):
                err("kit-roto", f"el enlace {m.group(1)} no existe en disco")
            elif os.path.exists(os.path.join(dir_kit, "faast-kit.css")) and \
                    sha256(destino) != sha256(os.path.join(dir_kit, "faast-kit.css")):
                err("kit-alterado", f"{m.group(1)} no es identico al kit obtenido (editado o de otra version)")

    # CSS propio de la pagina = <style> que no son el kit + atributos style
    propio = [s for s in estilos if MARCA_KIT not in s and "faast-kit.css compuesto" not in s]
    css_propio = RE_COMENT.sub("", "\n".join(propio))
    cuerpo = RE_SCRIPT.sub("", RE_SVG.sub("", RE_STYLE.sub("", html)))
    inline = "\n".join((a or b) for a, b in RE_ATTR_STYLE.findall(cuerpo))

    # 2. Cero colores literales fuera de la libreria (los SVG de ilustracion se revisan aparte)
    colores = [m.group(0) for m in RE_COLOR.finditer(css_propio + "\n" + inline)
               if not m.group(0).startswith("color(") or "var(" not in m.group(0)]
    colores = [c for c in colores if "var(--faast-" not in c]  # rgb(from var(...)) / color-mix
    if colores:
        unicos = sorted(set(colores))
        err("color-literal", f"{len(colores)} color(es) literal(es) en el CSS propio "
            f"({', '.join(unicos[:8])}{'…' if len(unicos) > 8 else ''}): usa los roles var(--faast-*)")
    svg_colores = set()
    for svg in RE_SVG.findall(RE_STYLE.sub("", html)):
        svg_colores.update(re.findall(r"(?:fill|stroke|stop-color)=\"(#[0-9a-fA-F]{3,8})\"", svg))
    if svg_colores:
        av("svg-color", f"{len(svg_colores)} color(es) fijo(s) en SVG ({', '.join(sorted(svg_colores)[:6])}): "
           "en iconos e ilustraciones de interfaz usa currentColor o var(--faast-*) para que sigan el tema")

    # 3. Tipografia: solo la de la libreria
    for m in RE_FONT.finditer(css_propio + "\n" + inline):
        valor = m.group(1).strip()
        if "var(--faast-font-" not in valor and valor not in ("inherit", "initial", "unset"):
            err("fuente-literal", f"font-family literal «{valor[:60]}»: usa var(--faast-font-sans|mono)")
    if RE_FUENTE_EXT.search(css_propio) or re.search(r"<link[^>]+fonts\.googleapis", html, re.I):
        err("fuente-externa", "la pagina carga fuentes externas: la tipografia es la de la libreria")
    px = RE_FONT_PX.findall(css_propio + "\n" + inline)
    if px:
        av("tamano-px", f"{len(px)} font-size en px: usa la escala var(--faast-font-size-*)")

    # 4. Clases y variables faast-* que la libreria no define (inventadas o de otra version)
    usadas = set()
    for a, b in RE_CLASS.findall(cuerpo):
        usadas.update(c for c in (a or b).split() if c.startswith("faast-"))
    inventadas = sorted(usadas - clases_kit)
    if inventadas:
        err("clase-inventada", f"clases faast-* que la libreria no define: {', '.join(inventadas[:12])}"
            f"{'…' if len(inventadas) > 12 else ''} — copia el markup de markup.json")
    redefinidas = sorted(set(re.findall(r"\.(faast-[A-Za-z0-9_-]+)", css_propio)))
    if redefinidas:
        err("clase-redefinida", f"el CSS propio redefine clases de la libreria: {', '.join(redefinidas[:10])} — "
            "si un componente no alcanza, se marca como «nuevo para la libreria», no se parcha")
    vars_usadas = set(RE_VAR_USO.findall(css_propio + "\n" + inline))
    vars_locales = set(RE_VAR_DEF.findall(css_propio + "\n" + inline))
    desconocidas = sorted(vars_usadas - vars_kit - vars_locales)
    if desconocidas:
        err("variable-inexistente", f"variables que la libreria no define: {', '.join(desconocidas[:12])}")
    pisadas = sorted(vars_locales & vars_kit)
    if pisadas:
        err("variable-pisada", f"el CSS propio redefine variables de la libreria: {', '.join(pisadas[:10])} — "
            "un tema de cliente se genera con createTenantTheme de @faast-app/themes, no a mano")
    if not usadas and not vars_usadas:
        av("sin-uso", "la pagina no usa ninguna clase ni variable de la libreria")

    # 5. Tema y base
    if not re.search(r"<html[^>]*\slang=", html, re.I):
        av("sin-lang", "<html> sin atributo lang")
    if "prefers-reduced-motion" not in css_propio and re.search(r"animation|transition", css_propio):
        av("reduced-motion", "hay animaciones propias sin @media (prefers-reduced-motion: reduce)")

    return {"archivo": ruta, "ok": not errores, "errores": errores, "avisos": avisos,
            "componentes": sorted({c.split("--")[0].split("__")[0] for c in usadas & clases_kit})}


def cmd_verificar(a):
    css, clases, variables, manifiesto = _kit(a.kit)
    resultados = [verificar_html(h, a.kit, css, clases, variables) for h in a.html]
    if a.json:
        print(json.dumps({"libreria": manifiesto.get("version"), "resultados": resultados},
                         ensure_ascii=False, indent=2))
    else:
        print(f"Libreria: {manifiesto.get('libreria', '@faast-app/ui')} {manifiesto.get('version', '?')}")
        for r in resultados:
            print(f"\n{'OK   ' if r['ok'] else 'FALLA'} {r['archivo']}")
            if r["componentes"]:
                print("  componentes de la libreria usados: " + ", ".join(r["componentes"]))
            for e in r["errores"]:
                print(f"  ERROR [{e['codigo']}] {e['detalle']}")
            for w in r["avisos"]:
                print(f"  aviso [{w['codigo']}] {w['detalle']}")
        malos = sum(1 for r in resultados if not r["ok"])
        print(f"\nHERENCIA: {'PASA' if not malos else 'FALLA'} ({len(resultados) - malos}/{len(resultados)} archivos)")
    sys.exit(1 if any(not r["ok"] for r in resultados) else 0)


# ---------------------------------------------------------------- incrustar

def cmd_incrustar(a):
    css, *_ = _kit(a.kit)
    html = open(a.html, encoding="utf-8").read()
    hechos = 0

    def reemplazo(m):
        nonlocal hechos
        href = RE_HREF.search(m.group(0))
        if href and "faast-kit.css" in href.group(1):
            hechos += 1
            return "<style>\n" + css.replace("</style", "<\\/style") + "\n</style>"
        return m.group(0)

    salida = RE_LINK.sub(reemplazo, html)
    if not hechos:
        fallar(f"{a.html} no enlaza faast-kit.css (nada que incrustar)")
    destino = a.salida or re.sub(r"\.html?$", "", a.html) + ".autocontenido.html"
    with open(destino, "w", encoding="utf-8") as f:
        f.write(salida)
    print(f"{destino} ({os.path.getsize(destino) // 1024} kB, kit incrustado)")


# ---------------------------------------------------------------- roles

def _hex(valor, primitivos):
    if isinstance(valor, str) and valor.startswith("{"):
        nodo = primitivos
        for parte in valor.strip("{}").split("."):
            nodo = nodo.get(parte, {}) if isinstance(nodo, dict) else {}
        return _hex(nodo.get("$value"), primitivos) if isinstance(nodo, dict) else "?"
    if isinstance(valor, dict) and "hex" in valor:
        return valor["hex"] + (f" / {valor['alpha']}" if "alpha" in valor else "")
    return "(sombra)" if isinstance(valor, list) else str(valor)


def _kebab(s):
    return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s).lower()


def cmd_roles(a):
    try:
        primitivos = json.load(open(os.path.join(a.kit, "tokens.json"), encoding="utf-8"))
        temas = json.load(open(os.path.join(a.kit, "themes.json"), encoding="utf-8"))
    except FileNotFoundError as e:
        fallar(f"falta {os.path.basename(e.filename)} en {a.kit} (la libreria debe ser >= 0.8.0)")
    filas = []

    def andar(claro, oscuro, ruta):
        for clave, nodo in claro.items():
            if clave.startswith("$"):
                continue
            if isinstance(nodo, dict) and "$value" in nodo:
                otro = (oscuro.get(clave) or {}).get("$value")
                var = "--faast-" + "-".join(_kebab(p) for p in ruta + [clave])
                ref = nodo["$value"] if isinstance(nodo["$value"], str) else ""
                filas.append((var, _hex(nodo["$value"], primitivos), _hex(otro, primitivos), ref))
            elif isinstance(nodo, dict):
                andar(nodo, oscuro.get(clave, {}), ruta + [clave])

    andar(temas["light"], temas["dark"], [])
    print("| Rol (variable CSS) | Claro | Oscuro | Primitivo (claro) |")
    print("| --- | --- | --- | --- |")
    for var, c, o, ref in filas:
        print(f"| `{var}` | {c} | {o} | {ref.strip('{}')} |")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("obtener")
    o.add_argument("--destino", required=True)
    o.add_argument("--version", default="latest")
    o.add_argument("--fuente", default="npm", help="npm (default) o la ruta a un clon compilado de la libreria")
    o.add_argument("--scope", default="@faast-app")
    o.set_defaults(fn=cmd_obtener)
    v = sub.add_parser("verificar")
    v.add_argument("html", nargs="+")
    v.add_argument("--kit", required=True)
    v.add_argument("--json", action="store_true")
    v.set_defaults(fn=cmd_verificar)
    i = sub.add_parser("incrustar")
    i.add_argument("html")
    i.add_argument("--kit", required=True)
    i.add_argument("-o", "--salida")
    i.set_defaults(fn=cmd_incrustar)
    r = sub.add_parser("roles")
    r.add_argument("--kit", required=True)
    r.set_defaults(fn=cmd_roles)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
