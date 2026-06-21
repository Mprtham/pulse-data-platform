import StatusTile from '../components/StatusTile.jsx';
import StatusPill from '../components/StatusPill.jsx';
import SnapshotBanner from '../components/SnapshotBanner.jsx';
import statusData from '../data/status_sample.json';
import './DemoSection.css';

export default function DemoSection() {
  const d = statusData;

  return (
    <section id="demo" className="demo-section">
      <div className="inner">
        <p className="section-label">Live Demo</p>
        <h2>Platform Status</h2>
        <p className="section-sub">
          Four tiles. One truth: either the pipeline is healthy, or it isn't.
        </p>

        <SnapshotBanner />

        <div className="demo-tiles">
          <StatusTile
            label="Last seed event"
            value={d.last_event_date}
            status="healthy"
          />
          <StatusTile
            label="Orders ingested"
            value={d.rows_today.toLocaleString()}
            status="healthy"
          />
          <StatusTile
            label="Tests passing"
            value={`${d.tests_passing}/${d.tests_total}`}
            status={d.tests_passing === d.tests_total ? 'healthy' : 'degraded'}
          />
          <StatusTile
            label="Pipeline"
            value={<StatusPill status={d.pipeline_status} />}
            status={d.pipeline_status.toLowerCase()}
          />
        </div>
      </div>
    </section>
  );
}
