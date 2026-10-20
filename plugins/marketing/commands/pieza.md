---
description: El disenador-grafico produce piezas graficas premium sobre la marca FAAST siguiendo el desglose - one-pager (el producto desglosado en una hoja - un bloque por parte con mini-captura real, nombre, una linea de valor y cifra con nota), panfleto (una parte por panfleto, cuando la parte lo merece) o redes (LinkedIn, Instagram, banners, carruseles con una parte por lamina), con identidad de campana como acento, HTML autocontenido exportado a PDF listo para imprimir (A4 o Carta, sangrado y marcas) y PNG en medidas exactas, verificado export por export. Uso - /marketing:pieza panfleto|one-pager|redes
argument-hint: 'one-pager | panfleto [P{NN}] | redes [linkedin|instagram|banner] [--campana CMP-...] [--imprenta] [--carta] [--carrusel]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su procedimiento en
> la sesion actual. NUNCA lo corras dentro de un subagente ni lo invoques via Agent/Task. Solo se
> delegan los AGENTES del equipo, y unicamente cuando este procedimiento lo indica.

# Pieza: impresos y redes, parte por parte

Pedido: $ARGUMENTS

Reglas: skill `piezas-graficas`. Agente: `disenador-grafico`.

## Prerrequisitos
Mapa y fichas APROBADOS; copy (`copy/impresos.md`, `copy/redes.md`; si faltan, el director los pide al
redactor); kit de marca; capturas reales.

## Tipos
- **`one-pager`** (A4; `--carta` para Carta): titular + bajada → un bloque por parte (4-8) con
  mini-captura real, nombre, una linea y cifra con nota → banda de prueba opcional (benchmark resumido o
  cifras de marca citadas) → llamado a la accion y contacto autorizado → notas de fuente.
- **`panfleto [P{NN}]`**: una parte por panfleto (A4/A5 o diptico/triptico): portada con la parte → que
  es y para quien → como funciona (3-4 pasos con capturas) → que gana (cifra) → antes/despues →
  contacto. Sin `P{NN}`: proponer que partes merecen panfleto y por que.
- **`redes [red]`**: LinkedIn 1200x627 / 1080x1350 / carrusel PDF 1080x1350; Instagram 1080x1080,
  1080x1350, historia 1080x1920; banners segun brief. Carrusel (`--carrusel`): gancho → una lamina por
  parte → marca y llamado. Si hay clips de video aprobados, sugerir combinarlos (`/marketing:video redes`).

## Procedimiento
1. **Plan primero**: piezas, medidas, imprenta o digital (`--imprenta` agrega sangrado 3 mm y marcas),
   partes incluidas, fecha. OK.
2. Invocar `disenador-grafico` (pedido textual + ruta absoluta).
3. Identidad de campana (si no existe) y bocetos de estructura → revision del director.
4. Construccion HTML → export PDF/PNG → `VERIFICACION.md` (desbordes, contraste AA, cuerpo minimo,
   tildes, cifras con nota, QR probado, medidas, sangrado).
5. Revision del director → usuario → aprobacion → `entregables/`.

## Salida
```
Pieza {tipo} v{N} — {ID}
Archivos: piezas/impresos/... | piezas/redes/... · Verificacion: OK
Esperando: aprobacion del usuario
```

## Reglas
- El one-pager es el mapa del producto en una hoja; un panfleto = una parte.
- Capturas reales; logo oficial sin redibujar ni recolorear; marcas de terceros solo con autorizacion.
- Cifras con nota; sin informacion interna ni datos de clientes. No se entrega sin aprobacion.
