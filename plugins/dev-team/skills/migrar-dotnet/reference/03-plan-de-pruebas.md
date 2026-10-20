# 03 — Plan de pruebas por componente

**Fase 3 de `migrar-dotnet`.**

## El problema de fondo

**Solo 17 de 61 repos backend tienen proyectos de test [V]:** `gw-app`,
`gw-mobile-fintec`, `gw-monitor-cesiones`, `gw-scoring`, `micro-agents-antropic`,
`micro-backoffice`, `micro-hangfire-tasks-scoring`, `micro-integration-services`,
`micro-monitor-cesiones(-hf)`, `micro-notificaciones-hf`, `micro-notification`,
`micro-reporting`, `micro-reversas`, `micro-scoring`, `micro-versions-manager`,
`micro-shared-library`.

Los 44 restantes — incluidos casi todos los EOL, que son los que más saltos dan — **no
tienen ninguna red de seguridad automática**.

De ahí la regla 4 de la skill: **el snapshot de contrato y la comparación de respuestas
contra el componente actual no son un complemento del plan de pruebas, son el plan de
pruebas.** Y solo funcionan si se toman **antes** de tocar el `.csproj`.

---

## 1. Build

| Verificación | Comando | Criterio |
|---|---|---|
| Restore limpio | `dotnet restore` | Sin `NU1605` ni `NU1608` sin resolver |
| Build limpio | `dotnet build -c Release` | 0 errores |
| Warnings nuevos | comparar contra el conteo del escalón anterior | Cada `SYSLIB*`/`CS0618` nuevo **anotado** en el informe, con decisión |
| Vulnerabilidades | `dotnet list package --vulnerable --include-transitive` | Ninguna de severidad alta sin ticket |
| Deprecados | `dotnet list package --deprecated` | Anotados |
| Publish | `dotnet publish -c Release -o out` | El `.dll` que sale coincide con `ASSEMBLY` de `parametros.env` |

**`TreatWarningsAsErrors`: opcional y al final.** Arrancar con `false`. Cuando el
componente compila limpio en el TFM destino, encenderlo una vez para ver qué aparece,
anotarlo, y decidir si se deja encendido. Encenderlo **al principio** convierte cada
escalón en una cacería de warnings preexistentes que no tienen nada que ver con el salto.

Excepción: `WarningsAsErrors=nullable` sí conviene si el repo ya lo tenía
(**[V]** `micro-versions-manager`); quitarlo sería una regresión.

---

## 2. Tests existentes (los 17 que los tienen)

```bash
dotnet test -c Release --logger "trx;LogFileName=tests-${TFM_DESTINO}.trx"
```

| Situación | Qué hacer |
|---|---|
| Pasan todos | Adjuntar el `.trx` al informe. Es la mejor evidencia disponible |
| Falla un test | **Se investiga, no se borra ni se marca `[Skip]`.** Un test que falla tras un salto está haciendo exactamente su trabajo |
| El proyecto de test no compila por su propio TFM | **[V]** `gw-mobile-fintec` (app net8 / test net10): alinear el TFM del test al mismo escalón que la app |
| No hay tests | Sección 3, y no se discute |

---

## 3. Snapshot de contrato (OpenAPI)

**Antes de tocar nada**, contra el componente **corriendo hoy en QA**:

```bash
./templates/snapshot-contrato.sh antes
# ... escalones ...
./templates/snapshot-contrato.sh despues
./templates/snapshot-contrato.sh diff
```

El script normaliza el JSON de OpenAPI (ordena claves, quita versión y timestamps)
para que el diff muestre cambios de contrato y no ruido del generador.

**Qué es aceptable en el diff y qué no:**

| Cambio en el diff | Veredicto |
|---|---|
| Orden de propiedades, `info.version` | Ruido. Aceptable |
| Un `format` que aparece o desaparece (`"format": "int32"`) | **Revisar.** Suele venir del cambio de generador de esquema |
| Un tipo que pasa de `string` a `object`, o un `nullable` que aparece | **Bloquea.** Es un cambio de contrato: el consumidor lo va a sentir |
| Un endpoint que **desaparece** | **Bloquea.** Casi siempre es un controller que dejó de registrarse por un cambio de convención |
| `required` que aparece en un campo que antes era opcional | **Bloquea.** Rompe a los clientes existentes |

**Advertencia [V]:** 40+ repos usan Swashbuckle 6.x. **No cambiar a
`Microsoft.AspNetCore.OpenApi` durante la migración**: genera un JSON distinto y el
diff se vuelve ilegible justo cuando más se lo necesita.

---

## 4. Pruebas de humo por endpoint

El mínimo por componente: **los endpoints que el negocio usa**, no todos los que
existen. Se sacan de `asis-qa-total-apis-micros.md` (quién consume a quién) y de los
logs del componente.

```bash
./templates/comparar-respuestas.sh    # corre la lista y compara contra la línea base
```

| Qué se compara | Cómo |
|---|---|
| Código de estado | Debe ser idéntico |
| Cuerpo de la respuesta | Diff normalizado (ver §5) |
| Headers relevantes | `Content-Type`, `Set-Cookie`, CORS |
| Latencia | Orden de magnitud, no milisegundos |

**Se compara contra el componente actual en QA, no contra lo que "debería" devolver.**
El objetivo de una migración de runtime es que **nada cambie**, incluidos los bugs.

---

## 5. Los cuatro diffs que hay que mirar con lupa

Son los que producen respuestas *parecidas pero no iguales*, y los que pasan un smoke
superficial.

### 5.1 Serialización JSON **[V] 15+ repos con Newtonsoft**

