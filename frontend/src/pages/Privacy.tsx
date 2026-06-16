import { Link } from "react-router-dom";

export default function Privacy() {
  return (
    <main className="doc-page">
      <Link to="/" className="brand"><span className="brand-mark">D</span>DriveMind</Link>
      <h1>Privacy Policy</h1>
      <p>DriveMind requests read-only Google permissions to list Google Docs metadata and extract Google Docs text for private indexing.</p>
      <p>Indexed chunks and embeddings are stored for search. OAuth tokens are encrypted at rest. Document contents are not written to backend logs.</p>
      <p>Users can delete indexed data and stored OAuth tokens from Settings at any time.</p>
    </main>
  );
}
