#!/usr/bin/env python3
"""po-team — revisa las cuentas de prueba de .po-team/accesos.env SIN mostrar ningun valor.

Uso: python3 accesos.py {ruta/.po-team/accesos.env} VAR1 [VAR2 ...]
Imprime por variable: OK (tiene valor) | VACIA | FALTA. Codigo 0 si todas OK, 1 si no.
Sirve para que el validador-po y el manualista confirmen ANTES del login que la cuenta esta
cargada; el valor lo inyecta el Playwright MCP (--secrets) cuando el agente escribe el NOMBRE.
"""
import os
import sys


def leer(ruta):
    vals = {}
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            k, v = linea.split("=", 1)
            k = k.strip().removeprefix("export ").strip()
            vals[k] = v.strip().strip('"').strip("'")
    return vals


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    ruta = sys.argv[1]
    if not os.path.isfile(ruta):
        print(f"FALTA el archivo {ruta}: correr /po-team:setup ambientes")
        return 1
    vals = leer(ruta)
    ok = True
    for var in sys.argv[2:]:
        if var not in vals:
            estado, ok = "FALTA", False
        elif not vals[var]:
            estado, ok = "VACIA", False
        else:
            estado = "OK"
        print(f"{var}: {estado}")
    return 0 if ok else 1


sys.exit(main())
