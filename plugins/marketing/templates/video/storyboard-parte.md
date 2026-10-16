# Storyboard cuadro a cuadro — Capitulo {N} · {P{NN}} {nombre de la parte}

**Campana:** {CMP-AAAA-NNN} · **Version:** v{N} · **Duracion total:** {s} s (= suma de planos) · **BPM:** {n} · **Formato:** {1920x1080}
**Guion:** `preproduccion/guion/P{NN}.md` · **Sub-composicion HyperFrames:** `compositions/frames/{NN}-P{NN}-{slug}.html`

| Plano | Inicio | Dur. (s) | Tipo de plano | Movimiento de camara virtual | Material real (ruta + origen) | Texto en pantalla | Sonido | Transicion de entrada | Blueprint / tecnica | Boceto |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0:00 | 2,5 | macro | push-in lento 1,0→1,15x | `capturas/P{NN}-2-*.png` (demo {fecha}) | — | pulso grave | corte desde negro | keyframes punch-in | `boceto-01.png` |
| 2 | 0:02,5 | 1,5 | negro + titulo | estatico | — | "{titular}" | golpe | corte en beat | kinetic-type-beats | — |
| 3 | 0:04 | 4,0 | dispositivo heroe | orbita 12° + push-in | `capturas/P{NN}-1-*.png` | — | sube | revelacion por luz | device-surface-showcase | — |
| 4 | 0:08 | 3,0 | desarmado en capas | separacion en Z y re-armado | capas recortadas de `P{NN}-1` | — | aire | — | 3D depth | — |
| 5 | 0:11 | 6,0 | recorrido guiado | camara sigue la consecuencia | `capture/rec-P{NN}.webm` (normalizar: OK) | "{paso clave}" | ticks | match cut | cursor-ui-demo / camera-journey | — |
| 6 | 0:17 | 3,0 | cifra a pantalla completa | estatico, cuenta ascendente | — | "{cifra} {unidad}" + nota | silencio 0,5 s + golpe | corte en beat | dataviz-countup | — |
| 7 | 0:20 | 1,0 | respiro | — | color de marca | — | cola | disolucion | — | — |

## Verificaciones del storyboard
- [ ] Suma de duraciones = duracion del capitulo.
- [ ] Cada plano con material real (o recurso de marca) y su origen.
- [ ] Cada cartela cumple su tiempo de lectura (0,4 s × palabras + 1 s).
- [ ] Una idea por plano; transiciones con proposito (corte por defecto).
- [ ] Encaje con la musica: cortes en beats marcados.
- [ ] Version 9:16 pensada (reencuadre de los planos 3, 5 y 6).
