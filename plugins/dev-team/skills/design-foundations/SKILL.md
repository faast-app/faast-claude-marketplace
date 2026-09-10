---
name: design-foundations
description: Fundamentos de diseño UI de nivel estudio para el equipo de diseño de dev-team - lectura de diseño, modos (persuadir/operar/leer/experimentar), tipografia, color y contraste, espaciado y layout, estados, lista anti-generico y puertas de calidad. Cargala antes de diseñar o maquetar cualquier pantalla.
---

# Design foundations (dev-team)

## 1. Lectura de diseño (antes de cualquier pixel)
Escribe UNA linea: "Leo esto como: {landing | dashboard | formulario | editorial | portal
| app movil} para {audiencia}, con lenguaje {vibe en 2-3 palabras}, modo {Persuadir |
Operar | Leer | Experimentar}". El modo manda:
- **Persuadir** (landing, pricing): atencion y accion; imagen y tipografia protagonistas.
- **Operar** (app, dashboard, admin): escaneabilidad, consistencia, densidad correcta,
  expectativas nativas; la marca vive en detalles, no en decoracion.
- **Leer** (docs, ayuda): estructura para comprender; medida 60-75 caracteres.
- **Experimentar** (portfolio, showcase): el contenido lidera, la interfaz se retira.
Si el brief es ambiguo, UNA pregunta ("¿mas cerca de Linear-limpio o de Awwwards-experimental?").

## 2. Tres diales
Densidad (1 aireado – 10 cabina), Varianza (1 simetrico – 10 caotico), Movimiento
(1 estatico – 10 cinematografico). Operar: densidad 5-8, varianza 2-4, movimiento 2-4.
Persuadir: densidad 3-5, varianza 5-8, movimiento 4-7. Declara los diales en el spec.

## 3. Tipografia
- ≤ 2 familias (display + texto) y ≤ 4 pesos; fallback del sistema siempre.
- Escala modular: 12 / 14 / 16 / 20 / 24 / 32 / 40 / 56 (fluida con `clamp()` en titulares).
- Interlineado: 1.1-1.2 titulares, 1.5 texto; tracking negativo leve en display ≥ 32 px.
- Numerales tabulares (`font-variant-numeric: tabular-nums`) en tablas y montos.
- Medida de lectura 60-75 caracteres; nunca titulares en 6 lineas angostas.

## 4. Color
- Neutros con temperatura decidida (calidos o frios, nunca mezclados) y UN acento
  calibrado (saturacion < 80 %); estados semanticos (exito, aviso, error, info) fijos.
- Nada de negro puro (#000): off-black / zinc-950. Fondo claro no es #fff puro si la
  marca lo permite.
- Contraste calculado y anotado: 4.5:1 texto, 3:1 UI y texto grande. Modo oscuro
  DISEÑADO (elevacion por tono, no por sombra), no invertido.
- Prohibido: gradientes purpura/neon, "AI glow", glassmorphism generalizado.

## 5. Espaciado y layout
- Sistema de 4/8 px; contenedor 1200-1280; grid 12 col; breakpoints 375 / 768 / 1280.
- Bento y tarjetas solo si agrupan informacion real; nunca tarjetas dentro de tarjetas;
  nunca tres tarjetas iguales "porque si".
- Hero: evita el reflejo texto-izquierda/imagen-derecha; considera centrado sobre imagen,
  abajo-izquierda, editorial fuera de grid, stacked.
- Jerarquia: una cosa importante por pantalla; lo secundario se ve secundario.

## 6. Estados y contenido
Siempre los 4 estados: loading (skeleton), error (accion de recuperacion), empty (que
hacer ahora), success. Textos reales del negocio, idioma del proyecto, cero lorem ipsum,
nombres y montos plausibles.

## 7. Lista anti-generico (rechazo automatico)
Gradiente purpura/azul neon · hero centrado sobre malla oscura · tres tarjetas iguales ·
glass en todo · Inter + slate-900 por reflejo · pills/etiquetas decorativas con jerga
falsa · iconos en circulos de color por defecto · sombras pesadas + radios enormes ·
micro-animaciones infinitas · mockup 3D flotante sin motivo · texto en imagen.

## 8. Puertas de calidad del entregable
Lectura de diseño explicita · direcciones que divergen en un eje nombrado · contraste
calculado · foco/targets/reduced-motion · 4 estados · 3 breakpoints · textos reales ·
captura 1280 y 375 · presupuesto de rendimiento · cero anti-generico.
