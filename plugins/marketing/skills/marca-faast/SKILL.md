---
name: marca-faast
description: La marca FAAST verificada para el equipo de Marketing - SOLO lo comprobado con su fuente y fecha, y lo no encontrado como pendiente a confirmar por el usuario (nada inventado). Cubre como se escribe el nombre (FaaST / FaaST.app en el sitio), el titular y la propuesta publica del sitio faast.app, productos (Factoring, Confirming, Ordering), paises, publico, tono de voz observado, cifras y reconocimientos que el sitio publica (citables con fuente y fecha), colores observados en el CSS del sitio y en el isotipo oficial, tipografias del sitio (Lato y Open Sauce One) y de las propuestas de producto Faast2.0, donde estan los logos (sin copiarlos al repo) y su estado (vector oficial pendiente), reglas de uso del logo, y la lista de pendientes de marca. Cargala antes de escribir copy o diseñar cualquier pieza.
---

# Marca FAAST — lo verificado y lo pendiente

> Regla: esta skill documenta SOLO lo verificado, con su fuente y fecha de verificacion. Lo que no
> se encontro queda como **PENDIENTE — confirmar con el usuario**. El kit vigente de cada proyecto
> vive en `.marketing/marca/kit.md` (lo arma `/marketing:marca`) y manda sobre esta skill cuando el
> usuario confirma algo nuevo. Verificacion inicial: **2026-10-16**.

## 1. Nombre y escritura
| Dato | Valor verificado | Fuente |
|---|---|---|
| Escritura en el sitio | **FaaST** y **FaaST.app** (mayusculas intermedias) | faast.app, `<title>` y pie (2026-10-16) |
| Titulo del sitio | "FaaST.app \| Core SaaS de Factoring, Confirming y Ordering para bancos y financieras de LATAM" | faast.app `<title>` (2026-10-16) |
| Alt del logo en el producto | "FaaST.app" | Faast2.0 `.coordination/design/DSN-002-acceso-identidad/02-ui/tema-login.faast.json` |
| Uso en documentos internos | "FAAST" (mayusculas) en repos y documentos del equipo | este marketplace (CLAUDE.md) |

**PENDIENTE**: cual es la escritura oficial para piezas externas (FaaST, FaaST.app o FAAST). Mientras
no se confirme, las piezas externas usan **FaaST** (como el sitio publico).

## 2. Mensaje publico (textual, citable con fuente)
Fuente: https://faast.app (consultado 2026-10-16).
- Titular: **"El CORE más ágil de Latinoamérica"**.
- Subtitulo: "Plataforma SaaS para Factoring, Confirming y Ordering".
- Descripcion (meta): "Escala tu operación de Factoring, Ordering y Confirming con automatización,
  trazabilidad y cumplimiento normativo."
- Bajada: "Automatiza y escala tu operación financiera desde una sola plataforma, con trazabilidad y
  cumplimiento normativo nativo en Chile, Perú y Colombia."
- Seccion: "Opera más en menos tiempo".
- Productos: Factoring, Confirming, Ordering. Integracion por API con bancos, burós y entidades
  tributarias (SII, SUNAT, DIAN) — segun el sitio.
- Publico declarado: empresas de factoring, instituciones financieras en crecimiento, grupos
  corporativos con lineas financieras propias; "bancos, fintech y empresas de servicios financieros".
- Llamado a la accion del sitio: "Agendar demo".

## 3. Cifras y reconocimientos que publica el sitio
Fuente: https://faast.app, seccion "Resultados que hablan por sí solos" (consultado 2026-10-16).
Son **autodeclaradas**: se citan como "segun FaaST" con fecha, y antes de usarlas en una pieza se
confirma con el usuario que siguen vigentes.
| Cifra (textual) | Etiqueta |
|---|---|
| +300K | Operaciones cursadas y giradas |
| +200K | Facturas monitoreadas |
| +US$2.000 millones (+2B) | cursados por nuestros clientes |
| +7.000 | Pequeñas y Medianas Empresas financiadas |
| +10.000 (+10K) | Empresas pagadoras |
| 15 y 3 | Clientes en Chile y en Perú, "próximamente en Colombia" |
| IFC (Banco Mundial) | "El IFC nos destacó como el único Core latinoamericano ágil y moderno, capaz de digitalizar y automatizar integralmente el proceso de factori[ng]..." |

**PENDIENTE**: vigencia de estas cifras a la fecha de cada pieza; documento fuente del reconocimiento
del IFC (para citarlo con su propia referencia).

