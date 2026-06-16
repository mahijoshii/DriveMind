import { Chrome, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "../api/client";

export default function Login() {
  return (
    <main className="center-page">
      <section className="auth-panel">
        <Link to="/" className="brand"><span className="brand-mark">D</span>DriveMind</Link>
        <h1>Connect Google Drive</h1>
        <p>DriveMind asks for read-only access so it can find Google Docs, extract text, and build a private search index for your account.</p>
        <div className="scope-list">
          <span><ShieldCheck size={16} /> Google profile and email for sign-in</span>
          <span><ShieldCheck size={16} /> Drive metadata to list Google Docs</span>
          <span><ShieldCheck size={16} /> Google Docs read-only text extraction</span>
        </div>
        <a className="primary wide" href={api.loginUrl}><Chrome size={18} /> Continue with Google</a>
        <p className="fine-print">DriveMind does not request file edit, delete, or broad Drive write permissions.</p>
      </section>
    </main>
  );
}
