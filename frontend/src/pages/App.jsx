import { useState } from 'react';
import { Activity, Database, ShieldCheck, Sparkles } from 'lucide-react';
import QueryComposer from '../components/QueryComposer.jsx';
import ResultsTable from '../components/ResultsTable.jsx';
import SqlPanel from '../components/SqlPanel.jsx';
import { submitQuestion } from '../services/api.js';

const examples = [
  'Show the latest paid orders with customer emails',
  'Which users have the highest order totals?',
  'Count orders by status',
];

const stats = [
  { label: 'Schema aware', icon: Database },
  { label: 'SELECT only', icon: ShieldCheck },
  { label: 'AI powered', icon: Sparkles },
];

export default function App() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const payload = await submitQuestion(trimmed);
      setResponse(payload);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="appShell">
      <section className="heroBand">
        <div className="heroCopy">
          <p className="eyebrow">AI SQL Assistant</p>
          <h1>Ask your database. Get validated SQL and live answers.</h1>
          <p className="heroText">
            Turn plain English into safe PostgreSQL queries with a validation layer that keeps every request read-only and bounded.
          </p>
        </div>

        <div className="heroStats" aria-label="System safeguards">
          {stats.map(({ label, icon: Icon }) => (
            <div className="statTile" key={label}>
              <Icon size={18} />
              <span>{label}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="querySurface">
        <div className="titleBar">
          <div>
            <h2>Query workspace</h2>
            <p>Ask about users, orders, revenue, status, and customer activity.</p>
          </div>
          <div className="statusPill"><Activity size={15} /> Live</div>
        </div>

        <QueryComposer
          value={question}
          onChange={setQuestion}
          onSubmit={handleSubmit}
          loading={loading}
        />

        <div className="examples" aria-label="Example questions">
          {examples.map((example) => (
            <button
              className={question === example ? 'activeExample' : ''}
              key={example}
              type="button"
              onClick={() => setQuestion(example)}
            >
              {example}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="notice">
            <span className="loaderDot" />
            Generating SQL, validating it, and reading from Postgres...
          </div>
        ) : null}
        {error ? <div className="errorBox">{error}</div> : null}
      </section>

      {response ? (
        <div className="answerSummary">
          <div>
            <span>Last question</span>
            <strong>{response.question}</strong>
          </div>
          <div>
            <span>Rows</span>
            <strong>{response.row_count}</strong>
          </div>
          <div>
            <span>Execution</span>
            <strong>{response.execution_time_ms} ms</strong>
          </div>
        </div>
      ) : null}

      <div className="contentGrid">
        <SqlPanel sql={response?.sql} />
        <ResultsTable response={response} />
      </div>
    </main>
  );
}
