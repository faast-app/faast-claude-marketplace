---
description: El investigador-mercado investiga en la web con fuente y fecha - mercado (tamano, crecimiento, regulacion y digitalizacion del factoring, confirming y ordering en Chile, Peru, Colombia y LATAM, y el costo de los problemas que resuelve cada parte), competencia (quienes, que ofrecen publicamente, donde), benchmark (por parte del mapa y general - tiene, parcial, no publica) o tendencias (mercado, producto y lenguaje visual de lanzamientos). Cada dato con URL, fecha de publicacion y de consulta, tipo y confianza; cifras clave cruzadas; nada inventado. Uso - /marketing:investigar mercado|competencia|benchmark|tendencias [tema]
argument-hint: 'mercado | competencia | benchmark | tendencias  [tema o pregunta] [--pais CL|PE|CO|LATAM] [--partes P01,P03] [--campana CMP-...]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su procedimiento en
> la sesion actual. NUNCA lo corras dentro de un subagente ni lo invoques via Agent/Task. Solo se
> delegan los AGENTES del equipo, y unicamente cuando este procedimiento lo indica.

# Investigar: el mercado, con fuente y fecha

Pedido: $ARGUMENTS

Metodo: skill `investigacion-mercado`. Agente: `investigador-mercado`.

## Paso 0 — Contexto
Carpeta canonica; campana (`--campana` o la en curso; para investigacion general sin campana se usa
`.marketing/investigacion/{AAAA-MM-DD}-{tema}/`). Leer `brief.md` y `desglose/mapa.md` si existen.

## Paso 1 — Plan primero
Preguntas concretas a responder (3-8), paises, tipo de fuentes, que se entregara y para que pieza o
ficha sirve. OK del usuario (en una linea si el pedido ya es claro).

## Modos
- **`mercado`**: tamano y crecimiento por pais (con año y moneda), marco regulatorio y tributario
  (factura electronica, cesion, registros), digitalizacion, dolores de las financieras y su costo
  (insumo del §2 de cada ficha) → `investigacion/mercado.md`.
- **`competencia`**: competidores comparables (cores de factoring/confirming, fintech, soluciones
  bancarias, desarrollo in-house), que declaran publicamente, publico y paises; marcado
  `autodeclarado` → `investigacion/competencia.md`.
- **`benchmark`**: matriz por parte del mapa (FAAST vs competidores vs alternativa actual) con estados
  ✔ / parcial / ✗ documentado / "sin info publica a {fecha}" + benchmark general con lectura honesta →
  `investigacion/benchmark.md` y §6 de cada ficha.
- **`tendencias`**: igual que `/marketing:tendencias` pero acotado al tema pedido.

## Paso 2 — Ejecutar
Invocar `investigador-mercado` con el pedido textual, el modo, las partes y la ruta absoluta de la
campana. Registro unico de fuentes: `investigacion/fuentes.md` (F-ID, URL, publicado, consultado, tipo,
confianza).

## Salida
```
Investigacion {modo} — {ID o tema}
Conclusion (3 lineas, piramide: respuesta primero)
Cifra mas fuerte: {valor} — {fuente, año} [F0xx]
Debil o pendiente: {lo que no se encontro, fuente unica, dato antiguo}
Archivos: investigacion/{...}.md · fuentes.md ({n} fuentes)
```

## Reglas
- Nada sin fuente abierta y verificada; nada de "segun estudios".
- "No publica" no es "no tiene"; competidores con precision y respeto.
- Solo informacion publica; sin datos personales; lo de la Mesa o de clientes es interno.
