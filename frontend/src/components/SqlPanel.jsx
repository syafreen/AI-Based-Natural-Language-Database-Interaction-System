import { Code2 } from 'lucide-react';

export default function SqlPanel({ sql }) {
  if (!sql) {
    return null;
  }

  return (
    <section className="panel sqlPanel">
      <div className="panelHeader">
        <h2><Code2 size={17} /> Generated SQL</h2>
        <span>Validated</span>
      </div>
      <pre className="sqlBlock"><code>{sql}</code></pre>
    </section>
  );
}
