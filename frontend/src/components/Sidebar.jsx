import { Network, ShieldCheck, X } from "lucide-react";

function Sidebar({
  navigation,
  activePage,
  setActivePage,
  mobileMenu,
  setMobileMenu,
  backendOnline,
}) {
  return (
    <>
      {mobileMenu && (
        <button className="mobile-overlay" onClick={() => setMobileMenu(false)} />
      )}
      <aside className={`sidebar ${mobileMenu ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark">
            <Network size={21} />
          </div>
          <div className="brand-text">
            <strong>NetSage</strong>
            <span>AI TROUBLESHOOTER</span>
          </div>
          <button className="sidebar-close" onClick={() => setMobileMenu(false)}>
            <X size={18} />
          </button>
        </div>

        <div className="workspace-label">WORKSPACE</div>
        <nav className="sidebar-nav">
          {navigation.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={`nav-item ${activePage === id ? "active" : ""}`}
              onClick={() => {
                setActivePage(id);
                setMobileMenu(false);
              }}
            >
              <Icon size={18} />
              <span>{label}</span>
              {activePage === id && <span className="nav-active-dot" />}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className={`status-card ${backendOnline ? "online" : ""}`}>
            <span className="status-dot" />
            <div>
              <b>{backendOnline ? "Backend online" : "Backend offline"}</b>
              <small>FastAPI · :8000</small>
            </div>
          </div>
          <div className="human-card">
            <ShieldCheck size={18} />
            <div>
              <b>Human review enabled</b>
              <small>AI recommendations require approval</small>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
export default Sidebar;