# Informe de testabilidad y suite de tests — `<componente>`

**Repo:** · **Ref analizado:** · **Rama de trabajo:**
**TFM de la app:** · **TFM de los tests:** · **Objetivo:** migración / regresión / desarrollo
**Autor:** · **Fecha:** · **Carril:** 🟢 / 🟡 / 🔴

**Leyenda:** **[V]** verificado (comando o lectura del código real) · **[G]** conocimiento
general, a confirmar.

---

## 0. Resumen ejecutivo

*Máximo cinco puntos. El primero es el veredicto; el último es lo que NO queda cubierto.*

1.
2.
3.
4.
5. **Lo que NO queda cubierto y por qué:**

---

## 1. Mapa del componente

*Salida de `analizar-testabilidad.sh`, resumida.*

| Dato | Valor |
|---|---|
| Controllers / endpoints | |
| Endpoints anónimos | |
| Documentos OpenAPI publicados | |
| LOC por capa | |
| `DbContext` y motores | |
| Dónde vive el negocio | |
| Proyectos de test existentes | |

---

## 2. Testabilidad por pieza

| Pieza | Acoplamiento | Testeable hoy | Qué haría falta |
|---|---|---|---|
| | alto / medio / bajo | sí / no | |

---

## 3. Dependencias externas

| Dependencia | Dónde | En unitarios | En integración | ¿Bloquea el arranque? |
|---|---|---|---|---|
| | | | | |

---

## 4. Bloqueadores

| Código | Bloqueador | Impacto | Fix propuesto | Tamaño | ¿Aprobado? |
|---|---|---|---|---|---|
| T-WAF-01 | | | | 1 línea | |
| T-CFG-01 | | | | | |
| T-DB-02 | | | | | |
| T-DB-04 | | | | | |
| T-DOCK-01 | | | | | |

**De dónde sale el esquema:** ☐ migraciones de EF ☐ dump versionado ☐ **de ningún lado**
→ si es la tercera, la integración con base **no es viable** hasta que el dba entregue el dump.

---

## 5. Cambios de testabilidad pedidos

*Solo los aditivos y acotados. Un refactor no entra acá (SKILL §4).*

| # | Cambio | Archivos | Riesgo de comportamiento | Estado |
|---|---|---|---|---|
| 1 | | | | propuesto / aprobado / rechazado |

---

## 6. La suite

| Suite | Proyectos | Nº de tests | Corre sin infra | En CI |
|---|---|---|---|---|
| Unit | | | sí | sí |
| Caracterización | | | sí | sí |
| Integración | | | no (Docker) | |
| Contrato | | | no (ambiente) | **no** |

### 6.1 Cobertura por riesgo

| Área de riesgo | Casos cubiertos | Cobertura de línea | Pendiente |
|---|---|---|---|
| Auth | | | |
| Dinero / cálculos | | | |
| Cifrado | | | |
| Jobs | | | |
| Fechas / cultura / TZ | | | |
| Contrato de endpoints | | | |

### 6.2 Líneas base generadas antes de migrar

- [ ] Token de oro, generado con el binario actual el ____
- [ ] Vectores de cifrado (incluido al menos uno con formato real de la base)
- [ ] Snapshots de OpenAPI: ____ documentos
- [ ] Golden-file de respuestas: ____ endpoints
- [ ] Línea base de contrato contra QA: ____ endpoints, tomada el ____

### 6.3 Tests en `[Skip]` y su motivo

| Test | Motivo | Ticket | Se quita cuando |
|---|---|---|---|
| | | | |

---

## 7. Lo que NO queda cubierto

*La sección más importante del informe. Sin esto, alguien va a leer "tiene tests" y asumir
una red que no existe.*

| Área | Por qué no | Qué haría falta | Riesgo que queda vivo |
|---|---|---|---|
| | | | |

---

## 8. Errores del catálogo que aparecieron

| Código | Dónde | Cómo se resolvió | ¿Se repromovió [G] → [V]? |
|---|---|---|---|

**Entradas nuevas propuestas para `04-catalogo-errores-tests.md`:**

---

## 9. Evidencia

- Salida de `analizar-testabilidad.sh`:
- Resultado de la suite (`.trx`):
- Reporte de cobertura:
- Corrida con `TZ=UTC` y con `TZ=<ambiente>`:
- Corrida sin red:
- Dos corridas seguidas / sin paralelismo:

---

## 10. Gates

| Gate | Quién | Estado | Fecha |
|---|---|---|---|
| cybersec (auth / cifrado) | | | |
| dba (dump de estructura) | | | |
| QA (lista de endpoints del contrato) | | | |
| infra (Docker en CI / cambio de Dockerfile) | | | |

---

## 11. Preguntas abiertas