| Qué mirar | Newtonsoft | System.Text.Json |
|---|---|---|
| Nombres de propiedad | Respeta el casing del C# | `camelCase` por defecto en ASP.NET |
| `null` | Se emite | Se emite, salvo configuración |
| Enums | Número (salvo converter) | Número por defecto |
| `DateTime` | `2026-09-21T10:00:00-05:00` | ISO 8601, pero con distinto manejo de offset |
| Ciclos de referencia | `ReferenceLoopHandling` | Lanza salvo `ReferenceHandler` |

**Regla:** si el componente usa Newtonsoft hoy, sigue usando Newtonsoft después.
`AddNewtonsoftJson()` explícito. Cambiar de serializador durante una migración de
runtime es cambiar el contrato de todos los endpoints a la vez.

### 5.2 Fechas, cultura y zona horaria **[V]**

Lo que hay que probar, con datos reales del ambiente:

| Caso | Por qué |
|---|---|
| Un monto formateado (`1.234,56` vs `1,234.56`) | ICU cambió respecto de NLS; la cultura del contenedor no es la del servidor |
| Una fecha serializada y una fecha **parseada de un request** | `DateTime.Parse` depende de `CurrentCulture` |
| Un `DateTime.Now` **[V] 30 usos solo en `micro-banco`** | En el contenedor `TZ` es UTC salvo que se declare. Con `America/Lima` el resultado cambia en 5 horas |
| Ordenamiento de strings con tildes/ñ | `string.Compare` cultural cambió con ICU |

**Bomba de tiempo verificada [V]:** 6 repos declaran `InvariantGlobalization=true`
(`gw-confirming`, `gw-portal-digital`, `gw-venta-cartera`, `micro-banco`,
`micro-portal-digital`, `micro-venta-cartera`). En modo invariante,
`new CultureInfo("es-PE")` **lanza `CultureNotFoundException`** (`PredefinedCulturesOnly`).

Revisado: `micro-portal-digital` tiene 40 usos y **todos son
`CultureInfo.InvariantCulture`** — consistente con la bandera, sin riesgo. Los otros 5
tienen 0-3 usos y ninguna cultura concreta. **Hoy no hay bug**, pero cualquiera que
agregue un `new CultureInfo("es-PE")` en esos repos rompe el componente en runtime.
Anotarlo; no arreglarlo en este PR.

### 5.3 Traducción de consultas de EF Core **[V] ~30 componentes**

El riesgo no es que el build falle: es que una consulta que antes se evaluaba en el
cliente ahora se traduzca (o al revés), y **devuelva otro conjunto de filas o tarde
100 veces más**.

| Prueba | Cómo |
|---|---|
| Consultas con `GroupBy`, `Skip/Take`, `Include` filtrado, `string.Contains` | Ejecutarlas y **comparar el conteo de filas** contra la versión actual |
| SQL generado | `ToQueryString()` o log de EF (`Microsoft.EntityFrameworkCore.Database.Command` en `Information`) — diff antes/después |
| Consultas que hoy son lentas | Medirlas. Un cambio de traducción se ve primero en el tiempo |

### 5.4 Hangfire **[V] 8 componentes**

| Verificación | Por qué |
|---|---|
| Los jobs recurrentes **siguen registrados con el mismo id** | Un id que cambia crea un job nuevo y deja el viejo huérfano corriendo |
| El dashboard abre y pide auth | `Hangfire.Dashboard.Basic.Authentication` va de 5.0.0 a 7.0.1 en la flota |
| **Una sola instancia registrada** en `HangFire.Server` | Regla dura P10 de ADR-016. Durante la migración conviven la vieja y la nueva: **apagar una** |
| Un job de prueba corre de punta a punta | El storage serializa los argumentos del job: un cambio de serializador los invalida |

> **Riesgo específico y no negociable:** durante la validación de un componente
> Hangfire migrado, el proceso anterior **no puede seguir vivo contra el mismo storage**.
> Dos instancias = jobs ejecutados dos veces = daño en datos de negocio. Es el riesgo
> R1 de ADR-016 y la lección `hangfire-contab-demo-cl`.

---

## 6. Rendimiento y memoria

No hace falta una prueba de carga formal. Sí hace falta **no migrar a ciegas**:

| Métrica | Cómo | Umbral |
|---|---|---|
| RSS en reposo tras 10 min | `docker stats` o `ps` | Si sube >50%, investigar (GC en modo Server es el sospechoso habitual) |
| Tiempo de arranque hasta el primer 200 | cronómetro | Orden de magnitud |
| p95 de los 3 endpoints más usados | 50 requests secuenciales | Sin degradación evidente |

**Contexto que importa [V]:** los servidores de QA Total tienen **1.9-3.8 GB de RAM**
con 9-15 procesos. Un componente que pasa de 150 MB a 400 MB no es un detalle: es un
servidor que empieza a swapear.

---

## 7. Plan reducido para carril Verde

Origen ≥ net6, sin nativas, sin auth, sin Hangfire, ≤2 saltos:

1. Build limpio en cada escalón.
2. Tests si existen.
3. Snapshot de contrato antes/después.
4. Humo de 3-5 endpoints de negocio.
5. Un caso de fecha y un caso de monto.

Todo lo demás es para Amarillo.

---

## 8. Quién firma

| Gate | Quién | Cuándo |
|---|---|---|
| Build + contrato + humo | backend | Cierre de la migración |
| Validación funcional **con capturas** | QA | Antes de proponer el cutover — regla de la casa: conformidad siempre con imágenes |
| Auth / crypto / certificados | cybersec | Antes de QA, si el análisis marcó algo en §6 de `01-analisis-previo` |
| Orden y ambiente | lead / infra | Para el despliegue |
