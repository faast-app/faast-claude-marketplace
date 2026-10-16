# QA de video — {pieza} v{N} · {CMP-AAAA-NNN}

**Archivo:** `entregas/{archivo}` · **Revisado por:** director-motion · **Fecha:** {AAAA-MM-DD}
**Resultado de qa_video.py:** {OK | OBSERVADO} · **Hoja de contactos:** `{archivo}-qa/contactos.png`

## 1. Tecnica (qa_video.py)
- [ ] Resolucion = especificacion ({WxH}) · fps = {n} · codec H.264 (o H.265 declarado) · yuv420p
- [ ] Duracion dentro de ±0,5 s del objetivo ({s} s)
- [ ] Loudness integrada -14 LUFS ±1 · true peak ≤ -1 dBTP (o version muda declarada)
- [ ] Sin tramos negros ≥ 1 s a mitad del video · sin congelados no intencionales ≥ 2 s
- [ ] Peso compatible con la plataforma de destino (limite verificado con fuente)

## 2. Material real (fotogramas de control, uno o mas por capitulo)
| Capitulo / parte | Fotograma | Producto real nitido | A tamaño completo (sin relleno gris, sin captura chica) | Sin pixelado por escalado | Datos ficticios | Rotulo "Prototipo" si aplica |
|---|---|---|---|---|---|---|
| P01 | f03 | ✔/✗ | ✔/✗ | ✔/✗ | ✔/✗ | ✔/✗/— |

- [ ] Todas las grabaciones usadas pasaron `normalizar_video.py` en OK (ninguna reparada).

## 3. Lenguaje y montaje
- [ ] Un capitulo por parte, en el orden aprobado (keynote) · una parte por clip
- [ ] Una idea por plano; ningun tramo de "slideshow" (capturas con fundido sin camara ni ritmo)
- [ ] Cortes en el beat; respiros entre capitulos; silencio antes de la cifra mas fuerte
- [ ] Transiciones con proposito (corte por defecto; ninguna de plantilla)
- [ ] Easing suave, sin rebotes; camara con intencion

## 4. Texto y subtitulos
- [ ] Cada cartela ≤ 7 palabras y en pantalla ≥ 0,4 s × palabras + 1 s
- [ ] Cifras con su nota (fuente o supuesto) en cartela, subtitulo o cierre
- [ ] Textos completos dentro de la zona segura (9:16: 250 px libres arriba y abajo)
- [ ] Subtitulos completos, sincronizados, ≤ 42 caracteres por linea, ortografia (tildes, eñes, ¿ ¡)
- [ ] Version muda autosuficiente

## 5. Marca, legal y confidencialidad
- [ ] Logo oficial (o provisional declarado) sin deformar, recolorear ni separar; zona de proteccion
- [ ] Colores de la interfaz y del logo sin alterar por el grade
- [ ] Musica, SFX, voz, fuentes y LUT en LICENCIAS.md con alcance que cubre el uso
- [ ] Ningun dato real, cliente no autorizado, ID de ticket, ruta o informacion interna en ningun fotograma
- [ ] Nada copiado de los referentes (logos, sonidos, musica, claims)

## 6. Accesibilidad
- [ ] Sin destellos de mas de 3 por segundo · contraste AA en texto sobreimpreso
- [ ] Pieza web animada con alternativa prefers-reduced-motion (si aplica)

## Veredicto
**{APTO PARA APROBACION | NO APTO}** — Observaciones: {lista con capitulo, segundo y correccion}
