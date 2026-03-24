# FAAST Claude Code Marketplace

Marketplace de plugins y agentes de Claude Code del equipo FAAST.

## Instalacion

```bash
# 1. Agregar el marketplace
claude plugin marketplace add faast-app/faast-claude-marketplace

# 2. Instalar plugins
claude plugin install senior-backend-architect
```

## Plugins disponibles

| Plugin | Descripcion |
|--------|-------------|
| **senior-backend-architect** | Analisis de arquitectura backend, code review, debugging, diseno de BD, documentacion tecnica. Soporta .NET, Python, Java, Node.js, C++, Go, Rust. Comando `/architect`. |

## Agregar un nuevo plugin

1. Crear el repo del plugin con la estructura `.claude-plugin/plugin.json` + `agents/` + `commands/`
2. Agregar la entrada en `.claude-plugin/marketplace.json` con el SHA del commit
3. Push y actualizar: `claude plugin marketplace update faast-marketplace`
