import json

REQUIRED_FIELDS = ("classification", "status", "likely_root_cause", "alternative_causes", "osi_layer", "concept", "severity", "evidence", "next_commands", "recommended_fix", "confidence", "human_review_required")


def fallback():
    return {"classification": "UNKNOWN", "status": "UNKNOWN", "likely_root_cause": "Unable to determine", "alternative_causes": [], "osi_layer": "Unknown", "concept": "Unknown", "severity": "Unknown", "evidence": [], "next_commands": ["Collect additional show-command evidence."], "recommended_fix": "Collect additional show-command evidence.", "confidence": 0.0, "human_review_required": True, "roadmap": [], "final_summary": None}


def investigator_fallback(user_input, checks=None, matched_cases=None):
    """Return a useful progressive turn when no model response is available."""
    checks = checks or []
    matched_cases = matched_cases or []
    failed = [item for item in checks if item.get("status") == "FAIL"]
    text = user_input.lower()
    if failed:
        primary = failed[0]
        possible = [{"name": "IP addressing / Gateway", "probability": 82}, {"name": "Routing", "probability": 48}, {"name": "ACL", "probability": 28}]
        question = {"question": "Can the device ping its default gateway?", "reason": "This separates local addressing and VLAN faults from downstream routing or ACL faults.", "options": ["Ping succeeds", "Ping fails", "I have not tested it"], "multi_select": False}
        message = f"I found one deterministic signal: {primary.get('evidence', 'a network validation failure')}. I have not confirmed the root cause yet. I need one observation to narrow the fault."
        command = None
    elif "hostname" in text or "dns" in text:
        possible = [{"name": "DNS", "probability": 62}, {"name": "Routing", "probability": 36}, {"name": "ACL", "probability": 24}]
        question = {"question": "Does the problem affect IP addresses, hostnames, or both?", "reason": "This separates name-resolution failure from network reachability failure.", "options": ["IP only", "Hostname only", "Both", "Not tested"], "multi_select": False}
        message = "I see a possible name-resolution issue, but the fault is not confirmed. One observation will help separate DNS from reachability."
        command = None
    else:
        possible = [{"name": "Routing", "probability": 58}, {"name": "ACL", "probability": 44}, {"name": "VLAN / Trunk", "probability": 35}, {"name": "Gateway", "probability": 27}, {"name": "DNS", "probability": 16}]
        question = {"question": "What can the device currently reach?", "reason": "This separates local Layer 2/addressing faults from downstream routing, ACL, and DNS faults.", "options": ["Gateway works", "Gateway fails", "Server IP fails", "Server hostname fails", "Internet also fails", "Not tested"], "multi_select": True}
        message = f"I found {len(matched_cases)} related test case(s), but I cannot confirm a root cause from the current evidence. I need one observation to narrow the possibilities."
        command = None
    return {"mode": "diagnose", "message": message, "possible_causes": possible, "next_question": question, "command_request": command, "matched_test_case_ids": [item.get("case_id") for item in matched_cases], **fallback(), "status": "UNKNOWN", "confidence": 0.0}


def parse_response(raw):
    try:
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end <= start:
            return fallback()
        value = json.loads(raw[start:end + 1])
        if not isinstance(value, dict):
            return fallback()
        if value.get("mode") == "chat":
            value.setdefault("message", "")
            return {**fallback(), **value, "human_review_required": True}
        model_diagnosis = value.get("diagnosis") or {}
        if model_diagnosis:
            value.setdefault("classification", (value.get("possible_causes") or [{"name": "UNKNOWN"}])[0].get("name", "UNKNOWN"))
            value.setdefault("status", "CONFIRMED" if float(model_diagnosis.get("confidence", 0)) >= 0.85 else "LIKELY")
            value.setdefault("likely_root_cause", model_diagnosis.get("root_cause", "Unable to determine"))
            value.setdefault("alternative_causes", [cause.get("name", "") for cause in value.get("possible_causes", [])[1:] if isinstance(cause, dict)])
            value.setdefault("osi_layer", model_diagnosis.get("osi_layer", "Unknown"))
            value.setdefault("concept", value.get("classification", "Unknown"))
            value.setdefault("severity", "Unknown")
            value.setdefault("evidence", model_diagnosis.get("evidence", []))
            value.setdefault("next_commands", [value["command_request"]["command"]] if value.get("command_request", {}).get("command") else [])
            value.setdefault("recommended_fix", "\n".join(model_diagnosis.get("recommended_fix", [])) if isinstance(model_diagnosis.get("recommended_fix"), list) else model_diagnosis.get("recommended_fix", "Collect additional evidence."))
            value.setdefault("confidence", model_diagnosis.get("confidence", 0.0))
            value.setdefault("human_review_required", True)
        if any(field not in value for field in REQUIRED_FIELDS):
            return fallback()
        value["confidence"] = max(0.0, min(1.0, float(value["confidence"])))
        value["human_review_required"] = True
        value.setdefault("roadmap", [])
        value.setdefault("final_summary", None)
        value.setdefault("mode", "diagnose")
        value.setdefault("message", "")
        value.setdefault("possible_causes", [])
        value.setdefault("next_question", None)
        value.setdefault("command_request", None)
        value.setdefault("matched_test_case_ids", [])
        return value
    except (ValueError, TypeError, json.JSONDecodeError):
        return fallback()
