---
description: Arma el MAPA DEL PRODUCTO y una FICHA por parte - el primer entregable obligatorio de toda campana. El analista-producto lee las fuentes reales (wiki, backlog, arquitectura y propuestas de diseño del dev-team en .coordination/, solicitudes y maquetas de la Mesa en .mesa/, y el producto en ambiente demo capturado con el Playwright MCP), propone 4 a 10 partes con nombre de negocio y estado real (disponible, en construccion, hoja de ruta) para aprobar, y luego escribe cada ficha (que es y para quien, problema y su costo, como funciona con pantallas reales, que gana el cliente con fuente, antes/despues, benchmark) con el estratega y el investigador. Doble aprobacion del usuario. Subcomandos - mapa, fichas, parte {Pnn}, actualizar.
argument-hint: '[mapa | fichas | parte P{NN} | actualizar] [--campana CMP-...] [--publico ceo|comercial|cliente] [--max N]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su procedimiento en
> la sesion actual. NUNCA lo corras dentro de un subagente ni lo invoques via Agent/Task. Solo se
> delegan los AGENTES del equipo, y unicamente cuando este procedimiento lo indica.

# Desglose: el producto parte por parte

Pedido: $ARGUMENTS

Metodo completo: skill `desglose-producto`. Sin este desglose aprobado no se produce ninguna pieza.

## Paso 0 — Contexto
Carpeta canonica de Marketing (`hooks/coord_root.py`). Campana: `--campana` o la ultima en curso; si
no hay, crear una con brief minimo (producto, publico, objetivo) — o derivar a
`/marketing:propuesta-comercial` si el pedido es una propuesta completa. Leer `config.json` →
`fuentes` y `ambientes.demo`.

## `mapa` (por defecto si no hay mapa aprobado)
1. **Plan primero** (4 lineas): fuentes que se leeran, si se capturara en demo, publico, cuando se
   presenta el mapa. OK del usuario.
2. Invocar `analista-producto` (con el pedido textual) → `desglose/inventario.md` y `desglose/mapa.md`
   (desde `templates/desglose/mapa-producto.md`). En paralelo, si no existe, `investigador-mercado` con
   un primer barrido de competidores por parte.
3. Presentar al usuario el mapa como tabla:
```
| ID | Parte (nombre de negocio) | Valor en una linea | Estado | Pantalla | Fuente |
Orden propuesto para {publico}: P01 → P03 → ... (por que)
¿Apruebas estas partes y este orden? Puedes quitar, unir, renombrar o reordenar.
```
4. Registrar la decision en `aprobaciones.md` (textual) y `estado.json` → `MAPA APROBADO`.

## `fichas` (requiere mapa aprobado)
1. `analista-producto` escribe §1-3, §5, §7-8 y captura las pantallas (`desglose/capturas/` +
   `ORIGEN.md`, solo demo con datos ficticios); `estratega-comercial` escribe §4 "que gana el cliente"
   con formula y supuestos; `investigador-mercado` aporta §6 benchmark. Pueden ir en paralelo por parte.
2. El director revisa cada ficha con la checklist de la skill.
3. Presentar al usuario una linea por ficha (parte · que gana · cifra con su tipo de fuente · pantallas
   disponibles · pendientes) + rutas. Aprobacion por lote o por ficha → `aprobaciones.md` →
   `FICHAS APROBADAS`.

## `parte P{NN}`
Crear o rehacer la ficha de una sola parte (agregada al mapa con OK del usuario), con el mismo metodo.

## `actualizar`
Cuando el producto avanzo (HUs cerradas, nuevo prototipo, demo con funciones nuevas): el analista
compara el mapa con las fuentes actuales y propone cambios de estado (`en construccion` → `disponible`)
y capturas nuevas; el usuario aprueba; las piezas afectadas se marcan para nueva version.

## Salida
```
Desglose {ID}: {n} partes ({n} disponibles · {n} en construccion · {n} hoja de ruta)
Mapa: desglose/mapa.md ({APROBADO|pendiente}) · Fichas: {n}/{n} aprobadas
Pendientes para el usuario: {supuestos a validar, accesos, autorizaciones}
Siguiente: /marketing:video keynote · /marketing:presentacion · /marketing:pieza one-pager
```

## Reglas
- 4 a 10 partes con nombre de negocio orientado a resultado; nunca nombres de servicios tecnicos.
- Estado real con evidencia; nada `en construccion` en presente.
- Pantallas reales (demo, prototipo o maqueta del proyecto, rotulados); jamas imaginadas.
- Cada numero con F-ID o `SUPUESTO`. Las fuentes se leen; nunca se escribe en `.coordination/` ni `.mesa/`.
