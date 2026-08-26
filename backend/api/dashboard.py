import csv
import json

from collections import Counter

from fastapi import APIRouter

from backend.config import settings


router = APIRouter(
    tags=["Dashboard"]
)


def load_cases():

    if not settings.CASES_FILE.exists():
        return []

    with open(
        settings.CASES_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return list(
            csv.DictReader(file)
        )


def load_json(
    path
):

    if not path.exists():
        return []

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except json.JSONDecodeError:

        return []


@router.get("")
def dashboard():

    cases = load_cases()

    reviews = load_json(
        settings.REVIEWS_FILE
    )

    responsible_ai = load_json(
        settings.RESPONSIBLE_AI_FILE
    )

    decisions = Counter(
        review.get(
            "decision",
            "UNKNOWN"
        )
        for review in reviews
    )

    concepts = Counter(
        case.get(
            "concept",
            "Unknown"
        )
        for case in cases
    )

    severity = Counter(
        case.get(
            "severity",
            "Unknown"
        )
        for case in cases
    )

    total_reviews = len(reviews)

    accepted = decisions.get(
        "ACCEPTED",
        0
    )

    agreement_rate = (
        accepted / total_reviews * 100
        if total_reviews
        else 0
    )

    return {

        "total_cases": len(cases),

        "review_count": total_reviews,

        "ai_human_agreement_rate": round(
            agreement_rate,
            2
        ),

        "accepted": accepted,

        "edited": decisions.get(
            "EDITED",
            0
        ),

        "rejected": decisions.get(
            "REJECTED",
            0
        ),

        "issue_types": dict(
            concepts
        ),

        "severity": dict(
            severity
        ),

        "responsible_ai_corrections": len(
            responsible_ai
        )
    }