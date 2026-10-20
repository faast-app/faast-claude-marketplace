<!-- Plantilla de bug (po-team / refinador). Titulo: que ve mal el usuario, en una frase.
     Si redaccion.prefijoAmbienteEnBugs = true y se detecto en Demo/Preprod: "{AMBIENTE} - {titulo}". -->
## Que pasa
{{que ve mal el usuario y a quien afecta}}

## Ambiente
{{nombre exacto del ambiente}} · {{fecha}} · perfil {{rol}}

## Pasos para reproducirlo (como usuario)
1. Entrar a {{pantalla real}}
2. {{accion}}

## Resultado esperado vs obtenido
- Esperado: {{en terminos de negocio}}
- Obtenido: {{en terminos de negocio}}

## Evidencia
<!-- subida ANTES de crear el issue con subir_evidencia.sh (destino REP-AAAAMMDD-slug); video: portada embebida + link al .mp4 -->
![{{descripcion}}](https://github.com/{{org}}/{{repo}}/raw/{{rama}}/{{carpeta}}/{{REP-AAAAMMDD-slug}}/{{tema}}/{{archivo}}.png)
[ver archivo](https://github.com/{{org}}/{{repo}}/blob/{{rama}}/{{carpeta}}/{{REP-AAAAMMDD-slug}}/{{tema}}/{{archivo}}.png)

## Impacto
{{Critico | Alto | Medio | Bajo}} — {{que proceso frena, a cuantos usuarios o clientes}}

## Reproduccion
{{REPRODUCIDO consistente | REPRODUCIDO intermitente (n de m)}} por {{Mesa de Servicios #ticket | validador-po}} el {{fecha}}

Relacionado con #{{n}}
