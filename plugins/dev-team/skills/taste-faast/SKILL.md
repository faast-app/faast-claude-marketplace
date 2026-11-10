---
name: taste-faast
description: Criterio de diseño (taste) del equipo de diseño de dev-team - como lograr que una pantalla, propuesta, deck o landing se vea hecha por un estudio y para ESTE producto, no generica ni "hecha por IA". Un solo sistema (el de la libreria FaaST), el producto real en pantalla, una idea por pantalla, bordes iguales, texto que dice que es, movimiento que responde, direcciones repartidas y no elegidas por reflejo, y una puerta final en navegador real. Adaptacion al contexto FaaST de tasteskill (Leonxlnx, MIT). Cargala al diseñar o revisar cualquier propuesta y siempre que algo "se vea generico".
---

# Taste FaaST: criterio de estudio sobre la libreria

El gusto no es decoracion: es **que no sobre nada, que se vea lo real y que todo pertenezca
al mismo sistema**. Esta skill pone el criterio; el sistema visual lo pone
`dev-team:libreria-faast` (cargala primero: aqui no se elige paleta ni fuente).

Base: tasteskill 2.5 de Leonxlnx (MIT; `references/atribucion.md`), pensada para sitios de
empresa. Aqui esta adaptada a producto fintech y a propuestas. Si el usuario tiene instalada
la skill original (`design-taste-frontend`) y el pedido es un **sitio/landing publico**,
usala con su kit, entregandole los colores de la libreria por su comando `brand` (seccion 7).

## Las reglas de la casa (ganan sobre todo lo demas de esta skill)

1. **Un solo sistema.** Un par de botones, un estilo de tarjeta, una escala de radios, un
   aspecto de enlace, una escala de titulos: los de la libreria. Dos cajas de profundidad
   como maximo. Si aparece una tercera variante de algo, sobra una.
2. **El producto real en pantalla.** La interfaz propuesta con datos del negocio (operaciones,
   montos, estados, fechas por pais), a tamaño real. Nunca un dashboard generico, un mockup
   flotante, ni fragmentos decorativos sobre paneles.
3. **Una idea por pantalla.** Cada vista responde una pregunta del usuario y tiene UNA accion
   principal. En deck y landing: una seccion por pantalla, sin que asome el titulo de la
   siguiente. Lo secundario se ve secundario.
4. **Bordes iguales.** Todo bloque cae sobre las mismas lineas izquierda y derecha del
   contenedor o de las columnas de la grilla. Nada corrido a un lado, nada escalonado, nada
   que haga scroll lateral.
5. **Todo dibuja.** Ningun marco vacio, imagen rota ni "aqui ira el grafico" a 1440, 1024,
   768 y 390. Si un dato no existe, la pantalla muestra su estado vacio real.
6. **Sin leyendas que se disculpan.** Nada de "ejemplo", "datos de muestra", "mockup",
   ni pies de imagen explicando lo que se ve. La anotacion vive en el deck, no en la pantalla.
7. **El movimiento responde, no adorna.** Todo control contesta al puntero y al foco; lo que
   entra, entra una vez. Nada se mueve porque la pagina hizo scroll.
8. **Nada inventado.** Ni clientes, ni cifras, ni testimonios, ni logos parecidos. Lo que
   falta se pide o queda como pendiente visible en el deck.

## 1. Lee el pedido: que registro es

| Registro | Que es | Quien manda |
| --- | --- | --- |
| **Operar** | Pantalla de producto: portal, backoffice, formulario, tabla | La libreria al 100 %: componentes del kit, densidad correcta, cero ornamento |
| **Presentar** | Deck de propuesta, informe, documento | Libreria para tema y tipografia; composicion editorial (seccion 4) |
| **Persuadir** | Landing, pagina de producto, pieza comercial | Tema de la libreria; aqui si hay heroe, ritmo y un momento (seccion 5) |

Escribe el registro en la primera linea del brief. Mezclarlos es el error mas comun: un
dashboard con heroe, o una landing con densidad de backoffice.

## 2. Reparte, no elijas por reflejo

Un modelo elige siempre lo mismo. Las 2-3 direcciones de una propuesta **se reparten** sobre
ejes con nombre y se anota el reparto, para que dos propuestas seguidas no salgan iguales:

- **Ejes de producto (Operar):** densidad (aireada ↔ compacta) · navegacion (lateral ↔
  superior ↔ por pasos) · protagonista (tabla ↔ tarjetas ↔ resumen + detalle) · orden de
  lectura (cifra primero ↔ tarea primero) · flujo (una pantalla ↔ asistente por pasos) ·
  detalle (pagina ↔ panel lateral ↔ fila expandida).
- **Ejes de presentacion/persuasion:** heroe (producto ↔ cifra ↔ titular) · ritmo (bandas
  alternas ↔ espacio ↔ banda de marca) · cierre (accion ↔ resumen).

Procedimiento: elige 2 ejes que respondan al brief; cada direccion toma un extremo distinto.
Antes, lee `<coordinacion>/design/_historial-direcciones.json` y evita repetir la
combinacion de las ultimas 3 propuestas del proyecto; al cerrar, agrega la tuya
(`{"dsn","ejes","direcciones","elegida","motivo"}`). La direccion **elegida por el usuario
y su motivo** es la señal que mas vale: registrala tambien como leccion
(`dev-team:memoria-equipo`).

## 3. Texto (el 50 % de que algo se vea profesional)

Detalle y lista de palabras vetadas: `references/texto.md`. Lo esencial:

