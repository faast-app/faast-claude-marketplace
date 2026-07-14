---
description: Prepara una solicitud de pase a ambiente (certificacion, puente, demo, preprod o productivo de cliente) - documento Word+PDF, auditoria de scripts del DBA y Scripts.zip. Usa el agente release-manager.
argument-hint: "[ambiente destino] [proyecto/servicio]"
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


Prepara un pase de ambiente usando el agente `release-manager`.

Pedido del usuario: $ARGUMENTS

## Flujo

1. **Recopilar datos del pase** (preguntar SOLO lo que falte):
   - Ambiente destino: certificacion | puente | demo (chile/peru/colombia) |
     preprod (co/pe) | productivo de cliente (¿cual cliente?)
   - Proyecto/servicios y versiones que se pasan
   - ¿El pase lleva scripts de BD? Si lleva: ¿el DBA ya entrego el paquete?
     (si no, crear primero handoff al `dba` para que prepare los scripts en el
     formato global de pases)

2. **Invocar al agente `release-manager`** con esos datos. El hara:
   - Auditoria del formato de los scripts del DBA (checklist completo) —
     si falla, RECHAZA y devuelve al DBA con hallazgos; repetir hasta aprobar
   - Consolidacion de `Scripts.zip` (solo con auditoria aprobada)
   - Llenado de la solicitud desde la plantilla + conversion a PDF
   - Carpeta final en `.coordination/pases/{fecha}-{ambiente}-{proyecto}/`
     con PDF + copia Word + Scripts.zip (si aplica)

3. **Mostrar al usuario**: ruta de la carpeta de pase, contenido verificado y
   resultado de la auditoria (incluyendo rechazos previos al DBA si los hubo).

## Reglas
- El documento de solicitud solo es obligatorio para los ambientes listados
  arriba; para ambientes internos preguntar si se desea
- Si el destino es productivo y no se especifico el cliente: DETENERSE y preguntar
- La carpeta de pase NUNCA se entrega incompleta
