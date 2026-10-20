<!-- Comentario de validacion PO en el ticket. Solo con plan aprobado. UN dueño por veredicto:
     VB PO → lo publica el validador-po (etiqueta vbPO, quita observadoPO; solo validaciones en Demo/Preprod).
     Observado → lo publica el refinador con los enlaces que subio el validador (etiqueta observadoPO, quita vbPO).
     Evidencia: destino {{numero}}-{{slug}}/{{validacion-…}} subido con subir_evidencia.sh. -->
### Validacion funcional del PO — {{✅ VB PO | ⚠️ Observado}}
**Ambiente:** {{nombre}} · **Fecha:** {{fecha y hora}} · **Perfil:** {{rol}}

| Criterio | Resultado |
|---|---|
| 1. {{criterio resumido}} | {{Cumple | Observado: …}} |

![CA1 — {{descripcion}}](https://github.com/{{org}}/{{repo}}/raw/{{rama}}/{{carpeta}}/{{numero}}-{{slug}}/{{tema}}/ca1-{{resumen}}.png)
[ver archivo](https://github.com/{{org}}/{{repo}}/blob/{{rama}}/{{carpeta}}/{{numero}}-{{slug}}/{{tema}}/ca1-{{resumen}}.png)

{{Observacion en lenguaje de negocio, si aplica: que se esperaba y que se vio.}}

_Validacion funcional rapida del PO por el camino normal de uso; no reemplaza la validacion de QA._
