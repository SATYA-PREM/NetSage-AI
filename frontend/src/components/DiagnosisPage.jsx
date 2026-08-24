import Diagnosis from '../components/Diagnosis.jsx';
import Evidence from '../components/Evidence.jsx';
import SimilarCases from '../components/SimilarCases.jsx';
import ReviewPanel from '../components/ReviewPanel.jsx';
import Roadmap from '../components/Roadmap.jsx';   // <-- add this

function DiagnosisPage({ record, onReview }) {
  if (!record) return <div className="panel">No diagnosis loaded.</div>;

  const roadmapSteps = record.diagnosis?.roadmap || [];
  const finalSummary = record.diagnosis?.final_summary || null;

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">{record.case_id}</span>
          <h1>Investigation report</h1>
        </div>
        <span className="pending-pill">Review pending</span>
      </div>

      <Diagnosis record={record} />

      {roadmapSteps.length > 0 && (
        <Roadmap
          caseId={record.case_id}
          initialSteps={roadmapSteps}
          initialSummary={finalSummary}
        />
      )}

      <div className="lower-grid">
        <Evidence checks={record.deterministic_checks} />
        <SimilarCases cases={record.matched_cases} />
      </div>

      <ReviewPanel caseId={record.case_id} onReview={onReview} />
    </>
  );
}

export default DiagnosisPage;