import { useState, useEffect } from 'react';
import { continueCase, getRoadmap, markStep } from '../api.js';

function Roadmap({ caseId, initialSteps = [], initialSummary = null, onUpdated }) {
  const [steps, setSteps] = useState(initialSteps);
  const [summary, setSummary] = useState(initialSummary);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [evidence, setEvidence] = useState('');
  const [continuing, setContinuing] = useState(false);

  const refresh = async () => {
    setLoading(true);
    try {
      const data = await getRoadmap(caseId);
      const diag = data.diagnosis || {};
      setSteps(diag.roadmap || []);
      setSummary(diag.final_summary || null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (caseId) refresh();
    // eslint-disable-next-line
  }, [caseId]);

  const executeStep = async (stepId) => {
    setError('');
    try {
      await markStep(caseId, stepId, 'done');
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  };

  const submitEvidence = async () => {
    if (!evidence.trim()) return;
    setContinuing(true);
    setError('');
    try {
      const updated = await continueCase(caseId, evidence);
      setEvidence('');
      setSteps(updated.diagnosis?.roadmap || []);
      setSummary(updated.diagnosis?.final_summary || null);
      onUpdated?.(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setContinuing(false);
    }
  };

  if (loading) return <div className="roadmap-loading">Loading roadmap…</div>;
  if (error) return <div className="roadmap-error">{error}</div>;
  if (!steps.length) {
    return <section className="roadmap panel"><div className="section-title"><div><span className="eyebrow">GUIDED INVESTIGATION</span><h3>Troubleshooting roadmap</h3></div><span>OPTIONAL</span></div><p className="roadmap-placeholder">No step-by-step roadmap was generated for this case. Use the recommended commands above to collect evidence. Commands are displayed for review only and are never run automatically.</p></section>;
  }

  const allDone = steps.every(step => step.status === 'done');

  return (
    <div className="roadmap panel">
      <div className="section-title">
        <h3>Troubleshooting Roadmap</h3>
        <span>{steps.filter(s => s.status === 'done').length} / {steps.length} done</span>
      </div>
      <ul className="roadmap-steps">
        {steps.map(step => (
          <li key={step.step_id} className={`roadmap-step ${step.status || 'pending'}`}>
            <div className="step-marker">
              {step.status === 'done' ? '✓' : step.status === 'failed' ? '✗' : '●'}
            </div>
            <div className="step-content">
              <div className="step-description">{step.description}</div>
              {step.command && <code className="step-command">{step.command}</code>}
              {step.expected_output && (
                <div className="step-expected">Expected: {step.expected_output}</div>
              )}
            </div>
            <div className="step-actions">
              {step.status === 'done' ? (
                <span className="step-done-badge">Done</span>
              ) : (
                <button
                  className="primary-button step-execute"
                  onClick={() => executeStep(step.step_id)}
                  disabled={step.status === 'done' || step.status === 'failed'}
                >
                  Mark done
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>

      {allDone && summary && (
        <div className="final-summary">
          <h4>Final Summary</h4>
          {summary.flagged_errors && summary.flagged_errors.length > 0 && (
            <div className="flagged-errors">
              <strong>Flagged errors:</strong>
              <ul>
                {summary.flagged_errors.map((err, i) => <li key={i}>{err}</li>)}
              </ul>
            </div>
          )}
          {summary.corrective_actions && summary.corrective_actions.length > 0 && (
            <div className="corrective-actions">
              <strong>Recommended corrective actions:</strong>
              <ul>
                {summary.corrective_actions.map((action, i) => <li key={i}>{action}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
      <div className="follow-up"><div><span className="eyebrow">USER VALIDATION</span><h4>Bring back the next result</h4><p>Run the displayed command yourself, then paste its output here. NetSage reassesses only after you submit evidence.</p></div><textarea value={evidence} onChange={(event) => setEvidence(event.target.value)} placeholder="Paste the validated command output..." /><button className="primary-button" disabled={continuing || !evidence.trim()} onClick={submitEvidence}>{continuing ? 'Reassessing...' : 'Submit evidence'}</button></div>
    </div>
  );
}

export default Roadmap;