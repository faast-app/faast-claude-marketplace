# {{ServiceName}}

Microfrontend (Module Federation remote) del proyecto {{ProjectName}}.

## Stack
- React 18, TypeScript, Vite
- Module Federation (vite-plugin-federation)
- Expone: ./App como remoteEntry.js

## Comandos
- Dev standalone: `npm run dev` (http://localhost:{{DevPort}})
- Build: `npm run build`
- Test: `npm test`

## Integracion con Shell
El shell app carga este remote via:
```js
{{ModuleName}}: "http://localhost:{{DevPort}}/assets/remoteEntry.js"
```

{{ServiceDependencies}}
