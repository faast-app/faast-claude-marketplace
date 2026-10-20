# 06 — Matriz de componentes de TOTAL QA

**Destino de referencia:** `${TFM_DESTINO}` = `net10.0` (ADR-017).
**Fecha:** 2026-09-21. **Fuentes:** `asis-qa-total-apis-micros.md`,
`asis-qa-total-front-gw.md`, `asis-repos-legado.md`, y verificación propia por
`git grep` sobre los 61 repos backend clonados.

---

## 1. Método y límites

- **TFM origen** sale del `.csproj` en el ref remoto (`origin/develop` salvo que se
  indique). **[V]**
- **TFM desplegado** sale del AS-IS de los servidores. **Cuando los dos no coinciden,
  se dice.** Es un hallazgo, no un error de transcripción.
- **Esfuerzo** es relativo (XS < S < M < L < XL), de arquitecto, para ordenar el plan.
  No es una estimación de fechas.
- **Los 21 frontends quedan fuera**: son React/Node. Su modernización es otro trabajo.
- **Los componentes cuyo repo no está clonado** en `~/Repositorios` están marcados
  `repo?`: de esos **no hay verificación de código**, solo lo que reporta el AS-IS.

**Leyenda de riesgo:** 🟢 mecánico · 🟡 requiere pruebas dirigidas · 🔴 hay que
resolver algo antes de empezar.

---

## 2. Gateways (12)

| # | Componente QA | Repo | TFM origen | Saltos | Riesgo | Bloqueadores / notas | Esfuerzo |
|---|---|---|---|---|---|---|---|
| G1 | QAGWBackoffice | `gw-backoffice` | net8.0 **[V]** | 1 | 🟡 | YARP + SignalR/Redis (backplane); GemBox; `MySql.Data` 8.0.18 (E-MYSQL-01); JWT **5.6.0** (E-JWT-01); versión flotante `8.0.*` | M |
| G2 | QAGW-GestionCobranza | `gw-gestion-cobranza` | net7.0 **[V]** | 2 | 🟢 | Sin nativas, sin Ocelot. Sentry 4.4.0 | S |
| G3 | GWPortalDigital | `gw-portal-digital` | net8.0 **[V]** | 1 | 🟢 | Ya en JWT 8.14.0 y Sentry 5.11.0 — **el más moderno de la flota**. `InvariantGlobalization=true` (E-CULT-01, sin uso de culturas hoy) | XS |
| G4 | QAGWFintec (.12) | `gw-factoring` (a confirmar) | net6.0 **[V]** | 2 | 🟡 | `gwSolution.dll`; 30 refs Newtonsoft; Sentry 3.40.0; Serilog a archivo (E-LOG-01) | M |
| G5 | QAGWFintec-Lea (.12) | repo? | netcoreapp3.0 | 3 | 🔴 | Repo no identificado. 9 `appsettings.*.json` por cliente. **Identificar el repo antes de nada** | L |
| G6 | QAGWFintec-Ordering (.12) | `gw-ordering` | netcoreapp3.0 **[V]** | 3 | 🟡 | Swashbuckle **5.0.0-rc4**; JWT 5.6.0; `MySql.Data` 8.0.18; GemBox; `bin/` versionado | L |
| G7 | QAGWOrdenCompras (.12) | repo? | netcoreapp3.1 (Ocelot) | 3 | 🟡 | Ocelot muy viejo. Referencia: `gw-contabilidad` (E-OC-01) | M |
| G8 | QAGWFintec-CRM (.12) | `gw-crm` | net5.0 **[V]** | 3 | 🟡 | **Ocelot 17.0.1**. Sin commits desde **2023-08**. Typo en BaseUrl (`.pee`) ya en config | M |
| G9 | QAGWRolesPerfiles (.12) | `gw-security` | net5.0 **[V]** | 3 | 🟡 | **Ocelot 17.0.1**. Sin commits desde 2023-10. Tiene Dockerfile net8 en ramas de ambiente, desalineado con `develop` net5 (E-DOCK-01) | M |
| G10 | QAGWReporteria (.12) | `gw-reporting` | net5.0 **[V]** | 3 | 🟡 | **Ocelot 17.0.1**. Sin commits desde 2023-10. `DownstreamScheme http` hacia host `https` (ya mal hoy) | M |
| G11 | QAGW-VentaCartera (.12) | `gw-venta-cartera` | net7.0 **[V]** | 2 | 🟢 | Sin Sentry, sin Newtonsoft, sin nativas. `InvariantGlobalization=true` sin culturas | XS |
| G12 | QAGW-Confirming (.12) | `gw-confirming` | net6.0 **[V]** | 2 | 🟢 | Solo Swashbuckle + Sentry. `InvariantGlobalization=true` sin culturas | XS |

