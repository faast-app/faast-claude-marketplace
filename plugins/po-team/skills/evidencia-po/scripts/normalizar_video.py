#!/usr/bin/env python3
"""Verifica y normaliza los videos de evidencia grabados con el Playwright MCP.

Problema que resuelve: Playwright comparte UNA captura de pantalla por pagina. Si la traza
(browser_start_tracing) arranca antes que el video, o si hubo una traza antes en la misma sesion
del navegador, la captura queda fijada en 800 px (p. ej. 800x500 para un viewport de 1440x900) y el
video la pega en la esquina superior izquierda de un lienzo mas grande relleno de gris. El archivo
"mide" 1440x900 pero la pantalla se ve chica.

Que hace, por cada .webm:
  1. Detecta el relleno gris a la derecha y abajo (muestrea varios cuadros).
  2. Genera {nombre}.mp4 (H.264, se abre en QuickTime, Teams, navegador y GitHub). Si habia relleno,
     recorta la zona real y la escala al tamano del lienzo (queda menos nitido que una grabacion
     correcta, pero ocupa toda la pantalla) y lo informa como REPARADO.
  3. Genera {nombre}-portada.png (cuadro central) para embeber en el tracker con link al video.
  El .webm original NO se modifica (la evidencia cruda es inmutable).

Uso:
  python3 normalizar_video.py video.webm [otro.webm ...]       # verifica + mp4 + portada
  python3 normalizar_video.py carpeta/                         # todos los .webm de la carpeta
  python3 normalizar_video.py --verificar video.webm           # solo verifica (no escribe nada)

Salida: una linea por video con OK / RELLENO / REPARADO y un resumen JSON.
Codigo de salida: 0 si ningun video tenia relleno, 2 si alguno lo tenia (aunque se haya reparado),
1 si hubo un error (ffmpeg ausente, archivo ilegible).

Requiere ffmpeg y ffprobe en el PATH (Playwright ya los usa). Solo libreria estandar de Python.
"""
import json
import os
import shutil
import subprocess
import sys

TOLERANCIA = 6          # diferencia maxima de luminancia para considerar un pixel "gris de relleno"
MUESTRAS = 6            # cuadros a analizar por video
MARGEN_MINIMO = 8       # px de relleno minimos para considerarlo relleno real


def ejecutar(cmd, binario=False):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        raise RuntimeError(f"{cmd[0]} fallo: {r.stderr.decode(errors='replace')[-400:]}")
    return r.stdout if binario else r.stdout.decode()


def info(video):
    out = ejecutar(["ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=width,height:format=duration",
                    "-of", "json", video])
    d = json.loads(out)
    w = int(d["streams"][0]["width"])
    h = int(d["streams"][0]["height"])
    dur = float(d.get("format", {}).get("duration") or 0)
    return w, h, dur


def cuadro_gris(video, t, w, h):
    raw = ejecutar(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1",
                    "-f", "rawvideo", "-pix_fmt", "gray", "-"], binario=True)
    return raw if len(raw) == w * h else None


def es_relleno(valores, ref):
    return max(valores) - ref <= TOLERANCIA and ref - min(valores) <= TOLERANCIA


def contenido_en_cuadro(frame, w, h):
    """Devuelve (ancho, alto) de la zona con contenido, o None si la esquina no es gris uniforme."""
    ref = frame[(h - 1) * w + (w - 1)]
    if not (110 <= ref <= 146):
        return None
    ancho = 0
    for x in range(w - 1, -1, -1):
        if not es_relleno(frame[x::w], ref):
            ancho = x + 1
            break
    alto = 0
    for y in range(h - 1, -1, -1):
        if not es_relleno(frame[y * w:(y + 1) * w], ref):
            alto = y + 1
            break
    return ancho, alto


def analizar(video):
    w, h, dur = info(video)
    tiempos = [dur * (i + 1) / (MUESTRAS + 1) for i in range(MUESTRAS)] if dur > 0 else [0]
    anchos, altos, validos = [], [], 0
    for t in tiempos:
        f = cuadro_gris(video, t, w, h)
        if f is None:
            continue
        validos += 1
        c = contenido_en_cuadro(f, w, h)
        if c is None:
            return {"w": w, "h": h, "dur": dur, "relleno": False}
        anchos.append(c[0])
        altos.append(c[1])
    if not validos or not anchos:
        return {"w": w, "h": h, "dur": dur, "relleno": False}
    cw, ch = max(anchos), max(altos)
    cw, ch = cw + (cw % 2), ch + (ch % 2)
    relleno = cw > 0 and ch > 0 and (w - cw >= MARGEN_MINIMO or h - ch >= MARGEN_MINIMO)
    return {"w": w, "h": h, "dur": dur, "relleno": relleno, "contenido": [cw, ch]}


def normalizar(video, a):
    base, _ = os.path.splitext(video)
    mp4, portada = base + ".mp4", base + "-portada.png"
    if a["relleno"]:
        cw, ch = a["contenido"]
        vf = f"crop={cw}:{ch}:0:0,scale={a['w']}:{a['h']}:flags=lanczos"
    else:
        vf = f"scale={a['w']}:{a['h']}"
    ejecutar(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", vf + ",format=yuv420p",
              "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-tune", "stillimage",
              "-movflags", "+faststart", "-an", mp4])
    t = a["dur"] / 2 if a["dur"] else 0
    ejecutar(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", mp4, "-frames:v", "1", portada])
    return mp4, portada


def videos_de(args):
    for p in args:
        if os.path.isdir(p):
            for n in sorted(os.listdir(p)):
                if n.lower().endswith(".webm"):
                    yield os.path.join(p, n)
        else:
            yield p


def main():
    args = sys.argv[1:]
    solo_verificar = "--verificar" in args
    args = [x for x in args if x != "--verificar"]
    if not args:
        print(__doc__)
        return 1
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("ERROR: ffmpeg/ffprobe no estan en el PATH")
        return 1
    resumen, hubo_relleno, hubo_error = [], False, False
    for v in videos_de(args):
        try:
            a = analizar(v)
            fila = {"video": v, "tamano": f"{a['w']}x{a['h']}", "duracion_s": round(a["dur"], 1)}
            if a["relleno"]:
                hubo_relleno = True
                cw, ch = a["contenido"]
                fila["contenido_real"] = f"{cw}x{ch}"
            if solo_verificar:
                fila["estado"] = "RELLENO" if a["relleno"] else "OK"
            else:
                mp4, portada = normalizar(v, a)
                fila.update({"estado": "REPARADO" if a["relleno"] else "OK", "mp4": mp4, "portada": portada})
            msg = f"{fila['estado']:9} {v} · {fila['tamano']} · {fila['duracion_s']} s"
            if a["relleno"]:
                msg += (f" · la pantalla real ocupaba solo {fila['contenido_real']} (relleno gris: la traza "
                        f"arranco antes que el video o hubo una traza previa en la sesion)")
            print(msg)
            resumen.append(fila)
        except Exception as e:  # noqa: BLE001 - se informa y se sigue con el resto
            hubo_error = True
            print(f"ERROR     {v} · {e}")
            resumen.append({"video": v, "estado": "ERROR", "detalle": str(e)})
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    if hubo_error:
        return 1
    return 2 if hubo_relleno else 0


if __name__ == "__main__":
    sys.exit(main())
