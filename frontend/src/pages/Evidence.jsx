import {
  ArrowLeft,
  AlertTriangle,
  CircleHelp,
  Database,
  FileText,
  Layers,
  Terminal,
  ShieldCheck,
  Search,
  Copy,
  CheckCircle2,
  Activity,
} from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";

function Evidence() {
  const navigate = useNavigate();
  const location = useLocation();
  const diagnosis = location.state?.diagnosis;
  const [copied, setCopied] = useState("");

  if (!diagnosis) {
    return (
      <section className="page-content evidence-page">
        <div className="page-back">
          <button className="back-button" onClick={() => navigate("/assistant")}>
            <ArrowLeft size={16} />
            Back to Assistant
          </button>
        </div>
        <div className="empty-evidence">
          <CircleHelp size={42} />
          <h1>No diagnosis selected</h1>
          <p>
            Run a network diagnosis first to see evidence
            requirements and recommended commands.
          </p>
          <button className="primary-button" onClick={() => navigate("/assistant")}>
            Go to Assistant
          </button>
        </div>
      </section>
    );
  }

  const evidence = Array.isArray(diagnosis.evidence) ? diagnosis.evidence : [];
  const commands = Array.isArray(diagnosis.recommended_commands)
    ? diagnosis.recommended_commands
    : [];
  const remediation = Array.isArray(diagnosis.proposed_remediation)
    ? diagnosis.proposed_remediation
    : [];
  const similarCases = Array.isArray(diagnosis.similar_cases)
    ? diagnosis.similar_cases
    : [];

  const copyCommand = async (command) => {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(command);
      setTimeout(() => setCopied(""), 1500);
    } catch {
      setCopied("");
    }
  };

  const getSimilarity = (item) => {
    if (typeof item === "string") return null;
    if (typeof item.similarity === "number") return Math.round(item.similarity * 100);
    if (typeof item.similarity === "string") return item.similarity;
    return null;
  };
  const getCaseId = (item, index) => {
    if (typeof item === "string") return item;
    return item.case_id || item.id || `CASE-${String(index + 1).padStart(3, "0")}`;
  };
  const getCaseTitle = (item) => {
    if (typeof item === "string") return "Related network case";
    return item.title || item.description || "Related network case";
  };
  const getCaseStatus = (item) => {
    if (typeof item === "string") return null;
    return item.status || null;
  };

  return (
    <section className="page-content evidence-page">
      <div className="page-back">
        <button className="back-button" onClick={() => navigate("/assistant")}>
          <ArrowLeft size={16} />
          Back to Diagnosis
        </button>
      </div>

      <div className="evidence-header">
        <div className="header-left">
          <div className="eyebrow">
            <span className="pulse-dot" />
            LIVE DIAGNOSTIC WORKSPACE
          </div>
          <h1>
            Find the fault. <span className="highlight">Prove the fix.</span>
          </h1>
          <p className="header-sub">
            NetSage combines deterministic network rules with Gemini reasoning.
            Historical cases provide supporting context while observed evidence
            remains separate from AI hypotheses.
          </p>
        </div>
        <div className="evidence-case-id">
          <span>Diagnosis</span>
          <strong>{diagnosis.diagnosis_id || "—"}</strong>
          <small>{diagnosis.case_id || "AD-HOC"}</small>
          <span className="status-badge">{diagnosis.status || "RESULT_READY"}</span>
        </div>
      </div>

      <div className="evidence-summary">
        <div className="summary-icon">
          <AlertTriangle size={22} />
        </div>
        <div className="summary-main">
          <span className="summary-label">MOST LIKELY ROOT CAUSE</span>
          <h2>{diagnosis.root_cause || "No root cause established"}</h2>
          <p>{diagnosis.diagnosis || "No detailed diagnosis provided."}</p>
        </div>
        <div className="summary-confidence">
          <strong>{Math.round(Number(diagnosis.confidence || 0) * 100)}%</strong>
          <span>confidence</span>
          <span className="osi-tag">{diagnosis.osi_layer || "Layer 3/4"}</span>
        </div>
      </div>

      <div className="evidence-grid">
        <div className="evidence-card">
          <div className="evidence-card-head">
            <div className="card-icon">
              <Database size={19} />
            </div>
            <div>
              <h3>Evidence summary</h3>
              <p>Deterministic findings extracted from the supplied incident data.</p>
            </div>
          </div>
          <div className="evidence-meta-row">
            <span>
              <Layers size={14} /> OSI layer: <strong>{diagnosis.osi_layer || "Layer 3/4"}</strong>
            </span>
            <span>
              <FileText size={14} /> Evidence items: <strong>{evidence.length}</strong>
            </span>
            <span>
              <Terminal size={14} /> Commands: <strong>{commands.length}</strong>
            </span>
            <span>
              <Database size={14} /> Similar cases: <strong>{similarCases.length}</strong>
            </span>
          </div>
          {evidence.length > 0 ? (
            <ul className="evidence-list numbered">
              {evidence.map((item, index) => (
                <li key={index}>
                  <span className="item-number">{String(index + 1).padStart(2, "0")}</span>
                  <CheckCircle2 size={16} className="item-icon" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="no-evidence">
              <AlertTriangle size={17} />
              <span>No structured evidence was returned by the diagnosis engine.</span>
            </div>
          )}
        </div>

        <div className="evidence-card">
          <div className="evidence-card-head">
            <div className="card-icon warning">
              <Search size={19} />
            </div>
            <div>
              <h3>Evidence requirements</h3>
              <p>Information needed to increase confidence.</p>
            </div>
          </div>
          {diagnosis.needs_more_evidence ? (
            <div className="missing-evidence">
              <AlertTriangle size={18} />
              <div>
                <strong>More evidence required</strong>
                <p>
                  The current evidence is insufficient to establish the
                  root cause. Collect the recommended command output
                  before accepting the diagnosis.
                </p>
              </div>
            </div>
          ) : (
            <div className="verified-evidence">
              <CheckCircle2 size={18} />
              <div>
                <strong>Evidence is sufficient</strong>
                <p>The current evidence is sufficient for the generated hypothesis.</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="commands-panel">
        <div className="section-heading">
          <div className="card-icon">
            <Terminal size={19} />
          </div>
          <div>
            <h2>Recommended next commands</h2>
            <p>Commands that can verify the diagnosis.</p>
          </div>
        </div>
        {commands.length > 0 ? (
          <div className="command-list">
            {commands.map((command, index) => (
              <div className="command-row" key={index}>
                <div className="command-number">{String(index + 1).padStart(2, "0")}</div>
                <code>{command}</code>
                <button className="copy-command" onClick={() => copyCommand(command)}>
                  {copied === command ? <CheckCircle2 size={16} /> : <Copy size={16} />}
                  {copied === command ? "Copied" : "Copy"}
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-evidence">
            <Terminal size={17} />
            <span>No additional commands were recommended.</span>
          </div>
        )}
      </div>

      <div className="remediation-panel">
        <div className="section-heading">
          <div className="card-icon success">
            <ShieldCheck size={19} />
          </div>
          <div>
            <h2>Proposed remediation</h2>
            <p>Suggested corrective actions. NetSage does not execute them automatically.</p>
          </div>
        </div>
        {remediation.length > 0 ? (
          <ol className="remediation-list">
            {remediation.map((item, index) => (
              <li key={index}>
                <span>{index + 1}</span>
                <p>{item}</p>
              </li>
            ))}
          </ol>
        ) : (
          <div className="no-evidence">
            <ShieldCheck size={17} />
            <span>No remediation was returned.</span>
          </div>
        )}
      </div>

      <div className="similar-panel">
        <div className="section-heading">
          <div className="card-icon">
            <Database size={19} />
          </div>
          <div>
            <h2>Similar historical cases</h2>
            <p>Previously stored network incidents used as supporting context.</p>
          </div>
        </div>
        {similarCases.length > 0 ? (
          <div className="similar-cases">
            {similarCases.map((item, index) => {
              const id = getCaseId(item, index);
              const title = getCaseTitle(item);
              const similarity = getSimilarity(item);
              const status = getCaseStatus(item);
              return (
                <div className="similar-case" key={id}>
                  <div className="case-header">
                    <strong>{id}</strong>
                    {status && <span className="case-status">{status}</span>}
                  </div>
                  <span className="case-title">{title}</span>
                  {similarity !== null && (
                    <span className="case-similarity">{similarity}% similarity</span>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="no-evidence">
            <Database size={17} />
            <span>No similar cases found.</span>
          </div>
        )}
      </div>

      <div className="metadata-panel">
        <div className="section-heading">
          <div className="card-icon">
            <Activity size={19} />
          </div>
          <div>
            <h2>Diagnosis metadata</h2>
            <p>Traceability information for this diagnosis.</p>
          </div>
        </div>
        <div className="metadata-grid">
          <div>
            <span>Diagnosis ID</span>
            <strong>{diagnosis.diagnosis_id || "—"}</strong>
          </div>
          <div>
            <span>Case ID</span>
            <strong>{diagnosis.case_id || "CUSTOM"}</strong>
          </div>
          <div>
            <span>Category</span>
            <strong>{diagnosis.category || "Routing / Security"}</strong>
          </div>
          <div>
            <span>Status</span>
            <strong className="status-ready">{diagnosis.status || "RESULT_READY"}</strong>
          </div>
          <div>
            <span>Confidence</span>
            <strong>{Math.round(Number(diagnosis.confidence || 0) * 100)}%</strong>
          </div>
          <div>
            <span>Evidence count</span>
            <strong>{evidence.length}</strong>
          </div>
        </div>
      </div>

      <div className="workflow-note">
        <ShieldCheck size={15} />
        <span>
          <strong>Responsible AI:</strong>
          Deterministic rules run before AI reasoning; historical cases are
          supporting evidence; network configuration is never modified automatically.
        </span>
      </div>
    </section>
  );
}
export default Evidence;