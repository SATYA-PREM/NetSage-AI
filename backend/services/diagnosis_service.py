from __future__ import annotations

import asyncio
import json
import logging
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.rules.checker import run_all_checks
from backend.services.ai_service import generate_diagnosis


logger = logging.getLogger(__name__)


ROOT_DIR = Path(__file__).resolve().parents[2]
CASES_FILE = ROOT_DIR / "data" / "cases.csv"
DIAGNOSES_FILE = ROOT_DIR / "data" / "diagnoses.json"
GENERIC_SIMILARITY_TOKENS = {
    "a",
    "address",
    "addresses",
    "cannot",
    "failure",
    "failing",
    "host",
    "hosts",
    "ip",
    "is",
    "network",
    "of",
    "on",
    "system",
    "the",
    "to",
}


# ---------------------------------------------------------
# Historical cases
# ---------------------------------------------------------

def load_cases() -> list[dict[str, Any]]:
    import csv

    if not CASES_FILE.exists():
        return []

    cases = []

    with open(
        CASES_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.reader(file)
        headers: list[str] = []

        for row in reader:
            if not row:
                continue

            if "case_id" in row and "title" in row:
                headers = [value.strip() for value in row]
                continue

            if not headers:
                continue

            values = row[:len(headers)]
            values.extend([""] * (len(headers) - len(values)))

            cases.append({
                key: value.strip()
                for key, value in zip(headers, values)
            })

    return cases


# ---------------------------------------------------------
# Text similarity
# ---------------------------------------------------------

def tokenize(text: str) -> set[str]:
    if not text:
        return set()

    text = re.sub(
        r"\bdomain[- ]name[- ]system\b",
        "dns",
        text.lower()
    )

    return set(
        token
        for token in re.findall(
            r"[a-zA-Z0-9_.:/-]+",
            text
        )
        if token not in GENERIC_SIMILARITY_TOKENS
    )


def similarity_score(
    current_text: str,
    historical_text: str
) -> float:

    current = tokenize(current_text)
    historical = tokenize(historical_text)

    if not current or not historical:
        return 0.0

    intersection = current.intersection(historical)
    union = current.union(historical)

    if not union:
        return 0.0

    return round(
        len(intersection) / len(union),
        3
    )


def historical_case_category(case: dict[str, Any]) -> str:
    category = case.get("category") or case.get("concept")
    if category:
        return str(category)

    text = " ".join([
        str(case.get("title", "")),
        str(case.get("issue", "")),
        str(case.get("description", "")),
    ]).lower()

    for keyword, category in [
        ("dns", "DNS"),
        ("vlan", "VLAN"),
        ("route", "Routing"),
        ("interface", "Interface"),
        ("arp", "ARP"),
        ("dhcp", "DHCP"),
        ("nat", "NAT"),
        ("acl", "Security"),
    ]:
        if keyword in text:
            return category

    return "Unknown"


def find_similar_cases(
    symptom: str,
    topology: str,
    command_output: str,
    limit: int = 5
) -> list[dict[str, Any]]:

    cases = load_cases()

    current_text = " ".join([
        symptom,
        topology,
        command_output
    ])

    matches = []

    for case in cases:

        historical_text = " ".join([
            str(case.get("title", "")),
            str(case.get("issue", "")),
            str(case.get("description", "")),
            str(case.get("expected_fault", "")),
            str(case.get("expected_category", "")),
            str(case.get("expected_root_cause", "")),
        ])

        score = similarity_score(
            current_text,
            historical_text
        )

        if score > 0:
            matches.append({
                **case,
                "similarity": score
            })

    matches.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return matches[:limit]


# ---------------------------------------------------------
# Deterministic evidence extraction
# ---------------------------------------------------------

def extract_vlan(command_output: str, topology: str) -> str | None:

    text = f"{topology}\n{command_output}"

    patterns = [
        r"vlan\s+(\d+)",
        r"vlan(\d+)",
        r"192\.168\.(\d+)\.\d+"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return None


def extract_allowed_vlans(
    command_output: str
) -> list[str]:

    match = re.search(
        r"vlans?\s+allowed\s+on\s+trunk.*?"
        r"(?:\n|\r\n)"
        r".*?\b([0-9,\-]+)\b",
        command_output,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        # fallback for simpler Cisco output
        match = re.search(
            r"Gi\d+/\d+\s+([0-9,]+)",
            command_output,
            re.IGNORECASE
        )

    if not match:
        return []

    value = match.group(1)

    return [
        vlan.strip()
        for vlan in value.split(",")
        if vlan.strip()
    ]


def deterministic_vlan_check(
    symptom: str,
    topology: str,
    command_output: str
) -> dict[str, Any]:

    vlan = extract_vlan(
        command_output,
        topology
    )

    allowed = extract_allowed_vlans(
        command_output
    )

    evidence = []

    if vlan:
        evidence.append(
            f"VLAN {vlan} is referenced by the incident."
        )

    if allowed:
        evidence.append(
            f"Trunk allowed VLANs: {', '.join(allowed)}."
        )

    if vlan and allowed and vlan not in allowed:

        return {
            "matched": True,
            "category": "VLAN",
            "root_cause": (
                f"VLAN {vlan} is not allowed on "
                "the trunk interface."
            ),
            "confidence": 0.92,
            "osi_layer": "Layer 2 — Data Link",
            "evidence": evidence + [
                f"VLAN {vlan} is absent from the "
                "allowed VLAN list."
            ],
            "recommended_commands": [
                "show interfaces Gi0/1 switchport",
                "show interfaces trunk",
                "show vlan brief"
            ],
            "proposed_remediation": [
                f"Verify that VLAN {vlan} should "
                "traverse the trunk.",
                f"If confirmed, add VLAN {vlan} "
                "to the trunk allowed VLAN list."
            ]
        }

    return {
        "matched": False,
        "category": "Unknown",
        "root_cause": None,
        "confidence": 0.0,
        "osi_layer": None,
        "evidence": evidence,
        "recommended_commands": [],
        "proposed_remediation": []
    }


# ---------------------------------------------------------
# Main diagnosis pipeline
# ---------------------------------------------------------

async def diagnose_network_issue(
    case_id: str,
    symptom: str,
    topology: str,
    command_output: str,
    device: str = "",
    device_type: str = "",
    severity: str = "Medium"
) -> dict[str, Any]:

    diagnosis_id = f"DGN-{uuid.uuid4().hex[:8].upper()}"
    logger.info(
        "Diagnosis started: id=%s case_id=%s device=%s severity=%s",
        diagnosis_id,
        case_id,
        device or "unspecified",
        severity
    )

    # 1. Historical comparison
    similar_cases = find_similar_cases(
        symptom=symptom,
        topology=topology,
        command_output=command_output
    )
    logger.info(
        "Historical matching complete: id=%s matches=%d",
        diagnosis_id,
        len(similar_cases)
    )

    # 2. Deterministic rules
    rule_result = deterministic_vlan_check(
        symptom=symptom,
        topology=topology,
        command_output=command_output
    )

    # 3. Run complete rule engine
    try:
        rule_findings = run_all_checks(
            symptom=symptom,
            context=topology,
            command_output=command_output
        )
    except Exception:
        logger.exception("Rule engine failed: id=%s", diagnosis_id)
        rule_findings = []

    logger.info(
        "Deterministic checks complete: id=%s focused_match=%s findings=%d",
        diagnosis_id,
        bool(rule_result.get("matched")),
        len(rule_findings)
    )

    # 4. Build evidence package
    evidence_package = {
        "incident": {
            "case_id": case_id,
            "symptom": symptom,
            "topology": topology,
            "command_output": command_output,
            "device": device,
            "device_type": device_type,
            "severity": severity
        },

        "deterministic_analysis": rule_result,

        "rule_engine_findings": rule_findings,

        "similar_historical_cases": similar_cases,

        "matched_test_cases": similar_cases
    }

    # 5. Ask Gemini to synthesize the report
    try:

        logger.info("Sending evidence package to Gemini: id=%s", diagnosis_id)
        ai_result = await asyncio.wait_for(
            generate_diagnosis(evidence_package),
            timeout=45
        )

    except Exception as exc:

        logger.warning(
            "Gemini unavailable; using deterministic fallback: id=%s error=%s",
            diagnosis_id,
            str(exc)
        )
        fallback_finding = (
            rule_findings[0]
            if rule_findings
            else (
                similar_cases[0]
                if similar_cases
                else {}
            )
        )
        fallback_category = (
            historical_case_category(fallback_finding)
            if similar_cases and not rule_findings
            else fallback_finding.get("category", "Unknown")
        )
        fallback_uncertainties = [
            f"AI diagnosis was unavailable: {str(exc)}"
        ]
        if similar_cases and not rule_findings:
            fallback_uncertainties.append(
                "Fallback diagnosis is based on the most similar historical case."
            )
        ai_result = {
            "ai_available": False,
            "error": str(exc),
            "category": fallback_category,
            "root_cause": fallback_finding.get(
                "finding",
                fallback_finding.get(
                    "expected_fault",
                    fallback_finding.get(
                        "description",
                        "No root cause established"
                    )
                )
            ),
            "confidence": 0.0,
            "osi_layer": "",
            "evidence": [
                fallback_finding.get("evidence", "")
            ] if fallback_finding.get("evidence") else [],
            "recommended_commands": [],
            "proposed_remediation": fallback_finding.get(
                "recommendation", []
            ),
            "historical_case_analysis": [
                (
                    f"Matched historical case {similar_cases[0].get('case_id')}: "
                    f"{similar_cases[0].get('title', 'No title')}."
                )
            ] if similar_cases and not rule_findings else [],
            "uncertainties": fallback_uncertainties,
            "human_review_required": True
        }

    # 6. A confirmed deterministic result overrides AI; otherwise AI mediates
    # the rule findings and historical references into the user-facing result.
    deterministic_match = bool(rule_result.get("matched"))
    root_cause = (
        rule_result.get("root_cause")
        if deterministic_match
        else ai_result.get("root_cause")
    ) or "No root cause established"

    confidence = max(
        float(rule_result.get("confidence", 0)),
        float(ai_result.get("confidence", 0))
    )

    category = (
        rule_result.get("category")
        if deterministic_match
        else ai_result.get("category")
    ) or "Unknown"

    osi_layer = (
        rule_result.get("osi_layer")
        if deterministic_match
        else ai_result.get("osi_layer")
    ) or None

    deterministic_evidence = [
        *rule_result.get("evidence", []),
        *[
            finding.get("evidence", "")
            for finding in rule_findings
            if finding.get("evidence")
        ]
    ]
    evidence = list(dict.fromkeys(
        deterministic_evidence + ai_result.get("evidence", [])
    ))

    recommended_commands = list(dict.fromkeys(
        rule_result.get("recommended_commands", [])
        + ai_result.get("recommended_commands", [])
        + [
            command
            for finding in rule_findings
            for command in finding.get("recommendation", [])
            if isinstance(command, str)
        ]
    ))

    proposed_remediation = list(dict.fromkeys(
        rule_result.get("proposed_remediation", [])
        + ai_result.get("proposed_remediation", [])
    ))

    # 7. Final frontend-safe response
    result = {
        "diagnosis_id": diagnosis_id,
        "case_id": case_id,

        "status": "RESULT_READY",

        "processing_status": (
            "AI_COMPLETE"
            if ai_result.get("ai_available", False)
            else "RULES_ONLY"
        ),

        "category": category,

        "root_cause": root_cause,

        "diagnosis": root_cause,

        "confidence": round(confidence, 2),

        "confidence_percent": round(
            confidence * 100
        ),

        "osi_layer": osi_layer,

        "evidence": evidence,

        "more_evidence_required": (
            confidence < 0.75
        ),

        "recommended_commands":
            recommended_commands,

        "proposed_remediation":
            proposed_remediation,

        "similar_cases": similar_cases,

        "deterministic_findings": rule_findings,

        "historical_case_analysis": ai_result.get(
            "historical_case_analysis", []
        ),

        "uncertainties": ai_result.get("uncertainties", []),

        "ai_analysis": ai_result,

        "gemini_input": evidence_package,

        "human_review_required": True,

        "created_at":
            datetime.utcnow().isoformat(),

        "responsible_ai": {
            "rules_run_before_ai": True,
            "historical_cases_used": True,
            "ai_mediated_case_and_rules": True,
            "human_review_required": True,
            "automatic_configuration_change": False
        }
    }

    save_diagnosis(result)

    logger.info(
        "Diagnosis complete: id=%s processing=%s category=%s confidence=%.2f",
        diagnosis_id,
        result["processing_status"],
        result["category"],
        result["confidence"]
    )

    return result


# ---------------------------------------------------------
# Save diagnosis
# ---------------------------------------------------------

def save_diagnosis(result: dict[str, Any]) -> None:

    existing = []

    if DIAGNOSES_FILE.exists():

        try:

            with open(
                DIAGNOSES_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                existing = json.load(file)

                if not isinstance(existing, list):
                    existing = []

        except Exception:
            existing = []

    existing.append(result)

    with open(
        DIAGNOSES_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            existing,
            file,
            indent=2,
            ensure_ascii=False
        )