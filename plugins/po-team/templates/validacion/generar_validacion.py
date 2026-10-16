#!/usr/bin/env python3
# po-team — genera el informe de validaciones: inyecta validacion-datos.json en la plantilla validacion.html.
# Uso: python3 generar_validacion.py {validacion-datos.json} {salida.html} [plantilla.html]
# Valida el JSON, quita la marca de "ejemplo" y escapa "</" para que no cierre el bloque script.
# Las rutas de evidencia (capturas/videos) quedan relativas a la carpeta del HTML: al publicar como
# artifact se suben con `files` (ver skill validacion-funcional-po).
import json, os, re, sys

ESTADOS = {"ok", "warn", "alert", "block", "pend", "na", "pr", "wait"}

def main():
    if len(sys.argv) < 3:
        print("uso: generar_validacion.py {datos.json} {salida.html} [plantilla.html]", file=sys.stderr)
        return 2
    datos_path, salida = sys.argv[1], sys.argv[2]
    plantilla = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "validacion.html")
    with open(datos_path, encoding="utf-8") as f:
        datos = json.load(f)                      # falla aqui si el JSON es invalido
    if "grupos" not in datos:
        print("aviso: falta la clave 'grupos' en los datos", file=sys.stderr)
    base = os.path.dirname(os.path.abspath(salida))
    faltan = []
    for g in datos.get("grupos", []):
        for it in g.get("items", []):
            if it.get("estado") not in ESTADOS:
                print(f"aviso: #{it.get('numero')} tiene estado '{it.get('estado')}' (usar {sorted(ESTADOS)})", file=sys.stderr)
            for e in it.get("evidencia", []):
                if not re.match(r"^(https?:|data:)", e.get("archivo", "")) and not os.path.exists(os.path.join(base, e.get("archivo", ""))):
                    faltan.append(e.get("archivo"))
    if faltan:
        print(f"aviso: {len(faltan)} archivo(s) de evidencia no estan junto al HTML: {faltan[:5]}", file=sys.stderr)
    datos.pop("ejemplo", None)
    bloque = json.dumps(datos, ensure_ascii=False, indent=1).replace("</", "<\\/")
    with open(plantilla, encoding="utf-8") as f:
        html = f.read()
    patron = re.compile(r'(<script id="datos" type="application/json">)(.*?)(</script>)', re.S)
    if len(patron.findall(html)) != 1:
        print("error: la plantilla debe tener exactamente un bloque script id=datos", file=sys.stderr)
        return 1
    html = patron.sub(lambda m: m.group(1) + "\n" + bloque + "\n" + m.group(3), html)
    os.makedirs(base, exist_ok=True)
    with open(salida, "w", encoding="utf-8") as f:
        f.write(html)
    n = sum(len(g.get("items", [])) for g in datos.get("grupos", []))
    ev = sum(len(it.get("evidencia", [])) for g in datos.get("grupos", []) for it in g.get("items", []))
    print(f"ok: {salida} ({n} tickets, {ev} archivos de evidencia)")
    return 0

sys.exit(main())
