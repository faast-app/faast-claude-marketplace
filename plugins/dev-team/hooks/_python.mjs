// Busca un Python 3 real en cualquier sistema. Compartido por run.mjs, py.mjs y mcp-playwright.mjs.
import { spawnSync } from 'node:child_process'

export const entornoPython = { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' }

/** Devuelve [comando, ...argumentosPrevios] o null. Descarta el alias de la Microsoft Store. */
export function buscarPython() {
  const windows = process.platform === 'win32'
  const candidatos = [
    ...(process.env.FAAST_PYTHON ? [[process.env.FAAST_PYTHON]] : []),
    ...(windows ? [['python'], ['py', '-3'], ['python3']] : [['python3'], ['python']]),
  ]
  for (const [cmd, ...previos] of candidatos) {
    const r = spawnSync(cmd, [...previos, '-c', 'import sys; print(sys.version_info[0])'], {
      encoding: 'utf8',
      env: entornoPython,
      timeout: 4000,
      windowsHide: true,
    })
    if (!r.error && r.status === 0 && r.stdout.trim() === '3') return [cmd, ...previos]
  }
  return null
}

export function comandoInstalarPython() {
  if (process.platform === 'win32')
    return 'winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements'
  if (process.platform === 'darwin')
    return 'brew install python@3.12   (sin Homebrew: instalador de https://www.python.org/downloads/macos/)'
  return 'sudo apt-get install -y python3   (Fedora/RHEL: sudo dnf install -y python3 · Arch: sudo pacman -S --noconfirm python)'
}
