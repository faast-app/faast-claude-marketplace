# Issue en GitHub

## Dónde vive el backlog

- **Proyecto:** GitHub Project **#38 "Product & Innovation Master Backlog"**, organización **faast-app**.
- Los issues pertenecen a **distintos repositorios**, todos agregados al mismo proyecto. Los números de issue son por repositorio, no por proyecto: el #120 de un repo no es el #120 de otro.
- **Campos del proyecto:** Tipo, Cliente, País, Área, Prioridad, Status y los sprints (Sprint BO, Sprint FO).
- Formularios de issue del equipo: "Solicitud de Funcionalidad o Mejora" y "Reporte de Bug".

## Qué entrega el skill al cerrar el ticket

| Elemento | Valor |
|---|---|
| Repositorio | [Repo donde se crean los requerimientos — confirmar con el equipo] |
| Título | `[Módulo] Verbo + qué — Cliente` |
| Cuerpo | La especificación aprobada completa (o la ficha de cambio menor) |
| Campo Tipo | Según la convención del proyecto para requerimientos |
| Campo Cliente | Cliente solicitante |
| Campo País | Países del alcance |
| Campo Área | Módulo o área |
| Campo Prioridad | Según la urgencia declarada |
| Adjuntos | Evidencia del visto bueno y capturas marcadas |
| Etiquetas | Ver tabla siguiente (se crean si no existen) |

## Etiquetas de la Mesa

| Etiqueta | Valores | Obligatoria |
|---|---|---|
| `tipo:` | `bug` · `proyecto` · `cotizacion` · `control-cambio` | Sí |
| `cliente:` / `alcance:` | `cliente:{codigo}` (uno por cliente) o `alcance:transversal` | Sí (una de las dos) |
| `producto:` | `factoring` · `confirming` · `ordering` · … (según el catálogo del equipo) | Sí |
| `prioridad:` | `critica` · `alta` · `media` · `baja` | Sí |
| `origen:` | `correo` · `reunion` · `ticket` · `chat` · `documento` | Sí |
| `mesa:` | `mesa:{correlativo}` (`mesa:PRY-2026-014`) | Sí |
| `cotizacion:` | `pendiente-aprobacion` → `aprobada` o `descartada` | Solo CTZ |
| `cc:` | `cc:sobre-{correlativo-original}` | Solo CC |

Una **CTZ sin aprobación comercial no es trabajo**: queda en el proyecto con `cotizacion:pendiente-aprobacion` y fuera de los sprints; al aprobarse cambia a `cotizacion:aprobada`, recibe su `PRY` y entra al flujo normal. Un **CC** sobre un issue que ya está en desarrollo se registra como issue nuevo con `Relacionado con #n` en el cuerpo.

## Desde Claude web

1. Entrega el **cuerpo del issue** completo (especificación o ficha) listo para pegar, el **título**, los campos del proyecto y la lista de etiquetas.
2. Si la sesión tiene **conector a GitHub** y el usuario confirma, crea el issue en el repositorio indicado, agrégalo al proyecto #38 y aplica las etiquetas. Si no, entrega además los comandos de abajo.
3. Recuerda al usuario registrar la fila en `registro-correlativos.md` (número, título, alcance, estado, enlace al issue).

## Crear el issue con `gh` (PowerShell)

Si quien usa el skill tiene `gh` instalado y autenticado (`gh auth login`; para el proyecto, `gh auth refresh -s project`):

```powershell
# 1. Crear el issue con la especificación como cuerpo
$url = gh issue create --repo faast-app/<repo> `
  --title "[Gastos] Configurar gastos por tramo de monto — Progreso" `
  --body-file .\ESP_Gastos_por_Tramo_FaaST.md

# 2. Agregarlo al proyecto #38
gh project item-add 38 --owner faast-app --url $url

# 3. Etiquetas (se crean si no existen)
gh label create "mesa:PRY-2026-014" --repo faast-app/<repo> --color "0E8A16" 2>$null
gh issue edit $url --add-label "tipo:proyecto,cliente:progreso,producto:factoring,prioridad:media,origen:reunion,mesa:PRY-2026-014"
```

Los campos del proyecto (Tipo, Cliente, País, Área, Prioridad) se completan en la vista del proyecto. Si el equipo quiere automatizarlo, se puede hacer con `gh project item-edit`, que necesita los identificadores de cada campo y opción.

## Imágenes: detalle práctico

El cuerpo del issue no puede referenciar archivos locales: `![Cambio 1](img/cambio-1.png)` no se verá en GitHub. Hay dos opciones:

- **Arrastrar las capturas al issue en la web**, en el editor del cuerpo. GitHub las sube y reemplaza la línea por su propia URL. Es lo más simple.
- Subirlas a una carpeta del repositorio y referenciarlas con su URL.

Al entregar, el skill recuerda este paso si el documento tiene capturas.

## Relación con las notas de versión

Las notas de versión se arman desde este mismo proyecto y usan la estructura "antes → ahora" en lenguaje de negocio. Si el issue trae bien escrito el bloque **"Qué cambia exactamente"** (hoy / después), la nota de versión casi se escribe sola.
