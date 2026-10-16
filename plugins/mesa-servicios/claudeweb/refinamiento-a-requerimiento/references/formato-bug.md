# Formato de reporte de bug del equipo

> **Fuente:** formato de bugs productivos adoptado por el equipo (marzo 2026), formulario "Reporte de Bug" en GitHub. Si el formulario vigente en GitHub difiere de este resumen, **manda el formulario**. Reemplaza este archivo por la versión vigente cuando cambie.

Un ticket que es un error no se refina como requerimiento: se documenta con este formato y sigue el flujo de bugs. Quien reporta prioriza, QA valida y luego pasa a desarrollo. El skill ayuda a completarlo, para que no llegue solo con un título del tipo "error en paso 4".

## Campos mínimos obligatorios

Sin estos campos, el bug se devuelve a quien lo reportó:

1. **Título descriptivo**: qué falla y dónde, no "error en paso 4".
2. **Prioridad**, con criterio claro.
3. **Impacto**: usuarios afectados y si es bloqueante (bloquea completamente · se puede usar con errores · solo visual · solo afecta a cierto tipo de usuario o cantidad).
4. **Ambiente** donde ocurre.
5. **Usuario o rol afectado.**
6. **Módulo y URL específica.**
7. **Mínimo 2 evidencias**: captura del error, captura del inspector (Console o Network), video corto, enlace a Sentry o logs copiados.
8. **Pasos completos para reproducir**:
   - ambiente o URL;
   - usuario o rol;
   - navegación (Menú › opción);
   - acción;
   - **resultado (error)**;
   - **esperado**.

## Secciones del formato

| Sección | Contenido |
|---|---|
| Datos del bug | Los campos obligatorios anteriores |
| Evidencia | Capturas, inspector, video, Sentry, logs |
| Pasos para reproducir | Con resultado y esperado |
| Solución temporal | Workaround, si existe ("No aplica" si no hay) |
| Si es backend | Microservicio, endpoint, código HTTP, Request ID / Trace ID, payload, enlace a Sentry |
| Información adicional | Navegador y versión, sistema operativo, si es consistente o intermitente, fecha y hora, observaciones |
| Etiquetas para GitHub Projects | Tipo de bug, área, navegador (opcional; QA puede completarlas) |
| Criterios de resolución | Los completa QA al validar la corrección |
| Reportado por | Nombre, fecha, ticket relacionado |

## Cómo ayuda el skill

0. **Usa `assets/plantilla-bug.md`**, con el correlativo `BUG-AAAA-NNN` del registro y el alcance (`Cliente: X` si solo lo ve ese cliente por su configuración o datos; `Transversal` si lo ven todos aunque lo reporte uno).
1. **Confirma que es un error**: el sistema no hace lo que ya debería según el AS-IS, una especificación o un release. Si en realidad pide algo nuevo, es un requerimiento; si ya funciona así por diseño, es una consulta.
2. **Arma el reporte en este formato** con lo que trae el ticket. **Pide lo que falta de los campos obligatorios**, en una sola lista: evidencias, pasos, ambiente, usuario.
3. **El "esperado" sale del contexto.** Si el AS-IS, una especificación o un release dicen cómo debería funcionar, cítalo; eso confirma que es un error y no un pedido nuevo.
4. **Sentry**: si la sesión tiene conector a Sentry, busca el evento por fecha, módulo o mensaje y adjunta el enlace como evidencia.
5. **No inventa**: lo que no está en el ticket ni lo confirma el usuario queda como campo por completar, no se supone.
6. Si el ticket mezcla un error y un pedido nuevo, separa: el error va en este formato y el pedido nuevo sigue el flujo de requerimiento.
