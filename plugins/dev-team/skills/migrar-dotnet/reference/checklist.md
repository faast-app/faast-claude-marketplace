# Checklist de migración .NET — `<componente>`

**Repo:** · **Rama:** `pase/{id}_migracion-dotnet_{instancia}` · **Carril:** 🟢/🟡/🔴
**TFM origen:** · **TFM destino:** `${TFM_DESTINO}` · **Saltos:**
**Responsable:** · **Fecha inicio:** · **Fecha cierre:**

> Cualquier "no" bloquea. Se adjunta al handoff.
> Los ítems marcados **(gate)** requieren firma de otro rol.

---

## 0. Encuadre

- [ ] `parametros.env` leído y **`SOPORTE_HASTA` no vencido**.
- [ ] El componente está **vivo** (commits recientes, tráfico por DNS, dueño de negocio).
- [ ] Decidido el orden respecto de la dockerización (`SKILL.md` §5) y anotado cuál.
- [ ] **No hay otra migración abierta en este repo.**

## 1. Análisis previo

- [ ] `analisis-previo.sh` ejecutado; salida en el informe.
- [ ] **TFM origen leído del `.csproj`** (y de `Directory.Build.props` si existe), no del Dockerfile.
- [ ] Verificado si `develop` y **lo desplegado** coinciden. Si no: **resuelto antes de empezar** (§5 de `06-matriz-componentes`).
- [ ] `AssemblyName` real verificado.
- [ ] `global.json` revisado (pin + `rollForward`).
- [ ] Bloqueadores duros evaluados: WCF servidor, EF6, `BinaryFormatter`, GDI+ **real**, LDAP.
- [ ] `using System.Drawing` clasificado: **huérfano / primitivas / GDI+ real**.
- [ ] `UseUrls` verificado (E-RT-02) — **no basta con que no diga `localhost`**.
- [ ] Hangfire: identificado si es host y **contra qué storage real** (no el del csproj).
- [ ] Licencias verificadas: GemBox, QuestPDF, AutoMapper, MediatR.
- [ ] Dependencias externas congeladas identificadas (Jasper, SSRS, Softland, Cavali, SII).
- [ ] **Carril asignado.** Si es 🔴: se paró y se escaló. No se sigue.

## 2. Preparación

- [ ] Versiones flotantes (`*`) **fijadas**, en commit propio (E-NU-03).
- [ ] Newtonsoft ≥ 13.0.3 (E-JSON-03), en commit propio.
- [ ] Rama `pase/` cortada **de la punta de la rama de ambiente**, no de `develop`.
- [ ] **Snapshot de contrato ANTES de tocar el csproj**, contra el componente corriendo hoy.
- [ ] Lista de endpoints de negocio para el humo, con su línea base de respuestas.

## 3. Escalones

Uno por fila. Cada uno cierra con build limpio y commit propio.

| Escalón | TFM | Build limpio | Commit | Warnings nuevos | Notas |
|---|---|---|---|---|---|
| 1 | | ☐ | | | |
| 2 | | ☐ | | | |
| 3 | `${TFM_DESTINO}` | ☐ | | | |

- [ ] Todos los `.csproj` **y** `Directory.Build.props` en `${TFM_DESTINO}`.
- [ ] Proyectos de test alineados al mismo TFM (E-CS-03).
- [ ] `global.json` actualizado con `rollForward: latestFeature`.
- [ ] `dotnet restore` sin `NU1605` / `NU1608` **sin resolver** (no silenciados).
- [ ] `dotnet build -c Release`: **0 errores**.
- [ ] **Ningún `NoWarn` agregado** durante la migración.
- [ ] `SYSLIB*` / `CS0618` **anotados con decisión** (no silenciados).
- [ ] `dotnet list package --vulnerable --include-transitive`: sin alta sin ticket.
- [ ] `dotnet list package --deprecated`: anotado.
- [ ] Solo se actualizaron los paquetes que el salto exigía.
- [ ] **AutoMapper ≤13 y MediatR ≤12.4.1** salvo decisión de negocio (E-LIC-02).

## 4. Comportamiento

- [ ] `dotnet test` pasa (si hay tests). `.trx` adjunto.
- [ ] Snapshot de contrato **después**; diff **explicado línea por línea**.
- [ ] Ningún endpoint desapareció; ningún tipo cambió; ningún `required` nuevo.
- [ ] Humo de endpoints de negocio: status + cuerpo comparados contra la línea base.
- [ ] **Serialización**: si usaba Newtonsoft, sigue usando Newtonsoft (E-JSON-01).
- [ ] **Fecha**: un caso parseado desde request y uno serializado.
- [ ] **Monto**: un caso formateado con separadores.
- [ ] **Zona horaria**: timestamp escrito en base con la hora correcta (E-TZ-01).
- [ ] **Cultura**: `InvariantGlobalization` coherente con el uso real (E-CULT-01).
- [ ] **EF**: SQL generado diffeado; conteo de filas idéntico en consultas complejas.
- [ ] **SQL Server**: `Encrypt`/`TrustServerCertificate` **explícitos** (E-SQL-01).
- [ ] **Hangfire**: mismos ids de job, **una sola** instancia en `HangFire.Server`, un job de punta a punta.
- [ ] **Documentos**: PDF/Excel real generado **y abierto** (E-LIC-01, E-NAT-01, E-SKIA-01).
- [ ] **Gateway**: cada ruta devuelve lo mismo que antes (E-OC-01).

## 5. Operación

- [ ] `ASPNETCORE_URLS` manda; sin `UseUrls`.
- [ ] Logs por stdout (E-LOG-01).
- [ ] Sentry: decidido **explícitamente** si se actualiza o se quita (E-LOG-02 / ADR-005 / ADR-012).
- [ ] Arranca y responde en el ambiente destino.
- [ ] Consumo de memoria del mismo orden que antes.
- [ ] **Rollback probado**: se volvió a la versión anterior, respondió, y se volvió a la nueva.
- [ ] **No se aplicó ninguna migración de esquema.** Si la había, la tomó el dba.

## 6. Gates

- [ ] **(gate) cybersec** — si toca JWT, claims, certificados, crypto o TLS. Firmado por: ____
- [ ] **(gate) dba** — si apareció migración de EF o cambio de storage. Firmado por: ____
- [ ] **(gate) QA** — validación funcional **con capturas de pantalla**. Firmado por: ____
- [ ] **(gate) lead / infra** — ventana y orden de despliegue. Firmado por: ____

## 7. Cierre

- [ ] Informe en `{coordinacion}/inventario/migracion/<repo>.md`.
- [ ] Errores del catálogo citados **por código** en el informe.
- [ ] **Entradas nuevas agregadas a `04-catalogo-errores.md`**, con su verificación.
- [ ] Entradas **[G]** que se ejecutaron de verdad, **repromovidas a [V]** con repo y versión.
- [ ] Correcciones al inventario (`asis-*.md`) señaladas al tech-writer.
- [ ] Handoff al lead.
- [ ] Pendientes anotados (endpoint `/health` propio, storage de Hangfire, Pomelo 10, minimal hosting).
