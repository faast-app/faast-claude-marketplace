# Catálogo heurístico de casos de borde

Recorre las categorías que aplican al requerimiento y genera candidatos concretos para **este** caso (no copies la lista). Al solicitante solo le preguntas los bordes que cambian el comportamiento de negocio; los puramente técnicos (concurrencia, timeouts, reintentos) se anotan como `PT-xx` para desarrollo, salvo que cambien lo que ve el usuario. Cada candidato termina en una de tres situaciones:

- El insumo ya define el comportamiento → regla `RN-xx` con su origen, fila en casos de borde y criterio `CA-xx` en la especificación.
- No está definido y cambia el diseño → pregunta `PR-xx` con propuesta por defecto.
- Es irrelevante para este requerimiento → se descarta sin mencionarlo.

## Valores y datos
- Valor en cero, negativo, vacío o nulo.
- Exactamente en el límite (igual al máximo/mínimo) y uno por encima/debajo.
- Decimales y redondeo: ¿se redondea cada línea o el total? ¿Monedas sin decimales (CLP) vs con decimales (PEN, USD, COP)?
- Formatos de identificación por país (RUT, RUC, NIT) inválidos o con dígito verificador erróneo.
- Texto muy largo, caracteres especiales, duplicados.
- Campos opcionales ausentes que una regla usa.

## Tiempo y fechas
- Fecha en feriado o fin de semana (calendarios distintos por país).
- Fecha pasada, fecha futura lejana, fecha igual a hoy.
- Fin de mes, mes de 28/29/30/31 días, año bisiesto.
- Cambio de día durante el proceso (cierre diario, procesos batch nocturnos).
- Vencimientos: ¿qué pasa el día del vencimiento y el día después?
- Zona horaria del usuario vs del servidor.

## Estados y ciclo de vida
- Acción sobre un objeto en estado no permitido.
- Objeto modificado por otro usuario entre que se abre y se guarda.
- Anulación o reversa después de confirmado; reversa parcial.
- Reintento de una acción ya ejecutada (doble clic, doble envío).
- Proceso interrumpido a mitad de camino.

## Permisos y roles
- Usuario sin el permiso intenta la acción (por UI y por API).
- El mismo usuario que creó intenta aprobar.
- Cambio de permisos con tareas en curso.

## Relaciones entre objetos
- Cliente bloqueado, sin cupo, con cupo vencido o en mora.
- Documento ya usado en otra operación.
- Cambios en datos maestros (tasas, gastos, parámetros) con operaciones en curso: ¿se usa el valor vigente al crear o al confirmar?
- Eliminación de un maestro referenciado.

## Integraciones
- Servicio externo no responde (timeout) o responde error.
- Respuesta duplicada, tardía o fuera de orden.
- Respuesta parcial en procesos masivos (algunos ítems OK, otros no).
- Datos externos contradictorios con los internos.
- ¿Reintento automático, manual o ninguno? ¿Con qué límite?

## Volumen y concurrencia
- Proceso masivo: carga de cientos o miles de registros.
- Dos procesos sobre el mismo recurso compartido (por ejemplo, el mismo cupo).
- Límites de tamaño de archivos adjuntos o cargas.

## Multipaís, multimoneda, multitenant
- Regla que difiere por país: ¿está explícita para cada país en alcance?
- Operación en moneda distinta a la del cupo o de la contabilidad.
- Tenant con parámetro desactivado: ¿comportamiento actual intacto?

## Contabilidad
- Asiento generado y luego la operación se anula: ¿reversa contable?
- Cambio que cruza un cierre contable de periodo.
- Diferencias de redondeo entre el monto operativo y el contable.
