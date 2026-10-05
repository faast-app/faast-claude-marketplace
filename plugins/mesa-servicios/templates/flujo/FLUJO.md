---
name: {{dominio}}-{{flujo}}
descripcion: {{que hace el flujo, en una linea de negocio}}
clase: consulta | accion
ambiente: pruebas | produccion
argument-hint: "cliente={{CODIGO}} [desde=YYYY-MM-DD] [estado=…]"
---
# Flujo: {{titulo de negocio}}

## Rol
Coordinador. No ejecuta: la UI la hace `qa-negocio` (grabando), las verificaciones `SELECT` el
`dba-mesa`. Nadie escribe por SQL dentro del flujo. Sigue la skill `flujos-mesa`.

## Argumentos
| Argumento | Valores | Default | Nota |
|-----------|---------|---------|------|
| cliente   | codigo de `config.json` → clientes | (preguntar) | |
| ambiente  | pruebas \| produccion | pruebas | produccion requiere autorizacion registrada por corrida |

## Precondiciones (solo lectura — `referencias/verificacion.md` §1)
- {{que debe existir: cliente activo, perfil con acceso, …}}

## Fases
0. Confirmar con el usuario de mesa (en produccion: registrar quien autoriza, cuando, para que caso).
1. Verificar precondiciones (`dba-mesa`, solo `SELECT`).
2. Ejecutar `runbook.md` (`qa-negocio` en UI, grabando). **Parada antes de cada paso que escribe.**
3. Verificar resultado (`verificacion.md` §2 + lo visible en pantalla).
4. Cierre: `informe-flujo.md` + `INDEX.md` en la carpeta de evidencia de la corrida.

## Paradas obligatorias (pasos que escriben)
- {{paso N: "Aprobar" — OK escrito del usuario de mesa en el momento}}  (vacio si es clase consulta)

## Errores conocidos (reportar; no re-diagnosticar)
- {{sintoma → que hacer}}

## Seguridad
Cuentas por NOMBRE de variable (`.mesa/accesos.env`); sin credenciales aqui. Datos personales en
pantalla se redactan en las capturas. En produccion solo lo declarado en `clase`/`ambiente`.

## No confirmado
- [ ] {{pantalla, columna o consulta que falta confirmar en el ambiente real}}
