import { ExternalLink } from "lucide-react";
import type { Citation } from "../types";

export default function CitationCard({ citation }: { citation: Citation }) {
  const relevance = Math.max(1, Math.round(citation.score * 100));
  const label = relevance >= 75 ? "Strong match" : relevance >= 45 ? "Good match" : "Possible match";
  return (
    <article className="citation-card">
      <div>
        <span className="score-pill">{label} - {relevance}</span>
        <h3>{citation.document_title}</h3>
        <p>{citation.excerpt}</p>
      </div>
      <a href={citation.document_url} target="_blank" rel="noreferrer">
        <ExternalLink size={16} />
        Open in Google Drive
      </a>
    </article>
  );
}
