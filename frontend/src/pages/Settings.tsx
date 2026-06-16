import { Trash2 } from "lucide-react";
import { useState } from "react";
import { api } from "../api/client";
import PageHeader from "../components/PageHeader";
import { useAsync } from "../hooks/useAsync";

export default function Settings() {
  const me = useAsync(api.me, []);
  const [message, setMessage] = useState("");

  async function deleteData() {
    if (!confirm("Delete indexed chunks and stored Google tokens? You will need to reconnect Google.")) return;
    const res = await api.deleteData();
    setMessage(res.message);
  }

  return (
    <>
      <PageHeader title="Settings" subtitle="Manage your beta account, OAuth connection, and indexed data." />
      <section className="panel">
        <h2>Account</h2>
        <p>{me.loading ? "Loading..." : me.data?.email}</p>
      </section>
      <section className="panel danger-zone">
        <h2>Privacy controls</h2>
        <p>Delete stored document chunks, embeddings, indexing status, and encrypted OAuth tokens.</p>
        <button className="danger" onClick={deleteData}><Trash2 size={18} /> Delete my indexed data</button>
        {message && <p className="success">{message}</p>}
      </section>
    </>
  );
}
