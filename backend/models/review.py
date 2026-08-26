from typing import Literal

from pydantic import BaseModel


ReviewDecision = Literal[
    "ACCEPTED",
    "EDITED",
    "REJECTED"
]


class ReviewCreate(BaseModel):

    case_id: str

    diagnosis_id: str

    decision: ReviewDecision

    reviewer_comment: str = ""

    corrected_diagnosis: str | None = None


class ReviewResponse(BaseModel):

    review_id: str

    case_id: str

    diagnosis_id: str

    decision: ReviewDecision

    reviewer_comment: str

    corrected_diagnosis: str | None

    created_at: str