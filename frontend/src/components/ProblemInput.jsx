import { useRef, useState } from 'react';

function ProblemInput({ onAnalyze, busy }) {
  const [mode, setMode] = useState('text');
  const [value, setValue] = useState('');
  const [fileName, setFileName] = useState('');
  const fileInput = useRef(null);
  const readCsv = (file) => { const reader = new FileReader(); reader.onload = () => { setValue(reader.result); setFileName(file.name); }; reader.readAsText(file); };
  return <section className="input-panel panel"><div className="panel-heading"><div><span className="eyebrow">NEW INVESTIGATION</span><h2>What is happening on the network?</h2></div><div className="tabs"><button className={mode === 'text' ? 'tab active' : 'tab'} onClick={() => setMode('text')}>Text</button><button className={mode === 'csv' ? 'tab active' : 'tab'} onClick={() => setMode('csv')}>CSV case</button></div></div>{mode === 'text' ? <textarea value={value} onChange={(event) => setValue(event.target.value)} placeholder={'Describe symptoms, topology, or paste Cisco output...\n\nPC has IP 192.168.10.20/24.\nDefault gateway: 192.168.20.1\n\nshow ip route:\n...'} /> : <><input ref={fileInput} hidden type="file" accept=".csv,text/csv" onChange={(event) => event.target.files[0] && readCsv(event.target.files[0])} /><button className="upload-zone" onClick={() => fileInput.current?.click()}><span className="upload-icon">+</span><strong>{fileName || 'Choose a CSV case'}</strong><small>Preview the parsed contents before analysis</small></button>{value && <pre className="csv-preview">{value.slice(0, 1800)}</pre>}</>}<div className="input-footer"><span>{value.length ? `${value.length.toLocaleString()} characters ready` : 'Evidence stays local to this workspace'}</span><button className="primary-button" disabled={busy || !value.trim()} onClick={() => onAnalyze(value, mode)}>{busy ? 'Analyzing...' : 'Analyze network'}</button></div></section>;
}
export default ProblemInput;
