import { useEffect, useState } from "react";
import { api } from "../api/client";
import PageHeader from "../components/PageHeader";
import StatusCard from "../components/StatusCard";
import { useAsync } from "../hooks/useAsync";

export default function Dashboard() {
  const status = useAsync(api.indexStatus, []);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    if (status.data?.status !== "running" && status.data?.status !== "queued") {
      return;
    }
    const interval = window.setInterval(() => {
      status.reload();
    }, 2000);
    return () => window.clearInterval(interval);
  }, [status.data?.status, status.reload]);

  async function startIndex() {
    setStarting(true);
    try {
      await api.startIndex();
      await status.reload();
    } finally {
      setStarting(false);
    }
  }

  return (
    <>
      <PageHeader title="Dashboard" subtitle="Index your Google Docs, monitor progress, and search with citations." />
      <section className="onboarding">
        <div>
          <span className="label">Beta safety</span>
          <h2>Privacy-first onboarding</h2>
          <p>DriveMind indexes Google Docs only. It stores document chunks and embeddings for search, never logs document contents, and lets you delete indexed data and OAuth tokens from Settings.</p>
        </div>
      </section>
      <StatusCard status={status.data} loading={starting || status.loading} onIndex={startIndex} />
      {status.error && <p className="error">{status.error}</p>}
    </>
  );
}
