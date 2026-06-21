import './SnapshotBanner.css';

export default function SnapshotBanner() {
  return (
    <div className="snapshot-banner" role="note">
      <span className="snapshot-icon">📸</span>
      <span>
        <strong>Snapshot demo</strong> — the full live system runs locally via{' '}
        <code>docker compose up</code>. This page shows a captured sample from{' '}
        <strong>2026-06-21</strong> (dbt build PASS=27).{' '}
        <a href="https://github.com/prathamesh-mishra/pulse-data-platform" target="_blank" rel="noopener noreferrer">
          View source on GitHub →
        </a>
      </span>
    </div>
  );
}
