import './WhatItDoes.css';

const STEPS = [
  { n: '01', head: 'Ingest live',         body: 'A Python generator streams synthetic UK retail orders, modelled on the UCI Online Retail II dataset, into Redpanda at configurable throughput. Redpanda is Kafka-compatible, so the same code runs against a production Kafka cluster unchanged.' },
  { n: '02', head: 'Check quality',       body: '23 automated dbt tests run on every build. They cover null checks, uniqueness, allowed-value ranges, and two custom SQL assertions written for this domain.' },
  { n: '03', head: 'Block bad data',      body: 'About 15% of events carry injected faults: missing keys, negative prices, and out-of-range countries. The staging model filters them out. Bad rows never reach the mart.' },
  { n: '04', head: 'Serve the dashboard', body: 'Clean mart tables are exposed to Power BI Desktop via DuckDB. A FastAPI status endpoint and React tile page give a live health view.' },
  { n: '05', head: 'Alarm on break',      body: 'A Python monitor checks data freshness every 30 seconds. If rows stop arriving or tests fail, it fires a Discord webhook alert and GitHub Actions blocks the merge.' },
];

export default function WhatItDoes() {
  return (
    <section id="what-it-does">
      <div className="inner">
        <p className="section-label">Plain English</p>
        <h2>What it does</h2>
        <p className="section-sub">Five stages. No jargon.</p>
        <ol className="steps">
          {STEPS.map(s => (
            <li key={s.n} className="step">
              <span className="step-n">{s.n}</span>
              <div>
                <strong className="step-head">{s.head}</strong>
                <p className="step-body">{s.body}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
