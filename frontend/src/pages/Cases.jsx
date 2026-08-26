import { ClipboardList, Server } from "lucide-react";
import { useEffect, useState } from "react";
import CaseCard from "../components/CaseCard";
import { getCases } from "../services/api";

function Cases({ onOpenAssistant }) {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadCases();
  }, []);

  async function loadCases() {
    try {
      setLoading(true);
      const response = await getCases();
      setCases(response.cases || response || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function openCase(caseData) {
    if (onOpenAssistant) onOpenAssistant(caseData);
  }

  return (
    <section className="page-content">
      <div className="page-title">
        <div>
          <div className="eyebrow">CASE LIBRARY</div>
          <h1>Network troubleshooting labs</h1>
          <p>Load a known network incident into the AI diagnostic workspace.</p>
        </div>
        <div className="count-card">
          <b>{cases.length}</b>
          <span>cases loaded</span>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="cases-loading">
          <Server size={28} />
          Loading cases...
        </div>
      ) : cases.length === 0 ? (
        <div className="empty-card">
          <ClipboardList size={30} />
          <h3>No cases loaded</h3>
          <p>Add records to data/cases.csv in the backend.</p>
        </div>
      ) : (
        <div className="case-grid">
          {cases.map((caseData) => (
            <CaseCard
              key={caseData.case_id}
              caseData={caseData}
              onOpen={openCase}
            />
          ))}
        </div>
      )}
    </section>
  );
}
export default Cases;