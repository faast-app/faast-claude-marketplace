#!/usr/bin/env node
// Ejecuta Python igual en cualquier terminal y sistema operativo.
//
//   node "<plugin>/hooks/py.mjs" <script.py | -c "codigo" | -m modulo> [args...]
//
// Sirve donde `python3` no existe (Windows lo llama `python` o `py`) o donde `python` no existe
// (macOS y Linux lo llaman `python3`). Es el reemplazo universal de `python3 ...` en los
// procedimientos del equipo: misma entrada, misma salida, mismo codigo de salida.
import { spawnSync } from 'node:child_process'
import { buscarPython, comandoInstalarPython, entornoPython } from './_python.mjs'

const python = buscarPython()
if (!python) {
  process.stderr.write(
    'No hay Python 3 en esta maquina. Instalalo con: ' + comandoInstalarPython() +
      ' , abre una terminal nueva y reintenta. (Python fuera del PATH: variable FAAST_PYTHON.)\n',
  )
  process.exit(127)
}
const [cmd, ...previos] = python
const r = spawnSync(cmd, [...previos, ...process.argv.slice(2)], { stdio: 'inherit', env: entornoPython })
process.exit(r.error ? 1 : (r.status ?? 1))
