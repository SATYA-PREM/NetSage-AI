import { ChevronDown, RefreshCw, Menu, Sparkles } from "lucide-react";

function Topbar({ navigation, activePage, backendOnline, onRefresh, onOpenMenu }) {
  const currentPage = navigation.find((item) => item.id === activePage);
  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="mobile-menu-button" onClick={onOpenMenu}>
          <Menu size={20} />
        </button>
        <div className="breadcrumb">
          <span>NETSAGE AI</span>
          <ChevronDown size={13} />
          <strong>{currentPage?.label}</strong>
        </div>
      </div>
      <div className="topbar-actions">
        <div className="model-pill">
          <Sparkles size={14} />
          <span>Gemini reasoning</span>
        </div>
        <div className={`backend-indicator ${backendOnline ? "online" : ""}`}>
          <span />
          {backendOnline ? "Connected" : "Offline"}
        </div>
        <button className="icon-button" title="Refresh backend status" onClick={onRefresh}>
          <RefreshCw size={17} />
        </button>
      </div>
    </header>
  );
}
export default Topbar;