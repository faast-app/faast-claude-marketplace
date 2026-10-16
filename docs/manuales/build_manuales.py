#!/usr/bin/env python3
"""Genera los PDF de los manuales de usuario de FaaST con el estilo de marca.

Uso (desde la raiz del repo):
  python3 docs/manuales/build_manuales.py            # todos los manuales
  python3 docs/manuales/build_manuales.py dev-team   # uno (clave de MANUALES)

Requisitos: pandoc, node y playwright-core (con su Chromium instalado). Si playwright-core no se
resuelve solo, exporta PLAYWRIGHT_CORE=/ruta/a/node_modules/playwright-core. Los HTML intermedios
van a una carpeta temporal fuera del repo; en el repo solo quedan los .md y los .pdf.
"""
import base64
import datetime
import glob
import html as html_lib
import os
import re
import subprocess
import sys
import tempfile

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AQUI = os.path.dirname(os.path.abspath(__file__))
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]

MANUALES = {
    "general": dict(md="GUIDE.md", pdf="GUIDE.pdf", etiqueta="Manual general",
                    titulo="Los equipos de agentes de FaaST",
                    subtitulo="Que hace cada equipo, como se instalan y como trabajan juntos: de lo que pide el cliente a un producto construido, probado, publicado y listo para vender.",
                    plugin=None),
    "dev-team": dict(md="plugins/dev-team/GUIDE.md", pdf="plugins/dev-team/GUIDE.pdf", etiqueta="Manual de usuario",
                     titulo="Dev Team",
                     subtitulo="El equipo que diseña, construye, prueba, asegura y publica tus productos, paso a paso y en lenguaje de negocio.",
                     plugin="plugins/dev-team"),
    "mesa-servicios": dict(md="plugins/mesa-servicios/GUIDE.md", pdf="plugins/mesa-servicios/GUIDE.pdf", etiqueta="Manual de usuario",
                           titulo="Mesa de Servicios",
                           subtitulo="El equipo que recibe todo lo que pide el cliente y lo convierte en un requerimiento cerrado, documentado y registrado.",
                           plugin="plugins/mesa-servicios"),
    "marketing": dict(md="plugins/marketing/GUIDE.md", pdf="plugins/marketing/GUIDE.pdf", etiqueta="Manual de usuario",
                      titulo="Marketing, Ventas y Publicidad",
                      subtitulo="El equipo que vende tus productos desglosados parte por parte: investigacion, propuesta comercial, presentaciones y video de lanzamiento.",
                      plugin="plugins/marketing"),
}


def version(plugin):
    if not plugin:
        return None
    try:
        import json
        return json.load(open(os.path.join(RAIZ, plugin, ".claude-plugin", "plugin.json"), encoding="utf-8")).get("version")
    except Exception:
        return None


def data_uri(nombre):
    with open(os.path.join(AQUI, "assets", nombre), "rb") as f:
        return "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode()


def playwright_core():
    if os.environ.get("PLAYWRIGHT_CORE"):
        return os.environ["PLAYWRIGHT_CORE"]
    cands = sorted(glob.glob(os.path.expanduser("~/.npm/_npx/*/node_modules/playwright-core/package.json")),
                   key=os.path.getmtime, reverse=True)
    return os.path.dirname(cands[0]) if cands else ""


CAJA = re.compile("[\u2500-\u257f\u25bc\u25b2\u25ba\u25c4]")  # dibujo de cajas y flechas de diagrama
ANCHO_PT = 470  # ancho util del bloque en puntos (A4 con margenes y relleno)


def diagrama(m):
    """Los diagramas dibujados con caracteres no se ajustan (se desarmarian): van en una linea por
    fila, con la letra reducida lo justo para que la fila mas larga entre completa."""
    apertura, codigo = m.group(1), m.group(2)
    texto = html_lib.unescape(re.sub(r"<[^>]+>", "", codigo))
    if not CAJA.search(texto):
        return m.group(0)
    largo = max((len(l) for l in texto.split("\n")), default=1)
    tam = max(5.4, min(8.8, ANCHO_PT / (0.6 * largo)))
    return (f'<pre class="diagrama" style="white-space:pre;overflow:hidden">'
            f'{apertura.replace("<code", f"<code style=\'font-size:{tam:.2f}pt;line-height:1.35\'", 1)}'
            f'{codigo}</code></pre>')


