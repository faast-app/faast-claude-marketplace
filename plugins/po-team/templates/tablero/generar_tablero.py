#!/usr/bin/env python3
# po-team — genera el dashboard del PO: inyecta tablero-datos.json en la plantilla tablero.html.
# Uso: python3 generar_tablero.py {tablero-datos.json} {salida.html} [plantilla.html]
# Valida el JSON, quita la marca de "ejemplo" y escapa "</" para que no cierre el bloque script.
import json, os, re, sys

def main():
    if len(sys.argv) < 3:
        print("uso: generar_tablero.py {datos.json} {salida.html} [plantilla.html]", file=sys.stderr)
        return 2
    datos_path, salida = sys.argv[1], sys.argv[2]
    plantilla = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "tablero.html")
    with open(datos_path, encoding="utf-8") as f:
        datos = json.load(f)                      # falla aqui si el JSON es invalido
    for clave in ("sprints", "etapas"):
        if clave not in datos:
            print(f"aviso: falta la clave '{clave}' en los datos", file=sys.stderr)
    datos.pop("ejemplo", None)
    bloque = json.dumps(datos, ensure_ascii=False, indent=1).replace("</", "<\\/")
    with open(plantilla, encoding="utf-8") as f:
        html = f.read()
    patron = re.compile(r'(<script id="datos" type="application/json">)(.*?)(</script>)', re.S)
    if len(patron.findall(html)) != 1:
        print("error: la plantilla debe tener exactamente un bloque script id=datos", file=sys.stderr)
        return 1
    html = patron.sub(lambda m: m.group(1) + "\n" + bloque + "\n" + m.group(3), html)
    os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)
    with open(salida, "w", encoding="utf-8") as f:
        f.write(html)
    n = sum(len(s.get("tickets", [])) for s in datos.get("sprints", []))
    print(f"ok: {salida} ({len(datos.get('sprints', []))} sprints, {n} tickets)")
    return 0

sys.exit(main())
