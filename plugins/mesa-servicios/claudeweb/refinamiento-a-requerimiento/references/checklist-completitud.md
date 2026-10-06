# Checklist de completitud

Úsalo en la Fase 1 para detectar vacíos. Para cada dimensión marca: **cubierta** (con evidencia), **no aplica** (con razón) o **vacío** (genera pregunta solo si el vacío cambia el diseño). No conviertas el checklist en un cuestionario para el usuario.

## 1. Problema y objetivo
- ¿Qué problema de negocio resuelve? ¿Qué pasa hoy sin esta funcionalidad (AS-IS)?
- ¿Cómo se sabe que funcionó? (resultado observable, no métrica inventada)
- ¿Quién lo pide y para qué cliente/tenant?

## 2. Alcance
- Producto(s) afectados (en FaaST: factoring, confirming, ordering, leasing, préstamo, microfinanzas, anticipos…).
- País(es): Chile, Perú, Colombia. ¿Comportamiento distinto por país? (normativa tributaria, documentos electrónicos, feriados, formatos de identificación).
- Moneda(s): ¿multimoneda? ¿conversión? ¿redondeo y decimales por moneda?
- ¿Aplica a todos los clientes o solo a uno? ¿Se parametriza por instancia/tenant? (En FaaST el core corre una instancia por tenant y la parametrización vive en cada instancia; el multi-tenant está en el front.)
- Qué queda explícitamente fuera.

## 3. Actores y permisos
- Roles que intervienen y qué puede hacer cada uno.
- ¿Requiere perfil/permiso nuevo? ¿Quién lo asigna?
- ¿Segregación de funciones (quien crea no aprueba)?

## 4. Flujo
- Disparador: ¿qué inicia el proceso? (acción de usuario, evento, proceso batch, integración)
- Flujo principal paso a paso.
- Flujos alternativos y de error.
- ¿Aprobaciones? ¿Cuántos niveles? ¿Por monto?
- ¿Se puede deshacer, anular, reversar, editar después de confirmado?

## 5. Reglas de negocio
- Validaciones con valores concretos (límites, rangos, formatos).
- Cálculos: fórmula, base, redondeo, orden de aplicación, fecha de referencia.
- Reglas que dependen de estado, fecha, cliente, producto o país.
- Precedencia cuando dos reglas chocan.

## 6. Datos
- Campos nuevos o modificados: tipo, obligatoriedad, validación, valor por defecto, origen.
- ¿Datos históricos/existentes? ¿Migración o solo aplica hacia adelante?
- ¿Datos personales? (Ley 21.719 en Chile y equivalentes: finalidad, retención)

## 7. Estados
- Estados del objeto y transiciones permitidas.
- Qué pasa con objetos en estados intermedios al momento de desplegar.

## 8. Integraciones e impactos cruzados
- Sistemas externos: entes tributarios (SII, SUNAT, DIAN), registros (RADIAN/CESIONBNK), bancos, bureaus, scoring, firma electrónica.
- Comportamiento ante caída, timeout, respuesta duplicada o parcial.
- **Contabilidad**: ¿genera, modifica o reversa asientos? ¿Impacto tributario?
- Otros módulos afectados: cupos/líneas, gastos, bloqueos, cobranza, reportes.
- Notificaciones: a quién, por qué canal, con qué contenido, cuándo.
- Reportes y exportaciones que deban reflejar el cambio.

## 9. Auditoría y trazabilidad
- ¿Qué debe quedar registrado? (quién, cuándo, valor anterior/nuevo)
- ¿Requisitos regulatorios o de cliente sobre la evidencia?

## 10. No funcionales (solo si el insumo o el usuario los mencionan, o si su ausencia es un riesgo evidente)
- Volumen esperado, tiempo de respuesta, procesos masivos.
- Concurrencia: ¿dos usuarios sobre el mismo objeto?
- Disponibilidad, horarios de corte.

## 11. Transición y despliegue
- Regla de gobierno de FaaST: toda funcionalidad nueva se despliega desactivada por defecto, con valores por defecto por tenant. ¿Cuál es el parámetro de activación? ¿Convive con el comportamiento actual?
- ¿Requiere configuración inicial por cliente?
- ¿Capacitación o comunicación al usuario final?
