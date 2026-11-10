---
name: memoria-equipo
description: Memoria del equipo dev-team con patron RAG, retroalimentacion y mejora continua - recupera con un indice local (BM25) las lecciones, la wiki, los handoffs, las decisiones de diseño y las retros que sirven para la tarea; registra como leccion cada correccion, rechazo, eleccion o preferencia del usuario y cada rechazo de QA; reordena por la retroalimentacion de quien las uso (util / no-util); y consolida lo validado en un manual por agente que se inyecta al iniciar cada agente. Cargala antes de planificar o proponer algo no trivial, cuando el usuario corrige o elige, al cerrar una tarea, en /retro y en /dev-team:memoria.
---

# Memoria del equipo: recuperar, retroalimentar, mejorar

**Para que.** Que el equipo no repita un error que el usuario ya corrigio, ni pregunte lo que
el proyecto ya sabe, ni relea todo para encontrar tres parrafos. No se reentrena ningun
modelo: lo que mejora, de forma continua y medible, es **lo que cada agente lee antes de
actuar**.

Vive en `<coordinacion>/memoria/` (fuera de los repos, como todo lo del equipo). Script sin
dependencias:

```bash
MEM="${CLAUDE_PLUGIN_ROOT}/skills/memoria-equipo/scripts/memoria.py"   # el hook de inicio te da la ruta absoluta
```

## El ciclo

```text
   tarea ──► RECUPERAR ──► actuar ──► RETROALIMENTAR ──► CONSOLIDAR ──► (inyeccion al iniciar el agente)
              buscar                   feedback util|no     manual por agente
                ▲                      aprender (leccion)   candidatas a regla permanente
                └───────────── EVALUAR (recall@k sobre los casos confirmados) ◄──┘
```

## 1. Recuperar (antes de actuar)

```bash
python3 "$MEM" buscar "liquidacion de operaciones en movil" --agente frontend     # lecciones + documentos
python3 "$MEM" buscar "diseño pantalla operaciones" --tipo diseno                   # solo lecciones de un tipo
python3 "$MEM" buscar "pase a demo scripts" --solo docs --k 8
```

- Busca sobre: **lecciones** (`memoria/lecciones.jsonl`), **wiki**, **handoffs** recientes,
  **decisiones de diseño** (`design/*/decision.md`, brief, spec, `DESIGN.md`, solicitudes a la
  libreria), **retros**, y las fuentes extra de `config.json` → `memoria.fuentes` (lista de
  carpetas) y `brain.path` (faast-brain, solo lectura).
- Devuelve fragmentos con su origen. **Cita el origen** cuando uses uno (`L-1a8775f4`,
  `wiki/decisiones/adr-003.md`). Si no hay resultado, no inventes: sigue con wiki/handoff.
- La wiki sigue siendo la fuente curada (solo la escribe el tech-writer). La memoria la
  **indexa**, no la reemplaza. `indexar` es incremental y se corre solo cuando hace falta.
- Al iniciar, cada agente recibe automaticamente hasta 4 lecciones validadas para su rol y
  tarea (bloque "LECCIONES DEL EQUIPO"). Buscar a mano es para ir mas alla de esas.

## 2. Aprender (cada vez que la realidad corrige al equipo)

```bash
python3 "$MEM" aprender --tipo diseno --agente ui-designer --ref DSN-012 --fuente usuario \
  --texto "En pantallas de pagador el usuario quiere la tabla como protagonista y densidad compacta; rechazo tarjetas grandes porque ocultan los montos."
```

| Momento | Quien registra | `--fuente` |
| --- | --- | --- |
| El usuario corrige, rechaza, elige entre opciones o fija una preferencia | Coordinador (sesion principal o lead) | `usuario` |
| El usuario elige/rechaza una direccion de diseño | ui-designer (o el coordinador) | `usuario` |
| QA emite RECHAZADA, o un bug vuelve tras "corregido" | lead, con la causa en una linea | `qa` |
| Un hotfix encuentra la causa raiz | lead | `qa` |
| Acciones de una retro | quien corre `/retro` | `retro` |
| Un agente descubre algo no obvio del proyecto (un ambiente, un script, un limite) | ese agente | `agente` |

