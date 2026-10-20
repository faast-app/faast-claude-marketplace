#!/usr/bin/env python3
"""Marca en una captura de pantalla dónde ocurre el cambio: recuadro, flecha y rótulo.

Uso:
    python anotar_captura.py entrada.png salida.png \
        --marca "x1,y1,x2,y2|1|Botón Calcular" \
        --marca "x1,y1,x2,y2|2|Campo Monto neto"

Cada --marca es: coordenadas del recuadro en píxeles | número | texto del rótulo [| posición].
La flecha sale del rótulo hacia el recuadro. El rótulo se ubica a la derecha si cabe,
si no a la izquierda, arriba o abajo; con el cuarto campo (derecha, izquierda, arriba,
abajo) se fuerza la posición cuando el rótulo tapa algo relevante.
Para obtener las coordenadas: ver la imagen y estimar el recuadro del elemento,
luego revisar la salida y ajustar si quedó desplazado.
"""
import argparse
import math
import sys

from PIL import Image, ImageDraw, ImageFont

COLOR = (220, 38, 38)
FONDO = (255, 255, 255)


def fuente(tam):
    for nombre in ["DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"]:
        try:
            return ImageFont.truetype(nombre, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def flecha(d, p0, p1, ancho):
    d.line([p0, p1], fill=COLOR, width=ancho)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    largo = ancho * 5
    for s in (-1, 1):
        a = ang + math.pi - s * math.radians(28)
        d.line([p1, (p1[0] + largo * math.cos(a), p1[1] + largo * math.sin(a))],
               fill=COLOR, width=ancho)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida")
    ap.add_argument("--marca", action="append", required=True)
    a = ap.parse_args()

    img = Image.open(a.entrada).convert("RGB")
    W, H = img.size
    esc = max(1, round(min(W, H) / 600))
    ancho = 3 * esc
    f = fuente(16 * esc)
    d = ImageDraw.Draw(img)

    for m in a.marca:
        coords, num, texto, pos = (m.split("|") + ["", "", ""])[:4]
        x1, y1, x2, y2 = [int(float(v)) for v in coords.split(",")]
        pad = 4 * esc
        d.rectangle([x1 - pad, y1 - pad, x2 + pad, y2 + pad], outline=COLOR, width=ancho)

        rotulo = f"{num}. {texto}".strip(". ") if texto else str(num)
        tb = d.textbbox((0, 0), rotulo, font=f)
        tw, th = tb[2] - tb[0] + 12 * esc, tb[3] - tb[1] + 10 * esc
        sep = 40 * esc
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        opciones = [
            ("derecha", x2 + pad + sep, cy - th / 2, (x2 + pad, cy)),
            ("izquierda", x1 - pad - sep - tw, cy - th / 2, (x1 - pad, cy)),
            ("arriba", cx - tw / 2, y1 - pad - sep - th, (cx, y1 - pad)),
            ("abajo", cx - tw / 2, y2 + pad + sep, (cx, y2 + pad)),
        ]
        if pos.strip():
            opciones.sort(key=lambda o: o[0] != pos.strip().lower())
        elegido = None
        for _nombre, lx, ly, punta in opciones:
            if 0 <= lx and lx + tw <= W and 0 <= ly and ly + th <= H:
                elegido = (lx, ly, punta)
                break
        if not elegido:
            lx = min(max(0, cx - tw / 2), W - tw)
            ly = min(max(0, y2 + pad + sep), H - th)
            elegido = (lx, ly, (cx, y2 + pad))
        lx, ly, punta = elegido
        d.rectangle([lx, ly, lx + tw, ly + th], fill=FONDO, outline=COLOR, width=ancho)
        d.text((lx + 6 * esc, ly + 3 * esc), rotulo, fill=COLOR, font=f)
        origen = (min(max(punta[0], lx), lx + tw), min(max(punta[1], ly), ly + th))
        if math.dist(origen, punta) > ancho * 4:
            flecha(d, origen, punta, ancho)

    img.save(a.salida)
    print(f"Imagen anotada: {a.salida} ({W}×{H}, {len(a.marca)} marca(s))")


if __name__ == "__main__":
    sys.exit(main())
