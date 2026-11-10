#!/usr/bin/env node
// Diagnostico del plugin: dice en lenguaje claro si el equipo puede trabajar en esta maquina y,
// si no, que falta y como arreglarlo. Funciona en cualquier sistema y terminal.
//
//   node "<plugin>/hooks/doctor.mjs" [--proyecto <carpeta>] [--json]
//
// Revisa: Node, Python 3, git, gh, npx; que cada hook del plugin exista y arranque; la carpeta
// del equipo y su config.json; y los ultimos fallos registrados de hooks. Solo lee: no cambia nada.
// Sale con 0 si todo lo indispensable esta bien, 1 si falta algo indispensable.
import { spawnSync } from 'node:child_process'
import { existsSync, readFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { buscarPython, comandoInstalarPython, entornoPython } from './_python.mjs'

const aqui = dirname(fileURLToPath(import.meta.url))
const raiz = join(aqui, '..')
const args = process.argv.slice(2)
const enJson = args.includes('--json')
const iProyecto = args.indexOf('--proyecto')
const proyecto = iProyecto >= 0 && args[iProyecto + 1] ? args[iProyecto + 1] : process.env.CLAUDE_PROJECT_DIR || process.cwd()
const windows = process.platform === 'win32'
const manifiesto = JSON.parse(readFileSync(join(raiz, '.claude-plugin', 'plugin.json'), 'utf8'))

const filas = []
const fila = (estado, nombre, detalle, arreglo = '') => filas.push({ estado, nombre, detalle, arreglo })

function version(cmd, argumentos = ['--version']) {
  const r = spawnSync(cmd, argumentos, { encoding: 'utf8', timeout: 8000, windowsHide: true, shell: windows })
  if (r.error || r.status !== 0) return null
  return (r.stdout || r.stderr || '').trim().split(/\r?\n/)[0]
}

// --- Indispensables
const mayorNode = Number(process.versions.node.split('.')[0])
fila(mayorNode >= 18 ? 'OK' : 'FALTA', 'Node.js', `v${process.versions.node}`,
  mayorNode >= 18 ? '' : 'Actualiza Node.js a la version LTS (nodejs.org).')

const python = buscarPython()
let versionPython = ''
if (python) {
  const [cmd, ...previos] = python
  const r = spawnSync(cmd, [...previos, '-c', 'import sys; print(sys.version.split()[0])'], { encoding: 'utf8', env: entornoPython, timeout: 5000, windowsHide: true })
  versionPython = (r.stdout || '').trim()
  fila('OK', 'Python 3', `${versionPython} (${python.join(' ')})`)
} else {
  fila('FALTA', 'Python 3', 'no se encontro', `Instalar: ${comandoInstalarPython()} — luego abrir una terminal nueva.`)
}

const git = version('git')
fila(git ? 'OK' : 'FALTA', 'git', git || 'no se encontro', git ? '' : 'Instalar git (git-scm.com) y abrir una terminal nueva.')

// --- Recomendados
const npx = version('npx')
fila(npx ? 'OK' : 'AVISO', 'npx (navegador de pruebas)', npx || 'no se encontro',
  npx ? '' : 'Sin npx no arranca el navegador de pruebas (Playwright). Viene con Node.js.')
const gh = version('gh')
fila(gh ? 'OK' : 'AVISO', 'gh (GitHub)', gh || 'no se encontro',
  gh ? '' : 'Sin gh el equipo no puede leer ni escribir el tablero de GitHub. Instalar desde cli.github.com.')

// --- Hooks del plugin
let hooks = {}
try {
  hooks = JSON.parse(readFileSync(join(aqui, 'hooks.json'), 'utf8')).hooks || {}
} catch (e) {
  fila('FALTA', 'hooks.json', `no se pudo leer: ${e.message}`, 'Reinstala el plugin.')
}
const scripts = new Set()
for (const grupos of Object.values(hooks))
  for (const g of grupos) for (const h of g.hooks || []) if (h.args?.[1]) scripts.add(h.args[1])
const faltan = [...scripts].filter((s) => !existsSync(join(aqui, s)))
fila(faltan.length ? 'FALTA' : 'OK', 'Archivos de los hooks', faltan.length ? `faltan: ${faltan.join(', ')}` : `${scripts.size} presentes`,
  faltan.length ? 'Reinstala o actualiza el plugin.' : '')

if (python && existsSync(join(aqui, 'session_context.py'))) {
  const inicio = Date.now()
  const r = spawnSync(process.execPath, [join(aqui, 'run.mjs'), 'session_context.py', '--proyecto', proyecto], {
    encoding: 'utf8', timeout: 20000, windowsHide: true, input: '',
  })
  const ms = Date.now() - inicio
  const cargo = !r.error && r.status === 0
  fila(cargo ? (ms > 5000 ? 'AVISO' : 'OK') : 'FALTA', 'Arranque del protocolo de sesion',
    cargo ? `${ms} ms${r.stdout.trim() ? '' : ' (sin carpeta del equipo aqui: no imprime protocolo)'}` : `fallo: ${r.error?.message || 'salida ' + r.status}`,
    cargo ? (ms > 5000 ? 'Tarda mas de 5 s: revisa antivirus o disco lento.' : '') : 'Mira "Ultimos fallos" abajo.')
}

// --- Carpeta del equipo y configuracion
if (python && existsSync(join(aqui, 'coord_root.py'))) {
  const [cmd, ...previos] = python
  const r = spawnSync(cmd, [...previos, join(aqui, 'coord_root.py'), proyecto], { encoding: 'utf8', env: entornoPython, timeout: 8000, windowsHide: true })
  let d = null
  try {
    d = JSON.parse(r.stdout)
  } catch {
    d = null
  }
  if (!d?.path) {
    fila('AVISO', 'Carpeta del equipo', `no hay ninguna para ${proyecto}`, 'Normal si aun no configuraste el proyecto: usa /start.')
  } else if (d.en_repo) {
    fila('AVISO', 'Carpeta del equipo', `${d.path} esta DENTRO de un repositorio`, 'Hay que moverla fuera del repo: pidele al equipo "migra la carpeta del equipo".')
  } else {
    fila('OK', 'Carpeta del equipo', d.path)
    const cfg = join(d.path, 'config.json')
    if (!existsSync(cfg)) {
      fila('AVISO', 'config.json', 'no existe', 'Usa /start o /setup para crearlo.')
    } else {
      try {
        const c = JSON.parse(readFileSync(cfg, 'utf8'))
        const sinClase = Object.entries(c.ambientes || {}).filter(([, v]) => !['pruebas', 'productivo'].includes(v?.clase)).map(([k]) => k)
        if (c.ambientes && sinClase.length)
          fila('AVISO', 'config.json', `ambientes sin clase pruebas/productivo: ${sinClase.join(', ')}`, 'Declara la clase de cada ambiente.')
        else fila('OK', 'config.json', 'valido')
      } catch (e) {
        fila('FALTA', 'config.json', `no es JSON valido: ${e.message}`, `Corrige el archivo ${cfg}.`)
      }
    }
  }
}

// --- Ultimos fallos de hooks
const registro = join(homedir(), '.faast-mcp', 'logs', 'hooks.log')
let fallos = []
try {
  fallos = readFileSync(registro, 'utf8').trim().split('\n').slice(-200).map((l) => JSON.parse(l)).filter((f) => f.plugin === manifiesto.name)
} catch {
  fallos = []
}
const dia = Date.now() - 24 * 3600 * 1000
const recientes = fallos.filter((f) => Date.parse(f.ts) > dia)
fila(recientes.length ? 'AVISO' : 'OK', 'Fallos de hooks (24 h)', recientes.length ? `${recientes.length} registrado(s)` : 'ninguno',
  recientes.length ? `Detalle en ${registro}` : '')

const indispensable = filas.some((f) => f.estado === 'FALTA')
if (enJson) {
  console.log(JSON.stringify({ plugin: manifiesto.name, version: manifiesto.version, sistema: process.platform, ok: !indispensable, filas, ultimosFallos: recientes.slice(-5) }, null, 2))
} else {
  console.log(`Diagnostico de ${manifiesto.name} ${manifiesto.version} — ${process.platform} ${process.arch}`)
  for (const f of filas) {
    console.log(`  [${f.estado.padEnd(5)}] ${f.nombre}: ${f.detalle}`)
    if (f.arreglo) console.log(`          → ${f.arreglo}`)
  }
  for (const f of recientes.slice(-3)) {
    const ultima = String(f.detalle).trim().split('\n').pop()
    console.log(`  · ${f.ts} ${f.script} (${f.estado}): ${ultima.slice(0, 200)}`)
  }
  console.log(indispensable ? '\nRESULTADO: FALTA algo indispensable (ver arriba).' : '\nRESULTADO: el equipo puede trabajar en esta maquina.')
}
process.exit(indispensable ? 1 : 0)
