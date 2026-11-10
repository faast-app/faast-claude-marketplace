# Revision de capturas (taste-faast)

Se revisa **mirando cada captura** (1440, 1024, 768, 390; claro y oscuro; recorrido a 320).
Cada linea que no se cumple es un hallazgo con archivo, ancho y que se ve.

## Primera pantalla
- [ ] Dice que es y muestra un dato duro; el titulo nombra la cosa.
- [ ] La accion principal esta visible sin scroll y es una sola.
- [ ] En Persuadir/Presentar: el heroe o la portada llena la pantalla sola.

## Una idea por pantalla
- [ ] Cada vista (o seccion) tiene un protagonista; nada compite con el.
- [ ] No hay bloques a medio llenar ni zonas vacias sin motivo.

## Bordes y alineacion
- [ ] Mismas lineas izquierda/derecha en todos los bloques; columnas enteras.
- [ ] Nada escalonado, cortado, montado sobre otra cosa ni fuera del viewport.
- [ ] Sin scroll lateral en ningun ancho (incluido 320).

## Todo dibuja
- [ ] Ningun marco vacio, imagen rota ni placeholder; logos y graficos presentes.
- [ ] Los 4 estados (cargando, vacio, error, con datos) existen y se ven terminados.
- [ ] Ninguna leyenda de "ejemplo"/"muestra" dentro de la pantalla.

## Un sistema (la libreria)
- [ ] `HERENCIA: PASA`. Un par de botones, un estilo de tarjeta, una escala de radios.
- [ ] Como maximo dos cajas de profundidad; sin tarjetas dentro de tarjetas.
- [ ] Claro y oscuro igual de cuidados (contraste, bordes, estados).
- [ ] Estado en palabras + color; montos a la derecha con cifras tabulares.

## Texto
- [ ] Titulos con sustantivo; botones verbo + objeto en Title Case; una accion, un nombre.
- [ ] Cero palabras vetadas, frases de plantilla o residuo (`references/texto.md`).
- [ ] Datos plausibles del negocio y del pais; nada inventado presentado como real.

## Movil (768, 390, 320)
- [ ] Una columna a 390; el texto antes que la imagen al apilar.
- [ ] Todo objetivo tactil ≥ 44 px y separado ≥ 8 px del vecino.
- [ ] Tablas con su estrategia movil de la libreria (scroll, apilada o tarjetas), no encogidas.
- [ ] Nada tapado por una barra fija; areas seguras respetadas.

## Teclado y lectura
- [ ] Tab llega a todo en orden visual; foco visible y nunca bajo un encabezado fijo.
- [ ] Encabezados de un nivel a la vez; `lang` correcto; imagenes con alternativa.
- [ ] Con `prefers-reduced-motion` nada se mueve y nada queda oculto.

## Tus ojos
- [ ] Puesto junto al producto real, ¿parece la misma aplicacion?
- [ ] ¿Se entiende en cinco segundos sin que nadie lo explique?
- [ ] ¿Quitarias algo? Entonces quitalo.
