import { ExternalLink, Search } from "lucide-react";
import { useNavigate } from "react-router-dom";
import EmptyState from "../components/EmptyState";
import PageHeader from "../components/PageHeader";
import { useAsync } from "../hooks/useAsync";
import { api } from "../api/client";

export default function Documents() {
  const { data, loading, error } = useAsync(api.documents, []);
  const navigate = useNavigate();

  function askDocument(id: number, title: string) {
    const params = new URLSearchParams({ docId: String(id), docTitle: title });
    navigate(`/search?${params.toString()}`);
  }

  return (
    <>
      <PageHeader title="Documents" subtitle="Google Docs currently available in your private search index." />
      {loading && <p className="muted">Loading documents...</p>}
      {error && <p className="error">{error}</p>}
      {data?.length === 0 && <EmptyState title="No indexed documents" text="Run Index Drive from the dashboard to populate this list." />}
      <div className="document-list">
        {data?.map((doc) => (
          <article className="document-row" key={doc.id}>
            <div>
              <strong>{doc.title}</strong>
              <span>{new Date(doc.indexed_at).toLocaleString()}</span>
            </div>
            <div className="document-actions">
              <button type="button" onClick={() => askDocument(doc.id, doc.title)}>
                <Search size={16} />
                Ask this doc
              </button>
              <a href={doc.web_url} target="_blank" rel="noreferrer">
                <ExternalLink size={16} />
                Open
              </a>
            </div>
          </article>
        ))}
      </div>
    </>
  );
}
