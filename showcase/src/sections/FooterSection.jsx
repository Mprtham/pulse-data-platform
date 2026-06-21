import './FooterSection.css';

export default function FooterSection() {
  return (
    <footer className="site-footer">
      <div className="inner footer-inner">
        <div className="footer-brand">
          <span className="footer-logo">Pulse</span>
          <span className="footer-tagline">Real-time data platform · UK portfolio project</span>
        </div>

        <div className="footer-links">
          <a
            href="https://github.com/Mprtham/pulse-data-platform"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub →
          </a>
        </div>

        <div className="footer-meta">
          <span>Built by <strong>Prathamesh Mishra</strong></span>
          <span className="footer-honest">
            Snapshot demo. Synthetic data, captured 2026-06-21.
            Full live system runs locally via <code>docker compose up</code>.
            Not deployed to production.
          </span>
          <span className="footer-stack">Redpanda · DuckDB · dbt · FastAPI · React · Power BI</span>
        </div>
      </div>
    </footer>
  );
}
