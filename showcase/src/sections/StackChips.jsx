import './StackChips.css';

const STACK = [
  { name: 'Redpanda',        note: 'Kafka-compatible stream' },
  { name: 'DuckDB',          note: 'Columnar warehouse'      },
  { name: 'dbt',             note: 'Transform + test'        },
  { name: 'Python',          note: 'Generator · monitor'     },
  { name: 'FastAPI',         note: 'Status API'              },
  { name: 'React',           note: 'Status tiles'            },
  { name: 'Docker',          note: 'Full-stack compose'      },
  { name: 'GitHub Actions',  note: 'CI gate'                 },
  { name: 'Power BI',        note: 'Executive dashboard'     },
];

export default function StackChips() {
  return (
    <section id="stack">
      <div className="inner">
        <p className="section-label">Stack</p>
        <h2>Built on free, proven tools</h2>
        <p className="section-sub">
          No paid cloud services. <code>git clone</code> + <code>docker compose up</code> = £0.
        </p>
        <div className="chips">
          {STACK.map(s => (
            <div key={s.name} className="chip">
              <span className="chip-name">{s.name}</span>
              <span className="chip-note">{s.note}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
