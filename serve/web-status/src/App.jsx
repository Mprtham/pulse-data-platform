import { useState, useEffect } from 'react';
import StatusTile from './components/StatusTile';
import StatusPill from './components/StatusPill';
import PulseIndicator from './components/PulseIndicator';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const POLL_MS = 5000;

function fmtAgo(seconds) {
  if (seconds == null) return null;
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  return `${Math.floor(seconds / 3600)}h`;
}

function agoStatus(seconds) {
  if (seconds == null) return 'down';
  if (seconds > 900) return 'down';
  if (seconds > 300) return 'degraded';
  return 'healthy';
}

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const res = await fetch(`${API_URL}/status`);
        if (!res.ok) throw new Error('non-200');
        const json = await res.json();
        if (!cancelled) { setData(json); setError(false); }
      } catch {
        if (!cancelled) setError(true);
      }
    }

    poll();
    const id = setInterval(poll, POLL_MS);
    return () => { cancelled = true; clearInterval(id); };
  }, []);

  const status = error ? 'DOWN' : (data?.pipeline_status ?? 'DOWN');
  const isLive = status === 'HEALTHY';

  return (
    <div className="layout">
      <header className="header">
        <div className="header-left">
          <PulseIndicator active={isLive} />
          <h1 className="brand">Pulse</h1>
          <span className="brand-sub">Data Platform</span>
        </div>
        <div className="header-right">
          <StatusPill status={status} />
          <span className="updated">
            {data
              ? `Updated ${new Date(data.updated_at).toLocaleTimeString()}`
              : 'Connecting…'}
          </span>
        </div>
      </header>

      <main className="tiles">
        <StatusTile
          label="Last event"
          value={fmtAgo(data?.last_event_ago_s)}
          unit="ago"
          status={agoStatus(data?.last_event_ago_s)}
        />
        <StatusTile
          label="Rows today"
          value={data?.rows_today?.toLocaleString() ?? null}
          status={isLive ? 'healthy' : 'down'}
        />
        <StatusTile
          label="Tests passing"
          value={data ? `${data.tests_passing}/${data.tests_total}` : null}
          status={
            !data ? 'down'
              : data.tests_passing === data.tests_total ? 'healthy'
              : 'degraded'
          }
        />
        <StatusTile
          label="Pipeline"
          value={<StatusPill status={status} />}
          status={status.toLowerCase()}
        />
      </main>

      <footer className="footer">
        <span>Synthetic UK retail orders · Redpanda → DuckDB → dbt</span>
        <span>Polls every {POLL_MS / 1000}s · WCAG AA</span>
      </footer>
    </div>
  );
}
