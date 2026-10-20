---
description: Carga y valida el kit de marca FAAST del proyecto (.marketing/marca/kit.md) - parte de lo verificado en la skill marca-faast (sitio faast.app y propuestas de diseño del proyecto), revisa el sitio publico y las carpetas del proyecto (brand kit, tokens, logos) con fuente y fecha, incorpora lo que el usuario confirme o entregue (manual, vector oficial del logo, paleta, tipografias con licencia, voz), mide contrastes, y deja la lista de pendientes explicita. Nada inventado y los logos no se copian a ningun repo. Uso - /marketing:marca [cargar|validar|pendientes]
argument-hint: '[cargar | validar | pendientes] [--manual ruta] [--logo ruta]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su procedimiento en
> la sesion actual. NUNCA lo corras dentro de un subagente ni lo invoques via Agent/Task. Solo se
> delegan los AGENTES del equipo, y unicamente cuando este procedimiento lo indica.

# Marca: el kit FAAST verificado

Pedido: $ARGUMENTS

Base: skill `marca-faast` (lo verificado y lo pendiente, con fuentes). Plantilla:
`templates/marca/kit-marca.md`. Lo ejecuta la sesion principal (o el director-marketing), con apoyo del
`disenador-grafico` para medir contrastes y del `investigador-mercado` para verificar el sitio.

## `cargar` (por defecto si no hay kit)
1. Leer `marca-faast`.
2. Verificar lo publico vigente: WebFetch de `https://faast.app` (titular, nombre, CTA) y del CSS del
   sitio (colores y `@font-face`); anotar fecha de consulta. Si algo cambio respecto de la skill, se
   registra el cambio con su fuente.
3. Buscar en la carpeta del proyecto (`config.json` → `fuentes.coordination`): `design/DSN-*/`
   (brandkit, logos, tokens, tipografia, color). Solo lectura; los logos NO se copian a ningun repo: se
   referencia su ruta. Si una pieza necesita el archivo, se copia a `.marketing/marca/assets/` (fuera
   de repos) con su origen anotado.
4. Si el usuario entrega manual o vector oficial (`--manual`, `--logo`): incorporarlo como fuente
   principal.
5. Escribir `.marketing/marca/kit.md` desde la plantilla: nombre y escritura, mensaje, voz, colores
   (con rol y contraste medido), tipografias (con licencia), logo (rutas, variantes, estado
   oficial/provisional, reglas), imagen, cifras citables con fecha, **pendientes**.
6. Actualizar `config.json` → `marca.kit` con la ruta y la fecha.

## `validar`
Medir contrastes (texto y acentos sobre fondos claros y oscuros, WCAG AA), revisar que las tipografias
tengan licencia para el uso (web, impreso, video), que el logo usado sea el oficial o este marcado
provisional, y que las cifras de marca citadas sigan vigentes. Informe en `marca/validacion-{fecha}.md`.

## `pendientes`
Listar lo que falta confirmar (escritura del nombre, paleta oficial, tipografias, vector del logo,
manual, voz, vigencia de cifras, clientes mostrables) con a quien pedirlo.

## Salida
```
Kit de marca — {fecha}: {n} verificados · {n} confirmados por el usuario · {n} pendientes
Pendientes criticos para piezas: {lista}
```

## Reglas
- Solo lo verificado con fuente y fecha; lo demas, PENDIENTE.
- El logo nunca se redibuja, recolorea ni se copia a un repo.
- Marcas de clientes del sitio: autorizadas por el usuario (2026-10-16); se usan tal cual, sin recolorear, y se anota en el brief que pieza las usa.
