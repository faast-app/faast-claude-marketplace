# FAAST Claude Code Marketplace

Marketplace de plugins y agentes de Claude Code del equipo FAAST.

## Instalacion

```bash
# 1. Agregar el marketplace (solo una vez)
claude plugin marketplace add faast-app/faast-claude-marketplace

# 2. Instalar plugins
claude plugin install senior-backend-architect
```

## Plugins disponibles

| Plugin | Descripcion |
|--------|-------------|
| **senior-backend-architect** | Analisis de arquitectura backend, code review, debugging, diseno de BD, documentacion tecnica. Soporta .NET, Python, Java, Node.js, C++, Go, Rust. Comando `/architect`. |

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
