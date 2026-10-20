# Migración .NET — `<componente>`

**Repo:** · **Rama:** `pase/{id}_migracion-dotnet_{instancia}`
**TFM origen:** `<netX>` → **TFM destino:** `<${TFM_DESTINO}>` · **Saltos:** N
**Carril:** 🟢/🟡/🔴 · **Responsable:** · **Inicio:** · **Cierre:**
**Orden respecto de la dockerización:** migrar antes / dockerizar antes / no se dockeriza

> Se guarda en `{coordinacion}/inventario/migracion/<repo>.md`. Es el entregable del componente.

---

## 0. Resumen

Tres a cinco líneas: qué se migró, qué se encontró, qué quedó pendiente, y si está
listo para QA. Que se entienda sin leer el resto.

---

## 1. Análisis previo

Salida de `analisis-previo.sh`:

```
(pegar acá)
```

**Interpretación:**

| Hallazgo | ¿Es real? | Decisión |
|---|---|---|
| ej. `using System.Drawing` ×2 | No — usings huérfanos, sin GDI+ (E-NAT-02) | No bloquea |
| | | |

**Carril asignado:** · **Por qué:**

**Divergencia `develop` vs desplegado:** sí / no. Si sí, cómo se resolvió y quién lo decidió.

---

## 2. Preparación

| Acción | Commit | Notas |
|---|---|---|
| Fijado de versiones flotantes | | qué paquetes |
| Newtonsoft → 13.0.3 | | |
| Snapshot de contrato "antes" | — | endpoints capturados: N |
| Línea base de respuestas | — | casos: N |

---

## 3. Escalones

| # | TFM | Commit | Errores del catálogo | Warnings nuevos | Tiempo |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | `${TFM_DESTINO}` | | | | |

### Paquetes movidos

| Paquete | De | A | Por qué (qué salto lo exigía) |
|---|---|---|---|
| | | | |

**Paquetes que NO se movieron, a propósito:**

| Paquete | Versión | Por qué se dejó |
|---|---|---|
| ej. MediatR | 12.4.1 | v13+ es licencia comercial (E-LIC-02) |

---

## 4. Errores encontrados

| Código | Síntoma real | Fix aplicado | Verificado con |
|---|---|---|---|
| E-xxx-nn | | | |

**Entradas nuevas propuestas para el catálogo:** (o "ninguna")

**Entradas [G] que se ejecutaron y pasan a [V]:**

---

## 5. Evidencia de comportamiento

### Contrato (OpenAPI)

```
(salida de snapshot-contrato.sh diff)
```

**Cada línea del diff, explicada:**

| Cambio | Causa | ¿Bloquea? |
|---|---|---|
| | | |

### Respuestas

```
(salida de comparar-respuestas.sh diff)
```

### Casos dirigidos

| Caso | Antes | Después | OK |
|---|---|---|---|
| Fecha parseada de request | | | ☐ |
| Fecha serializada en respuesta | | | ☐ |
| Monto con separadores | | | ☐ |
| Timestamp escrito en base (TZ) | | | ☐ |
| Consulta EF compleja: conteo de filas | | | ☐ |
| Job de Hangfire de punta a punta | | | ☐ |
| Documento generado y **abierto** | | | ☐ |
| Token: emisión, validación y expirado | | | ☐ |

### Tests

| | |
|---|---|
| ¿Tiene tests? | sí / no |
| Resultado | N pasan / N fallan |
| `.trx` | ruta |

### Recursos

| Métrica | Antes | Después |
|---|---|---|
| RSS en reposo (10 min) | | |
| Arranque hasta primer 200 | | |
| p95 de los 3 endpoints top | | |

---

## 6. Rollback

| | |
|---|---|
| Mecanismo | PM2 (carpeta anterior) / imagen `sha-<sha>` anterior |
| **¿Se probó?** | sí / no — **"no" bloquea** |
| Evidencia | |
| ¿Hubo cambios de esquema? | no / sí → quién los tomó (dba) |

---

## 7. Gates

| Gate | Aplica | Firmado por | Fecha | Observaciones |
|---|---|---|---|---|
| cybersec | | | | |
| dba | | | | |
| QA (con capturas) | | | | |
| lead / infra | | | | |

---

## 8. Pendientes

| # | Pendiente | Dueño | Cuándo |
|---|---|---|---|
| 1 | | | |

---

## 9. Correcciones al inventario

Lo que esta migración demostró que estaba mal en `asis-*.md` o en los ADR, para que
el tech-writer lo refleje:

| Documento | Decía | Es | Evidencia |
|---|---|---|---|
| | | | |
