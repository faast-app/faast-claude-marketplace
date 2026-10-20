# 05 — Rollback, coexistencia con la dockerización, DoD y gates

**Fase 5 de `migrar-dotnet`.**

---

## 1. La propiedad que hace viable este plan

ADR-016 tiene el **puente de vhost**: un componente se contenedoriza y el rollback es
revertir una línea de `ProxyPass`.

La migración de runtime tiene una propiedad equivalente, y es **más simple todavía**:

> Un componente migrado de TFM **no cambia su puerto, ni su hostname, ni su vhost, ni
> su contrato, ni su forma de desplegarse.** Desde afuera es indistinguible del anterior.

Consecuencia práctica: **un componente migrado se puede desplegar con el `d.sh` de
siempre, en PM2, sin haber resuelto nada de Docker.** El rollback es el rollback de
siempre — `pm2 stop`, apuntar a la carpeta de la versión anterior, `pm2 start` — y esa
carpeta sigue en disco porque el modelo de despliegue de QA Total deja las versiones
como carpetas hermanas.

Esto es lo que permite cumplir la regla 3 de la skill: **migrar y dockerizar por
separado**. Si fuera obligatorio contenedorizar para validar el runtime nuevo, las dos
cosas estarían forzosamente acopladas.

---

## 2. Niveles de rollback

| Nivel | Mecanismo | Tiempo | Precondición |
|---|---|---|---|
| **Escalón** | `git reset` al commit del escalón anterior | segundos | Cada escalón tiene commit propio (regla de `02-ruta-por-saltos`) |
| **Rama** | Cerrar el PR sin mergear | minutos | La rama de migración nunca es la de ambiente |
| **Artefacto (PM2)** | `pm2 stop` + apuntar a la carpeta de la versión anterior + `pm2 start` | < 1 min | La carpeta anterior **no se borra** |
| **Artefacto (Docker)** | `docker compose up -d` con el `sha-<sha>` anterior | < 1 min | Tags inmutables, `sha-<sha>` nunca se borra (§A.12 / ADR-013) |
| **Componente completo** | Revertir el `ProxyPass` del vhost | < 1 min | Solo aplica si además se contenedorizó |

**La condición que hace falso todo lo anterior:** si la migración tocó **datos**
(migración de EF Core aplicada, esquema de Hangfire modificado, jobs reencolados), el
rollback de código **no alcanza**. Por eso:

> **Regla dura: una migración de TFM no aplica migraciones de esquema.** Si el salto
> de EF Core genera una migración pendiente, se para y se trata como cambio de base de
> datos, con el dba, con su propio script y su propio rollback.

---

## 3. Modelo de ramas (ADR-039)

Se usa el mismo mecanismo que ya está en la casa, sin inventar nada:

```
release/faast/<ambiente>          rama de ambiente (punta)
        │
        ├─▶ pase/{id}_migracion-dotnet_{instancia}    ← la migración vive acá
        │      · escalón 1: net6   (commit)
        │      · escalón 2: net8   (commit)
        │      · escalón 3: ${TFM_DESTINO}  (commit)
        │      · fijado de versiones, ajustes del catálogo (commits)
        │      · bump de VERSION
        │
        └──── PR ────▶ release/faast/<ambiente>
```

| Regla | Por qué |
|---|---|
| **Una rama `pase/` por componente** | Regla 1 de la skill. Un PR con 5 repos migrados no se puede revertir por componente |
| **La rama se corta de la punta de la rama de ambiente**, no de `develop` | ADR-039 §2. La rama de ambiente es lo que está desplegado |
| **Un commit por escalón** | Es lo que hace posible `git bisect` cuando el síntoma aparece tres escalones después |
| **Sin cambios funcionales en la rama** | Regla 5. Si aparece un bug preexistente, va a su propio ticket |
| **Migración y dockerización en ramas distintas** | Regla 3 / §5 de `SKILL.md` |
| **Bump de `VERSION` en la rama `pase/`** | ADR-039. En los repos donde el bump ya es automático por tags, no tocar `version.txt` |

---

## 4. Coexistencia con la dockerización

### 4.1 La tabla de orden

Está en `SKILL.md` §5. El resumen: **migrar primero, salvo que el componente ya esté
en net8/net9**, en cuyo caso el contenedor es un buen laboratorio para el único salto
que queda.

### 4.2 Dónde se tocan las dos skills

| Punto de contacto | Quién manda |
|---|---|
| `DOTNET_VERSION` del Dockerfile | **`migrar-dotnet`**: sale de `DOTNET_TAG` en `parametros.env`. El Dockerfile lo recibe como `ARG`, nunca lo escribe |
| Familia de Dockerfile (D1-D7) | **`dockerizar-componente`**. Pero la migración la **cambia**: un componente que sale de D5 (EOL) entra en D1 |
| `libgdiplus` en la plantilla D4 | **`migrar-dotnet`**: la verificación de `01-analisis-previo` §3.1 dice que no hace falta |
| `UseUrls` | **`migrar-dotnet`**: es un cambio de código, no de imagen. Se arregla en la migración aunque el disparador sea la dockerización |
| `TZ` e ICU | Ambas. El TFM decide el comportamiento, la imagen provee `tzdata` e ICU |
| Healthcheck | **`dockerizar-componente`**, pero E-SWAG-02 puede romperlo en la migración |
| Secretos a variables de entorno | **`dockerizar-componente`**. La migración **no** toca configuración |

