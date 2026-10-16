---
description: El Product Owner arma y mantiene un GitHub Project v2 completo desde una propuesta, plan o lista - fases con condicion de salida (milestones), epicas por categoria con sub-issues, historias de negocio con Gherkin (issues reales, nunca borradores), campos Fase/Categoria/Prioridad/Tipo/Status, etiquetas, vistas y espejo local. Plan primero (modo prueba) y escritura solo con OK del usuario. Subcomandos - crear, agregar, verificar, espejo. Uso - /dev-team:project {subcomando}
argument-hint: 'crear {ruta a propuesta/plan o texto} [--project "Nombre"] | agregar {pedido o ruta} [--project "Nombre"] | verificar [--corregir] | espejo'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Project: backlog completo en un GitHub Project

Pedido: $ARGUMENTS

Aplica el procedimiento del agente `product-owner` siguiendo la skill `github-project-backlog`
(cargala: reglas duras, redaccion por tipo de item, trampas conocidas). El trabajo pesado lo
hace el script idempotente:

```bash
S="${CLAUDE_PLUGIN_ROOT}/skills/github-project-backlog/scripts/project_backlog.py"
```

Diferencia con `/dev-team:refine`: refine crea UNAS pocas HUs sueltas; este comando arma (o
completa) un **Project entero** ordenado por fases y categorias.

## Paso 0: Contexto (todos los subcomandos)
1. Leer `.coordination/config.json` → `tracker`. Si `provider` es `azure`, avisar que este
   comando es para GitHub Projects y sugerir `/dev-team:refine`. Si no hay config, sirve igual
   (se pregunta lo necesario).
2. Tomar `org`, `repo` (repo de issues) y `project` (nombre EXACTO) de `tracker.github`; lo
   que falte (o `--project` si viene en el pedido) se pregunta **una sola vez**, todo junto.
   Si el tema aun no tiene repos propios, los issues van al repo transversal del proyecto:
   nunca se crea un repo sin autorizacion.
3. `gh auth status`: si no hay sesion o falta el scope `project`, decirlo y parar
   (el usuario corre `gh auth refresh -s project`). Si falta `gh` → `/dev-team:setup`.
4. Leer la wiki (`.coordination/wiki/`) y `.coordination/backlog.md` antes de redactar, para
   no duplicar lo que ya existe.

## `crear {fuente}` — Project completo desde una propuesta, plan o lista
1. **Leer la fuente completa** (ruta .md/.docx/.pdf/.txt, handoffs o texto libre). Si hay
   ambiguedades criticas, MAXIMO 3 preguntas concretas al usuario.
2. **Derivar** fases (con titulo, objetivo y condicion de salida verificable), categorias (con
   descripcion; seran las epicas), items por fase (historias, decisiones, riesgos, tareas de
   negocio), riesgos y decisiones abiertas, y lo que ya esta hecho (estado `Hecho`).
3. **Redactar** cada item en lenguaje 100% de negocio con la estructura de la skill
   (historias con Como/Quiero/Para y Gherkin; decisiones con quien decide y criterio de
   cierre; riesgos con como lo reducimos). Cada fase termina con su "Salida de la Fase N"
   (si no la redactas, el script la genera desde la condicion de salida).
4. **Escribir el spec** JSON (formato en la skill; ejemplo en
   `${CLAUDE_PLUGIN_ROOT}/skills/github-project-backlog/assets/spec-ejemplo.json`) y guardarlo
   junto al estado, fuera de todo repo: `.coordination/project-state/<nombre>.spec.json` en la
   carpeta paraguas, o `~/.dev-team/project-state/<nombre>.spec.json` en mono-repo.
5. **Plan primero (modo prueba)**: `python3 "$S" aplicar SPEC --dry-run`
   (o `--dry-run --offline` si todavia no hay acceso a GitHub). Mostrar al usuario el plan:
   que se crea / reutiliza / actualiza, items por fase con categoria, tipo, prioridad y estado,
   conteos planificados y advertencias de redaccion. Corregir el spec si hay avisos de jerga o
   historias sin Gherkin, y volver a mostrar el plan.
