import './StatusPill.css';

const LABELS = { HEALTHY: 'Healthy', DEGRADED: 'Degraded', DOWN: 'Down' };

export default function StatusPill({ status }) {
  const key = (status || 'DOWN').toUpperCase();
  return (
    <span className={`pill pill--${key.toLowerCase()}`}>
      {LABELS[key] ?? key}
    </span>
  );
}
