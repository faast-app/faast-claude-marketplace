import { Link } from 'react-router-dom';

export function NotFound() {
  return (
    <main>
      <h1>404 — Pagina no encontrada</h1>
      <Link to="/">Volver al inicio</Link>
    </main>
  );
}
