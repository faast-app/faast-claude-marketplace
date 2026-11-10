# Cambios

Que trae cada version de los plugins. Una entrada por subida de version, lo mas nuevo arriba.

## Sin publicar

- **Agentes mas livianos, medidos:** las reglas comunes de los 49 agentes se reescribieron mas
  cortas (unos 80 kB menos en total) y el agente lider de QA paso su catalogo de borde fintech y
  el instructivo de Playwright a referencias que lee cuando las necesita. Comprobado con las
  evaluaciones de comportamiento de QA antes y despues: ninguna regla dura bajo.
- **La brevedad es para el chat:** el mensaje del agente tiene forma fija y cabe en una pantalla;
  los informes de QA, los comentarios en el ticket con evidencia y los documentos conservan todo
  su detalle.
- **Evaluaciones de comportamiento de QA** (`plugins/dev-team/evals/`, 12 casos).

## dev-team 2.20.0 · mesa-servicios 1.3.0 · po-team 1.2.0 · marketing 1.2.0

- **Calidad del repo:** validador estructural (`tools/validar.py`), pruebas automaticas de los
  hooks y scripts de los cuatro equipos (`tests/`) y revision en Windows, macOS y Linux en cada
  PR (`.github/workflows/ci.yml`).
- **Los hooks ya no fallan en silencio:** cualquier error queda en `~/.faast-mcp/logs/hooks.log`.
- **QA avanzado (dev-team):** skill `qa-avanzado` con puertas condicionales 8-11 (tiempo,
  rendimiento, otros navegadores, calidad de los tests del desarrollador), revision de
  testabilidad antes del desarrollo e indice de confianza del veredicto. La plantilla de pruebas
  trae reloj controlado, presupuesto de Core Web Vitals, WebKit y Firefox para flujos criticos,
  foto de la estructura accesible, barrido de contrato sin bash y suite repartida en 3 maquinas.
- **`/diagnostico` en los cuatro equipos:** revisa la maquina, los hooks, la carpeta y la
  configuracion del proyecto y los ultimos fallos, y lo cuenta en lenguaje claro.
- **Guardia de repos en Windows:** reconoce rutas con unidad y barra invertida en comandos, y
  deja de bloquear la lectura de archivos `.md`.

## dev-team 2.19.0 · mesa-servicios 1.2.0 · po-team 1.1.0 · marketing 1.1.0

- **Diseño heredado de la libreria UI de FaaST** (dev-team): skills `libreria-faast`,
  `taste-faast`, `web-interface-guidelines` y `vercel-react-patterns`; toda propuesta usa el kit
  de `@faast-app` (0.8.0) y pasa la puerta `HERENCIA: PASA`.
- **Memoria del equipo** (dev-team): `/memoria`, lecciones con retroalimentacion, inyeccion al
  iniciar cada agente.
- **Canal unico con el usuario** (todos): ningun agente pide "escribeme en mi hilo"; la
  autorizacion reenviada se verifica en el registro de mensajes del usuario.
- **Permisos** (todos): una herramienta denegada no se reintenta ni se rodea; el informe se
  escribe una sola vez si `SubagentHandback` es rechazada; `/dev-team:setup permisos`.
- **Cualquier sistema y terminal** (todos): hooks sin bash con lanzador en Node, Python con
  cualquier nombre, salida UTF-8, Playwright sin `npx` directo, instalacion de Node y Python si
  faltan.
- **Comunicacion clara** (todos): un mensaje un proposito, resultado primero en lenguaje
  sencillo, preguntas aparte y pocas.
