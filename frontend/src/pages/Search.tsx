import { Search as SearchIcon, Send, Sparkles } from "lucide-react";
import { FormEvent, useState } from "react";
import { api } from "../api/client";
import CitationCard from "../components/CitationCard";
import EmptyState from "../components/EmptyState";
import PageHeader from "../components/PageHeader";
import type { QueryResponse } from "../types";

export default function Search() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await api.query(question));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <PageHeader title="Search" subtitle="Ask across indexed Docs and verify every answer with citations." />
      <section className="search-hero">
        <div className="search-badge"><Sparkles size={24} /></div>
        <form className="search-box" onSubmit={submit}>
          <SearchIcon size={20} />
          <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask about plans, notes, decisions, or research..." />
          <button className="primary" disabled={loading}><Send size={18} /> {loading ? "Searching..." : "Ask"}</button>
        </form>
      </section>
      {error && <p className="error">{error}</p>}
      {!result && <EmptyState title="No question yet" text="Index Drive from the dashboard, then ask a question to see cited answers here." />}
      {result && (
        <section className="answer-area">
          <div className="panel">
            <h2>Answer</h2>
            <p>{result.answer}</p>
          </div>
          <h2>Citations</h2>
          <div className="citation-list">
            {result.citations.map((citation, index) => <CitationCard citation={citation} key={`${citation.document_url}-${index}`} />)}
          </div>
        </section>
      )}
    </>
  );
}