> **`gw-contabilidad` no está en QA Total** pero es la pieza más útil de la tabla: ya
> corre **Ocelot 24.0.1 / net8 / Swashbuckle 9.0.4**. Es la referencia viva para G7-G10.

---

## 3. APIs y micros (26)

### 3.1 Servidor `.10` — núcleo net8

| # | Componente QA | Repo | TFM `develop` | TFM desplegado | Saltos | Riesgo | Notas | Esf. |
|---|---|---|---|---|---|---|---|---|
| A1 | QAApiBack **activo** | `micro-api-back` | net8.0 **[V]** | net8 (2.0.38) | 1 | 🟢 | **Ya dockerizado en Stage/Puente con el mismo tag.** AutoMapper 11 + MediatR ausente; Pomelo 8.0.2 (E-EF-03) | S |
| A2 | QAMicroBackoffice **activo** | `micro-backoffice` | net8.0 **[V]** | net8 (5.1.62) | 1 | 🟡 | **Corrección al inventario: NO usa EF6**, usa EF Core 8.0.6. Redis/SignalR (flotante `8.0.*`); iText; NLog a archivo; `cert/` → gate cybersec | M |
| A3 | QAMicroGestionCobranza **activo** | `micro-gestion-cobranza` | **net7.0** **[V]** | **net8** (2.4.0) | 2 | 🔴 | **Divergencia**: lo desplegado no sale de `develop`. Resolver antes (§5) | S |
| A4 | QAMicroVentaCartera **activo** | `micro-venta-cartera` | net8.0 **[V]** | net8 (1.7.10) | 1 | 🟢 | iText, ClosedXML. `InvariantGlobalization=true` sin culturas | S |
| A5 | MicroPortalDigital **activo** | `micro-portal-digital` | net8.0 **[V]** | net8 (1.1.44) | 1 | 🟡 | Hangfire embebido (18 arch.) → E-HF-02. 40 usos de `CultureInfo.InvariantCulture`, coherentes con la bandera invariante | M |
| A6 | QAMicroOperaciones *(sin tráfico)* | `micro-operations` | **net7.0** **[V]** | **net8** (2.1.1) | 2 | 🔴 | Divergencia + copia ociosa (decisión (h) de ADR-016). `cert/` → cybersec | S |
| A7 | QAMicroRolesPerfiles *(sin tráfico)* | `micro-security` | **net6.0** **[V]** | **net8** (1.4.0) | 2 | 🔴 | Divergencia. Sin dependencias: sería XS si no fuera por eso | XS |
| A8 | QAMicroConfirming *(sin tráfico)* | `micro-confirming` | **net6.0** **[V]** | **net8** (2.0.2) | 2 | 🔴 | Divergencia. Apunta a `preprd-aws-apiback.progreso.cl` (¡preprod Chile!) | S |
| A9 | QAMicroFactoring *(sin tráfico)* | `micro-factoring` | **net6.0** **[V]** | **net8** (4.7.23) | 2 | 🔴 | Divergencia + **el componente más difícil del ambiente**: PuppeteerSharp 12, QuestPDF 2023.12.6 + Skia 2.88.7, GemBox 35, 83 refs Newtonsoft, `MySql.Data` 8.0.33 | **XL** |
| A10 | QAMicroCrm *(sin tráfico)* | `micro-crm` | net6.0 **[V]** | net6 (3.0.23) | 2 | 🟢 | `MySql.Data` 8.4.0, JWT 7.5.1. Sin nativas reales (E-NAT-02) | S |

