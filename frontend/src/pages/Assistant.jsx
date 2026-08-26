import {
  Activity,
  AlertTriangle,
  Bot,
  Code2,
  Layers3,
  ShieldCheck,
  Zap,
  FileText,
  Terminal,
  Database,
  Brain,
  Search,
} from "lucide-react";
import { useEffect, useState } from "react";
import DiagnosisPanel from "../components/DiagnosisPanel";
import EvidencePanel from "../components/EvidencePanel";
import ReviewPanel from "../components/ReviewPanel";
import { createReview, getCases, runDiagnosis } from "../services/api";

const initialForm = {
  symptom: "",
  topology_note: "",
  show_outputs: "",
};

function Assistant() {
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState("");
  const [form, setForm] = useState(initialForm);
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [reviewState, setReviewState] = useState("idle");
  const [reviewComment, setReviewComment] = useState("");

  useEffect(() => {
    loadCases();
  }, []);

  async function loadCases() {
    try {
      const response = await getCases();
      setCases(Array.isArray(response) ? response : response.cases || []);
    } catch (err) {
      setError(err.message);
    }
  }

  function handleCaseChange(caseId) {
    setSelectedCase(caseId);
    setDiagnosis(null);
    setError("");
    setReviewState("idle");
    if (!caseId) {
      setForm({ ...initialForm });
      return;
    }
    const selected = cases.find(
      (item) => item.case_id === caseId || item.id === caseId
    );
    if (!selected) return;
    setForm({
      symptom: selected.symptom || selected.description || "",
      topology_note: selected.topology_note || selected.topology || "",
      show_outputs: selected.show_outputs || selected.command_output || "",
    });
  }

  async function handleDiagnosis() {
    if (!form.symptom.trim()) {
      setError("Enter a network symptom before running diagnosis.");
      return;
    }
    setError("");
    setDiagnosis(null);
    setReviewState("idle");
    setLoading(true);
    try {
      const payload = {
        case_id: selectedCase || null,
        symptom: form.symptom.trim(),
        topology: form.topology_note.trim(),
        command_output: form.show_outputs.trim(),
      };
      const response = await runDiagnosis(payload);
      if (!response) throw new Error("Backend returned an empty diagnosis.");
      setDiagnosis(response);
    } catch (err) {
      setError(err.message || "Diagnosis failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleReview(decision) {
    if (!diagnosis) return;
    try {
      await createReview({
        case_id: diagnosis.case_id || selectedCase || "AD-HOC",
        diagnosis_id: diagnosis.diagnosis_id,
        decision,
        reviewer_comment: reviewComment,
        corrected_diagnosis: decision === "EDITED" ? reviewComment : null,
      });
      setReviewState(decision);
      setReviewComment("");
    } catch (err) {
      setError(err.message);
    }
  }

  const confidence = diagnosis
    ? Math.round(Number(diagnosis.confidence || 0) * 100)
    : 0;
  const evidenceCount =
    diagnosis && Array.isArray(diagnosis.evidence) ? diagnosis.evidence.length : 0;
  const commandsCount =
    diagnosis && Array.isArray(diagnosis.recommended_commands)
      ? diagnosis.recommended_commands.length
      : 0;
  const similarCount =
    diagnosis && Array.isArray(diagnosis.similar_cases)
      ? diagnosis.similar_cases.length
      : 0;

  return (
    <section className="page-content assistant-page">
      {/* Hero */}
      <div className="assistant-hero">
        <div>
          <div className="eyebrow">
            <span className="pulse-dot" />
            LIVE DIAGNOSTIC WORKSPACE
          </div>
          <h1>
            Find the fault.
            <br />
            <span>Prove the fix.</span>
          </h1>
          <p>
            NetSage combines deterministic network rules with Gemini reasoning.
            Historical cases provide supporting context while observed evidence
            remains separate from AI hypotheses.
          </p>
        </div>
        <div className="architecture-strip">
          <span>Evidence</span>
          <b>→</b>
          <span>Rules</span>
          <b>→</b>
          <span className="architecture-ai">AI</span>
          <b>→</b>
          <span>Review</span>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <AlertTriangle size={17} />
          <span>{error}</span>
          <button onClick={() => setError("")}>×</button>
        </div>
      )}

      <div className="assistant-grid">
        <DiagnosisPanel
          cases={cases}
          selectedCase={selectedCase}
          setSelectedCase={handleCaseChange}
          form={form}
          setForm={setForm}
          loading={loading}
          onDiagnose={handleDiagnosis}
        />

        <div className="panel result-panel">
          <div className="panel-head">
            <div className="panel-heading">
              <span className="step-number">02</span>
              <div>
                <h2>Diagnosis</h2>
                <p>AI hypothesis backed by supplied evidence.</p>
              </div>
            </div>
            {diagnosis && (
              <span className="result-badge">
                {diagnosis.status || "RESULT_READY"}
              </span>
            )}
          </div>

          {loading && (
            <div className="loading-state">
              <div className="loading-orbit">
                <Bot size={28} />
              </div>
              <h3>Reasoning over evidence</h3>
              <p>
                Running deterministic checks, comparing historical cases,
                and generating the diagnosis with Gemini.
              </p>
              <div className="loading-dots">
                <span />
                <span />
                <span />
              </div>
            </div>
          )}

          {!loading && !diagnosis && (
            <div className="empty-state">
              <div className="empty-orbit">
                <Search size={28} />
              </div>
              <h3>Awaiting diagnosis</h3>
              <p>
                Describe the incident in the input panel and click
                <strong> Run diagnosis</strong> to start the AI‑powered
                troubleshooting workflow.
              </p>
              <div className="empty-tags">
                <span>VLAN</span>
                <span>Routing</span>
                <span>ACL</span>
                <span>DHCP</span>
                <span>DNS</span>
                <span>NAT</span>
              </div>
            </div>
          )}

          {!loading && diagnosis && (
            <div className="diagnosis-result">
              {/* Root cause card */}
              <div className="cause-card">
                <div className="cause-icon">
                  <AlertTriangle size={20} />
                </div>
                <div className="cause-main">
                  <span>MOST LIKELY ROOT CAUSE</span>
                  <h3>
                    {diagnosis.root_cause ||
                      diagnosis.diagnosis ||
                      "No root cause established"}
                  </h3>
                </div>
                <div className="confidence">
                  <strong>{confidence}%</strong>
                  <small>confidence</small>
                  <div className="confidence-bar">
                    <i style={{ width: `${confidence}%` }} />
                  </div>
                </div>
              </div>

              {/* Quick stats */}
              <div className="diagnosis-stats">
                <div>
                  <Layers3 size={16} />
                  <span>OSI layer</span>
                  <b>{diagnosis.osi_layer || "—"}</b>
                </div>
                <div>
                  <FileText size={16} />
                  <span>Evidence</span>
                  <b>{evidenceCount}</b>
                </div>
                <div>
                  <Terminal size={16} />
                  <span>Commands</span>
                  <b>{commandsCount}</b>
                </div>
                <div>
                  <Database size={16} />
                  <span>Similar cases</span>
                  <b>{similarCount}</b>
                </div>
                <div>
                  <Activity size={16} />
                  <span>More evidence</span>
                  <b>{diagnosis.needs_more_evidence ? "Required" : "No"}</b>
                </div>
                <div>
                  <Brain size={16} />
                  <span>AI status</span>
                  <b>
                    {diagnosis.ai_analysis?.ai_available ? "Available" : "—"}
                  </b>
                </div>
              </div>

              <EvidencePanel diagnosis={diagnosis} />

              <ReviewPanel
                diagnosis={diagnosis}
                reviewState={reviewState}
                reviewComment={reviewComment}
                setReviewComment={setReviewComment}
                onSubmit={handleReview}
              />
            </div>
          )}
        </div>
      </div>

      <div className="workflow-note">
        <ShieldCheck size={15} />
        <span>
          <strong>Responsible AI:</strong>
          deterministic rules run before AI reasoning; historical cases
          are supporting evidence; network configuration is never modified
          automatically.
        </span>
      </div>
    </section>
  );
}
export default Assistant;