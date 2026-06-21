import './KPIs.css';

const METRICS = [
  {
    value: '23/23',
    label: 'Tests passing',
    body: "Every automated check passes on every build. Data quality isn't assumed; it's verified.",
  },
  {
    value: '~15%',
    label: 'Fault catch rate',
    body: 'About 1 in 7 events carries an injected fault. All are caught or dropped before they reach the clean tables.',
  },
  {
    value: '30 s',
    label: 'Freshness check interval',
    body: "An alert fires if data goes stale. You'd know before the business does.",
  },
  {
    value: '100%',
    label: 'CI gate coverage',
    body: 'No change ships if it breaks a test. GitHub Actions enforces it on every push.',
  },
  {
    value: '£0',
    label: 'Infrastructure cost',
    body: 'The whole platform runs locally with one command. No cloud account needed.',
  },
];

export default function KPIs() {
  return (
    <section id="kpis">
      <div className="inner">
        <p className="section-label">What we measure</p>
        <h2>The numbers that matter</h2>
        <p className="section-sub">
          Real figures from a local run. No estimates, no rounding up.
        </p>
        <div className="kpi-grid">
          {METRICS.map(m => (
            <div key={m.label} className="kpi-card">
              <span className="kpi-value">{m.value}</span>
              <span className="kpi-label">{m.label}</span>
              <p className="kpi-body">{m.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
