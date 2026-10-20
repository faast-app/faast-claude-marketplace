# FAAST Claude Code Marketplace

Marketplace de plugins y agentes de Claude Code del equipo FAAST.

## Instalacion

```bash
# 1. Agregar el marketplace (solo una vez)
claude plugin marketplace add faast-app/faast-claude-marketplace

# 2. Instalar los plugins que uses
claude plugin install dev-team@faast-marketplace
claude plugin install mesa-servicios@faast-marketplace
claude plugin install po-team@faast-marketplace
claude plugin install marketing@faast-marketplace
claude plugin install senior-backend-architect@faast-marketplace

# 3. Actualizar cuando haya novedades publicadas
claude plugin marketplace update faast-marketplace
```

## Manuales de usuario

Escritos en lenguaje de negocio, paso a paso desde la instalacion, para cualquier persona:

| Manual | Markdown | PDF |
|---|---|---|
| General (todos los equipos y como se encadenan) | [GUIDE.md](GUIDE.md) | [GUIDE.pdf](GUIDE.pdf) |
| Dev Team | [plugins/dev-team/GUIDE.md](plugins/dev-team/GUIDE.md) | [GUIDE.pdf](plugins/dev-team/GUIDE.pdf) |
| Mesa de Servicios | [plugins/mesa-servicios/GUIDE.md](plugins/mesa-servicios/GUIDE.md) | [GUIDE.pdf](plugins/mesa-servicios/GUIDE.pdf) |
| Equipo del Product Owner | [plugins/po-team/GUIDE.md](plugins/po-team/GUIDE.md) | [GUIDE.pdf](plugins/po-team/GUIDE.pdf) |
| Marketing, Ventas y Publicidad | [plugins/marketing/GUIDE.md](plugins/marketing/GUIDE.md) | [GUIDE.pdf](plugins/marketing/GUIDE.pdf) |

Los PDF se regeneran con el estilo de marca FaaST: `python3 docs/manuales/build_manuales.py`.

## Plugins disponibles

| Plugin | Descripcion |
|--------|-------------|
| **senior-backend-architect** | Analisis de arquitectura backend, code review, debugging, diseno de BD, documentacion tecnica. Soporta .NET, Python, Java, Node.js, C++, Go, Rust. Comando `/architect`. |
| **dev-team** | Equipo completo de desarrollo con 23 agentes IA: PO, Arquitecto, Lead, Backend, Frontend, DBA, Infra, Release Manager, equipo de QA (lider, frontend y backend), equipo de diseño (6), equipo de ciberseguridad (4), Tech Writer y Setup. Mono-repo o multi-repo, proyectos nuevos o existentes, GitHub o Azure DevOps. Empieza con `/dev-team:start`. |
| **mesa-servicios** | Mesa de Servicios con 10 agentes IA: recibe todo lo que pide el cliente (correo, reunion, documentos, audio), pregunta lo necesario, reproduce errores con evidencia en video, arma scripts sin ejecutarlos, maqueta, documenta (BUG/PRY/CTZ) y registra el ticket en el backlog. Empieza con `/mesa-servicios:start`. |
| **po-team** | Equipo del Product Owner con 8 agentes IA: refina lo que deja la Mesa en HUs de negocio con Gherkin y puntos, planifica sprints con fechas de pase, tablero con avance por puntos y dashboard, validacion funcional rapida del PO (no reemplaza a QA), documentos y manuales. Empieza con `/po-team:start`. |
| **marketing** | Equipo de Marketing, Ventas y Publicidad con 8 agentes IA: vende el producto desglosado parte por parte — investigacion de mercado, propuesta comercial, presentaciones, video de lanzamiento cinematografico por capitulos, one-pagers y piezas para redes, sobre la marca FaaST. Empieza con `/marketing:start`. |

## Agregar un nuevo plugin

1. Crear carpeta en `plugins/nombre-del-plugin/` con la estructura:
   ```
   plugins/nombre-del-plugin/
   ├── .claude-plugin/
   │   └── plugin.json
   ├── agents/
   │   └── mi-agente.md
   ├── commands/
   │   └── mi-comando.md
   ├── README.md
   └── LICENSE
   ```
2. Agregar la entrada en `.claude-plugin/marketplace.json` con source `"./plugins/nombre-del-plugin"`
3. Push a main
4. Usuarios actualizan con: `claude plugin marketplace update faast-marketplace`
