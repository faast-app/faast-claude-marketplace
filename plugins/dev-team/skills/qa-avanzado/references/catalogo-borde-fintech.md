# Catalogo de casos negativos y de borde de negocio fintech

Material de consulta del QA Lead: se LEE completo antes de diseñar los casos de una HU R1 o R2.

Revisa este catalogo en cada HU R1/R2 y toma lo que aplique (lo que no aplique, no se fuerza):

**Montos y redondeo**
- `0`, negativo, decimal en moneda sin decimales, maximo permitido, maximo + 1, overflow (numero
  enorme), notacion cientifica (`1e6`), separadores locales (`1.234.567` vs `1,234,567.50`),
  espacios, pegar desde Excel.
- Redondeo por moneda segun la regla de la HU/negocio (referencia ISO 4217: CLP sin decimales;
  PEN, COP y USD con 2; UF con su propia precision). Verificar que el MISMO monto redondeado
  aparece igual en pantalla, API, BD, PDF/Excel exportado y correo.
- Sumas y prorrateos: total = suma de las partes (sin centavos perdidos), comision e impuesto
  sobre la base correcta, tasa con los decimales definidos.

**Fechas y plazos**
- Fecha de vencimiento en fin de semana o **feriado del pais** de la operacion (CL/PE/CO tienen
  calendarios distintos): verificar la regla definida (corre al habil siguiente, se rechaza, etc.).
- Fin de mes (28/29/30/31), 29-02, cambio de año, hora limite de corte del dia, zona horaria del
  pais (`America/Santiago`, `America/Lima`, `America/Bogota`) y cambio de horario en Chile.
- Fecha pasada, fecha hoy, rango invertido (desde > hasta), rango maximo permitido.

**Concurrencia, doble envio e idempotencia**
- Doble clic en "Girar"/"Pagar"/"Aprobar"; Enter + clic; F5 durante el envio; atras del
  navegador despues de confirmar; reenviar el mismo request (misma `Idempotency-Key` si la API la
  usa) → UNA sola operacion/giro, no dos.
- Dos usuarios aprobando o editando la misma operacion a la vez → uno gana, el otro recibe un
  conflicto claro; nunca estado mixto.
- Timeout de red en el medio → al reintentar no se duplica.

**Permisos, rol y tenant**
- Cada rol del criterio, y al menos un rol que NO deberia poder (boton oculto Y endpoint 403).
- **Tenant/cliente:** el usuario del cliente A no ve, no lista, no exporta ni modifica objetos del
  cliente B (cambiando el ID en URL o en el request). Fuga entre tenants = BLOQUEANTE severidad
  critica + aviso al Lead para gate de cybersec.

**Sesion**
- Sesion expirada a mitad de un formulario o de un giro → no se ejecuta la accion, se pide login,
  no se pierde ni se duplica nada. Token vencido, revocado o de otro ambiente.
- Dos pestañas abiertas; logout en una.

**Datos de identificacion y texto**
- RUT chileno con DV `K` y con DV invalido, con y sin puntos/guion; RUC peruano (11 digitos);
  NIT colombiano con DV. Acentos y `ñ` en nombres/razon social, apostrofes, textos largos,
  emojis en campos libres.
- Listas vacias, un elemento, limite de pagina, ultima pagina.

