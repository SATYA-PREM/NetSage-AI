import Diagnosis from '../components/Diagnosis.jsx';
import Evidence from '../components/Evidence.jsx';
import SimilarCases from '../components/SimilarCases.jsx';
import ReviewPanel from '../components/ReviewPanel.jsx';
import Roadmap from '../components/Roadmap.jsx';

function DiagnosisPage({ record, onReview, onUpdated }) {
	if (!record) {
		return <section className="panel empty-state"><span className="eyebrow">NO INVESTIGATION SELECTED</span><h2>Start with a network symptom</h2><p className="muted">Return to the dashboard to submit text or a CSV case.</p></section>;
	}

	const reviewStatus = record.human_review?.status || 'pending';
	const diagnosis = record.diagnosis || {};

	return <>
		<div className="page-heading"><div><span className="eyebrow">{record.case_id}</span><h1>Investigation report</h1></div><span className={`pending-pill ${reviewStatus}`}>{reviewStatus}</span></div>
		<Diagnosis record={record} />
		<Roadmap caseId={record.case_id} initialSteps={diagnosis.roadmap || []} initialSummary={diagnosis.final_summary || null} onUpdated={onUpdated} />
		<div className="lower-grid"><Evidence checks={record.deterministic_checks} /><SimilarCases cases={record.matched_cases} /></div>
		<ReviewPanel caseId={record.case_id} onReview={onReview} />
	</>;
}
export default DiagnosisPage;
