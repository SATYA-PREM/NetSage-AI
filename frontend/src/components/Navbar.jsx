function Navbar({ page, onNavigate, backendOnline }) {
  return <header className="navbar"><button className="brand" onClick={() => onNavigate('dashboard')}><span className="brand-mark">N</span><span><strong>NetSage <b>AI</b></strong><small>AI NETWORK TROUBLESHOOTER</small></span></button><nav>{[['dashboard', 'Dashboard'], ['diagnosis', 'Diagnose'], ['cases', 'Test Cases'], ['history', 'History']].map(([key, label]) => <button className={page === key ? 'nav-link active' : 'nav-link'} key={key} onClick={() => onNavigate(key)}>{label}</button>)}</nav><span className={backendOnline ? 'status online' : 'status'}><i /> {backendOnline ? 'API online' : 'API offline'}</span></header>;
}
export default Navbar;
