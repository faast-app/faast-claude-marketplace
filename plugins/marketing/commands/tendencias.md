---
description: Refresca la base de tendencias del equipo de Marketing (.marketing/tendencias/) - el investigador-mercado revisa las vencidas (vigente_hasta anterior a hoy), las renueva solo con evidencia nueva o las archiva, busca tendencias nuevas de mercado (factoring, confirming, ordering, regulacion, open finance, IA en riesgo y cobranza), de producto y del lenguaje visual de lanzamientos premium (decks, video, redes), y clasifica cada una como tendencia, moda o senal con fuente y fecha. Se puede programar semanal con /schedule. Uso - /marketing:tendencias [refrescar|nuevas|listar] [ambito]
argument-hint: '[refrescar | nuevas | listar] [mercado|producto|regulacion|diseno|video|redes] [--pais CL|PE|CO]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su procedimiento en
> la sesion actual. NUNCA lo corras dentro de un subagente ni lo invoques via Agent/Task. Solo se
> delegan los AGENTES del equipo, y unicamente cuando este procedimiento lo indica.

# Tendencias: la base, siempre vigente

Pedido: $ARGUMENTS

Metodo: skill `investigacion-mercado` (§7-8). Agente: `investigador-mercado`.

## Modos
- **`listar`** (solo lectura): tabla de `.marketing/tendencias/INDEX.md` con vigentes, vencidas y
  archivadas, por ambito.
- **`refrescar`** (por defecto): para cada tendencia vencida o que vence en 14 dias → buscar evidencia
  NUEVA (fuente con fecha posterior a la ultima) → renovar `vigente_hasta`, reclasificar (moda que se
  sostuvo → tendencia; senal confirmada → tendencia; tendencia que se apago → archivo) o mover a
  `tendencias/archivo/`. Nunca se extiende una vigencia sin evidencia nueva.
- **`nuevas [ambito]`**: barrido de tendencias nuevas en el ambito pedido (o en todos) y alta de archivos
  desde `templates/tendencias/tendencia.md`.

## Procedimiento
1. Plan corto (ambitos, cuantas vencidas, tiempo) → OK (salvo `listar`).
2. Invocar `investigador-mercado` con el modo y la ruta absoluta de `.marketing/`.
3. Actualizar `INDEX.md` y registrar eventos `trend_added`, `trend_renewed`, `trend_expired`.

## Salida
```
Tendencias — {fecha}: {n} vigentes · {n} renovadas · {n} archivadas · {n} nuevas
Para las piezas en curso: {tendencias relevantes y a que pieza aplican}
```

## Programarlo
Se puede dejar semanal con `/schedule` (p. ej. "cada lunes 8:00, /marketing:tendencias refrescar").
El hook de inicio de sesion avisa cuantas tendencias estan vencidas.

## Reglas
- Cada tendencia con fuentes fechadas y `vigente_hasta`; tipo correcto (tendencia / moda / senal).
- Las tendencias de diseño y video son guias de estilo: nunca se copian marcas ni piezas ajenas.