### 4.3 El efecto que la migración tiene sobre ADR-016

Si se migra antes de dockerizar, **la familia D5 (netcoreapp3.x / net5, EOL total)
deja de existir**: esos 18 componentes pasan a D1. Eso:

- elimina la necesidad de imágenes base sin parches de seguridad;
- vacía de contenido al servidor `qa-total-private-legacy` de ADR-016 §3.1, que fue
  diseñado justamente para alojarlos;
- y **reabre la decisión (c) de ADR-016**, que recomienda "retarget a net8" — una
  recomendación que quedó obsoleta el día que se verificó que net8 muere el
  2026-11-10 (ver ADR-017).

Es material para el lead: **si la migración avanza, ADR-016 se simplifica.**

---

## 5. Gates

| Gate | Quién firma | Cuándo | Qué mira |
|---|---|---|---|
| **Análisis** | architect | Fin de fase 1 | Carril asignado; si es Rojo, no sigue |
| **Build y contrato** | backend | Fin de cada escalón | Build limpio, diff de OpenAPI, warnings anotados |
| **Cybersec** | cybersec | **Antes** de QA | E-JWT-01/02/03, E-CS-02 (X509), E-TLS-01 si se bajó SECLEVEL. Obligatorio en: `apiauth`, `micro-security`, `micro-authorization`, `micro-integration-services`, `micro-api-cloud`, y cualquiera con `cert/` montado |
| **Datos** | dba | Si aparece una migración de EF pendiente | Script propio, rollback propio. La skill **no** aplica migraciones |
| **QA funcional** | QA | Antes del cutover | Validación **con capturas de pantalla** (regla de la casa: conformidad siempre con imágenes) |
| **Despliegue** | infra / lead | Cutover | Ambiente, orden, ventana |

**Hangfire tiene un gate propio:** ningún componente D6 se valida en paralelo con su
versión anterior. Una instancia, siempre. Ver E-HF-02.

---

## 6. Definition of Done

Un componente está migrado cuando **todas** estas son ciertas:

**Código**
- [ ] Todos los `.csproj` (y `Directory.Build.props` si existe) en `${TFM_DESTINO}`.
- [ ] `global.json` al SDK del destino con `rollForward: latestFeature`.
- [ ] Cero versiones flotantes (`*`) en los `PackageReference`.
- [ ] Un commit por escalón, todos con build limpio.
- [ ] Sin cambios funcionales en la rama.
- [ ] Sin `NoWarn` agregado durante la migración.

**Build**
- [ ] `dotnet build -c Release` con 0 errores.
- [ ] `dotnet list package --vulnerable --include-transitive` sin severidad alta sin ticket.
- [ ] Warnings nuevos (`SYSLIB*`, `CS0618`) anotados con decisión.
- [ ] `dotnet test` pasa, si el repo tiene tests.

**Comportamiento**
- [ ] Snapshot de OpenAPI antes/después, con el diff **explicado línea por línea**.
- [ ] Humo de los endpoints de negocio, con respuestas comparadas contra la línea base.
- [ ] Un caso de fecha, uno de monto y uno de zona horaria verificados.
- [ ] Si usa EF: conteo de filas idéntico en las consultas complejas.
- [ ] Si usa Hangfire: los jobs se registran con el mismo id y **una sola** instancia.
- [ ] Si genera documentos: un PDF/Excel real, **abierto y mirado**.

**Operación**
- [ ] `ASPNETCORE_URLS` manda (sin `UseUrls`).
- [ ] Logs por stdout.
- [ ] Arranca y responde en el ambiente destino.
- [ ] Rollback probado: se volvió a la versión anterior y respondió.

**Trazabilidad**
- [ ] `reference/checklist.md` completo, sin ningún "no".
- [ ] Informe en `{coordinacion}/inventario/migracion/<repo>.md`.
- [ ] Errores del catálogo que aparecieron, citados por código.
- [ ] Entradas nuevas agregadas al catálogo.
- [ ] Gates firmados.
- [ ] Handoff al lead.

---

## 7. Qué NO cierra un componente

Para que no haya ambigüedad:

| No alcanza | Por qué |
|---|---|
| "Compila" | La mitad de los errores de este catálogo son de runtime |
| "Arranca" | E-EF-02, E-JSON-01 y E-CULT-02 no impiden arrancar |
| "El healthcheck da verde" | Solo prueba que un endpoint responde |
| "Probé en local" | En local hay ICU, `tzdata`, la zona horaria correcta y red a todos lados |
| "QA dijo que está bien" **sin capturas** | Regla de la casa: conformidad siempre con imágenes |
| "Es igual que el otro que ya migré" | Cada componente tiene su propio conjunto de paquetes viejos |
