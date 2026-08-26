import { ArrowRight, RefreshCw, ShieldCheck, Zap, AlertCircle } from "lucide-react";

function DiagnosisPanel({ cases, selectedCase, setSelectedCase, form, setForm, loading, onDiagnose }) {
  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }
  const isFormValid = form?.symptom?.trim().length > 0;

  return (
    <div className="panel input-panel">
      <div className="panel-head">
        <div className="panel-heading">
          <span className="step-number">01</span>
          <div>
            <h2>Describe the incident</h2>
            <p>Give NetSage enough evidence to reason safely.</p>
          </div>
        </div>
      </div>

      <div className="form-content">
        <div className="field-group">
          <label>
            LOAD A LAB CASE <span className="optional-tag">OPTIONAL</span>
          </label>
          <select
            value={selectedCase}
            onChange={(e) => setSelectedCase(e.target.value)}
            disabled={loading}
            className="case-select"
          >
            <option value="">Start from scratch</option>
            {cases.map((caseItem, index) => {
              const id = caseItem.case_id || caseItem.id || `CASE-${index + 1}`;
              const title = caseItem.title || caseItem.description || "Network case";
              return (
                <option key={id} value={id}>
                  {id} · {title}
                </option>
              );
            })}
          </select>
        </div>

        <div className="field-group required">
          <label>
            SYMPTOM <em className="required-asterisk">*</em>
          </label>
          <textarea
            className="symptom-input"
            value={form?.symptom || ""}
            onChange={(e) => updateField("symptom", e.target.value)}
            placeholder="Example: PC receives an IP address but cannot reach the default gateway."
            disabled={loading}
            rows={2}
          />
          {!isFormValid && form?.symptom !== undefined && (
            <div className="field-hint error">
              <AlertCircle size={14} />
              <span>Symptom is required to run a diagnosis.</span>
            </div>
          )}
        </div>

        <div className="field-group">
          <label>TOPOLOGY / CONTEXT</label>
          <textarea
            value={form?.topology_note || ""}
            onChange={(e) => updateField("topology_note", e.target.value)}
            placeholder="PC1 → SW-ACCESS-01 → SW-CORE-01 → Gateway\nVLAN 20 is the client network..."
            disabled={loading}
            rows={2}
          />
        </div>

        <div className="field-group">
          <label>SHOW COMMAND OUTPUT</label>
          <textarea
            className="terminal-input"
            value={form?.show_outputs || ""}
            onChange={(e) => updateField("show_outputs", e.target.value)}
            placeholder="Paste Cisco output here...\n\nshow interfaces trunk\nshow vlan brief\nshow ip route"
            disabled={loading}
            rows={4}
          />
        </div>

        <button
          className="primary-button diagnose-button"
          onClick={onDiagnose}
          disabled={loading || !isFormValid}
        >
          {loading ? (
            <>
              <RefreshCw size={17} className="spin" />
              Analyzing evidence...
            </>
          ) : (
            <>
              <Zap size={17} />
              Run diagnosis
              <ArrowRight size={17} />
            </>
          )}
        </button>

        <div className="safe-note">
          <ShieldCheck size={14} />
          No network configuration is changed by NetSage.
        </div>
      </div>
    </div>
  );
}
export default DiagnosisPanel;