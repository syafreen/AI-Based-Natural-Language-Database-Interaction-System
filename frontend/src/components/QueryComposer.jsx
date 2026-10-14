import { LoaderCircle, SendHorizontal } from 'lucide-react';

export default function QueryComposer({ value, onChange, onSubmit, loading }) {
  return (
    <form className="composer" onSubmit={onSubmit}>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Ask a question about your data..."
        rows={3}
        disabled={loading}
      />
      <button type="submit" disabled={loading || value.trim().length < 3} aria-label="Send question">
        {loading ? <LoaderCircle className="spinIcon" size={20} /> : <SendHorizontal size={20} />}
      </button>
    </form>
  );
}
