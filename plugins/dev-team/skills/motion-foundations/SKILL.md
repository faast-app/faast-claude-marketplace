---
name: motion-foundations
description: Fundamentos de animacion y micro-interacciones para el equipo de diseño de dev-team - proposito del movimiento, motion tokens (duraciones, curvas, springs), reglas por componente, coreografia entre pantallas, prefers-reduced-motion, rendimiento y eleccion de tecnologia (CSS/WAAPI, GSAP, Lottie, Rive, video). Cargala antes de especificar o implementar movimiento.
---

# Motion foundations (dev-team)

## 1. Proposito o nada
Cada animacion responde a una de estas: **orientar** (de donde vino / a donde fue),
**dar feedback** (que paso), **enfocar** (que mirar), **dar caracter** (identidad). Si
no puedes escribir el proposito en una linea, no se anima.

## 2. Motion tokens (base; ajustar por producto)
| Token | Valor | Uso |
|---|---|---|
| `duration.instant` | 80 ms | hover, pressed, toggles |
| `duration.fast` | 150 ms | tooltips, menus, chips |
| `duration.base` | 220 ms | modales, sheets, tabs, listas |
| `duration.slow` | 320 ms | paneles grandes, expansiones |
| `duration.page` | 400 ms | transicion entre pantallas |
| `ease.out` | cubic-bezier(.2,.8,.2,1) | ENTRADAS (aparece rapido, asienta suave) |
| `ease.in-out` | cubic-bezier(.4,0,.2,1) | movimientos de un lugar a otro |
| `ease.in` | cubic-bezier(.4,0,1,1) | SOLO salidas |
| `spring.gesture` | masa 1 · rigidez 300 · amortiguacion 30 | arrastres, sheets, rubber-band |
Salidas siempre mas rapidas que entradas. UI < 300 ms. Escalonados (stagger) 20-40 ms
y maximo 6-8 items.

## 3. Reglas por componente
- **Boton**: pressed `scale(.98)` 80 ms; loading con spinner que reemplaza el texto sin
  cambiar el ancho.
- **Toast**: entra desde el borde con `ease.out` 220 ms + fade; sale 150 ms; apilable.
- **Modal/Sheet**: fondo fade 150 ms; contenido `translateY(8px)`→0 + fade 220 ms;
  sheet con spring y arrastre interrumpible.
- **Lista/tabla**: skeleton → contenido con fade; reordenar con FLIP (`transform`).
- **Tabs/segmented**: indicador se DESLIZA (elemento compartido), contenido cross-fade.
- **Navegacion**: View Transitions API cuando el stack lo permita; elemento compartido
  (imagen/titulo) entre lista y detalle.
- **Estados vacios/ilustraciones**: una sola entrada suave; nada en bucle.

## 4. Coreografia
Una idea por transicion. El elemento que dispara la accion es el que guia (origen
espacial). Lo que aparece despues del cambio entra escalonado; lo que desaparece se va
primero. Nunca dos coreografias compitiendo.

## 5. Accesibilidad y rendimiento
- `@media (prefers-reduced-motion: reduce)`: movimientos → fade; parallax y autoplay
  apagados; duraciones ≤ 100 ms. Obligatorio en TODO entregable.
- Solo `transform` y `opacity` (y `clip-path` con cuidado); nunca `width/height/top/left`.
- 60 fps en portatil comun; medir (Playwright MCP + devtools tracing). `will-change`
  solo justo antes de animar.

## 6. Tecnologia por caso
CSS transitions/keyframes y Web Animations API → UI cotidiana · GSAP (+ScrollTrigger) →
coreografias, scroll, timelines · Lottie → ilustraciones animadas exportadas (ligero,
no interactivo) · Rive → animaciones interactivas con maquina de estados (mas ligero que
Lottie para lo complejo) · Three.js → 3D · Video (HyperFrames) → marketing y demos,
nunca para UI.

## 7. Vocabulario util
Pop in · Fade through · Shared element · Rubber-banding · Overshoot · Stagger · FLIP ·
Skeleton · Cross-fade · Container transform · Parallax · Scrub.
