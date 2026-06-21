import './StatusTile.css';

export default function StatusTile({ label, value, unit, status }) {
  return (
    <div className={`tile ${status ? `tile--${status}` : ''}`}>
      <span className="tile-label">{label}</span>
      <span className="tile-value">
        {value ?? <span className="tile-dash">—</span>}
        {unit && <span className="tile-unit">{unit}</span>}
      </span>
    </div>
  );
}
