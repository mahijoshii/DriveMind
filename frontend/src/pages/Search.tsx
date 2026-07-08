import { Search as SearchIcon, Send, Sparkles } from "lucide-react";
import { FormEvent, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import CitationCard from "../components/CitationCard";
import EmptyState from "../components/EmptyState";
import PageHeader from "../components/PageHeader";
import type { QueryResponse } from "../types";

const examples = [
  "What documents mention DriveMind?",
  "Find notes about internships.",
  "What deadlines are mentioned?",
  "Summarize action items from my recent docs."
];

const documentExamples = [
  "Summarize this document.",
  "What are the key points?",
  "What action items are mentioned?",
  "What dates or deadlines appear here?"
];

export default function Search() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const rawDocId = searchParams.get("docId");
  const parsedDocId = rawDocId ? Number(rawDocId) : undefined;
  const selectedDocId = Number.isFinite(parsedDocId) ? parsedDocId : undefined;
  const selectedDocTitle = searchParams.get("docTitle");
  const [question, setQuestion] = useState(selectedDocId ? "Summarize this document." : "");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await api.query(question, selectedDocId));
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
        <div className="search-hero-top">
          <div className="search-badge"><Sparkles size={24} /></div>
          <div>
            <h2>Ask your Drive like a knowledge base</h2>
            <p>{selectedDocTitle ? `Searching only inside ${selectedDocTitle}.` : "Use specific words from your docs for the strongest local-mode results."}</p>
          </div>
        </div>
        {selectedDocTitle && (
          <div className="scope-banner">
            <span>Document scope</span>
            <strong>{selectedDocTitle}</strong>
            <button type="button" onClick={() => navigate("/search")}>Search all docs</button>
          </div>
        )}
        <form className="search-box" onSubmit={submit}>
          <SearchIcon size={20} />
          <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask about plans, notes, decisions, or research..." />
          <button className="primary" disabled={loading}><Send size={18} /> {loading ? "Searching..." : "Ask"}</button>
        </form>
        <div className="prompt-row">
          {(selectedDocId ? documentExamples : examples).map((example) => (
            <button type="button" key={example} onClick={() => setQuestion(example)}>
              {example}
            </button>
          ))}
        </div>
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
