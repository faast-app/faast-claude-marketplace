# po-team — Equipo del Product Owner

Equipo de 8 agentes IA (9 comandos) que acompaña al **Product Owner**: toma lo que llega de la
**Mesa de Servicios**, lo deja **listo para desarrollo** (HUs y bugs en lenguaje de negocio con
criterios Gherkin y estimacion Fibonacci), planifica el sprint con sus **fechas de pase**, sigue
cada ticket por el ciclo FaaST en un **tablero** con avance por puntos, hace la **validacion
funcional rapida del PO** y produce **documentos de negocio** y **manuales de usuario**, hasta
conseguir el **VB del cliente**.

```
Mesa de Servicios ──► po-team ──(tickets en GitHub/Azure)──► equipo de desarrollo
                         │
   Desarrollo → Validacion QA → Pase a Demo → Validacion Demo / Preprod → VB cliente
```

## Instalacion

```bash
/plugin marketplace add faast-app/faast-claude-marketplace
/plugin install po-team@faast-marketplace
```

## Uso

```bash
/po-team:start
```
Eso es todo: detecta si el equipo esta configurado y te guia. La primera vez corre el `setup`
(herramientas y tablero, con una confirmacion) y crea `.po-team/config.json` preguntando una sola
vez organizacion, repos, Projects, mapeo de estados a etapas, ambientes, clientes y capacidad.

## Comandos
| Comando | Que hace |
|---|---|
| `/po-team:start` | Punto de entrada unico: entiende lo que pides en tus palabras y te lleva al flujo |
| `/po-team:refinar` | HUs y bugs en lenguaje de negocio (INVEST, 3-8 criterios Gherkin con bordes, Definition of Ready), estimacion; bugs solo reproducidos; observaciones; VB del cliente |
| `/po-team:sprint` | Sprint por capacidad, orden con metodo visible, filtro DoR, fechas de pase (Demo, Preprod, VB) y riesgos; `cierre N` hace review + retro desde los datos |
| `/po-team:tablero` | Te pregunta cual quieres: tablero generico, Organizacion PO, validaciones del sprint, o crear un backlog nuevo en GitHub. Estado real del Project, avance por puntos, cambios, informe diario/semanal y dashboard HTML (artifact si se puede) |
| `/po-team:validar` | Validacion funcional rapida del PO (VB PO / Observado), un ticket, lista o `--lote sprint N`; `--reproducir` confirma un reporte antes de registrar el bug; `--revalidar #n` prueba el arreglo con par antes/despues; `--video` a tamaño real; `--artifact` publica el informe de validaciones |
| `/po-team:documento` | `hu`, `especificacion`, `aceptacion` (acta) o `sprint` en PDF + DOCX |
| `/po-team:manual` | Manual de un flujo en version QA y version para cualquier persona (HTML + PDF + DOCX), con recorrido repetible (`steps.yaml`) para actualizarlo |
| `/po-team:estado` | Vistazo rapido sin consultar el tracker |
| `/po-team:setup` | Prerequisitos y configuracion del tablero |

## El equipo
| Agente | Rol | Modelo |
|---|---|---|
| **po-lead** | Coordina, decide que sigue, escala; presenta el plan antes de escribir en el tracker; unico que delega | sonnet |
| **refinador** | HUs y bugs 100% negocio, INVEST, Gherkin con bordes, DoR, Fibonacci; bugs solo reproducidos y su ciclo hasta la revalidacion; lee faast-brain; crea/actualiza en GitHub o Azure | sonnet |
| **planificador** | Sprint por capacidad, orden (MoSCoW + valor/riesgo/esfuerzo), filtro DoR, fechas de pase, riesgos; cierre con review + retro | sonnet |
| **seguimiento** | Lee el Project (ProjectV2 via `gh api graphql`), avance, cambios, informe y dashboard | sonnet |
| **validador-po** | Validacion funcional rapida con Playwright MCP, una captura por criterio, modo lote; reproducir (REPRODUCIDO / NO REPRODUCIDO / BLOQUEADO) y revalidar con video. Respeta la clase del ambiente. **No reemplaza a QA** | sonnet |
| **documentador** | Documentos de negocio desde plantilla, HTML → LibreOffice → PDF/DOCX | sonnet |
| **manualista** | Manual QA + manual general del mismo recorrido, capturas anotadas, `steps.yaml` repetible | sonnet |
| **setup** | git, gh (scopes project/read:project), Playwright MCP, LibreOffice, python3; configura el tracker | haiku |

Override de modelo por agente en `.po-team/config.json` → `team.models` (o
`~/.claude/po-team.config.json`); `setup` queda fijo en haiku; `fable` nunca.

## Skills incluidas
`redaccion-negocio` · `estimacion-fibonacci` · `ciclo-pase-faast` · `validacion-funcional-po` ·
`manual-dual` · `evidencia-po` · `dashboard-po`. El plugin es autocontenido: no necesita que
dev-team ni mesa-servicios esten instalados.

## Principios
- **Plan primero**: nada se escribe en el tracker (crear, editar, mover, comentar, subir
  evidencia) sin mostrar el plan y recibir el OK.
- **El validador-po no reemplaza a QA**: valida solo los criterios por el camino normal; nunca
  mueve estados reservados a QA ni cierra tickets.
- **El PO redacta funcional**: lenguaje de negocio, titulos limpios, criterios Gherkin.
- **Evidencia embebida** en el ticket via rama `evidence`, nunca link suelto; secretos y datos
  personales redactados.
- **Nada hardcodeado**: org, Projects, campos, estados, ambientes, clientes y personas viven en el
  config.
- **Bugs solo reproducidos**: un error reportado se reproduce (Mesa o `--reproducir`) antes de
  registrarse; el arreglo se revalida con par antes/despues en el mismo issue.
- **Ambientes por clase**: en `pruebas` las acciones de negocio son normales; en `productivo` el
  equipo solo mira salvo autorizacion por accion. La clase se declara, nunca se presume.
- **Nada dentro de un repo**: estado y memoria en `.po-team/`, en la carpeta del proyecto o del
  PO, nunca dentro de un repositorio (un hook lo bloquea; registro
  `~/.claude/po-team.config.json` → `proyectos`). Separado de `.mesa/` y `.coordination/`: pueden
  convivir.
- **Pendientes que no se caen**: lo que espera respuesta del PO, la Mesa o el cliente se lista al
  abrir cada sesion.

## Relacion con los otros plugins
- **mesa-servicios** esta antes: deja el requerimiento cerrado, documentado y registrado. po-team
  lo lee del ticket y lo refina; si falta algo, devuelve preguntas a la Mesa (no al cliente). Si
  la Mesa tiene `faast-brain`, po-team lo LEE (nunca escribe) para usar el vocabulario del negocio.
- **dev-team** (o cualquier equipo de desarrollo) esta despues: recibe el trabajo **solo como
  tickets** en el tracker. po-team no invoca sus agentes (el hook lo bloquea). Las solicitudes de
  pase las hace desarrollo/release; el PO fija las fechas y valida.
- Si conviven los tres, cada uno trae su propio servidor Playwright MCP con su carpeta de
  evidencia; no hace falta uno personal.

Manual completo en lenguaje de negocio: [GUIDE.md](GUIDE.md).
