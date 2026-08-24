import json

SYSTEM_PROMPT = """You are NetSage AI, a Cisco and Packet Tracer troubleshooting investigator.
For greetings or casual messages, respond in mode=chat with a short reply and do not fabricate a diagnosis.
For network problems, analyze only supplied evidence. Never invent facts. Separate CONFIRMED, LIKELY, POSSIBLE, and UNKNOWN.
Do not force a diagnosis: when evidence is insufficient, ask exactly one purposeful question or request exactly one command.
Rank possible fault domains with probabilities. Every question must explain why it reduces uncertainty.
A human must approve every fix. Never execute commands. Return ONLY valid JSON."""


def build_prompt(user_input, checks, matched_cases):
    schema = {
        "classification": "",
        "status": "UNKNOWN",
        "likely_root_cause": "",
        "alternative_causes": [],
        "osi_layer": "",
        "concept": "",
        "severity": "",
        "evidence": [],
        "next_commands": [],
        "recommended_fix": "",
        "confidence": 0.0,
        "human_review_required": True,
        "roadmap": [],
        "final_summary": None,
        "mode": "diagnose",
        "message": "",
        "possible_causes": [],
        "next_question": None,
        "command_request": None,
        "matched_test_case_ids": [],
    }
    return f"{SYSTEM_PROMPT}\n\nTreat the following as the current request and primary evidence:\n--- CURRENT REQUEST ---\n{user_input}\n--- END CURRENT REQUEST ---\n\nUse these deterministic checks as machine-generated evidence:\n{json.dumps(checks)}\n\nUse these stored, verified RAG cases only as supporting context. Do not copy a case conclusion unless the current request supports it:\n{json.dumps(matched_cases)}\n\nRequired schema:\n{json.dumps(schema)}"