- El titulo de la pantalla **nombra la cosa** ("Operaciones", "Liquidacion de la operacion
  OP-2026-0418"), no una promesa ni un saludo.
- La primera pantalla lleva **un dato duro**: una cifra, una fecha, un estado.
- Todo titulo tiene un sustantivo que nombra algo. Los botones son **verbo + objeto** en
  Title Case ("Enviar Solicitud", "Descargar Comprobante"); nunca "Aceptar", "Continuar"
  a secas, "Ver mas" ni "Click aqui".
- Una accion, un nombre: si es "Nueva Operacion" en el encabezado, lo es en el vacio y en
  el cierre.
- Errores y vacios dicen **que paso y que hacer ahora**. Cero signos de exclamacion.
- Fuera: adjetivos que reemplazan un dato ("potente", "robusto", "sin fricciones",
  "de ultima generacion"), frases de plantilla, raya larga en cada oracion, emojis.

## 4. Composicion

- **Jerarquia en tres niveles y no mas:** que es esto (titulo), que importa (la cifra o la
  tabla), que hago (la accion). Si todo pesa igual, nada pesa.
- **Contenedor y columnas:** un ancho maximo, margenes iguales, 12 columnas; los bloques
  ocupan columnas enteras. La medida de lectura no pasa de `--faast-size-measure`.
- **Agrupa por proximidad antes que por caja.** Una tarjeta agrupa informacion real; nunca
  tarjetas dentro de tarjetas, ni tres tarjetas iguales para llenar.
- **Numeros:** montos a la derecha, cifras tabulares, moneda y decimales del pais; la cifra
  que decide (neto, total) es la unica destacada.
- **Estado:** palabra + color + punto/icono, igual en toda la aplicacion.
- **Densidad honesta:** un backoffice de trabajo diario es compacto; un portal de cliente
  ocasional respira. Se decide por frecuencia de uso, no por estetica.
- **Deck (Presentar):** una idea por lamina; el titulo es la conclusion ("La liquidacion se
  entiende en una pantalla"), no el tema ("Liquidacion"); captura real grande, texto corto.

## 5. Persuadir (landing, pagina de producto, pieza)

- El heroe llena la primera pantalla solo: que se vende y para quien, un dato duro, la
  accion principal dentro. El producto real como imagen, no una ilustracion de ambiente.
- Cada seccion mide una o dos pantallas, con su titulo arriba y un solo protagonista.
- Como mucho **uno o dos "momentos"** (una entrada del heroe, una seccion que se revela con
  intencion). Nada de carruseles, pestañas con temporizador, inclinaciones 3D, parallax en
  texto ni scroll secuestrado.
- Fotos reales o ninguna. Iconos de terceros con su icono real o ninguno.

## 6. Movimiento

Tokens de la libreria (`--faast-duration-fast|base|slow`, `--faast-ease-standard|exit`).
Todo boton, enlace y fila enlazada responde a hover, foco y pulsacion · una tarjeta enlazada
sube 2 px como maximo · el heroe o la vista entra **una vez** al cargar · nada aparece con
fade por fila al hacer scroll · lo que se mueve mas de 5 s tiene pausa · con
`prefers-reduced-motion` todo queda en reposo y **nada queda oculto**. El detalle lo define
el motion-designer (`dev-team:motion-foundations`).

## 7. La puerta final (en navegador real, no "de ojo")

En este orden, y hasta **3 rondas**; lo que no pase a la tercera se reporta abierto:

1. `kit_libreria.py verificar … --kit faast-kit` → **HERENCIA: PASA** (`dev-team:libreria-faast`).
2. Capturas con Playwright a **1440, 1024, 768 y 390**, en **claro y oscuro**, y recorrido a
   **320** sin scroll lateral ni solapes.
3. Lee CADA captura contra `references/revision.md` (primera pantalla, una idea, bordes,
   todo dibuja, un sistema, texto, movil, teclado). Mirar la captura es obligatorio: el
   codigo "correcto" con un bloque montado sobre otro no pasa.
4. Revision de interfaz con `dev-team:web-interface-guidelines` sobre el HTML.
5. Reporte en el entregable: resultado de cada paso, lo que se corrigio, lo que queda
   abierto y por que, y lo que no se pudo comprobar.

Un hallazgo que juzgas falso se **declara** con su motivo; nunca se oculta el elemento ni se
edita el kit para que la comprobacion pase.

## 8. Nunca

Violeta o lavanda como acento, fondo o degradado (en la libreria el violeta es solo un tono
de estado) · degradados neon, "glow de IA", vidrio esmerilado generalizado · heroe centrado
sobre malla oscura · tres tarjetas iguales · iconos en circulos de color por defecto ·
sombras pesadas con radios enormes · texto en imagenes · fade-in en cada seccion ·
testimonios, clientes o cifras inventados · copiar codigo, textos, imagenes o el efecto
insignia de un sitio de referencia · una segunda fuente "para dar caracter".

## Con la skill original instalada (opcional, solo Persuadir)

`design-taste-frontend` trae su propio kit, repartidores y verificador. Para una landing
FaaST: corre su flujo completo y pasale la marca con
`start.mjs brand --bg <--faast-bg-ground> --ink <--faast-text-primary> --accent <--faast-accent-text>`
(valores de `kit_libreria.py roles`), tipografia Inter, radio `sharp` (fintech). Su puerta
(`GATE: PASS`) se suma a la de esta skill; no la reemplaza. Nunca la uses para pantallas de
producto: ahi manda la libreria.