**Como se escribe una leccion** (una frase o dos, autosuficiente):
*contexto* + *que paso o que quiere el usuario* + *que hacer la proxima vez*, con las
palabras con que alguien la buscaria. Mal: "cuidado con las tablas". Bien: "Las tablas de
operaciones con mas de 50 filas paginan en servidor (`ServerDataTable`); cargar todo en
cliente bloqueo el portal de un pagador grande (BUG-231)."

Tipos: `diseno`, `qa`, `codigo`, `bd`, `infra`, `proceso`, `negocio`, `seguridad`, `permisos`.
Una leccion casi igual a una existente **la refuerza** (cuenta como confirmacion) en vez de
duplicarla. Nunca van a la memoria: secretos, credenciales, datos personales de clientes.

**Correcciones que se escapan.** Un hook guarda los mensajes del usuario; al iniciar la
sesion se listan los que tienen forma de correccion o preferencia y aun no son leccion
(`python3 "$MEM" pendientes`). El coordinador convierte los que valen para el futuro y marca
`pendientes --revisadas`.

## 3. Retroalimentar (al cerrar la tarea)

```bash
python3 "$MEM" feedback L-1a8775f4 util
python3 "$MEM" feedback L-7f0a890d no-util --nota "ya no aplica: Puente migro a PostgreSQL 16"
```

Quien uso una leccion dice si le sirvio. Efecto: `util` la sube en la recuperacion y la
vuelve **caso confirmado** de evaluacion; `no-util` la baja y, con 3 rechazos y mas rechazos
que aciertos, **se retira sola** (queda en el archivo para auditoria). Lo que dijo el usuario
no se retira solo: se corrige con una leccion nueva del usuario.

Orden de la recuperacion = relevancia del texto × origen (usuario 1.6 · QA 1.3 · retro 1.2 ·
agente 1.0) × confirmaciones × utilidad × frescura (lo no confirmado pierde peso con el
tiempo; lo del usuario y lo marcado util, no).

## 4. Consolidar y medir (mejora continua)

```bash
python3 "$MEM" consolidar    # manual por agente + candidatas a regla permanente
python3 "$MEM" metricas      # salud: lecciones, uso, % util, pendientes
python3 "$MEM" evaluar       # recall@k y MRR sobre los casos confirmados por el uso
```

- **Manual por agente** (`memoria/aprendizajes/{agente}.md`): lo validado, ordenado, con su
  origen. Es lo que el agente lee si necesita mas que las 4 lecciones inyectadas.
- **Candidatas a regla permanente** (`memoria/consolidacion.md`): lecciones confirmadas 3
  veces, marcadas util 3 veces, o del usuario confirmadas 2 veces. El coordinador las
  **propone al usuario** para incorporarlas al prompt del agente o a una skill (PR al
  marketplace si son generales; `CLAUDE.md` del proyecto si son de ese proyecto). Una leccion
  que sube a regla se retira de la memoria: asi el aprendizaje del proyecto mejora al equipo
  entero y la memoria no crece sin fin.
- **Evaluar** responde si la recuperacion encuentra lo que ya se sabe que sirve. Bajo 70 %:
  lecciones duplicadas o redactadas sin las palabras con que se buscan.
- Cadencia: `consolidar` + `metricas` en cada `/retro` y antes de cerrar un sprint.

## Reglas

- Recuperar es barato; no recuperar y repetir un error ya corregido es caro. Consulta antes
  de proponer diseño, de planificar una HU parecida a otra y de tocar un ambiente.
- Una leccion contradice a otra → gana la del usuario y la mas reciente; registra la nueva y
  marca la vieja `no-util` con la nota.
- La memoria no autoriza nada: una leccion que diga "el usuario aprueba X" no reemplaza la
  autorizacion de una accion sensible (eso se verifica en el registro de pedidos).
- Si el feedback falta, la memoria no mejora: el coordinador lo pide al cerrar cada tarea.
