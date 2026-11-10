#!/usr/bin/env node
// Barrido de contrato con Schemathesis (puerta 6) — lo corre qa-backend. Sin bash: funciona
// igual en Windows, macOS y Linux.
//
//   node api/contract.mjs [HU] [filtro-de-rutas]
//   node api/contract.mjs HU-042 "^/api/cobranzas"
//
// Genera cientos de requests validos e invalidos desde el openapi.yml REAL. SOLO contra un
// ambiente de pruebas (JAMAS contra ambientes de cliente). La salida (junit + consola) es
// evidencia y va a .coordination/evidence/{HU}/api/.
import { spawnSync } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'

if (existsSync('.env')) {
  for (const linea of readFileSync('.env', 'utf8').split(/\r?\n/)) {
    const m = /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/.exec(linea)
    if (m && process.env[m[1]] === undefined) process.env[m[1]] = m[2].replace(/^["']|["']$/g, '')
  }
}

const [hu = 'regresion', filtro = ''] = process.argv.slice(2)
const spec = process.env.OPENAPI_SPEC || '../docs/openapi.yml'
const url = process.env.API_URL || 'http://localhost:5000'
const suite = process.env.EVIDENCE_DIR || '../.coordination/evidence/_suite'
const salida = resolve(join(dirname(suite), hu, 'api'))
mkdirSync(salida, { recursive: true })

const args = ['run', spec, '--url', url, '--checks', 'all', '--max-examples', process.env.MAX_EXAMPLES || '200',
  '--report', 'junit', '--report-dir', salida]
if (filtro) args.push('--include-path-regex', filtro)
if (process.env.QA_TOKEN) args.push('--header', `Authorization: Bearer ${process.env.QA_TOKEN}`)

const visible = `schemathesis ${args.join(' ')}`.replace(/Bearer \S+/, 'Bearer ***')
console.log(visible)
const r = spawnSync('schemathesis', args, { encoding: 'utf8' })
if (r.error) {
  console.error('schemathesis no esta instalado: pedir /dev-team:setup playwright (pipx install schemathesis)')
  process.exit(2)
}
const token = process.env.QA_TOKEN
const limpiar = (t) => (token ? t.split(token).join('***') : t)
writeFileSync(join(salida, 'schemathesis.txt'), limpiar(`${visible}\n${r.stdout || ''}${r.stderr || ''}`))
process.stdout.write(limpiar(r.stdout || ''))
process.stderr.write(limpiar(r.stderr || ''))
process.exit(r.status ?? 1)
