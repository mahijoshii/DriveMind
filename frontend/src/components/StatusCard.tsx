import { RefreshCw } from "lucide-react";
import type { IndexMode, IndexStatus } from "../types";

type Props = {
  status?: IndexStatus | null;
  loading?: boolean;
  mode: IndexMode;
  onModeChange: (mode: IndexMode) => void;
  onIndex: () => void;
};

const modes: Array<{ value: IndexMode; label: string; description: string }> = [
  { value: "recent_opened", label: "Recently opened", description: "Docs you viewed most recently." },
  { value: "recent_modified", label: "Recently modified", description: "Docs with the newest edits." },
  { value: "owned_by_me", label: "Owned by me", description: "Docs created or owned by you." },
  { value: "shared_with_me", label: "Shared with me", description: "Docs other people shared." },
];

export default function StatusCard({ status, loading, mode, onModeChange, onIndex }: Props) {
  const processed = status?.processed ?? 0;
  const total = status?.total ?? 0;
  const pct = total ? Math.round((processed / total) * 100) : 0;
  const isIndexing = status?.status === "running" || status?.status === "queued";
  const buttonText = loading || isIndexing ? "Indexing..." : status?.status === "complete" ? "Re-index Drive" : "Index Drive";

  return (
    <section className="panel">
      <div className="section-row">
        <div>
          <h2>Indexing status</h2>
          <p>{status?.message ?? "Connect Google and index your Docs to start searching."}</p>
        </div>
        <button className="primary" onClick={onIndex} disabled={loading || isIndexing}>
          <RefreshCw size={18} />
          {buttonText}
        </button>
      </div>
      <div className="filter-grid" aria-label="Document indexing filters">
        {modes.map((item) => (
          <button
            type="button"
            className={mode === item.value ? "filter-option active" : "filter-option"}
            disabled={loading || isIndexing}
            key={item.value}
            onClick={() => onModeChange(item.value)}
          >
            <strong>{item.label}</strong>
            <span>{item.description}</span>
          </button>
        ))}
      </div>
      <div className="progress">
        <span style={{ width: `${pct}%` }} />
      </div>
      <div className="meta-row">
        <span>{status?.status ?? "idle"}</span>
        <span>{processed} / {total} docs</span>
      </div>
    </section>
  );
}
