import { useEffect, useState } from 'react';
import Navbar from './components/Navbar.jsx';
import { continueCase, diagnoseCase, getCase, getCases, getHealth, getHistory, submitReview, verifyCase } from './api.js';
import Home from './pages/Home.jsx';
import DiagnosisPage from './pages/DiagnosisPage.jsx';
import HistoryPage from './pages/HistoryPage.jsx';
import TestCasesPage from './pages/TestCasesPage.jsx';

function App() {
  const [page, setPage] = useState('dashboard');
  const [records, setRecords] = useState([]);
  const [cases, setCases] = useState([]);
  const [record, setRecord] = useState(null);
  const [busy, setBusy] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getHealth().then(() => setBackendOnline(true)).catch(() => setBackendOnline(false));
    getHistory().then(setRecords).catch(() => {});
    getCases().then(setCases).catch(() => {});
  }, []);

  const analyze = async (input, inputType) => {
    setBusy(true); setError('');
    try { const result = await diagnoseCase(input, inputType); setRecord(result); setRecords((current) => [result, ...current.filter((item) => item.case_id !== result.case_id)]); setPage('dashboard'); }
    catch (caught) { setError(caught.message); }
    finally { setBusy(false); }
  };
  const openCase = async (caseId) => { setError(''); try { setRecord(await getCase(caseId)); setPage('diagnosis'); } catch (caught) { setError(caught.message); } };
  const review = async (caseId, payload) => { try { const updated = await submitReview(caseId, payload); setRecord(updated); setRecords((current) => current.map((item) => item.case_id === caseId ? updated : item)); } catch (caught) { setError(caught.message); } };
  const continueInvestigation = async (evidence) => { if (!record || !evidence.trim()) return; setBusy(true); setError(''); try { const updated = await continueCase(record.case_id, evidence); updateRecord(updated); } catch (caught) { setError(caught.message); } finally { setBusy(false); } };
  const verifyInvestigation = async (result, detail) => { if (!record) return; setBusy(true); setError(''); try { const updated = await verifyCase(record.case_id, result, detail); updateRecord(updated); } catch (caught) { setError(caught.message); } finally { setBusy(false); } };
  const navigate = (nextPage) => { setError(''); setPage(nextPage); if (nextPage === 'history') getHistory().then(setRecords).catch(() => {}); if (nextPage === 'cases') getCases().then(setCases).catch(() => {}); };

  const updateRecord = (updated) => { setRecord(updated); setRecords((current) => current.map((item) => item.case_id === updated.case_id ? updated : item)); };
  return <div className="app-shell"><Navbar page={page} onNavigate={navigate} backendOnline={backendOnline} /><main className="content">{error && <div className="error-banner global-error">{error}</div>}{page === 'dashboard' && <Home onAnalyze={analyze} onContinue={continueInvestigation} onVerify={verifyInvestigation} busy={busy} records={records} record={record} onNavigate={navigate} onOpen={openCase} onReview={review} />}{page === 'diagnosis' && <DiagnosisPage record={record} onReview={review} onUpdated={updateRecord} />}{page === 'history' && <HistoryPage records={records} onOpen={openCase} />}{page === 'cases' && <TestCasesPage cases={cases} onNavigate={navigate} />}</main>{page !== 'dashboard' && <footer><span>NETSAGE AI / LOCAL-FIRST DIAGNOSTICS</span><span>Recommendations never execute automatically</span></footer>}</div>;
}

export default App;
