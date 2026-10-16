# Marketing, Ventas y Publicidad

Equipo de 8 agentes IA (10 comandos) para **vender** lo que FAAST construye: un proyecto nuevo, una
propuesta comercial a un CEO, el lanzamiento de un modulo o las mejoras que hay que contarle a la
cartera. Produce videos cinematograficos de producto, presentaciones, one-pagers, panfletos, piezas
para redes y benchmarks — con estetica de lanzamiento (keynote de Apple, presentacion de un
hiperdeportivo, comercial de perfume) y con el producto REAL.

## La idea central: el producto desglosado, parte por parte
Una presentacion generica del producto no vende. Por eso el equipo siempre empieza por el
**mapa del producto**: sus partes (modulos, capacidades, mejoras), cada una con su **ficha**:

1. Que es y para quien.
2. Que problema resuelve hoy y cuanto cuesta ese problema.
3. Como funciona, paso a paso, con pantallas reales o prototipos del proyecto.
4. Que gana el cliente, en numeros, con fuente.
5. Antes / despues.
6. Frente a la competencia (benchmark de esa parte).

**Tu apruebas el mapa y las fichas. Recien ahi se producen las piezas**, y todas siguen el desglose:

| Pieza | Como sigue el desglose |
|---|---|
| **Video keynote** (la pieza mas importante) | un capitulo por parte: apertura → problema → partes → prueba → hoja de ruta → cierre |
| **Clips por parte** | uno de 6-15 s por parte, para usar suelto (16:9, vertical y cuadrado) |
| **Deck de propuesta** | una seccion por parte: imagen principal, detalle, como funciona, resultado |
| **One-pager** | el mapa del producto en una hoja |
| **Panfletos** | uno por parte, cuando la parte lo merece |
| **Redes** | una parte por pieza o por lamina de carrusel |

## Instalacion
```bash
/plugin marketplace add faast-app/faast-claude-marketplace
/plugin install marketing@faast-marketplace
```

## Como empezar
```bash
/marketing:start
```
La primera vez pregunta lo minimo (que producto, donde estan sus fuentes, si hay un ambiente demo,
a quien se le vende) y crea la carpeta de trabajo `.marketing/` en la carpeta del proyecto
(**nunca dentro de un repositorio**). Despues:

```bash
/marketing:propuesta-comercial "Faast2.0 para el CEO de {empresa}"
```
Eso arma el paquete completo: desglose → video keynote + clips por parte → deck → one-pager.

## Comandos
| Comando | Que hace |
|---|---|
| `/marketing:start` | Entrada unica: configura, detecta lo que esta en curso y te lleva al paso correcto |
| `/marketing:propuesta-comercial` | Paquete completo para un ejecutivo: desglose → video keynote y clips → deck → one-pager |
| `/marketing:desglose` | Mapa del producto y fichas por parte (siempre lo primero) |
| `/marketing:video` | Videos: `keynote`, `parte {n}`, `clips`, `teaser`, `redes`, `preproduccion`, `revisar` |
| `/marketing:presentacion` | Deck de propuesta, de benchmark o version corta para enviar |
| `/marketing:pieza` | One-pager, panfleto por parte o piezas para redes |
| `/marketing:investigar` | Mercado, competencia, benchmark o tendencias, con fuente y fecha |
| `/marketing:tendencias` | Refresca la base de tendencias (se puede programar semanal con `/schedule`) |
| `/marketing:marca` | Carga y valida el kit de marca FAAST (lo verificado y lo pendiente) |
| `/marketing:estado` | Que esta en curso, que espera tu aprobacion y que sigue |

## El equipo
| Agente | Rol |
|---|---|
| **director-marketing** | Dirige la campana: brief, plan, reparto, revision y tu aprobacion; unico que delega |
| **investigador-mercado** | Mercado, competencia, benchmark y tendencias, siempre con fuente y fecha |
| **analista-producto** | Conoce el producto de verdad (backlog, wiki, diseño, Mesa, demo) y arma el mapa y las fichas |
| **estratega-comercial** | Propuesta de valor, mensajes por publico, narrativa del pitch, objeciones, "que gana el cliente" |
| **redactor-publicitario** | Titulares, copy por parte, guiones de video |
| **disenador-presentaciones** | Decks con estetica de lanzamiento (PowerPoint, PDF, HTML) |
| **director-motion** | Videos cinematograficos con HyperFrames: preproduccion, captura real, produccion, post y control de calidad |
| **disenador-grafico** | One-pagers, panfletos, redes e identidad de campana sobre la marca FAAST |

Todos corren en `sonnet` por defecto; se sube por agente en `.marketing/config.json` → `team.models`.

## Principios
- **Nada se inventa**: cada cifra, comparacion o afirmacion tiene fuente y fecha; lo que no tiene
  respaldo se marca como supuesto.
- **El producto se muestra real**: capturas del producto en un ambiente demo, prototipos o maquetas
  del proyecto — nunca pantallas imaginadas.
- **Nada sale sin tu aprobacion**: plan primero, mapa y fichas aprobados, y cada pieza aprobada antes
  de entregarse.
- **Confidencialidad**: sin datos de clientes ni informacion interna en piezas externas.
- **Marcas ajenas**: nunca como propias; los logos de clientes, solo con autorizacion.
- **Precios**: solo los que entrega comercial.

## Requisitos para el video
Node 22+, FFmpeg y HyperFrames (skills `hyperframes` y `product-launch-video`). El Playwright MCP
viene con el plugin para capturar el producto (salida en `~/.faast-mcp/marketing`, fuera de los repos).

## Convive con
- **dev-team**: el equipo lee su `.coordination/` (wiki, backlog, diseño) para conocer el producto.
- **mesa-servicios**: lee su `.mesa/` (lo que piden los clientes, maquetas, propuestas).
Solo lee; nunca escribe en las carpetas de otros equipos.
