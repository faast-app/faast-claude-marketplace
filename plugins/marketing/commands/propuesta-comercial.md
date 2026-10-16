---
description: Paquete completo de propuesta comercial para un ejecutivo (p. ej. el CEO de una financiera) - brief y plan primero, investigacion de mercado y competencia, el MAPA DEL PRODUCTO desglosado parte por parte con una ficha por parte (aprobados por el usuario), estrategia y copy, y luego en paralelo SIEMPRE el video keynote por capitulos (uno por parte) mas un clip de 6-15 s por parte, el deck de propuesta con una seccion por parte y el one-pager con el desglose (panfletos por parte si hacen falta). Cada pieza pasa revision del director y aprobacion del usuario. Usa el agente director-marketing y todo el equipo.
argument-hint: '"{producto} para {publico/empresa}" [--pais CL|PE|CO] [--fecha AAAA-MM-DD] [--sin-impresos] [--formatos 16x9,9x16,1x1] [--corta]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su procedimiento en
> la sesion actual. NUNCA lo corras dentro de un subagente ni lo invoques via Agent/Task. Solo se
> delegan los AGENTES del equipo, y unicamente cuando este procedimiento lo indica.

# Propuesta comercial: el producto desglosado, listo para el CEO

Pedido: $ARGUMENTS

## Lo que sale de aqui (siempre)
| Pieza | Contenido | Agente |
|---|---|---|
| Mapa del producto + fichas | las partes y su prueba (interno, base de todo) | analista-producto + estratega + investigador |
| **Video keynote** | un capitulo por parte + apertura, problema, prueba, hoja de ruta, cierre; 16:9 4K/1080p + version muda + poster | director-motion |
| **Clips por parte** | uno de 6-15 s por parte, 16:9 (+9:16 y 1:1 si `--formatos`) | director-motion |
| Deck de propuesta | apertura + mercado → una seccion por parte → benchmark → hoja de ruta → propuesta → anexo | disenador-presentaciones |
| One-pager | el desglose en una hoja (+ panfletos por parte si hacen falta) | disenador-grafico |
`--sin-impresos` omite el one-pager; el video keynote y los clips NO se omiten nunca (son la pieza mas
importante). `--corta` comprime los tiempos (mapa de 4-6 partes, keynote de 90-120 s).

## Paso 0 — Contexto
Carpeta canonica (`hooks/coord_root.py`); si no hay → `/marketing:start`. Leer `config.json`
(fuentes, ambiente demo, marca). Si el kit de marca no esta cargado, avisar y ofrecer `/marketing:marca`
(se puede avanzar con el desglose mientras tanto).

## Paso 1 — Brief (una ronda, maximo 5 preguntas)
Crear la campana: ID `CMP-AAAA-NNN-{slug}` (correlativo en `correlativos.json`), carpeta
`campanas/{ID}/` con `brief.md` (desde `templates/campana/brief.md`), `estado.json`, `aprobaciones.md`.
Preguntar solo lo que falta: quien es el ejecutivo y su empresa/pais; que DECISION debe tomar; que se
puede y no se puede decir (clientes nombrables, cifras internas autorizadas); precios (¿los entrega
comercial?); fecha y como se usara (reunion presencial, envio, ambas).

## Paso 2 — Plan primero
Presentar en 6-10 lineas: partes probables (del primer barrido de fuentes), orden de trabajo, que corre
en paralelo, que se necesita del usuario (demo, cifras, autorizaciones), piezas y fecha. Esperar OK.
Registrar `esperando_usuario`.

## Paso 3 — Desglose (doble aprobacion)
Invocar `director-marketing` con el pedido textual del usuario. El director lanza en paralelo
`analista-producto` (inventario → MAPA) e `investigador-mercado` (mercado, competencia, benchmark):
1. **MAPA** → al usuario como tabla (ver `/marketing:desglose`) → **aprobacion 1** registrada.
2. **FICHAS** (analista + estratega + benchmark) → resumen de una linea por ficha → **aprobacion 2**.
Sin ambas aprobaciones no se produce ninguna pieza.

## Paso 4 — Estrategia y copy
Estratega: propuesta de valor, mensajes para el publico, narrativa (orden de las partes), objeciones.
Redactor: titulares por parte, copy por lamina, guion del keynote por capitulos, guion de cada clip,
textos del one-pager. El director revisa.

## Paso 5 — Produccion en paralelo (el video es el camino critico)
- **Video** (`/marketing:video keynote` + `clips`): preproduccion (concepto, tratamiento, guion tecnico y
  storyboard por parte, animatic) → **aprobacion de preproduccion** → captura real → HyperFrames →
  postproduccion → preview → aprobacion → render → QA cuadro a cuadro.
- **Deck** (`/marketing:presentacion propuesta`): storyboard → aprobacion del director → construccion →
  previews.
- **One-pager / panfletos** (`/marketing:pieza one-pager`): identidad de campana → bocetos → piezas.

## Paso 6 — Revision del director y aprobacion del usuario (por pieza)
Checklist del director (desglose, fuentes, producto real, estado honesto, marca, confidencialidad,
calidad de lanzamiento, accesibilidad, tecnica, video). Luego cada pieza al usuario con 3 lineas y su
vista previa → `approved` / `changes_requested`. Lo aprobado pasa a `entregables/` con nombre final
`{Proyecto}-{pieza}-{publico}-v{N}-{AAAA-MM-DD}.{ext}`.

## Paso 7 — Entrega
```
Propuesta {ID} — {producto} para {publico}
Video:   entregables/...keynote...mp4 (+1080p, muda, poster) · {n} clips por parte
Deck:    entregables/...deck...pptx | pdf
Impreso: entregables/...one-pager...pdf (+ panfletos)
Pendiente: {precios de comercial / supuestos a validar con el cliente}
```
Recordar: el envio o la presentacion al cliente la hace el usuario.

## Reglas
- Desglose parte por parte antes de cualquier pieza; nada generico.
- Nada inventado: cifras con fuente y fecha o `SUPUESTO`; pantallas reales; precios solo de comercial.
- Confidencialidad en piezas externas; marcas de terceros nunca como propias.
- Ninguna pieza sale sin aprobacion del usuario. `.marketing/` fuera de los repos.
