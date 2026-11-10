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
//   - `@project` en los argumentos se reemplaza por la carpeta del proyecto;
//   - nunca rompe la sesion: si no hay Python sale con 0, y con --avisar (hooks de inicio de
//     sesion) deja UNA linea en el contexto para que el usuario sepa que falta.
import { spawnSync } from 'node:child_process'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const aqui = dirname(fileURLToPath(import.meta.url))
const args = process.argv.slice(2)
const avisar = args.includes('--avisar')
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

const windows = process.platform === 'win32'
const candidatos = [
  ...(process.env.FAAST_PYTHON ? [[process.env.FAAST_PYTHON]] : []),
  ...(windows ? [['python'], ['py', '-3'], ['python3']] : [['python3'], ['python']]),
]
const env = { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' }

function esPython3([cmd, ...previos]) {
  const r = spawnSync(cmd, [...previos, '-c', 'import sys; print(sys.version_info[0])'], {
    encoding: 'utf8',
    env,
    timeout: 4000,
    windowsHide: true,
  })
  // El alias de la Microsoft Store existe en PATH pero no ejecuta nada (sale distinto de 0).
  return !r.error && r.status === 0 && r.stdout.trim() === '3'
}

for (const candidato of candidatos) {
  if (!esPython3(candidato)) continue
  const [cmd, ...previos] = candidato
  const r = spawnSync(cmd, [...previos, ruta, ...extra], {
    input: entrada,
    env,
    windowsHide: true,
    maxBuffer: 16 * 1024 * 1024,
  })
  if (r.stdout?.length) process.stdout.write(r.stdout)
  if (r.stderr?.length) process.stderr.write(r.stderr)
  process.exit(r.error ? 0 : (r.status ?? 0))
}

if (avisar) {
  process.stdout.write(
    'AVISO DEL PLUGIN: no se encontro Python 3 en esta maquina, asi que el protocolo del equipo, ' +
      'los pendientes y el registro de actividad NO se cargaron. Dile al usuario, en una linea, que ' +
      'instale Python 3 (en Windows: `winget install Python.Python.3.12`, marcando "Add python.exe ' +
      'to PATH") y reinicie la sesion; o que defina la variable de entorno FAAST_PYTHON con la ruta ' +
      'de su python.exe.\n',
  )
}
process.exit(0)
