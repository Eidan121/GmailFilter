import { Link } from 'react-router-dom';

export function NotFound() {
  return (
    <div style={{ textAlign: 'center', paddingTop: 80 }}>
      <p style={{ fontSize: '4rem', fontFamily: 'Syne, sans-serif', fontWeight: 800, color: 'var(--text-faint)' }}>404</p>
      <p style={{ color: 'var(--text-muted)', marginBottom: 24 }}>Page not found.</p>
      <Link to="/" style={{
        background: 'var(--red)',
        color: '#fff',
        padding: '8px 20px',
        borderRadius: 'var(--radius-sm)',
        fontWeight: 600,
        fontSize: '0.875rem',
      }}>
        Go home
      </Link>
    </div>
  );
}
