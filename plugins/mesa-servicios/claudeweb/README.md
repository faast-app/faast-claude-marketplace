# Mesa de Servicios en Claude web — skill `refinamiento-a-requerimiento`

Versión **simplificada** de la Mesa de Servicios para usar en **Claude (claude.ai)** como
*capability* de la organización, sin herramientas locales (sin Playwright, sin CLI de GitHub, sin
transcripción local). Mantiene la filosofía del plugin `mesa-servicios`: nada se inventa, lenguaje
de negocio, alcance delimitado y aprobado, correlativo y alcance en todo documento.

## Qué contiene

```
refinamiento-a-requerimiento/
├── SKILL.md                      instrucciones principales (las cuatro salidas, fases, reglas)
├── references/                   documentos de instrucciones que la skill consulta según el caso
│   ├── tipos-y-correlativo.md    BUG · PRY · CTZ · CC, correlativo TIPO-AÑO-NNN, alcance, etiquetas
│   ├── contexto-del-sistema.md   insumos, faast-brain, fichas, pedido consolidado, aprendizaje
│   ├── preguntas.md · checklist-completitud.md · casos-de-borde.md · casuisticas.md · impactos.md
│   ├── redaccion.md              lenguaje por documento, términos prohibidos, IDs
│   ├── formato-bug.md            formato de bugs del equipo
│   └── github.md                 proyecto #38, campos, etiquetas, comandos
├── assets/                       plantillas de los documentos que emite
│   ├── plantilla-bug.md                 BUG
│   ├── plantilla-propuesta.md           PRY: propuesta funcional (visto bueno del solicitante)
│   ├── plantilla-especificacion.md      PRY: especificación (issue de backlog)
│   ├── plantilla-cambio-menor.md        PRY menor: ficha única
│   ├── plantilla-proyecto.md            PRY grande: documento de proyecto (fases, hitos, riesgos)
│   ├── plantilla-cotizacion.md          CTZ: cotización (valorización la pone comercial)
│   ├── plantilla-control-cambio.md      CC: control de cambio sobre algo aprobado
│   ├── maqueta-base.html                maqueta tipo boceto (artefacto HTML navegable)
│   ├── registro-correlativos.md         el registro de números (se guarda en el Proyecto de Claude)
│   ├── plantilla-ficha-contexto.md · plantilla-aprendizajes-generales.md
└── scripts/                      validador de requerimientos, extractor de fórmulas de Excel, anotador de capturas
```

## Cómo subirla a la organización (claude.ai)

1. Genera el paquete (o usa el `.skill` que está junto a esta carpeta):
   ```bash
   python3 -m scripts.package_skill plugins/mesa-servicios/claudeweb/refinamiento-a-requerimiento plugins/mesa-servicios/claudeweb
   ```
   (se ejecuta desde la carpeta de la skill `skill-creator`; valida nombre, descripción y estructura).
2. En claude.ai, con rol de administrador: **Configuración de la organización → Capabilities / Skills →
   Subir skill** y selecciona `refinamiento-a-requerimiento.skill`. Habilítala para los equipos de
   MDS e Implementaciones.
3. Crea un **Proyecto de Claude** "Mesa de Servicios" y sube ahí: el `registro-correlativos.md`
   (vivo), las fichas de contexto por módulo, los aprendizajes generales y, si existe, el contenido
   de **faast-brain** (productos, clientes, procesos, reglas, glosario). La skill lee eso antes de preguntar.

## Cómo se usa (quien atiende la mesa)

Pega o adjunta lo que llegó (ticket, correo, transcripción de Teams, documento, Excel) y pide:
"refina esto", "¿es un bug?", "cotízame esto", "el cliente cambió lo que aprobamos". La skill:
1. Clasifica la salida: **BUG / PRY / CTZ / CC**, asigna correlativo y alcance.
2. Lee el contexto del Proyecto, confirma lo sabido y pregunta solo lo que falta (rondas de hasta 7,
   tope 3), con opciones para responder por dictado. Tú llevas las preguntas al cliente y traes las respuestas.
3. Ofrece una **maqueta tipo boceto** si hay pantallas (artefacto que el cliente recorre).
4. Emite el documento desde la plantilla, en Markdown y, si lo pides, **Word / PDF**.
5. Entrega el cuerpo del **issue** con sus etiquetas (y lo crea si hay conector a GitHub).
6. Propone guardar lo aprendido (ficha del módulo / faast-brain).

## Diferencias con el plugin `mesa-servicios` (Claude Code)

| | Plugin (Claude Code) | Skill (Claude web) |
|---|---|---|
| Fuentes de audio/video | Transcribe en la máquina (Whisper) | Pega la transcripción que genera Teams/Meet |
| Reproducir bugs | QA de negocio graba todo con Playwright | Pide y organiza las evidencias del cliente; QA valida después |
| Scripts de datos | DBA de mesa arma paquetes (cero escritura) | Fuera de alcance: se deriva al DBA |
| Maqueta | Prototipador con capturas automáticas | Artefacto HTML que el cliente recorre |
| Ticket | Lo crea el registrador con `gh` | Cuerpo listo + comandos, o conector a GitHub |
| Correlativo | Archivo `correlativos.json` automático | Registro en el Proyecto de Claude |
| Memoria del negocio | Repo `faast-brain` curado | Archivos del Proyecto de Claude |

## Regenerar el `.skill` después de editar

Edita los archivos de `refinamiento-a-requerimiento/`, vuelve a ejecutar el empaquetado (paso 1) y
sube la nueva versión en claude.ai (reemplaza la anterior).
