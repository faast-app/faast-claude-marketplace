---
name: {dominio}-{flujo}
descripcion: {que hace el flujo, en una linea de negocio}
argument-hint: "variante={a|b} [monto=...] [ambiente=qa] [otros=...]"
---
# Flujo: {titulo de negocio}

## Rol
Coordinador. NO ejecuta el flujo: delega a los agentes del equipo (qa-frontend para la UI,
qa-backend/dba para el SQL), pregunta al usuario en los puntos de parada y consolida. Sigue la
skill `flow-recording`.

## Argumentos
| Argumento | Valores | Default | Nota |
|-----------|---------|---------|------|
| variante  | {a \| b} | (preguntar) | que camino del flujo |
| ambiente  | {desa \| qa} | qa | si falta credencial o runbook para otro ambiente, detener y preguntar |
| {otro}    | {...}   | {...}   | {...} |

## Precondiciones y switches (los que apliquen)
| Parametro | Donde | Que gobierna | valor esperado por variante |
|-----------|-------|--------------|-----------------------------|
| {param}   | {BD/pantalla} | {que decide} | a: {valor} · b: {valor} |
Regla: se VERIFICAN primero (solo lectura) y se registra el valor INICIAL; se cambian solo con
parada obligatoria (fase 2) y se restauran al final (fase 6). Si varios deben coincidir, se
cambian JUNTOS, nunca uno solo.

## Fases
### 0. Confirmar con el usuario (texto plano)
Enunciar los riesgos reales: crea datos reales, cambia parametros que afectan a usuarios. Pedir OK.
### 1. Verificar precondiciones (solo lectura) y registrar valores iniciales
Correr `referencias/verificacion.md` §1. Anotar el valor inicial de cada parametro/switch.
### 2. (si aplica) Cambiar parametros: PARADA OBLIGATORIA
Lo ejecuta el **dba** con el patron guardado (`referencias/verificacion.md` §2). Re-verificar.
### 3. Ejecutar el flujo (delegado) — pasos de `runbook.md`
qa-frontend hace la UI (un browser compartido, captura por paso); qa-backend/dba el SQL de lectura.
### 4. Puntos de parada obligatorios — OK escrito del usuario EN EL MOMENTO
{listar cada escritura sensible: grabar, aprobar, confirmar giro/desembolso, elegir banco, write en BD}
### 5. Verificar resultado (solo lectura + UI) contra lo esperado
`referencias/verificacion.md` §3 + comprobacion en pantalla. 0 errores de consola, 0 4xx/5xx inesperados.
### 6. Cierre
Escribir `informe-flujo.md`. PREGUNTAR si restaurar los parametros a los valores del paso 1.

## Errores conocidos (reportar; no re-diagnosticar)
- {sintoma → que significa}

## Seguridad
Sin passwords ni tokens en este archivo. Las credenciales se leen de los archivos de acceso del
proyecto (`.coordination/dba-access.json`, `qa-secrets.env`, ...) por NOMBRE de variable. Ambiente
preferente NO productivo.

## No confirmado (marcar lo que aun no se verifico en el ambiente real)
- [ ] {endpoint/tabla/nombre que falta confirmar}
