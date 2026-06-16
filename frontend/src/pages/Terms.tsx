import { Link } from "react-router-dom";

export default function Terms() {
  return (
    <main className="doc-page">
      <Link to="/" className="brand"><span className="brand-mark">D</span>DriveMind</Link>
      <h1>Terms</h1>
      <p>DriveMind is beta software intended for testing. Do not index highly sensitive production data until you have reviewed your deployment security posture.</p>
      <p>AI-generated answers may be incomplete. Always verify important decisions against the cited source documents.</p>
    </main>
  );
}
