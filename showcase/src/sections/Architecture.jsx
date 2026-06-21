import './Architecture.css';

const STAGES = [
  { id: 'gen',      label: 'Generator',       sub: 'Python · synthetic orders', active: true  },
  { id: 'redpanda', label: 'Redpanda',         sub: 'Kafka-compatible broker',   active: true  },
  { id: 'duckdb',   label: 'DuckDB',           sub: 'Columnar warehouse',        active: true  },
  { id: 'dbt',      label: 'dbt',              sub: 'Transform + 23 tests',      active: true  },
  { id: 'serve',    label: 'Serve',            sub: 'FastAPI · React · Power BI', active: true },
];

const SUPPORT = [
  { label: 'Monitor',        sub: 'Freshness · Discord alerts' },
  { label: 'GitHub Actions', sub: 'CI gate · blocks on failure' },
];

export default function Architecture() {
  return (
    <section id="architecture" className="arch-section">
      <div className="inner">
        <p className="section-label">Architecture</p>
        <h2>Seven-stage pipeline</h2>
        <p className="section-sub">Data flows left to right. Bad data never reaches the right side.</p>

        <div className="arch-flow">
          {STAGES.map((s, i) => (
            <div key={s.id} className="arch-stage-wrap">
              <div className={`arch-stage ${s.active ? 'arch-stage--active' : ''}`}>
                <span className="arch-stage-label">{s.label}</span>
                <span className="arch-stage-sub">{s.sub}</span>
              </div>
              {i < STAGES.length - 1 && (
                <span className="arch-arrow" aria-hidden="true">→</span>
              )}
            </div>
          ))}
        </div>

        <div className="arch-support">
          {SUPPORT.map(s => (
            <div key={s.label} className="arch-support-item">
              <span className="arch-support-label">{s.label}</span>
              <span className="arch-support-sub">{s.sub}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
