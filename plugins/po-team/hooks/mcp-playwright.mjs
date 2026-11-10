#!/usr/bin/env node
// Lanza el Playwright MCP del plugin en cualquier sistema operativo, sin bash.
//
//   node "<plugin>/hooks/mcp-playwright.mjs" [--secretos] [carpeta del proyecto]
//
// - En Windows `npx` es un .cmd que no se puede ejecutar sin shell, y `${HOME}` no existe: aqui
//   se resuelve la carpeta del usuario con el sistema y se lanza npx como corresponde.
// - Los archivos del MCP van a ~/.faast-mcp/<plugin>/ (fuera de cualquier repo).
// - --secretos: si la carpeta canonica del equipo tiene accesos.env, se pasa con --secrets (el
//   agente escribe el NOMBRE de la variable y el MCP sustituye y redacta el valor; el valor no
//   pasa por el modelo). Sin archivo se arranca sin secretos. Se lee al ARRANCAR el MCP.
import { spawn, spawnSync } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { buscarPython, entornoPython } from './_python.mjs'

const VERSION = '0.0.80'
const aqui = dirname(fileURLToPath(import.meta.url))
const plugin = JSON.parse(readFileSync(join(aqui, '..', '.claude-plugin', 'plugin.json'), 'utf8')).name
const args = process.argv.slice(2)
const conSecretos = args.includes('--secretos')
const dado = args.find((a) => !a.startsWith('--') && !a.startsWith('${'))
const proyecto = dado || process.env.CLAUDE_PROJECT_DIR || process.cwd()

const salida = join(homedir(), '.faast-mcp', plugin)
try {
  mkdirSync(salida, { recursive: true })
} catch {
  // si no se puede crear, el MCP lo intentara al escribir
}

const extra = []
if (conSecretos) {
  const python = buscarPython()
  if (python) {
    const [cmd, ...previos] = python
    const r = spawnSync(cmd, [...previos, join(aqui, 'coord_root.py'), proyecto], {
      encoding: 'utf8',
      env: entornoPython,
      timeout: 8000,
      windowsHide: true,
    })
    try {
      const d = JSON.parse(r.stdout)
      const accesos = d.path && !d.en_repo ? join(d.path, 'accesos.env') : ''
      if (accesos && existsSync(accesos)) extra.push(`--secrets=${accesos}`)
    } catch {
      // sin carpeta del equipo: se arranca sin secretos
    }
  }
}

const mcp = [
  '-y',
  `@playwright/mcp@${VERSION}`,
  '--browser=chromium',
  '--caps=testing,devtools,vision',
  '--isolated',
  `--output-dir=${salida}`,
  '--test-id-attribute=data-testid',
  '--timeout-action=8000',
  '--timeout-navigation=45000',
  '--console-level=warning',
  '--ignore-https-errors',
  ...extra,
]

const windows = process.platform === 'win32'
// En Windows hace falta shell para el .cmd; las rutas con espacios van entre comillas.
const hijo = windows
  ? spawn('npx.cmd', mcp.map((a) => (/\s/.test(a) ? `"${a}"` : a)), { stdio: 'inherit', shell: true, windowsHide: true })
  : spawn('npx', mcp, { stdio: 'inherit' })

hijo.on('error', (e) => {
  process.stderr.write(`No se pudo lanzar el Playwright MCP (¿falta Node.js/npx?): ${e.message}\n`)
  process.exit(1)
})
hijo.on('exit', (codigo, senal) => process.exit(senal ? 1 : (codigo ?? 0)))
for (const s of ['SIGINT', 'SIGTERM']) process.on(s, () => hijo.kill(s))
