# Revision de PR y auto-revision del diff

Lo usa cada dev sobre su propio diff antes de entregar (paso 5 del metodo) y el Lead /
`/dev-team:review-pr` sobre el PR ajeno. La revision busca **defectos y riesgos**, no gustos.

## 1. Antes de leer codigo

- ¿El PR referencia el item (`[WI-id]` / `(#n)`) y su descripcion tiene Contexto, Causa raiz,
  Cambio, Criterios de Aceptacion y Detalles Tecnicos (repo, rama, commits, version, archivos)?
- ¿Es **un** cambio coherente y del tamaño revisable (idealmente < 400 lineas de logica)? Si
  mezcla refactor + feature + formato masivo, se pide separar.
- ¿Salio de `origin/{defaultBranch}` actualizado y trae el bump de version en commit separado
  (cuando el proyecto lo exige)?
- ¿CI en verde (build, tests, lint, SCA/secret scan)? Sin CI verde no se revisa a fondo.

## 2. Lectura del diff (en este orden)

1. **Tests primero**: ¿prueban los criterios y los bordes caros? ¿un bug trae la prueba que lo
   reproduce? ¿algun test se borro, se debilito o se `Skip`eo sin motivo?
2. **Contrato y datos**: cambios de API/OpenAPI, de tipos compartidos, migraciones (expand/
   contract, reversa, revision DBA), scripts de pase (formato global).
3. **Logica de negocio**: calculos de dinero (decimal, moneda, redondeo), estados y
   transiciones, idempotencia, concurrencia, transacciones.
4. **Seguridad**: authz por endpoint y por recurso, validacion de entrada, SQL parametrizado,
   secretos/PII en codigo y logs, XSS en front, dependencias nuevas (licencia y CVE).
5. **Operacion**: logs y errores, timeouts y reintentos, config por variables (sin valores
   hardcodeados), health, impacto en Docker/CI.
6. **Mantenibilidad**: sigue el patron del repo, nombres claros, sin duplicacion evitable, sin
   codigo muerto ni comentarios obsoletos.

## 3. Severidad de los hallazgos

| Severidad | Ejemplos | Efecto |
|---|---|---|
| **Bloqueante** | Monto en float, giro sin idempotencia, endpoint sin auth, SQL concatenado, secreto en el diff, migracion destructiva sin reversa, test borrado para que pase, borrado de datos en manejo de error | No se mergea |
| **Mayor** | Falta prueba de un criterio, N+1 en endpoint caliente, llamada externa sin timeout, error que filtra detalle, contrato roto sin aviso | Se corrige en este PR |
| **Menor** | Nombre confuso, log en nivel incorrecto, duplicacion local | Se corrige o se registra |
| **Sugerencia** | Alternativa de estilo/diseño | Opcional, marcada como tal |

Cada comentario dice **que** (archivo:linea), **por que** (riesgo concreto) y **como** (fix
sugerido). Nada de "esto no me gusta".

## 4. Gates que la revision no reemplaza

- **QA** (APROBADA) antes del merge, siempre.
- **Cybersec** si toca auth, pagos/dinero, PII o superficie publica.
- **DBA** si hay migraciones o scripts.
- **Diseño** (handoff aprobado) si es una pantalla nueva.
- Solo el **Lead** mergea.

## 5. Auto-revision rapida (comandos)

```bash
git fetch origin && git diff --stat origin/{defaultBranch}...HEAD     # alcance: ¿solo lo de la tarea?
git diff origin/{defaultBranch}...HEAD                                # leer TODO el diff
git diff origin/{defaultBranch}...HEAD | grep -nE "console\.log|print\(|Debug\.Write|TODO|FIXME|debugger"
git diff origin/{defaultBranch}...HEAD | grep -niE "password|secret|apikey|token|BEGIN .*PRIVATE KEY|connectionstring"
git status --short                                                    # nada sin trackear que deberia ir, nada ajeno
```
