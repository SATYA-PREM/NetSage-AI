import { ArrowRight, Layers3, Network } from "lucide-react";

function CaseCard({ caseData, onOpen }) {
  const severity = String(caseData.severity || "medium").toLowerCase();
  return (
    <article className="case-card">
      <div className="case-top">
        <span>{caseData.case_id}</span>
        <span className={`severity ${severity}`}>
          {caseData.severity || "MEDIUM"}
        </span>
      </div>
      <h3>{caseData.title}</h3>
      <p>{caseData.symptom}</p>
      <div className="case-meta">
        <span>
          <Layers3 size={14} />
          {caseData.osi_layer || "Network"}
        </span>
        <span>
          <Network size={14} />
          {caseData.concept || "Troubleshooting"}
        </span>
      </div>
      <button onClick={() => onOpen(caseData)}>
        Open case
        <ArrowRight size={15} />
      </button>
    </article>
  );
}
export default CaseCard;