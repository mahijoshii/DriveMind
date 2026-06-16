import { RefreshCw } from "lucide-react";
import type { IndexStatus } from "../types";

type Props = {
  status?: IndexStatus | null;
  loading?: boolean;
  onIndex: () => void;
};

export default function StatusCard({ status, loading, onIndex }: Props) {
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
