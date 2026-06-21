import './WhyWhoWhich.css';

const TOOLS = [
  { name: 'Redpanda',       plain: 'Moves live data fast and reliably, like a conveyor belt for events.' },
  { name: 'DuckDB',         plain: 'Stores and queries the data. A fast, free local warehouse.' },
  { name: 'dbt',            plain: 'Cleans, shapes and tests the data automatically on every build.' },
  { name: 'Python',         plain: 'Generates the live order data and watches the pipeline for problems.' },
  { name: 'FastAPI',        plain: 'Serves the live health status so anything can read it.' },
  { name: 'React',          plain: 'Shows the pipeline status on screen in real time.' },
  { name: 'Docker',         plain: 'Packages the whole system so it runs anywhere with one command.' },
  { name: 'GitHub Actions', plain: 'Blocks a code change that would break data quality before it ships.' },
  { name: 'Power BI',       plain: 'The business dashboard leaders actually read.' },
];

const WHAT = [
  "It catches missing, negative or invalid values before they reach a report.",
  "It flags the moment data stops arriving, so a broken pipeline never goes unnoticed.",
  "It blocks a code change that would break data quality.",
  "It gives a live health view anyone can read at a glance.",
  "It produces clean tables ready for a Power BI dashboard.",
];

export default function WhyWhoWhich() {
  return (
    <section id="context" className="wwwq-section">
      <div className="inner">

        <div className="wwwq-block">
          <p className="wwwq-label">Why</p>
          <p className="wwwq-body">
            Businesses lose money when reports run on bad data. One wrong number in a
            revenue report leads to one wrong decision. Most data problems stay invisible
            until they've already done damage. Pulse catches bad data the moment it
            arrives, before anyone acts on it.
          </p>
        </div>

        <div className="wwwq-block">
          <p className="wwwq-label">Who it's for</p>
          <p className="wwwq-body">
            This shows the skills a Data Engineer or Analytics Engineer uses every day.
            The people who benefit: data analysts who get data they can trust, finance
            and ops teams who get correct dashboards, and engineering leads who get an
            alert before something breaks.
          </p>
        </div>

        <div className="wwwq-block">
          <p className="wwwq-label">Which tools, and what each one does</p>
          <table className="wwwq-table">
            <tbody>
              {TOOLS.map(t => (
                <tr key={t.name}>
                  <td className="wwwq-tool">{t.name}</td>
                  <td className="wwwq-plain">{t.plain}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="wwwq-block wwwq-block--last">
          <p className="wwwq-label">What it handles</p>
          <ul className="wwwq-list">
            {WHAT.map(item => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

      </div>
    </section>
  );
}
