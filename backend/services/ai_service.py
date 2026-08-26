import json
import logging
import re
from typing import Any

from backend.config import settings

from google import genai


logger = logging.getLogger(__name__)


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


async def generate_diagnosis(
    evidence_package: dict[str, Any]
) -> dict[str, Any]:

    incident = evidence_package.get("incident", {})
    logger.info(
        "Gemini processing started: case_id=%s model=%s historical_matches=%d rule_findings=%d",
        incident.get("case_id", "CUSTOM"),
        settings.GEMINI_MODEL,
        len(evidence_package.get("similar_historical_cases", [])),
        len(evidence_package.get("rule_engine_findings", []))
    )

    prompt_template = settings.PROMPT_FILE.read_text(
        encoding="utf-8"
    )
    prompt = (
        f"{prompt_template}\n\n"
        "EVIDENCE PACKAGE (the only source of truth):\n"
        f"{json.dumps(evidence_package, indent=2, ensure_ascii=False)}"
    )

    response = await client.aio.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    text = (response.text or "").strip()
    logger.info(
        "Gemini response received: case_id=%s characters=%d",
        incident.get("case_id", "CUSTOM"),
        len(text)
    )

    try:
        result = json.loads(_remove_json_fences(text))

        return _normalize_result(result)

    except json.JSONDecodeError:

        logger.warning(
            "Gemini returned invalid JSON: case_id=%s",
            incident.get("case_id", "CUSTOM")
        )

        return _normalize_result({
            "ai_available": False,
            "category": "Unknown",
            "root_cause": "",
            "confidence": 0,
            "osi_layer": "",
            "evidence": [],
            "recommended_commands": [],
            "proposed_remediation": [],
            "historical_case_analysis": [],
            "uncertainties": [
                "Gemini returned invalid JSON."
            ],
            "human_review_required": True,
            "raw_response": text
        })


def _remove_json_fences(text: str) -> str:
    """Accept JSON wrapped in markdown fences without trusting extra text."""

    match = re.fullmatch(
        r"\s*```(?:json)?\s*(.*?)\s*```\s*",
        text,
        re.IGNORECASE | re.DOTALL
    )

    return match.group(1) if match else text


def _as_string_list(value: Any) -> list[str]:

    if not isinstance(value, list):
        return []

    return [
        item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)
        for item in value
    ]


def _normalize_result(result: Any) -> dict[str, Any]:
    """Keep Gemini output predictable for the API and the frontend."""

    if not isinstance(result, dict):
        result = {}

    try:
        confidence = float(result.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0.0

    return {
        "ai_available": bool(result.get("ai_available", True)),
        "category": str(result.get("category") or "Unknown"),
        "root_cause": str(result.get("root_cause") or ""),
        "confidence": max(0.0, min(1.0, confidence)),
        "osi_layer": str(result.get("osi_layer") or ""),
        "evidence": _as_string_list(result.get("evidence")),
        "recommended_commands": _as_string_list(
            result.get("recommended_commands")
        ),
        "proposed_remediation": _as_string_list(
            result.get("proposed_remediation")
        ),
        "historical_case_analysis": _as_string_list(
            result.get("historical_case_analysis")
        ),
        "uncertainties": _as_string_list(result.get("uncertainties")),
        "human_review_required": True,
    }