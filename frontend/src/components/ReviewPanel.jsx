import { CheckCircle2, Code2, ShieldCheck, X } from "lucide-react";

function ReviewPanel({ diagnosis, reviewState, reviewComment, setReviewComment, onSubmit }) {
  if (!diagnosis) return null;
  if (reviewState !== "idle") {
    return (
      <div className="review-box">
        <div className="review-complete">
          <CheckCircle2 size={18} />
          <div>
            <strong>Review recorded</strong>
            <span>Decision: {reviewState}</span>
          </div>
        </div>
      </div>
    );
  }
  return (
    <div className="review-box">
      <div className="review-title">
        <ShieldCheck size={18} />
        <div>
          <strong>Human review</strong>
          <span>Approve, edit, or reject the AI recommendation.</span>
        </div>
      </div>
      <textarea
        value={reviewComment}
        onChange={(e) => setReviewComment(e.target.value)}
        placeholder="Reviewer note..."
      />
      <div className="review-actions">
        <button className="review-accept" onClick={() => onSubmit("ACCEPTED")}>
          <CheckCircle2 size={15} /> Accept
        </button>
        <button className="review-edit" onClick={() => onSubmit("EDITED")}>
          <Code2 size={15} /> Edit
        </button>
        <button className="review-reject" onClick={() => onSubmit("REJECTED")}>
          <X size={15} /> Reject
        </button>
      </div>
    </div>
  );
}
export default ReviewPanel;