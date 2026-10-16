# Equipo del Product Owner (po-team) — Manual de Usuario

**Version del plugin:** 1.0.x · **Integrantes del equipo:** 8 · **Comandos:** 9

El equipo del Product Owner es un **grupo de asistentes de inteligencia artificial que acompaña
al PO** desde que la Mesa de Servicios deja registrado un pedido hasta que el cliente da su visto
bueno. Escribe las historias de usuario en lenguaje de negocio, arma el sprint con sus fechas,
mantiene el tablero al dia, hace una validacion rapida de lo construido, prepara actas e informes
y escribe los manuales de uso.

Tu decides; el equipo prepara. No necesitas saber programar. Este manual esta escrito para el PO,
para quien dirige un area y para quien nunca abrio una herramienta tecnica. La parte tecnica
(instalar y configurar) esta al final, en el **Anexo tecnico**.

---

## Indice

**Parte 1 — Para todas las personas**
1. [En dos minutos: como se usa](#1-en-dos-minutos-como-se-usa)
2. [Conoce al equipo](#2-conoce-al-equipo)
3. [El camino de un ticket hasta el VB del cliente](#3-el-camino-de-un-ticket-hasta-el-vb-del-cliente)
4. [Las palabras que vas a escuchar](#4-las-palabras-que-vas-a-escuchar)
5. [Las reglas de la casa](#5-las-reglas-de-la-casa)
6. [Que puedes pedir (lista de comandos)](#6-que-puedes-pedir-lista-de-comandos)

**Parte 2 — Situaciones reales, paso a paso**
- [Caso 1: La Mesa dejo un pedido nuevo](#caso-1--la-mesa-dejo-un-pedido-nuevo)
- [Caso 2: Armar el proximo sprint](#caso-2--armar-el-proximo-sprint)
- [Caso 3: ¿Como vamos? El tablero y el informe del dia](#caso-3--como-vamos-el-tablero-y-el-informe-del-dia)
- [Caso 4: Dar el VB PO a lo que llego a Demo](#caso-4--dar-el-vb-po-a-lo-que-llego-a-demo)
- [Caso 5: Algo quedo observado](#caso-5--algo-quedo-observado)
- [Caso 6: El acta para el cliente y su VB](#caso-6--el-acta-para-el-cliente-y-su-vb)
- [Caso 7: Un manual para QA y otro para los usuarios](#caso-7--un-manual-para-qa-y-otro-para-los-usuarios)
- [Caso 8: El informe del sprint para gerencia](#caso-8--el-informe-del-sprint-para-gerencia)

**Parte 3 — Preguntas frecuentes y problemas comunes**

**Anexo tecnico (para quien instala y configura)**
- [A. Instalacion y actualizacion](#a-instalacion-y-actualizacion)
- [B. Configuracion](#b-configuracion)
- [C. La carpeta del equipo](#c-la-carpeta-del-equipo)
- [D. Solucion de problemas tecnicos](#d-solucion-de-problemas-tecnicos)

---

# Parte 1 — Para todas las personas

## 1. En dos minutos: como se usa

1. Alguien instala el plugin una vez (ver [Anexo A](#a-instalacion-y-actualizacion)).
2. Abres Claude Code en tu carpeta de trabajo de PO (la primera vez te ayuda a configurarla).
3. Escribes esto y cuentas lo que necesitas, como se lo pedirias a un colega:

```
/po-team:start
```

| Lo que escribes | Lo que pasa |
|---|---|
| `/po-team:start` | El equipo mira el tablero y te propone que hacer primero |
| `/po-team:start la mesa dejo el #131, hay que pasarlo a HU` | Lee el pedido de la Mesa y te propone las historias con criterios y puntos |
| `/po-team:start armemos el sprint 13` | Propone que entra, que sale, las fechas de pase y los riesgos |
| `/po-team:start como vamos` | Actualiza el tablero y te da el informe del dia |
| `/po-team:start revisa en Demo lo del sprint 12` | Valida rapido cada ticket y te entrega la tabla cumple / observado |
| `/po-team:start necesito el acta del #102` | Prepara el acta de aceptacion en PDF y Word |

**Tres cosas que siempre van a pasar:**

- **Te muestran el plan antes de tocar el tablero.** Crear historias, mover estados, comentar o
  subir capturas solo ocurre despues de tu "adelante".
- **La validacion del PO no es la de QA.** Es una revision rapida de lo pedido; QA sigue
  haciendo su prueba completa.
- **Todo en lenguaje de negocio.** Historias, comentarios, documentos y manuales los entiende
  cualquier persona.

---

## 2. Conoce al equipo

| Integrante | Que hace, en palabras simples | Cuando aparece |
|---|---|---|
| 🧭 **po-lead** (coordinador) | Decide que sigue, reparte el trabajo y te muestra el plan antes de tocar el tablero. Es el unico que puede pedir ayuda a los demas | Detras de cada pedido |
| ✍️ **refinador** (el que escribe las historias) | Convierte lo que llego de la Mesa en historias y bugs claros, con criterios para saber si quedo bien y su tamaño en puntos | Cuando llega algo nuevo, cuando algo queda observado y cuando el cliente da su VB |
| 📅 **planificador** (el del sprint) | Arma el sprint segun lo que el equipo puede hacer, propone que dejar afuera y fija las fechas de Demo, Preprod y VB | Antes de cada sprint o si hay que replanificar |
| 📊 **seguimiento** (el del tablero) | Lee el tablero real, calcula cuanto se avanzo, avisa lo atrasado y arma el panel visual y el informe | Cada vez que preguntas "como vamos" |
| ✅ **validador-po** (el revisor rapido) | Revisa en Demo o Preprod que cada criterio se cumpla, con una foto por criterio. Si algo falla, lo anota y sigue con el proximo. **No reemplaza a QA** | Cuando algo llega a Demo/Preprod o quieres adelantarte |
| 📄 **documentador** (el de los documentos) | Prepara historias, especificaciones, actas e informes en PDF y Word | Cuando necesitas presentar algo |
| 📘 **manualista** (el de los manuales) | Recorre el flujo y escribe dos manuales: uno para QA y otro para cualquier persona, con fotos marcadas | Cuando hay que enseñar a usar algo |
| 🧰 **setup** (el que prepara la oficina) | Revisa que la computadora tenga todo y configura el tablero, con tu permiso | Al empezar o si algo no funciona |

---

## 3. El camino de un ticket hasta el VB del cliente

```
 Desarrollo ──► Validacion QA ──► Pase a Demo ──► Validacion Demo / Preprod ──► VB cliente
     ▲                                                                              │
     └─────────────────────── si algo queda Observado, vuelve ◄─────────────────────┘
```

| Etapa | Que significa | Quien la mueve | Que hace el equipo del PO |
|---|---|---|---|
| **Desarrollo** | El equipo de desarrollo lo esta construyendo | Desarrollo | Responde dudas; no cambia la historia a mitad de sprint sin avisar |
| **Validacion QA** | QA lo prueba a fondo | **Solo QA** | Puede revisar antes para detectar algo temprano, sin reemplazar a QA |
| **Pase a Demo** | Se instala en la Demo del pais | Desarrollo | Fija la fecha y avisa si algun ambiente recibe los cambios por lotes |
| **Validacion Demo / Preprod** | El PO revisa en Demo (y en el Preprod del cliente, si tiene) | PO | El revisor rapido da **VB PO** u **Observado** |
| **VB cliente** | El cliente dice "esta bien" | PO, con la confirmacion del cliente | Prepara el acta y deja registrado quien, cuando y como dio el VB |

Los nombres exactos de los estados y de los ambientes son los de tu tablero: se configuran una
vez y el equipo los usa siempre.

---

## 4. Las palabras que vas a escuchar

| Palabra | Que significa |
|---|---|
| **Historia de usuario (HU)** | La descripcion de algo que alguien necesita hacer: quien, que y para que |
| **Criterios de aceptacion** | Las condiciones que se revisan para saber si quedo bien. Se escriben como "Dado… cuando… entonces…" |
| **Puntos** | El tamaño de una historia (1, 2, 3, 5, 8, 13). Mas grande que 8 se divide antes de entrar al sprint |
| **Sprint** | El periodo de trabajo (por ejemplo, dos semanas) con un objetivo y un conjunto de historias |
| **Capacidad** | Cuantos puntos puede hacer el equipo en un sprint |
| **Pase** | Instalar lo construido en otro ambiente (Demo, Preprod) |
| **Demo / Preprod** | Copias del sistema donde se muestra y valida antes de produccion. Preprod es la de un cliente |
| **VB PO** | El visto bueno del PO despues de su revision rapida |
| **Observado** | Algo que no cumple un criterio; vuelve a desarrollo con la explicacion y la foto |
| **VB cliente** | El visto bueno del cliente; cierra el ciclo |
| **Acta de aceptacion** | El documento que el cliente firma para dar su VB |
| **Tablero** | Donde vive el estado de cada ticket (GitHub Projects o Azure DevOps) |
| **Dashboard** | La vista visual del tablero que arma el equipo: sprints, etapas, puntos, fechas y alertas |
| **Evidencia** | Las fotos que muestran lo revisado; se ven dentro del ticket |

---

## 5. Las reglas de la casa

1. **Plan primero.** Nada se crea, mueve, comenta ni sube al tablero sin tu "adelante".
2. **La revision del PO no reemplaza a QA.** El revisor rapido nunca pone estados de QA ni da algo
   por probado.
3. **Todo en lenguaje de negocio.** Titulos limpios, sin codigos ni palabras tecnicas.
4. **Nada se inventa.** Si falta informacion, se pregunta a la Mesa; lo pendiente queda escrito.
5. **Las fotos se ven dentro del ticket**, nunca como un enlace suelto.
6. **Sin claves ni datos personales** en fotos, tickets, documentos ni manuales.
7. **Nadie cierra tickets por su cuenta.** El VB del cliente se registra; cerrar es una decision tuya.
8. **Nada fijo a mano.** Organizacion, tableros, estados, ambientes, clientes y personas salen de
   la configuracion.
9. **No se promete una fecha** al cliente sin que el planificador la revise contra la capacidad.
10. **Al equipo de desarrollo se le pide trabajo con tickets**, no de otra forma.

---

## 6. Que puedes pedir (lista de comandos)

Con `/po-team:start` y una frase basta. Esta lista es para cuando ya sabes que quieres.

| Escribes | Que consigues |
|---|---|
| `/po-team:start` | El punto de partida: mira el tablero y te guia |
| `/po-team:estado` | Un vistazo rapido sin consultar el tablero |
| `/po-team:refinar {#ticket o texto}` | Historias o bugs listos, con criterios y puntos ([Caso 1](#caso-1--la-mesa-dejo-un-pedido-nuevo)) |
| `/po-team:refinar --observacion #n` | Devolver una observacion a desarrollo ([Caso 5](#caso-5--algo-quedo-observado)) |
| `/po-team:refinar --vb-cliente #n` | Registrar el VB del cliente ([Caso 6](#caso-6--el-acta-para-el-cliente-y-su-vb)) |
| `/po-team:sprint planificar {N}` | La propuesta del sprint con fechas y riesgos ([Caso 2](#caso-2--armar-el-proximo-sprint)) |
| `/po-team:tablero` | Te pregunta qué quieres ver: el tablero genérico, el de Organización PO, las validaciones del sprint, o crear un backlog nuevo en GitHub ([Caso 3](#caso-3--como-vamos-el-tablero-y-el-informe-del-dia)) |
| `/po-team:validar {#n o --lote sprint N}` | La revision rapida con fotos ([Caso 4](#caso-4--dar-el-vb-po-a-lo-que-llego-a-demo)). Con `--artifact` queda una página con todas las validaciones del sprint |
| `/po-team:documento {hu, especificacion, aceptacion, sprint} …` | Documentos en PDF y Word ([Caso 6](#caso-6--el-acta-para-el-cliente-y-su-vb), [Caso 8](#caso-8--el-informe-del-sprint-para-gerencia)) |
| `/po-team:manual {flujo}` | Manual QA y manual de usuario ([Caso 7](#caso-7--un-manual-para-qa-y-otro-para-los-usuarios)) |
| `/po-team:setup` | Revisar e instalar lo necesario, configurar el tablero |

---

# Parte 2 — Situaciones reales, paso a paso

Los ejemplos usan tickets y clientes ficticios; aplican a cualquiera.

## Caso 1 — La Mesa dejo un pedido nuevo

**Situacion:** la Mesa de Servicios registro el #131: el cliente quiere ver el IVA de cada gasto
en el resumen de la operacion.

**Que escribes:**
```
/po-team:refinar #131
```

**Que hace el equipo:**
1. El refinador lee el ticket completo: el documento de la Mesa, lo que se decidio con el cliente
   y lo que quedo pendiente.
2. Revisa que no exista ya algo parecido en el tablero.
3. Escribe la historia: quien la usa, que necesita y para que; los criterios para saber si quedo
   bien; que incluye y que no; donde se validara; y propone los puntos con su motivo.
4. Te muestra el plan: "crear 1 historia de 5 puntos en el tablero, relacionada con #131".

**Recibes** (despues de tu "adelante"):
```
Creada: #140 Mostrar el IVA de cada gasto en el resumen de la operacion (5 pts, propuesta)
Siguiente: /po-team:sprint para incluirla
```
Si el pedido de la Mesa tenia dudas sin resolver, no se inventan: el equipo escribe las preguntas
en el ticket de la Mesa y la historia queda "pendiente de informacion".

---

## Caso 2 — Armar el proximo sprint

**Que escribes:**
```
/po-team:sprint planificar 13
```

**Que hace el equipo:** calcula cuanto puede hacer el equipo (por la configuracion o por lo que
logro en los ultimos sprints), toma lo mas prioritario y te propone **sacar** lo que no esta listo:
lo que no tiene criterios claros, lo que no tiene una entrega definida o lo que es demasiado grande.
Propone las fechas de Demo, Preprod y VB cliente, y avisa los riesgos.

**Recibes:**
```
Sprint 13 · 20/10 – 31/10 · capacidad 30 pts
Objetivo: que el cliente reciba el detalle de gastos en su liquidacion
Entra (28 pts): #140 (5), #141 (3), …
Propongo sacar: #118 — sin criterios claros (→ refinar) · #125 — 13 pts, dividir
Fechas: Demo 04/11 (en lote) · Preprod Cliente A 07/11 · VB cliente 11/11
Riesgos: MEDIO — #141 depende de un dato que el cliente aun no envia
¿Adelante? (asigna el sprint a 7 tickets)
```

---

## Caso 3 — ¿Como vamos? El tablero y el informe del dia

**Que escribes:**
```
/po-team:tablero diario
```

**Que hace el equipo:** lee el tablero real, ubica cada ticket en su etapa, suma los puntos,
compara con la ultima revision y arma el panel visual. Si tu sesion lo permite, lo publica como
una pagina privada que puedes abrir y compartir cuando quieras; si no, te deja el archivo.

**Recibes** el informe:
```
Sprint 12 (06/10–17/10): 34 pts · VB cliente 26% · avance ponderado 58%
Cambios: #104 paso a Validado por QA · #130 quedo observado en Demo CO
Atencion: ALTO — la fecha de Demo del 20/10 esta en riesgo (2 tickets aun en QA)
```
Y el panel: cada sprint con sus cinco etapas, los tickets como etiquetas de color con sus puntos,
las fechas comprometidas (en rojo si se vencieron) y lo que cambio desde la ultima vez.

---

## Caso 4 — Dar el VB PO a lo que llego a Demo

**Que escribes:**
```
/po-team:validar --lote sprint 12 --ambiente demo-co
```

**Que hace el equipo:** el revisor rapido entra a la Demo con la cuenta de prueba configurada y,
ticket por ticket, recorre solo los criterios de cada historia por el camino normal, con una foto
por criterio (unos 10-20 minutos por ticket). Si un criterio no se cumple, toma la foto, lo anota
en palabras simples y pasa al siguiente ticket. **No busca por que falla** y **no reemplaza a QA**.

**Recibes:**
```
| Ticket | Titulo | Pts | Veredicto | Criterios |
| #123 | Filtrar operaciones por fecha | 3 | ✅ VB PO | 3/3 |
| #130 | Total con IVA en el resumen | 5 | ⚠️ Observado | 1/3 — el total no incluye el IVA |
¿Publico las fotos y el resultado en cada ticket?
```

---

## Caso 5 — Algo quedo observado

**Que escribes:**
```
/po-team:refinar --observacion #130
```
**Que hace el equipo:** redacta la observacion en lenguaje de negocio (que se esperaba, que se vio,
en que ambiente y cuando) con las fotos dentro del ticket, y lo devuelve a desarrollo. Si lo
observado es algo distinto a lo que pedia la historia, propone un bug nuevo relacionado.

---

## Caso 6 — El acta para el cliente y su VB

**Que escribes:**
```
/po-team:documento aceptacion #102
```
**Recibes** el acta en PDF y Word: que se entrega, cada criterio con su resultado y su foto, donde
y cuando se valido, las observaciones pendientes y el espacio para la firma del cliente.

Cuando el cliente responde que esta conforme:
```
/po-team:refinar --vb-cliente #102
```
El equipo te pregunta quien dio el VB, cuando y por que medio (correo, acta firmada, reunion), y
lo deja registrado en el ticket. Cerrar el ticket es una decision tuya.

---

## Caso 7 — Un manual para QA y otro para los usuarios

**Que escribes:**
```
/po-team:manual aprobar una operacion como Jefe Comercial --ambiente demo-co
```
**Que hace el equipo:** recorre el flujo una vez en el sistema y escribe dos manuales del mismo
recorrido:
- **Manual QA:** que se necesita antes, con que perfil y datos, cada paso numerado con lo que
  deberia pasar, y una lista para verificar el resultado.
- **Manual de usuario:** en palabras simples, una foto por paso con numeros que señalan donde
  hacer clic, consejos y preguntas frecuentes.

**Recibes** ambos en PDF (y Word, y la version web).

---

## Caso 8 — El informe del sprint para gerencia

**Que escribes:**
```
/po-team:documento sprint 12
```
**Recibes** un informe en PDF y Word: objetivo del sprint, puntos comprometidos y logrados por
etapa, resultado de cada ticket, fechas comprometidas versus reales, riesgos y proximos pasos.

---

# Parte 3 — Preguntas frecuentes y problemas comunes

**¿Tengo que saber programar?** No. Todo se pide y se recibe en lenguaje normal.

**¿El equipo cambia cosas en el tablero sin preguntarme?** No. Siempre te muestra el plan antes.
Mirar el tablero, el informe y el estado no cambia nada.

**¿La revision rapida del PO reemplaza a QA?** No. QA hace la prueba completa; el PO revisa que
se cumpla lo pedido por el camino normal antes de mostrarlo al cliente.

**¿Por que el revisor no me dice por que falla algo?** Porque su trabajo es mostrar que no se
cumple, con la foto. La causa la busca el equipo de desarrollo.

**¿Puedo usarlo con Azure DevOps?** Si. Se elige al configurar.

**¿Funciona junto con la Mesa de Servicios y el equipo de desarrollo?** Si. Usan carpetas
distintas. La Mesa deja el pedido; este equipo lo refina y lo sigue; desarrollo lo recibe como
ticket.

**¿Quien ve el panel publicado?** Solo tu, hasta que decidas compartirlo.

## Si algo no anda

- **"No puedo leer el tablero"** → `/po-team:setup tracker` (permiso de lectura de Projects).
- **"Hay tickets 'sin etapa' en el panel"** → un estado del tablero no esta asignado a ninguna
  etapa: `/po-team:setup tracker`.
- **"El revisor no puede abrir el sistema"** → revisa la cuenta de prueba y el ambiente:
  `/po-team:setup ambientes`.
- **"No genera el PDF o el Word"** → `/po-team:setup documentos`.

---

# Anexo tecnico (para quien instala y configura)

## A. Instalacion y actualizacion

```bash
# 1. Agregar el marketplace (una sola vez)
/plugin marketplace add faast-app/faast-claude-marketplace

# 2. Instalar el plugin
/plugin install po-team@faast-marketplace

# 3. Actualizar cuando haya cambios publicados
claude plugin marketplace update faast-marketplace
claude plugin update po-team@faast-marketplace
# → reiniciar la sesion de Claude Code despues de actualizar
```

**Requisitos** (el agente `setup` los valida e instala con una confirmacion): git · `gh` con los
permisos `project` y `read:project` (`gh auth refresh -s project,read:project`), o `az` con la
extension de Boards · Node.js ≥ 18 (el servidor Playwright MCP viene incluido) y el navegador
(`npx playwright install chromium`) · LibreOffice (`soffice`) para PDF y Word · python3.

## B. Configuracion

Todo vive en `.po-team/config.json` (lo crea `setup` desde `templates/po-team/config.json`):

| Campo | Efecto |
|---|---|
| `tracker.provider` | `github` o `azure` |
| `tracker.github.org` / `repoDefault` / `repos` | Donde se crean y leen HUs y bugs |
| `tracker.github.projects[]` | Projects (numero, alias) y nombres de campos: Status, puntos, sprint, prioridad, fechas |
| `tracker.etiquetas` | Etiquetas de HU, bug, VB PO, observado PO, VB cliente, cliente y ambiente |
| `tracker.reglas.estadosSoloQA` | Estados que solo mueve QA humana (el equipo nunca los asigna) |
| `tracker.reglas.cerrarIssues` | Si el equipo puede cerrar issues (por defecto `false`) |
| `ciclo.etapas[]` | Que estados y/o etiquetas del tablero corresponden a cada etapa del ciclo |
| `ciclo.estadosObservado` / `estadosBloqueado` / `diasAlertaSinMovimiento` | Alertas del tablero |
| `ambientes` | Desa, QA, Demo por pais y Preprod por cliente: nombre, URL, variables de cuentas, `paseEnLote` |
| `clientes[]` | Codigo, nombre y ambientes de cada cliente |
| `capacidad` / `estimacion` | Puntos por sprint, uso de velocidad, escala y maximo por sprint |
| `redaccion.prefijoAmbienteEnBugs` | Titulo de bugs de Demo/Preprod con prefijo del ambiente |
| `evidencia` | Repo, rama (`evidence`) y carpeta donde se publican las fotos para verlas en el ticket |
| `documentos` / `manuales` / `tablero` | Carpetas de salida, aprobadores del acta, URL del panel publicado |
| `team.models` | Subir un integrante a un modelo mas potente (default `sonnet`; `setup` fijo en `haiku`) |

**Cuentas de prueba**: `.po-team/accesos.env` (nunca en git); el equipo solo usa el NOMBRE de la
variable.

## C. La carpeta del equipo

```
.po-team/
├── config.json            configuracion
├── backlog.md             espejo: una linea por item refinado
├── sprints/{sprint}.json  objetivo, capacidad, comprometidos, sacados, fechas, riesgos
├── tickets/{numero}/      validaciones (fotos + validacion.md) y capturas para documentos
├── tickets/lote-*.md|json resultados de validaciones en lote (insumo del panel)
├── tablero/               tablero-datos.json · tablero.html · snapshots/ · informes/
├── documentos/            documentos de negocio (HTML, PDF, DOCX)
├── manuales/{flujo}/      recorrido, capturas y los dos manuales
├── evidencia/_mcp/        temporal del navegador — gitignored
├── handoffs/              notas entre integrantes
├── metrics/activity.jsonl actividad automatica
├── accesos.env            cuentas de prueba — NUNCA en git
└── setup-status.json      estado del entorno — NUNCA en git
```

## D. Solucion de problemas tecnicos

| Sintoma | Causa probable | Que hacer |
|---|---|---|
| `gh` no lee el Project | Falta el permiso | `gh auth refresh -s project,read:project` |
| No aparecen las herramientas `browser_*` | Sesion vieja | Reiniciar Claude Code; `claude mcp list` |
| Varios servidores `playwright` | dev-team y mesa-servicios instalados | Normal: cada plugin trae el suyo con su carpeta. Quitar solo uno personal duplicado |
| El PDF sale sin acentos | Conversion incorrecta | `/po-team:setup documentos` (prueba real) |
| Tickets "Sin etapa" | Mapeo incompleto | Completar `ciclo.etapas[].estados` con `/po-team:setup tracker` |
| El panel no se publica | La sesion no tiene la herramienta de artifacts | Se entrega el archivo local `tablero.html` |
