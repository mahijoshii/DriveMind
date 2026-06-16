import EmptyState from "../components/EmptyState";
import PageHeader from "../components/PageHeader";
import { useAsync } from "../hooks/useAsync";
import { api } from "../api/client";

export default function Documents() {
  const { data, loading, error } = useAsync(api.documents, []);
  return (
    <>
      <PageHeader title="Documents" subtitle="Google Docs currently available in your private search index." />
      {loading && <p className="muted">Loading documents...</p>}
      {error && <p className="error">{error}</p>}
      {data?.length === 0 && <EmptyState title="No indexed documents" text="Run Index Drive from the dashboard to populate this list." />}
      <div className="document-list">
        {data?.map((doc) => (
          <a className="document-row" href={doc.web_url} target="_blank" rel="noreferrer" key={doc.id}>
            <strong>{doc.title}</strong>
            <span>{new Date(doc.indexed_at).toLocaleString()}</span>
          </a>
        ))}
      </div>
    </>
  );
}
