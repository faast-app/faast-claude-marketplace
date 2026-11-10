#!/usr/bin/env node
// Lanzador de hooks multiplataforma: ejecuta un hook Python del plugin sin depender de bash.
//
//   node "<plugin>/hooks/run.mjs" <script.py> [args...] [--avisar]
//
// Por que existe: en Windows (PowerShell, cmd, Windows Terminal) no hay bash, asi que los
// envoltorios .sh fallaban y el protocolo del equipo no se cargaba; ademas el interprete no se
// llama `python3` sino `python` o `py`. Este lanzador:
//   - busca Python 3 (FAAST_PYTHON, luego python3/python/py segun el sistema) y descarta el
//     alias de la Microsoft Store, que no es un Python real;
//   - pasa el stdin del hook (el payload JSON) y devuelve stdout, stderr y el codigo de salida;
//   - fuerza UTF-8 para que acentos y simbolos no rompan la salida en la consola de Windows;
//   - `@project` en los argumentos se reemplaza por la carpeta del proyecto, y
//     `--proyecto <carpeta>` la fija (sirve igual en bash, PowerShell y cmd);
//   - nunca rompe la sesion: si no hay Python sale con 0, y con --avisar (hooks de inicio de
//     sesion) deja UNA linea en el contexto para que el usuario sepa que falta.
import { spawnSync } from 'node:child_process'
import { appendFileSync, existsSync, mkdirSync, readFileSync, renameSync, statSync } from 'node:fs'
import { homedir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { buscarPython, comandoInstalarPython, entornoPython } from './_python.mjs'

const aqui = dirname(fileURLToPath(import.meta.url))

// Registro de fallos de hooks: un hook nunca rompe la sesion, pero tampoco falla en silencio.
// `node hooks/doctor.mjs` (comando /diagnostico) muestra las ultimas entradas.
const REGISTRO = join(homedir(), '.faast-mcp', 'logs', 'hooks.log')
function registrar(script, estado, detalle) {
  try {
    mkdirSync(dirname(REGISTRO), { recursive: true })
    try {
      if (statSync(REGISTRO).size > 512 * 1024) renameSync(REGISTRO, REGISTRO + '.1')
    } catch {
      // aun no existe
    }
    const plugin = aqui.split(/[\\/]/).slice(-2, -1)[0]
    const linea = { ts: new Date().toISOString(), plugin, script, estado, detalle: String(detalle).slice(-2000) }
    appendFileSync(REGISTRO, JSON.stringify(linea) + '\n')
  } catch {
    // sin disco o sin permisos: no hay donde registrar
  }
}
const args = process.argv.slice(2)
const avisar = args.includes('--avisar')
const iProyecto = args.indexOf('--proyecto')
if (iProyecto >= 0 && args[iProyecto + 1]) {
  process.env.CLAUDE_PROJECT_DIR = args[iProyecto + 1]
  args.splice(iProyecto, 2)
}
const [script, ...resto] = args.filter((a) => a !== '--avisar')
const ruta = script ? join(aqui, script) : ''
if (!script || !existsSync(ruta)) process.exit(0)

const proyecto = process.env.CLAUDE_PROJECT_DIR || process.cwd()
const extra = resto.map((a) => (a === '@project' ? proyecto : a))

let entrada = ''
try {
  if (!process.stdin.isTTY) entrada = readFileSync(0)
} catch {
  entrada = '' // sin stdin (algunos eventos no envian payload)
}

const python = buscarPython()
if (python) {
  const [cmd, ...previos] = python
  const r = spawnSync(cmd, [...previos, ruta, ...extra], {
    input: entrada,
    env: entornoPython,
    windowsHide: true,
    maxBuffer: 16 * 1024 * 1024,
  })
  if (r.stdout?.length) process.stdout.write(r.stdout)
  // stderr no se reenvia (ensuciaria la sesion): queda en el registro para el diagnostico.
  if (r.error) registrar(script, 'no-ejecuto', r.error.message)
  else if (r.status !== 0 || r.stderr?.length) registrar(script, `salida ${r.status}`, r.stderr.toString('utf8'))
  process.exit(r.error ? 0 : (r.status ?? 0))
}

registrar(script, 'sin-python', 'no se encontro Python 3')
if (avisar) {
  const instalar = comandoInstalarPython()
  process.stdout.write(
    'ENTORNO INCOMPLETO (plugin FaaST): no hay Python 3 en esta maquina, asi que el protocolo del ' +
      'equipo, los pendientes, la memoria y el registro de actividad NO se cargaron. ANTES de cualquier ' +
      'otra cosa: dile al usuario en una linea que vas a instalar Python 3 porque el equipo lo necesita, ' +
      'e instalalo con: ' + instalar + ' . Luego verifica (`python --version` o `python3 --version`) y ' +
      'pidele reiniciar la sesion para que el equipo cargue completo. Si la instalacion falla o el ' +
      'usuario no quiere, sigue trabajando y avisale que el equipo esta en modo reducido. (Si Python ' +
      'esta instalado en una ruta fuera del PATH: variable de entorno FAAST_PYTHON con la ruta de python.exe.)\n',
  )
}
process.exit(0)
