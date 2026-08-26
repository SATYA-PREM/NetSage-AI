import json
import uuid

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.config import settings

from backend.models.review import (
    ReviewCreate,
    ReviewResponse
)


router = APIRouter(
    tags=["Human Review"]
)


def load_reviews():

    if not settings.REVIEWS_FILE.exists():
        return []

    try:

        with open(
            settings.REVIEWS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except json.JSONDecodeError:

        return []


def save_reviews(
    reviews: list
):

    with open(
        settings.REVIEWS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            reviews,
            file,
            indent=2
        )


@router.get("")
def get_reviews():

    return {
        "count": len(load_reviews()),
        "reviews": load_reviews()
    }


@router.post(
    "",
    response_model=ReviewResponse
)
def create_review(
    review: ReviewCreate
):

    reviews = load_reviews()

    review_record = ReviewResponse(
        review_id=str(uuid.uuid4()),
        case_id=review.case_id,
        diagnosis_id=review.diagnosis_id,
        decision=review.decision,
        reviewer_comment=review.reviewer_comment,
        corrected_diagnosis=review.corrected_diagnosis,
        created_at=datetime.now(
            timezone.utc
        ).isoformat()
    )

    reviews.append(
        review_record.model_dump()
    )

    save_reviews(reviews)

    # Responsible-AI logging
    if review.decision in {
        "EDITED",
        "REJECTED"
    }:

        save_responsible_ai_correction(
            review_record
        )

    return review_record


def save_responsible_ai_correction(
    review: ReviewResponse
):

    path = settings.RESPONSIBLE_AI_FILE

    if path.exists():

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                records = json.load(file)

        except json.JSONDecodeError:

            records = []

    else:

        records = []

    records.append(
        {
            "review_id": review.review_id,
            "case_id": review.case_id,
            "diagnosis_id": review.diagnosis_id,
            "decision": review.decision,
            "reviewer_comment": review.reviewer_comment,
            "corrected_diagnosis": (
                review.corrected_diagnosis
            ),
            "created_at": review.created_at
        }
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=2
        )