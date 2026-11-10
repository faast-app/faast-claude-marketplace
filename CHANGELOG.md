# Cambios

Que trae cada version de los plugins. Una entrada por subida de version, lo mas nuevo arriba.

## Sin publicar

- **Calidad del repo:** validador estructural (`tools/validar.py`), pruebas automaticas de los
  hooks y scripts de los cuatro equipos (`tests/`) y revision en Windows, macOS y Linux en cada
  PR (`.github/workflows/ci.yml`).
- **Los hooks ya no fallan en silencio:** cualquier error queda en `~/.faast-mcp/logs/hooks.log`.
- **`/diagnostico` en los cuatro equipos:** revisa la maquina, los hooks, la carpeta y la
  configuracion del proyecto y los ultimos fallos, y lo cuenta en lenguaje claro.

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