## 4. Tono de voz (observado, no normado)
Observado en faast.app (2026-10-16): profesional, directo, orientado a resultados; **tuteo** ("tu
operación"); verbos de accion en imperativo ("Automatiza", "Escala", "Opera más en menos tiempo");
afirmaciones de liderazgo respaldadas con cifras. **PENDIENTE**: guia de voz oficial (si existe).

## 5. Color (lo observado y su contexto)
| Uso | Valor | Fuente | Nota |
|---|---|---|---|
| Verde del isotipo oficial | **#71af26** | mediana de pixeles del raster oficial del logo; Faast2.0 `.coordination/design/DSN-002-acceso-identidad/03-visual/logos/README.md` (2026-10-09) | el redibujo de DSN-001 (#66a412) NO es fiel; no usar |
| Texto / wordmark claro | **#151515** | CSS del sitio (`--color-black-900`, el color de texto mas usado) y wordmark en `DSN-001.../brandkit/faast-real/README.md` | — |
| Wordmark sobre oscuro | #f1f8ff | `DSN-001.../brandkit/faast-real/README.md` | version para fondo oscuro del producto |
| Verdes del sitio | #22b14c (brillo/sombra), #2eb741, #4dca77, #56bca7, #bcec6d, #d0f88e; clases Tailwind green-500/600 | CSS de faast.app (`/_astro/*.css`, 2026-10-16) | acentos y degradados del sitio |
| Azul en el sitio | `--color-primary-500: #4259f5`; `theme-color` **#0F72FF** | CSS y meta de faast.app (2026-10-16) | presencia secundaria; rol no confirmado |
| Neutros del sitio | #f6f6f6, #f0f0f0, #212121, #2b2b2b | CSS de faast.app | fondos y superficies |
| Boton primario del login Faast2.0 | fill #487700, secundario #1f3a00 | `DSN-002.../02-ui/tema-login.faast.json` | derivado por contraste para UI del producto, NO es color de marca |

**PENDIENTE**: paleta oficial de marca (primario, secundarios, uso del azul #0F72FF/#4259f5 frente al
verde del isotipo). Hasta confirmarlo: el **verde del isotipo #71af26** como acento de marca y
**#151515** como texto, con verdes del sitio como acentos; el azul no se usa como color principal.
Contraste: #71af26 como texto sobre blanco NO cumple AA (2,67:1 calculado WCAG; DSN-002 midio 2,51:1 sobre tarjeta #f6f8f8): se usa como
acento grafico, no como texto pequeño.

## 6. Tipografia
| Contexto | Familias | Fuente |
|---|---|---|
| Sitio faast.app | **Lato** (300, 400, 700, 900; autoalojada en `/fonts/`) y **Open Sauce One** (400) | CSS `@font-face` de faast.app (2026-10-16) |
| Producto Faast2.0 (propuesta DSN-001) | pila de sistema para texto; **Figtree** 600/700 recomendada para display (candidatas: IBM Plex Sans, Manrope) | `DSN-001.../03-visual/tipografia.md` — es propuesta de producto, no marca corporativa |

Lato es SIL OFL; Open Sauce One es de licencia libre (verificar el texto de la licencia antes de
embeberla en una pieza). **PENDIENTE**: tipografia oficial de marca para piezas (¿Lato + Open Sauce
One como el sitio?).

## 7. Logo: donde esta (no se copia al repo)
- Publicos en el sitio: `https://faast.app/media/2025/11/Footer-Logo-Container.svg` y
  `https://faast.app/media/2025/11/Footer-Logo-Container-1.svg`; favicon `https://faast.app/favicon.svg`
  y `/favicon.png`; imagen social `https://faast.app/images/og-default.jpg`.
- Copias y trabajo en el proyecto Faast2.0 (fuera de este repo):
  `.../Proyectos/Faast2.0/.coordination/design/DSN-001-contenedora-glass/03-visual/brandkit/faast-real/`
  (copia del SVG del pie; su isotipo es un **raster embebido** de 1024 px, exportacion de Figma) y
  `.../DSN-002-acceso-identidad/03-visual/logos/` (`faast-isotipo-v2-ajustado.svg`,
  `faast-principal-v2-ajustado-{claro,oscuro}.svg`: aproximacion vectorial medida, IoU 0,957 contra el
  raster, con el verde oficial — **provisional, no es el vector oficial**).
- Composicion: isotipo (cuadrado verde redondeado con flecha diagonal blanca) + wordmark "FaaST.app".
- Pie del sitio: "Diseño: Fixu Agencia Web" (agencia del sitio; posible duena de los archivos fuente).

**Reglas de uso** (mientras no haya manual oficial): nunca redibujar, recolorear, deformar, invertir
ni filtrar el logo; zona de proteccion = media altura del isotipo; altura minima 24 px en pantalla;
sobre foto, siempre sobre placa solida; si una pieza usa la version provisional, se anota en `NOTAS.md`.

**PENDIENTE**: archivo vectorial oficial del logo (AI/EPS/PDF/SVG con el isotipo en formas, no raster),
version monocroma, manual de marca. Pedirlo al dueño de la marca o a la agencia del sitio.

## 8. Imagen y estilo observado en el sitio
Iconografia lineal en SVG, fotografia de personas en contexto de trabajo (hero), mapa de LATAM,
fondos claros con degradados suaves de verde y azul, sombras con brillo verde. Logos de clientes en
carrusel (`progreso`, `tsf`, `toquea`, `orsan`, `lateral`, `kaplen`, `ipsofactoring`): **son marcas de
terceros**; en piezas solo con autorizacion registrada en el brief.

## 9. Lista de pendientes de marca (para `/marketing:marca`)
1. Escritura oficial del nombre en piezas externas.
2. Paleta oficial y rol del azul frente al verde.
3. Tipografias oficiales para piezas (y licencias).
4. Vector oficial del logo, variantes y manual.
5. Guia de voz oficial.
6. Vigencia de las cifras publicas y fuente del reconocimiento IFC.
7. Clientes cuyo logo o caso se puede mostrar (autorizacion por cliente).

## 10. Contrastes calculados (WCAG 2.x, 2026-10-16)
Calculo propio sobre los hex verificados (formula de luminancia relativa WCAG). Umbrales: 4,5:1 texto
normal · 3:1 texto grande (≥ 24 px o ≥ 18,66 px bold) y elementos graficos.
| Color | sobre #ffffff | sobre #151515 | sobre #f6f6f6 | Uso que permite |
|---|---|---|---|---|
| #71af26 (isotipo) | 2,67 | 6,84 | 2,47 | sobre oscuro: texto y graficos; sobre claro: solo grafico decorativo o con borde/placa |
| #151515 (texto) | 18,26 | — | 16,90 | texto principal sobre claros |
| #22b14c (verde sitio) | 2,81 | 6,49 | 2,60 | igual que el isotipo |
| #4259f5 (azul sitio) | 5,28 | 3,46 | 4,88 | texto sobre blanco; sobre oscuro solo texto grande |
| #0F72FF (theme-color) | 4,31 | 4,24 | 3,99 | texto grande o grafico; no texto chico |
| #487700 (fill login Faast2.0) | 5,36 | 3,40 | 4,96 | boton/texto sobre claro (es derivado de UI, no color de marca) |
Consecuencia practica: en fondos claros, el verde de marca va como acento grafico (bloques, lineas,
isotipo) y el texto en #151515; en fondos oscuros (estudio, video), el verde puede ser texto.

## 11. Como se aplica la marca por pieza (mientras no haya manual)
| Pieza | Logo | Color | Tipografia | Notas |
|---|---|---|---|---|
| Deck | apertura y cierre; no en cada lamina | neutros + verde como acento | la del kit (sitio: Lato / Open Sauce One) | cifras en display |
| Video | apertura (sting) y cierre; animacion solo aparicion por fundido/escala/luz (no deformar ni separar el isotipo sin manual) | fondo estudio oscuro + verde | la del kit | logo nunca recoloreado por el grade |
| One-pager / panfletos | cabecera con zona de proteccion | blanco + tinte del verde | la del kit | version provisional anotada si se usa |
| Redes | esquina o cierre de carrusel, tamaño discreto | segun pieza | la del kit | sin marca de agua |

## 12. Procedimiento para re-verificar (cada vez que se arma o valida el kit)
1. WebFetch de `https://faast.app`: titulo, H1, subtitulo, CTA, cifras de "Resultados", pie.
2. Descargar el HTML y los CSS enlazados (`/_astro/*.css`) a una carpeta temporal fuera de repos y
   extraer `--color-*`, colores hex mas usados y `@font-face`.
3. Revisar `{proyecto}/.coordination/design/DSN-*/03-visual/` (logos, brandkit, color, tipografia).
4. Comparar con esta skill; registrar diferencias con fecha en `.marketing/marca/kit.md`.
5. Lo que cambie de forma relevante (nuevo color, nuevo logo) se confirma con el usuario antes de usarlo.

## 13. Lo que nunca se hace con la marca
- Redibujar, "mejorar", recolorear, deformar, invertir, filtrar o separar el logo sin manual.
- Inventar un color "de marca" o una tipografia "corporativa" no verificada.
- Usar el redibujo de DSN-001 como logo (no es fiel).
- Usar logos de clientes del sitio en piezas sin autorizacion por cliente.
- Citar cifras del sitio sin la fecha de consulta ni la etiqueta "segun FaaST".
