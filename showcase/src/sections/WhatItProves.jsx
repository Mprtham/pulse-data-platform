import './WhatItProves.css';

const PROOFS = [
  {
    need: 'Streaming & real-time pipelines',
    proof: 'Redpanda consumer ingests events end-to-end in < 1 s. Generator publishes at configurable throughput.',
  },
  {
    need: 'Data governance & quality',
    proof: '23 automated tests + fault injection + staging filter. Bad rows are blocked before they touch any mart.',
  },
  {
    need: 'Power BI + SQL delivery',
    proof: 'PBIP file version-controlled in Git. Mart tables query directly via DuckDB connector. No export step.',
  },
  {
    need: 'Reproducibility',
    proof: 'Single docker compose up spins the full stack. dbt seeds + models are deterministic. Any reviewer can verify.',
  },
  {
    need: 'Observability & alerting',
    proof: 'Python monitor checks freshness every 30 s. Discord webhook fires on breach. GitHub Actions CI gate blocks merges on test failure.',
  },
];

export default function WhatItProves() {
  return (
    <section id="what-it-proves">
      <div className="inner">
        <p className="section-label">Portfolio signal</p>
        <h2>What it proves</h2>
        <p className="section-sub">Mapped to what UK data engineering roles actually ask for.</p>

        <div className="proves-grid">
          <div className="proves-header">
            <span>Employer need</span>
            <span>How Pulse shows it</span>
          </div>
          {PROOFS.map(p => (
            <div key={p.need} className="proves-row">
              <span className="proves-need">{p.need}</span>
              <span className="proves-proof">{p.proof}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
