import { Database, FileText, MessageSquare, Search, Settings, Sparkles } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

const nav = [
  { to: "/dashboard", label: "Dashboard", icon: Database },
  { to: "/search", label: "Search", icon: Search },
  { to: "/documents", label: "Documents", icon: FileText },
  { to: "/settings", label: "Settings", icon: Settings },
  { to: "/feedback", label: "Feedback", icon: MessageSquare }
];

export default function AppShell() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <NavLink to="/dashboard" className="brand">
          <span className="brand-mark">D</span>
          <span>DriveMind</span>
        </NavLink>
        <div className="sidebar-card">
          <Sparkles size={18} />
          <p>Private Drive search with cited AI answers.</p>
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
      </aside>
      <main className="main-panel">
        <Outlet />
      </main>
    </div>
  );
}
