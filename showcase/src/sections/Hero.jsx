import PulseIndicator from '../components/PulseIndicator.jsx';
import StatusPill from '../components/StatusPill.jsx';
import './Hero.css';

export default function Hero() {
  return (
    <section className="hero" id="top">
      <div className="hero-glow" aria-hidden="true" />
      <div className="inner hero-inner">
        <div className="hero-status-row">
          <PulseIndicator active={true} />
          <StatusPill status="HEALTHY" />
          <span className="hero-status-note">Snapshot · 23/23 tests passing</span>
        </div>

        <h1 className="hero-heading">Pulse</h1>
        <p className="hero-pitch">A real-time data platform that refuses to serve bad data.</p>
        <p className="hero-sub">
          Streaming orders flow from generator to warehouse in under a second.
          Every row is tested before it reaches the dashboard. Bad data is blocked,
          not buried.
        </p>

        <div className="hero-ctas">
          <a
            className="btn btn-primary"
            href="https://github.com/Mprtham/pulse-data-platform"
            target="_blank"
            rel="noopener noreferrer"
          >
            View on GitHub
          </a>
          <a className="btn btn-secondary" href="#demo">
            See how it works
          </a>
        </div>
      </div>
    </section>
  );
}
