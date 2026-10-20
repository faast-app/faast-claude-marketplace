#!/usr/bin/env python3
"""QA de entrega de los videos del equipo de Marketing (keynote, clips por parte, teaser, redes).

Verifica cada render contra su especificacion y deja material para revisar cuadro a cuadro:
  1. ffprobe: contenedor, codec, resolucion, fps, duracion, bitrate, pista de audio.
  2. Compara contra la especificacion pedida (--spec: 1920x1080, 3840x2160, 1080x1920, 1080x1080) y,
     si se da, la duracion objetivo (--duracion SEG, tolerancia ±0,5 s) y los fps (--fps).
  3. Loudness integrada (EBU R128, filtro ebur128 de ffmpeg): objetivo -14 LUFS ±1 y true peak
     ≤ -1 dBTP para web/redes (--lufs para otro objetivo). Sin audio → se informa (version muda).
  4. Fotogramas de control: extrae N fotogramas (--fotogramas, default 12) a tamaño completo en
     {video}-qa/fNN-{t}s.png y una hoja de contactos {video}-qa/contactos.png para revisar que el
     producto real se vea NITIDO y a TAMAÑO COMPLETO (sin relleno gris, sin capturas chicas).
  5. Cuadros negros largos (blackdetect ≥ 1,0 s fuera del inicio/fin) y congelados (freezedetect ≥ 2 s).

Uso:
  python3 qa_video.py keynote-v1.mp4 --spec 1920x1080 --duracion 190 --fps 30
  python3 qa_video.py carpeta/ --spec 1080x1920            # todos los .mp4/.mov de la carpeta
  python3 qa_video.py clip.mp4 --sin-fotogramas            # solo mediciones

Salida: una linea por video (OK / OBSERVADO) + {video}-qa/qa.json. Codigo 0 si todo OK, 2 si hubo
observaciones, 1 si hubo error (ffmpeg ausente, archivo ilegible). Solo libreria estandar de Python;
requiere ffmpeg y ffprobe en el PATH. El video original nunca se modifica.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

EXT = (".mp4", ".mov", ".m4v", ".webm", ".mkv")


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return r.returncode, r.stdout.decode(errors="replace"), r.stderr.decode(errors="replace")


def probe(video):
    code, out, err = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", video])
    if code != 0:
        raise RuntimeError(f"ffprobe fallo: {err[-300:]}")
    d = json.loads(out)
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    if not v:
        raise RuntimeError("sin pista de video")
    num, den = (v.get("avg_frame_rate") or "0/1").split("/")
    fps = round(float(num) / float(den), 3) if float(den or 0) else 0.0
    fmt = d.get("format", {})
    return {
        "contenedor": fmt.get("format_name"),
        "codec": v.get("codec_name"), "perfil": v.get("profile"), "pix_fmt": v.get("pix_fmt"),
        "ancho": int(v.get("width", 0)), "alto": int(v.get("height", 0)), "fps": fps,
        "duracion": round(float(fmt.get("duration") or 0), 3),
        "bitrate_kbps": round(int(fmt.get("bit_rate") or 0) / 1000),
        "peso_mb": round(int(fmt.get("size") or 0) / 1048576, 2),
        "audio": bool(a), "audio_codec": a.get("codec_name") if a else None,
        "audio_hz": int(a.get("sample_rate", 0)) if a else None,
    }


def loudness(video):
    code, out, err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-filter_complex",
                          "ebur128=peak=true", "-f", "null", "-"])
    resumen = err[err.rfind("Summary:"):] if "Summary:" in err else err
    i = re.search(r"I:\s*(-?[\d.]+)\s*LUFS", resumen)
    tp = re.search(r"Peak:\s*(-?[\d.]+)\s*dBFS", resumen)
    return (float(i.group(1)) if i else None, float(tp.group(1)) if tp else None)


def detectar(video, filtro, clave):
    code, out, err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-vf", filtro, "-an", "-f", "null", "-"])
    eventos = []
    if clave == "black":
        for m in re.finditer(r"black_start:([\d.]+)\s+black_end:([\d.]+)\s+black_duration:([\d.]+)", err):
            eventos.append({"inicio": float(m.group(1)), "fin": float(m.group(2)), "dur": float(m.group(3))})
    else:
        inicios = [float(x) for x in re.findall(r"freeze_start:\s*([\d.]+)", err)]
        durs = [float(x) for x in re.findall(r"freeze_duration:\s*([\d.]+)", err)]
        eventos = [{"inicio": s, "dur": d} for s, d in zip(inicios, durs)]
    return eventos


def fotogramas(video, dur, n, carpeta):
    os.makedirs(carpeta, exist_ok=True)
    rutas = []
    for k in range(n):
        t = dur * (k + 0.5) / n
        ruta = os.path.join(carpeta, f"f{k + 1:02d}-{t:06.2f}s.png")
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", ruta])
        if os.path.exists(ruta):
            rutas.append(ruta)
    cols = 4
    filas = max(1, (n + cols - 1) // cols)
    hoja = os.path.join(carpeta, "contactos.png")
    fps_hoja = max(n / dur, 0.01) if dur else 1
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf",
         f"fps={fps_hoja:.5f},scale=480:-1,tile={cols}x{filas}:padding=8:color=white", "-frames:v", "1", hoja])
    return rutas, (hoja if os.path.exists(hoja) else None)


def revisar(video, a):
    obs = []
    p = probe(video)
    if a.spec:
        w, h = (int(x) for x in a.spec.lower().split("x"))
        if (p["ancho"], p["alto"]) != (w, h):
            obs.append(f"resolucion {p['ancho']}x{p['alto']} distinta de la especificada {w}x{h}")
    if a.fps and abs(p["fps"] - a.fps) > 0.05:
        obs.append(f"fps {p['fps']} distinto de {a.fps}")
    if a.duracion and abs(p["duracion"] - a.duracion) > 0.5:
        obs.append(f"duracion {p['duracion']} s fuera de {a.duracion}±0,5 s")
    if p["codec"] not in ("h264", "hevc"):
        obs.append(f"codec {p['codec']}: para entregar usar H.264 (o H.265 si el destino lo soporta)")
    if p["pix_fmt"] and p["pix_fmt"] != "yuv420p":
        obs.append(f"pix_fmt {p['pix_fmt']}: usar yuv420p para compatibilidad (QuickTime, redes)")
    res = {"video": video, "medicion": p}
    if p["audio"]:
        i, tp = loudness(video)
        res["lufs"], res["true_peak_dbfs"] = i, tp
        if i is not None and abs(i - a.lufs) > 1.0:
            obs.append(f"loudness {i} LUFS fuera de {a.lufs}±1")
        if tp is not None and tp > -1.0:
            obs.append(f"true peak {tp} dBFS sobre -1 dBTP")
    else:
        res["lufs"] = None
        obs.append("sin pista de audio (aceptable solo si es la version muda declarada)") if not a.muda else None
    negros = [e for e in detectar(video, "blackdetect=d=1.0:pix_th=0.10", "black")
              if e["inicio"] > 0.5 and e["fin"] < p["duracion"] - 0.5]
    congelados = [e for e in detectar(video, "freezedetect=n=0.003:d=2", "freeze")]
    if negros:
        obs.append(f"{len(negros)} tramo(s) negros ≥ 1 s a mitad del video: {negros[:3]}")
    if congelados and not a.permitir_congelados:
        obs.append(f"{len(congelados)} tramo(s) congelados ≥ 2 s (revisar si es intencional): {congelados[:3]}")
    res["negros"], res["congelados"] = negros, congelados
    if not a.sin_fotogramas:
        carpeta = os.path.splitext(video)[0] + "-qa"
        rutas, hoja = fotogramas(video, p["duracion"], a.fotogramas, carpeta)
        res["fotogramas"], res["contactos"] = rutas, hoja
        with open(os.path.join(carpeta, "qa.json"), "w", encoding="utf-8") as f:
            json.dump({**res, "observaciones": obs}, f, ensure_ascii=False, indent=2)
    res["observaciones"] = obs
    return res


def main():
    ap = argparse.ArgumentParser(description="QA de entrega de videos de Marketing")
    ap.add_argument("rutas", nargs="+")
    ap.add_argument("--spec", help="resolucion esperada, p. ej. 1920x1080")
    ap.add_argument("--fps", type=float)
    ap.add_argument("--duracion", type=float, help="duracion objetivo en segundos")
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--fotogramas", type=int, default=12)
    ap.add_argument("--sin-fotogramas", action="store_true")
    ap.add_argument("--muda", action="store_true", help="la version es muda a proposito")
    ap.add_argument("--permitir-congelados", action="store_true", help="planos fijos intencionales")
    a = ap.parse_args()
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("ERROR: falta ffmpeg/ffprobe en el PATH")
        sys.exit(1)
    videos = []
    for r in a.rutas:
        if os.path.isdir(r):
            videos += sorted(os.path.join(r, f) for f in os.listdir(r) if f.lower().endswith(EXT))
        else:
            videos.append(r)
    estado, resumen = 0, []
    for v in videos:
        try:
            res = revisar(v, a)
        except Exception as e:
            print(f"ERROR     {v}: {e}")
            estado = 1
            continue
        p = res["medicion"]
        tag = "OK" if not res["observaciones"] else "OBSERVADO"
        if res["observaciones"] and estado == 0:
            estado = 2
        print(f"{tag:9} {v} — {p['ancho']}x{p['alto']} {p['fps']}fps {p['codec']} {p['duracion']}s "
              f"{p['bitrate_kbps']}kbps LUFS={res.get('lufs')}")
        for o in res["observaciones"]:
            print(f"          · {o}")
        resumen.append({"video": v, "estado": tag, "observaciones": res["observaciones"]})
    print(json.dumps({"videos": resumen}, ensure_ascii=False))
    sys.exit(estado)


if __name__ == "__main__":
    main()
