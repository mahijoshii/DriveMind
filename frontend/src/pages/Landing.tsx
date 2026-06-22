import { ArrowRight, FileText, LockKeyhole, Search, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <main className="landing">
      <nav className="topnav">
        <Link to="/" className="brand"><span className="brand-mark">D</span>DriveMind</Link>
        <div>
          <Link to="/privacy">Privacy</Link>
          <Link to="/terms">Terms</Link>
          <Link className="button-link" to="/login">Sign in</Link>
        </div>
      </nav>
      <section className="hero">
        <div>
          <p className="eyebrow">Private beta for Google Drive knowledge search</p>
          <h1>DriveMind</h1>
          <p className="hero-copy">Turn scattered Google Docs into a searchable memory layer. Ask a question, get a direct answer, and open the exact source in Drive.</p>
          <div className="hero-actions">
            <Link className="primary large" to="/login">Connect Google <ArrowRight size={18} /></Link>
            <Link className="ghost-link" to="/privacy">Review privacy</Link>
          </div>
        </div>
        <div className="product-preview">
          <div className="preview-window">
            <span />
            <span />
            <span />
          </div>
          <div className="preview-search"><Search size={18} /> What did we decide about launch scope?</div>
          <div className="preview-answer">
            <span>Answer</span>
            The launch plan narrows the beta to Google Docs indexing, cited answers, feedback capture, and one-click data deletion before inviting testers.
          </div>
          <div className="mini-citation"><FileText size={16} /> Product Planning Doc - "beta to Google Docs indexing..."</div>
          <div className="preview-footer">
            <span>Strong match - 94</span>
            <span>Open in Drive</span>
          </div>
        </div>
      </section>
      <section className="trust-grid">
        <div><ShieldCheck /><h2>Least-privilege access</h2><p>Read-only Drive metadata and Docs content scopes for indexing Google Docs.</p></div>
        <div><LockKeyhole /><h2>Encrypted tokens</h2><p>OAuth tokens are encrypted at rest and can be deleted from Settings.</p></div>
        <div><Search /><h2>Cited answers</h2><p>Every answer includes source titles, excerpts, and Google Drive links.</p></div>
      </section>
    </main>
  );
}
