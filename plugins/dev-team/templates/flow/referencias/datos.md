# Datos y usuarios del flujo — {dominio}/{flujo}

> Usuarios por paso (SIN secretos), datos de prueba y como distinguir variantes/modos. Las
> credenciales se leen de los archivos de acceso del proyecto por NOMBRE de variable; aqui solo
> se dice QUE cuenta usa cada paso y QUE datos se necesitan, nunca la contraseña ni el token.

## Usuarios por paso (estacion)
| Paso / Estacion | Rol | Cuenta (nombre de variable en el archivo de acceso) | Que hace |
|-----------------|-----|------------------------------------------------------|----------|
| 1 | {rol} | {VAR_USUARIO_1} | {accion} |
| 2 | {rol} | {VAR_USUARIO_2} | {accion} |

## Datos de prueba
| Dato | Valor de prueba | Nota |
|------|-----------------|------|
| {campo} | {valor} | {debe existir antes / se crea en el flujo} |

## Como distinguir variantes / modos
- **variante a:** {como se reconoce — parametro, pantalla, comportamiento}
- **variante b:** {...}

## Como encontrar un usuario por perfil (si hace falta)
{consulta o pantalla para ubicar una cuenta con el perfil correcto}