### 3.2 Servidor `.11` — legacy

| # | Componente QA | Repo | TFM origen | Saltos | Riesgo | Notas | Esf. |
|---|---|---|---|---|---|---|---|
| A11 | QAMicroEncuestas | repo? | netcoreapp3.1 | 3 | 🟡 | SSH.NET, ClosedXML. **Sin verificar** | M |
| A12 | QAMicroJuicios | repo? | netcoreapp3.1 | 3 | 🔴 | GemBox + iText + SSH.NET + **LDAP `localhost:30000` ya roto hoy**. Deploy por script Bitbucket obsoleto. **Sin verificar** | L |
| A13 | QAMicroLeasing | repo? | netcoreapp3.0 | 3 | 🔴 | GemBox + iText html2pdf + `System.Drawing.Common` **según AS-IS, sin verificar** (E-NAT-02 dice que en los repos clonados es falso positivo: **verificar este**). 9 appsettings por cliente, 454 MB | **XL** |
| A14 | QAMicroOrderingBO | repo? (`prod_micro_backoffice_ordering`) | netcoreapp3.0 | 3 | 🔴 | **El único caso reportado de EntityFramework 6** en todo el ambiente. Si se confirma, es carril Rojo. Carpeta `D:` creada en disco | **XL** |
| A15 | QAMicroOrdenCompras | repo? | netcoreapp3.1 | 3 | 🟡 | iTextSharp, Assets/. **Sin verificar** | M |
| A16 | QAMicroReporteria | `micro-reporting` | net5.0 **[V]** | 3 | 🔴 | **`System.Data.SqlClient 4.8.5` → E-SQL-01**. Depende de **Jasper Server y SSRS externos** (E-TLS-01). Sin commits desde 2024-08 | L |
| A17 | QAMicroOpeOrdering | `micro-operations-ordering` | netcoreapp3.1 **[V]** | 3 | 🟡 | Swashbuckle 5.0.0-rc4, JWT 5.6.0, Sentry 2.1.3 (los tres de 2019). `cert/` → cybersec. Ruta Windows | L |
| A18 | QAMicroOrdering | `micro-ordering` | net6.0 **[V]** | 2 | 🔴 | **PuppeteerSharp 12** (E-NAT-03) + GemBox 35 + iText. Hermano menor de `micro-factoring` | L |

### 3.3 Servidor `.14` — APIs 01

| # | Componente QA | Repo | TFM origen | Saltos | Riesgo | Notas | Esf. |
|---|---|---|---|---|---|---|---|
| A19 | QAApiBO | repo? (`prod-bo-micro`) | netcoreapp3.1 | 3 | 🔴 | **`System.DirectoryServices` (LDAP)** — no es multiplataforma. Si se confirma: **carril Rojo, no es migración**. Neitcom externo | **XL** |
| A20 | QAApiInterface | repo? | netcoreapp3.1 | 3 | 🟡 | iTextSharp + BouncyCastle. Proxy con timeout 120 s (operaciones largas). **Sin verificar** | M |
| A21 | QAApi-Int | `progreso-api-int` | net5.0 **[V]** | 3 | 🟡 | **`UseUrls` (E-RT-02)**, 71 refs Newtonsoft, NLog a archivo, `Microsoft.Data.SqlClient` (E-SQL-01), Pomelo 5.0.0 | L |
| A22 | Api-Int-portal-Clientes | `micro-integracion-portal-cliente` | net5.0 **[V]** | 3 | 🟡 | **`UseUrls`**, 62 refs Newtonsoft, NLog, Pomelo 5.0.0, Swashbuckle 5.6.3 | L |
| A23 | QAApiHangfire | `api-background-tasks` | net5.0 **[V]** | 3 | 🔴 | Hangfire + **`Hangfire.MySqlStorage` (E-HF-01)**. Sin commits desde **2023-08**. Carpeta de 2.5 GB con `.git`. **Candidato a no migrar** | L |
| A24 | QAApiCDL | `micro-cdl-portal-cliente` / `progreso-api-cdl` | net5.0 **[V]** | 3 | 🔴 | **WCF cliente** (`System.ServiceModel` flotante `4.8.*`), **`UseUrls`**, Hangfire + MySqlStorage, 76-79 refs Newtonsoft, SkiaSharp. Timeout 120 s | **XL** |
| A25 | QAApiAuth | `micro-authorization` | net6.0 **[V]** | 2 | 🔴 | **Componente de autenticación**: E-JWT-01/02/03 + E-CS-02 (`cert/`). **Gate de cybersec obligatorio.** Técnicamente simple (Pomelo 6.0.3, MediatR 11), operativamente el más sensible | M |
| A26 | QAMicroContabilidad | `micro-contabilidad` | net7.0 **[V]** | 2 | 🔴 | Hangfire 1.8.10 + **MySqlStorage** (E-HF-01/02) + **los dos conectores SQL a la vez** (E-SQL-01). Integraciones Softland/Defontana/Nubefact/Falcon. **Apunta al LB de PRODUCCIÓN** (riesgo R2 de ADR-016) | L |
| A27 | QAApiHangfire-Tasks | `micro-hangfire-tasks` | net6.0 **[V]** | 2 | 🔴 | Hangfire 1.7.33 + MySqlStorage + **jobs cada 10 min contra casi todo el ecosistema** + FTP/SFTP saliente. E-HF-02 es crítico acá | L |