6. **Pedir confirmacion explicita** ("¿Creo esto en GitHub?"). Sin un si claro del usuario, no
   se escribe nada.
7. **Ejecutar**: `python3 "$S" aplicar SPEC`. Si se corta (rate limit, red), re-ejecutar el
   mismo comando: reanuda sin duplicar.
8. **Entregar** (ver "Entrega").

## `agregar {pedido o fuente}` — sumar items a un Project existente
1. Partir del spec guardado del Project (`<nombre>.spec.json`, o la clave `spec` del archivo de
   estado `<nombre>.json`). Si no existe (Project creado a mano o por otra via), armar uno con
   `org`, `repo`, `project`, y las fases y categorias tal como estan en el Project (mismos
   nombres; los milestones existentes se reutilizan con `"milestone": "<titulo exacto>"`).
2. Redactar SOLO los items nuevos con las mismas reglas y agregarlos al spec (una fase o
   categoria nueva tambien vale: el script agrega la opcion del campo, la etiqueta, el
   milestone o la epica que falte).
3. Plan con `--dry-run`: los existentes deben salir como `[REUTILIZAR]` y solo lo nuevo como
   `[CREAR]`. Revisar que no haya un item parecido ya creado con otro titulo (no duplicar).
4. Confirmacion del usuario → `python3 "$S" aplicar SPEC` → Entrega.
   En re-ejecuciones el script solo llena campos vacios: no pisa el Status que el equipo movio.

## `verificar [--corregir]` — revisar la salud del Project
1. Usar el spec guardado (o uno minimo con org, repo, project, fases y categorias).
2. `python3 "$S" verificar SPEC` (solo lectura): reporta borradores, items sin campos (el caso
   "Content already exists"), issues del proyecto fuera del Project, historias que no cuelgan de
   su epica, cerrados que no estan en Hecho, y conteos por Fase / Categoria / Status / Tipo.
3. Mostrar el reporte. Si hay hallazgos corregibles, pedir OK y correr
   `python3 "$S" verificar SPEC --corregir` (convierte borradores en issues, re-llena campos
   vacios desde el spec o las etiquetas, agrega lo que falta, enlaza sub-issues). Lo que no
   tiene dato (p. ej. prioridad) lo define el PO con el usuario.

## `espejo` — regenerar el backlog local
`python3 "$S" espejo SPEC --dry-run` para ver la seccion y luego `python3 "$S" espejo SPEC`
para escribirla al principio de `.coordination/backlog.md` (solo reemplaza su propia seccion
marcada; nunca borra lo demas). Escribir el espejo local no requiere confirmacion: no toca GitHub.

## Entrega
- URL del Project, conteo por fase y por categoria, 5 titulos de ejemplo y los avisos del script.
- Recordar lo pendiente manual: en cada vista marcar el **agrupamiento en la interfaz**
  (Tablero por Status, Tabla por Fase, Tabla por Categoria, Roadmap por Fase) — la API no lo
  permite. Tambien repos por crear y decisiones abiertas.
- Confirmar que `.coordination/backlog.md` y `config.json` → `tracker.github` quedaron
  actualizados (el script lo hace al ejecutar).
- Handoff `po-to-lead-{fecha}.md` con el link al Project y el orden recomendado por fase.
  Siguiente paso sugerido: `/dev-team:assign-task`.

## Reglas
- Nunca borradores: cada item es un issue real (`gh project item-create` esta prohibido).
- Lenguaje 100% de negocio en titulos y cuerpos; acentos en el texto, nombres de campos y
  etiquetas sin acentos.
- Plan primero y escritura en GitHub solo con pedido/confirmacion explicita del usuario.
- No se toca ningun ambiente ni se crean repos por armar el backlog.
- Reutilizar el Project si existe (nombre exacto); si hay dos con el mismo nombre, preguntar.
- El estado del script nunca va al directorio actual ni dentro de un repo git.
