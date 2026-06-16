import { FormEvent, useState } from "react";
import { api } from "../api/client";
import PageHeader from "../components/PageHeader";

export default function Feedback() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [sent, setSent] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    await api.feedback(message, email || undefined);
    setSent(true);
    setMessage("");
  }

  return (
    <>
      <PageHeader title="Feedback" subtitle="Share tester notes, bugs, confusing moments, or missing features." />
      <form className="panel form" onSubmit={submit}>
        <label>Email<input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" /></label>
        <label>Feedback<textarea value={message} onChange={(e) => setMessage(e.target.value)} rows={8} required /></label>
        <button className="primary">Submit feedback</button>
        {sent && <p className="success">Thanks, your feedback was saved.</p>}
      </form>
    </>
  );
}
