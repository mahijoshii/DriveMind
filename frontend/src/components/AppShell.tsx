import { Database, FileText, LogOut, MessageSquare, Search, Settings, Sparkles } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { api } from "../api/client";

const nav = [
  { to: "/dashboard", label: "Dashboard", icon: Database },
  { to: "/search", label: "Search", icon: Search },
  { to: "/documents", label: "Documents", icon: FileText },
  { to: "/settings", label: "Settings", icon: Settings },
  { to: "/feedback", label: "Feedback", icon: MessageSquare }
];

export default function AppShell() {
  const navigate = useNavigate();

  async function logout() {
    await api.logout();
    navigate("/", { replace: true });
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <NavLink to="/dashboard" className="brand">
            <span className="brand-mark">D</span>
            <span>DriveMind</span>
          </NavLink>
          <div className="sidebar-card">
            <Sparkles size={18} />
            <p>Private Drive search with cited AI answers and source excerpts.</p>
          </div>
          <nav>
            {nav.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink key={item.to} to={item.to} className="nav-link">
                  <Icon size={18} />
                  {item.label}
                </NavLink>
              );
            })}
          </nav>
        </div>
        <button type="button" className="logout-button" onClick={logout}>
          <LogOut size={18} />
          Sign out
        </button>
      </aside>
      <main className="main-panel">
        <Outlet />
      </main>
    </div>
  );
}