def construir(clave, tmp):
    m = MANUALES[clave]
    md = os.path.join(RAIZ, m["md"])
    if not os.path.exists(md):
        print(f"- {clave}: no existe {m['md']}, se omite")
        return
    cuerpo = subprocess.run(["pandoc", md, "-f", "gfm", "-t", "html5", "--no-highlight"],
                            capture_output=True, text=True, check=True).stdout
    # el primer H1 del .md es el titulo: ya va en la portada
    cuerpo = re.sub(r"^\s*<h1[^>]*>.*?</h1>", "", cuerpo, count=1, flags=re.S)
    cuerpo = re.sub(r'<pre class="mermaid"><code>(.*?)</code></pre>',
                    lambda m: f'<div class="diagrama-mermaid"><pre class="mermaid">{m.group(1)}</pre></div>',
                    cuerpo, flags=re.S)
    cuerpo = re.sub(r"<pre>(<code[^>]*>)(.*?)</code></pre>", diagrama, cuerpo, flags=re.S)
    hoy = datetime.date.today()
    fecha = f"{hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}"
    v = version(m["plugin"])
    meta_izq = f"<b>Versión {v}</b>" if v else "<b>Marketplace FaaST</b>"
    css = open(os.path.join(AQUI, "manual.css"), encoding="utf-8").read()
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>FaaST — {m['titulo']}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<section class="portada">
  <div class="franja"></div>
  <img class="logo" src="{data_uri('faast-logo-oscuro.svg')}" alt="FaaST">
  <img class="isotipo-fondo" src="{data_uri('faast-isotipo.svg')}" alt="">
  <div class="etiqueta">{m['etiqueta']}</div>
  <h1 class="titulo">{m['titulo']}</h1>
  <div class="subtitulo">{m['subtitulo']}</div>
  <div class="meta"><span>{meta_izq}</span><span>{fecha}</span><span>faast.app</span></div>
</section>
<main class="contenido">{cuerpo}</main>
<script type="module">
  const bloques = document.querySelectorAll("pre.mermaid");
  if (!bloques.length) {{ window.__diagramasListos = true; }}
  else {{
    try {{
      const {{ default: mermaid }} = await import("https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs");
      mermaid.initialize({{
        startOnLoad: false, theme: "base", securityLevel: "strict",
        flowchart: {{ curve: "basis", htmlLabels: true, nodeSpacing: 34, rankSpacing: 46, padding: 14 }},
        themeVariables: {{
          fontFamily: "Lato, Helvetica, Arial, sans-serif", fontSize: "16px",
          primaryColor: "#f1f7e9", primaryBorderColor: "#71af26", primaryTextColor: "#151515",
          secondaryColor: "#151515", secondaryTextColor: "#ffffff", secondaryBorderColor: "#151515",
          tertiaryColor: "#ffffff", tertiaryBorderColor: "#dfe3da",
          lineColor: "#4a4f45", textColor: "#151515", clusterBkg: "#fafbf8", clusterBorder: "#d5e8bd",
          edgeLabelBackground: "#ffffff", noteBkgColor: "#f1f7e9", noteBorderColor: "#71af26"
        }}
      }});
      await mermaid.run({{ nodes: bloques }});
    }} catch (e) {{ console.error("mermaid", e); }}
    window.__diagramasListos = true;
  }}
</script>
</body></html>"""
    ruta_html = os.path.join(tmp, f"{clave}.html")
    open(ruta_html, "w", encoding="utf-8").write(html)
    pdf = os.path.join(RAIZ, m["pdf"])
    env = dict(os.environ, PLAYWRIGHT_CORE=playwright_core())
    subprocess.run(["node", os.path.join(AQUI, "render-pdf.mjs"), ruta_html, pdf,
                    f"FaaST · {m['titulo']} — {m['etiqueta']}"], check=True, env=env)


def main():
    claves = sys.argv[1:] or list(MANUALES)
    with tempfile.TemporaryDirectory(prefix="manuales-faast-") as tmp:
        for c in claves:
            if c not in MANUALES:
                print(f"clave desconocida: {c} (opciones: {', '.join(MANUALES)})")
                return 1
            construir(c, tmp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
