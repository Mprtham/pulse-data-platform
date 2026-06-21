import { martDailyRevenue } from '../data/mart_sample.js';
import './DataQuality.css';

const TESTS = [
  { type: 'Schema (dbt)',  count: 21, examples: 'not_null, unique, accepted_values on every column' },
  { type: 'Custom SQL',    count: 2,  examples: 'assert_revenue_non_negative, assert_no_duplicate_orders_in_mart' },
];

const FAULTS = [
  { fault: 'Null invoice_no',   action: 'Dropped in stg_orders WHERE clause' },
  { fault: 'Null quantity',     action: 'Dropped in stg_orders WHERE clause' },
  { fault: 'Negative price',    action: 'Caught by assert_revenue_non_negative' },
  { fault: 'Invalid country',   action: 'Caught by accepted_values test' },
];

export default function DataQuality() {
  return (
    <section id="data-quality" className="dq-section">
      <div className="inner">
        <p className="section-label">Data Quality</p>
        <h2>The differentiator</h2>
        <p className="section-sub">
          Bad data costs UK businesses an estimated £12.9bn per year (Experian, 2021).
          Pulse catches it at the boundary — not in the boardroom.
        </p>

        <div className="dq-grid">
          <div>
            <h3 className="dq-sub-head">Test suite — 23 passing, 0 failing</h3>
            <table className="dq-table">
              <thead>
                <tr><th>Type</th><th>Count</th><th>Examples</th></tr>
              </thead>
              <tbody>
                {TESTS.map(t => (
                  <tr key={t.type}>
                    <td>{t.type}</td>
                    <td className="mono">{t.count}</td>
                    <td className="lo">{t.examples}</td>
                  </tr>
                ))}
                <tr className="dq-total">
                  <td><strong>Total</strong></td>
                  <td className="mono"><strong>23</strong></td>
                  <td className="lo">All PASS · dbt build 2026-06-21</td>
                </tr>
              </tbody>
            </table>

            <h3 className="dq-sub-head" style={{marginTop: '32px'}}>Fault injection (~15% of events)</h3>
            <table className="dq-table">
              <thead>
                <tr><th>Injected fault</th><th>How Pulse handles it</th></tr>
              </thead>
              <tbody>
                {FAULTS.map(f => (
                  <tr key={f.fault}>
                    <td className="mono lo">{f.fault}</td>
                    <td>{f.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div>
            <h3 className="dq-sub-head">Sample mart output — real data, honest snapshot</h3>
            <p className="dq-note">Synthetic UK retail orders · GBP · 3 days · 10 raw rows → 10 clean rows</p>
            <table className="dq-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Orders</th>
                  <th>Customers</th>
                  <th>Revenue (£)</th>
                  <th>Avg order (£)</th>
                </tr>
              </thead>
              <tbody>
                {martDailyRevenue.map(r => (
                  <tr key={r.revenue_date}>
                    <td className="mono">{r.revenue_date}</td>
                    <td className="mono">{r.order_count}</td>
                    <td className="mono">{r.unique_customers}</td>
                    <td className="mono">{r.total_revenue_gbp.toFixed(2)}</td>
                    <td className="mono">{r.avg_order_value_gbp.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}