### 3.4 Servidor `.17`

| # | Componente QA | Repo | TFM origen | Saltos | Riesgo | Notas | Esf. |
|---|---|---|---|---|---|---|---|
| A28 | QAApi-Int-Ext | `api-integracion-externa` | net6.0 **[V]** | 2 | 🟡 | **Superficie pública** (Cavali, IP pública — ver inventario de servidores) → cybersec. `global.json` pinea SDK 6.0.412 **sin rollForward** (E-NU-05). Apunta a apiback **prod** | M |

---

## 4. Piloto recomendado: `micro-banco`

**No está en QA Total.** Es deliberado.

| Criterio | `micro-banco` |
|---|---|
| Saltos | **2** (net7 → net8 → net10) |
| Tamaño | 1 solo `.csproj`, 1 `.sln`, `AssemblyName` explícito (`ApiBanco`) **[V]** |
| Bloqueadores | **Ninguno.** Sin WCF, sin EF6, sin `BinaryFormatter`, sin GDI+ real, sin Hangfire, sin nativas **[V]** |
| Hosting | Ya usa `WebApplication.CreateBuilder`, sin `Startup`, **sin `UseUrls`** **[V]** |
| Cobertura del catálogo | Ejercita **6 entradas de golpe**: E-JWT-01/02 (JWT 7.5.1 + JwtBearer 7), E-CS-02 (6 usos de `new X509Certificate2`), E-CULT-01 (`InvariantGlobalization=true`), E-TZ-01 (30 `DateTime.Now`), E-JSON-03 (Newtonsoft **10.0.1**, con CVE), E-EF-03 (EF Core 7 + Pomelo 7) **[V]** |
| Radio de explosión | Bajo: no está en QA Total, no tiene consumidores críticos declarados |
| Lo que **no** ejercita | Hangfire, Ocelot, nativas, EOL de 3 saltos. Para eso está el segundo piloto |

**Por qué no `micro-api-back`** (el piloto de ADR-016): es el componente con más
tráfico real del ambiente y **el único ya dockerizado en Stage/Puente**. Usarlo como
piloto de migración mezcla las dos variables que la regla 3 manda separar, sobre el
componente más crítico.

**Segundo piloto, una vez validado el primero: `gw-venta-cartera`** (G11, net7, XS, sin
dependencias) — valida el patrón en un gateway. **Tercero: `micro-authorization`**
(A25), para ejercitar el gate de cybersec con el catálogo ya probado.

### Checklist del piloto

