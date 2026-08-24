import { useState } from 'react';

function TestCasesPage({ cases, onNavigate }) {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('All');
  const categories = ['All', 'Routing', 'VLAN', 'DHCP', 'DNS', 'ACL', 'Gateway', 'NAT'];
  const filtered = cases.filter((item) => {
    const text = JSON.stringify(item).toLowerCase();
    return text.includes(query.toLowerCase()) && (category === 'All' || text.includes(category.toLowerCase()));
  });
  return <><div className="page-heading explorer-heading"><div><span className="eyebrow">VERIFIED KNOWLEDGE / RAG LIBRARY</span><h1>Test case explorer</h1><p className="page-subtitle">Browse the evidence patterns NetSage uses to ground its investigations.</p></div><div className="case-count"><strong>{cases.length}</strong><span>Stored cases</span></div></div><section className="explorer-toolbar"><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search symptoms, faults, commands..." /><div className="category-filters">{categories.map((item) => <button className={category === item ? 'filter-button active' : 'filter-button'} key={item} onClick={() => setCategory(item)}>{item}</button>)}</div></section><div className="case-grid">{filtered.map((item) => <article className="case-card" key={item.case_id}><div className="case-card-top"><span className="case-id">{item.case_id}</span><span className="severity-tag">{item.severity || 'Unknown'}</span></div><h2>{item.expected_fault || 'Verified network case'}</h2><p>{item.symptom || 'No symptom description stored.'}</p><dl><div><dt>OSI</dt><dd>{item.osi_layer || 'Unknown'}</dd></div><div><dt>CONCEPT</dt><dd>{item.concept || 'Unknown'}</dd></div></dl><div className="case-evidence"><span>Evidence</span><code>{item.next_command || 'Additional output required'}</code></div><button onClick={() => onNavigate('history')}>View investigation context <span>→</span></button></article>)}{!filtered.length && <div className="empty-state"><span className="eyebrow">NO MATCHES</span><h2>No verified cases match this search</h2><p className="muted">Try a different fault domain or add a case through the backend API.</p></div>}</div></>;
}
export default TestCasesPage;
