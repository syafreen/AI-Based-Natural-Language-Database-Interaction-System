import { TableProperties } from 'lucide-react';

export default function ResultsTable({ response }) {
  if (!response) {
    return null;
  }

  const rows = response.data || [];
  const columns = response.columns || [];

  return (
    <section className="panel resultsPanel">
      <div className="panelHeader">
        <h2><TableProperties size={17} /> Results</h2>
        <span>{response.row_count} rows in {response.execution_time_ms} ms</span>
      </div>

      {response.summary ? <p className="summary">{response.summary}</p> : null}

      {rows.length === 0 ? (
        <div className="emptyState">No rows returned.</div>
      ) : (
        <div className="tableWrap">
          <table>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={index}>
                  {columns.map((column) => (
                    <td key={column}>{formatCell(row[column])}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function formatCell(value) {
  if (value === null || value === undefined) {
    return 'NULL';
  }

  if (typeof value === 'object') {
    return JSON.stringify(value);
  }

  return String(value);
}