1. [ ] `analisis-previo.sh micro-banco` → adjuntar al informe.
2. [ ] Fijar Newtonsoft 10.0.1 → 13.0.3 (commit propio).
3. [ ] Snapshot de contrato **contra el componente corriendo hoy**.
4. [ ] Escalón net7 → net8: TFM + `global.json` + restore + build. Commit.
5. [ ] Resolver E-JWT-01 (claims explícitos) con volcado de claims antes/después.
6. [ ] Escalón net8 → `${TFM_DESTINO}`. Commit.
7. [ ] Resolver E-CS-02 (`X509CertificateLoader`) en los 6 usos.
8. [ ] Verificar E-EF-03: EF Core 9 + Pomelo 9 bajo net10, humo de datos.
9. [ ] Diff de contrato + diff de respuestas + caso de fecha/monto/TZ.
10. [ ] Gate de cybersec (JWT + X509).
11. [ ] **Marcar en `04-catalogo-errores.md` como [V] cada entrada que se ejecutó de verdad.**
12. [ ] Informe + handoff. **El piloto no termina hasta que el catálogo esté actualizado.**

---

## 5. El hallazgo que hay que resolver antes de migrar nada

**En 6 componentes, lo desplegado no coincide con `develop`** **[V]**:

| Componente | `develop` | Desplegado en `.10` |
|---|---|---|
| `micro-gestion-cobranza` | net7.0 | **net8** (2.4.0) |
| `micro-operations` | net7.0 | **net8** (2.1.1) |
| `micro-security` | net6.0 | **net8** (1.4.0) |
| `micro-confirming` | net6.0 | **net8** (2.0.2) |
| `micro-factoring` | net6.0 | **net8** (4.7.23) |
| `micro-crm` | net6.0 | net6 (3.0.23) |

Alguien **ya migró estos componentes a net8** y lo desplegado no salió de `develop`
(o salió y nunca volvió). Cuatro de ellos son además las **copias ociosas sin tráfico**
del riesgo R1 / decisión (h) de ADR-016.

**Consecuencia directa para esta skill:** en esos 6, la pregunta "¿cuál es el TFM
origen?" **no tiene respuesta** hasta que alguien diga cuál es la versión buena.
Migrar desde `develop` significaría tirar un trabajo que ya está hecho y desplegado.

**Se resuelve con la decisión (h) de ADR-016, y es prerrequisito de la ola 2.**

---

## 6. Orden sugerido

Alineado con las olas de ADR-016, para que migración y dockerización avancen sobre el
mismo componente y no en orden cruzado.

| Ola | Componentes | Por qué |
|---|---|---|
| **M0** | `micro-banco` (piloto) | Valida el procedimiento y el catálogo con riesgo bajo |
| **M1** | G3 `gw-portal-digital`, G11 `gw-venta-cartera`, G12 `gw-confirming`, A4 `micro-venta-cartera`, A1 `micro-api-back` | 1-2 saltos, sin bloqueadores. Es donde se gana velocidad |
| **M2** | A10 `micro-crm`, A2 `micro-backoffice`, G2 `gw-gestion-cobranza`, A5 `micro-portal-digital` | Igual de simples, con algún detalle (Redis, Hangfire embebido) |
| **M3** | Los 6 de la §5, **una vez resuelta la decisión (h)** | Bloqueados por decisión, no por técnica |
| **M4** | A25 `micro-authorization`, A28 `api-integracion-externa`, G1 `gw-backoffice` | Auth y superficie pública: gate de cybersec |
| **M5** | G7-G10 (los 4 gateways Ocelot) | Se hacen **juntos**, tomando `gw-contabilidad` como referencia (E-OC-01). El primero cuesta, los otros tres son repetición |
| **M6** | A26, A27, A23 (Hangfire) | Requieren resolver E-HF-01 (storage) y la ventana sin jobs. **No se solapan entre sí** |
| **M7** | A18 `micro-ordering`, A9 `micro-factoring` | Nativas y navegador. `micro-factoring` al final: es el más difícil del ambiente |
| **M8** | A11-A15, A19-A22, A24, G5, G6 (EOL de 3 saltos) | **Bloqueados por la decisión (c) de ADR-016**, que además hay que reabrir a la luz de ADR-017 |

**Lo que este orden deja explícito:** nueve componentes (A11-A15, A19-A20, G5, G7) son
de **repos que no están clonados**. Antes de meterlos en cualquier ola hay que
conseguir el repo y correr `analisis-previo.sh`. Hoy sobre esos hay hipótesis, no datos.
