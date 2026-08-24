import csv
import io
import json
import re
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from .config import FRONTEND_URL, HISTORY_DIR, KNOWLEDGE_FILE, PORT, REVIEWS_DIR, HOST
    from .classifier import investigator_fallback
    from .llm import run_llm
    from .prompts import build_prompt
    from .retriever import CaseRetriever
    from .storage import get_history, list_history, save_history, update_review
    from .validator import run_checks
except ImportError:
    from config import FRONTEND_URL, HISTORY_DIR, KNOWLEDGE_FILE, PORT, REVIEWS_DIR, HOST
    from classifier import investigator_fallback
    from llm import run_llm
    from prompts import build_prompt
    from retriever import CaseRetriever
    from storage import get_history, list_history, save_history, update_review
    from validator import run_checks

app = Flask(__name__)
CORS(app, origins=[FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"])
retriever = CaseRetriever(KNOWLEDGE_FILE)
GREETING_PATTERN = re.compile(r"^(hi|hello|hey|thanks|thank you|how are you|ok|okay)[!.? ]*$", re.I)
NETWORK_SIGNAL_PATTERN = re.compile(r"\b(cisco|packet tracer|router|switch|vlan|trunk|dhcp|dns|nat|acl|firewall|routing|route|gateway|subnet|mask|interface|ping|ip address|hostname|network|server|wireless|wifi|show\s+\w+)\b", re.I)
FAULT_SIGNAL_PATTERN = re.compile(r"\b(cannot|can't|unable|problem|issue|fail(?:s|ed|ure)?|down|unreachable|not working|slow|error|lost|missing|timeout|timed out|no ip|doesn't)\b", re.I)
GENERAL_QUESTION_PATTERN = re.compile(r"^(what|why|how|when|where|which|can you|could you|please explain|define)\b", re.I)


def normalize_input(payload):
    value = payload.get("input", "")
    input_type = payload.get("input_type", "text")
    if input_type == "csv":
        rows = list(csv.DictReader(io.StringIO(value)))
        if not rows:
            raise ValueError("Invalid CSV")
        return json.dumps(rows), input_type
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Input is required")
    return value.strip(), input_type


def is_greeting(value):
    return bool(GREETING_PATTERN.match(value.strip()))


def general_chat_reply(value):
    text = value.lower()
    if "what can you do" in text or "how can you help" in text:
        return "I can investigate Cisco and Packet Tracer network faults step by step, compare evidence with stored cases, and suggest the next validation command. I never execute fixes automatically."
    if "who are you" in text or "what are you" in text:
        return "I am NetSage AI, an evidence-driven network troubleshooting assistant. I help narrow possible faults and keep a human in control of every fix."
    if "thank" in text:
        return "You're welcome. Share another symptom or command output whenever you are ready."
    if "vlan" in text:
        return "A VLAN is a logical Layer 2 network that separates devices into broadcast domains. Routers or Layer 3 switches are needed for traffic between VLANs."
    if "dns" in text:
        return "DNS translates hostnames into IP addresses. A useful first check is whether the same destination works by IP but fails by hostname."
    if "dhcp" in text:
        return "DHCP automatically provides clients with network settings such as an IP address, subnet mask, gateway, and DNS server."
    if "subnet" in text or "ip address" in text:
        return "An IP address identifies a device, while the subnet mask determines which addresses are local. The default gateway handles traffic outside that local subnet."
    return "I can help with general networking questions as well as fault investigation. Ask your question directly, or share symptoms and command output when you want a diagnosis."


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "NetSage API", "llm": True})


@app.post("/api/diagnose")
def diagnose():
    try:
        user_input, input_type = normalize_input(request.get_json(silent=True) or {})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    checks = run_checks(user_input)
    matched = retriever.search(user_input)
    prompt = build_prompt(user_input, checks, matched)
    if is_greeting(user_input):
        raw = json.dumps({"mode": "chat", "message": "Hello. I am NetSage AI. Ask a general networking question or share a network symptom and I will help step by step."})
        diagnosis = {"mode": "chat", "message": json.loads(raw)["message"]}
        llm_available = True
    elif (not NETWORK_SIGNAL_PATTERN.search(user_input) or (GENERAL_QUESTION_PATTERN.search(user_input) and not FAULT_SIGNAL_PATTERN.search(user_input))):
        raw, diagnosis, llm_available = run_llm(prompt)
        if not llm_available:
            diagnosis = {"mode": "chat", "message": general_chat_reply(user_input)}
            raw = json.dumps(diagnosis)
    else:
        raw, diagnosis, llm_available = run_llm(prompt)
        if not llm_available:
            diagnosis = investigator_fallback(user_input, checks["checks"], matched)
            raw = json.dumps(diagnosis)
    case_id = datetime.now(timezone.utc).strftime("CASE-%Y%m%d%H%M%S%f")[:-3]
    record = {"case_id": case_id, "timestamp": datetime.now(timezone.utc).isoformat(), "input": user_input, "input_type": input_type, "deterministic_checks": checks["checks"], "matched_cases": matched, "matched_test_case_ids": [case.get("case_id") for case in matched], "prompt": prompt, "raw_llm_response": raw, "diagnosis": diagnosis, "message": diagnosis.get("message", ""), "mode": diagnosis.get("mode", "diagnose"), "possible_causes": diagnosis.get("possible_causes", []), "next_question": diagnosis.get("next_question"), "command_request": diagnosis.get("command_request"), "human_review": {"status": "pending", "correct": None, "reviewer_note": ""}}
    save_history(HISTORY_DIR, record)
    return jsonify({**record, "llm_available": llm_available})


@app.post("/api/continue/<case_id>")
def continue_case(case_id):
    record = get_history(HISTORY_DIR, case_id)
    payload = request.get_json(silent=True) or {}
    evidence = payload.get("evidence", "")
    if not record:
        return jsonify({"error": "Case not found"}), 404
    if not isinstance(evidence, str) or not evidence.strip():
        return jsonify({"error": "New evidence is required"}), 400
    combined_input = f"{record['input']}\n\nUser-validated follow-up evidence:\n{evidence.strip()}"
    checks = run_checks(combined_input)
    matched = retriever.search(combined_input)
    prompt = build_prompt(combined_input, checks, matched)
    raw, diagnosis, llm_available = run_llm(prompt)
    if not llm_available:
        diagnosis = investigator_fallback(combined_input, checks["checks"], matched)
        raw = json.dumps(diagnosis)
    record.update({"input": combined_input, "deterministic_checks": checks["checks"], "matched_cases": matched, "matched_test_case_ids": [case.get("case_id") for case in matched], "prompt": prompt, "raw_llm_response": raw, "diagnosis": diagnosis, "possible_causes": diagnosis.get("possible_causes", []), "next_question": diagnosis.get("next_question"), "command_request": diagnosis.get("command_request"), "llm_available": llm_available, "last_user_evidence": evidence.strip()})
    save_history(HISTORY_DIR, record)
    return jsonify(record)


@app.post("/api/verify/<case_id>")
def verify_case(case_id):
    record = get_history(HISTORY_DIR, case_id)
    payload = request.get_json(silent=True) or {}
    result = payload.get("result")
    if not record:
        return jsonify({"error": "Case not found"}), 404
    if result not in {"success", "failure", "partial"}:
        return jsonify({"error": "Verification result must be success, failure, or partial"}), 400
    detail = str(payload.get("detail", ""))
    record["verification"] = {"result": result, "detail": detail, "timestamp": datetime.now(timezone.utc).isoformat()}
    record["stage"] = "verified" if result == "success" else "diagnose"
    if result != "success":
        follow_up = f"The reviewed fix was applied but verification was {result}. New observation: {detail or 'Connectivity is not fully restored.'}"
        checks = run_checks(f"{record.get('input', '')}\n{follow_up}")
        matched = retriever.search(f"{record.get('input', '')}\n{follow_up}")
        prompt = build_prompt(f"{record.get('input', '')}\n{follow_up}", checks, matched)
        raw, diagnosis, llm_available = run_llm(prompt)
        if not llm_available:
            diagnosis = investigator_fallback(f"{record.get('input', '')}\n{follow_up}", checks["checks"], matched)
            raw = json.dumps(diagnosis)
            llm_available = False
        record.update({"deterministic_checks": checks["checks"], "matched_cases": matched, "prompt": prompt, "raw_llm_response": raw, "diagnosis": diagnosis, "message": diagnosis.get("message", ""), "possible_causes": diagnosis.get("possible_causes", []), "next_question": diagnosis.get("next_question"), "command_request": diagnosis.get("command_request"), "llm_available": llm_available})
    save_history(HISTORY_DIR, record)
    return jsonify(record)


@app.get("/api/history")
def history():
    return jsonify(list_history(HISTORY_DIR))


@app.get("/api/history/<case_id>")
def case(case_id):
    record = get_history(HISTORY_DIR, case_id)
    return jsonify(record) if record else (jsonify({"error": "Case not found"}), 404)


@app.get("/api/roadmap/<case_id>")
def roadmap(case_id):
    record = get_history(HISTORY_DIR, case_id)
    if not record:
        return jsonify({"error": "Case not found"}), 404
    return jsonify({"case_id": case_id, "diagnosis": record.get("diagnosis", {})})


@app.post("/api/step/<case_id>")
def step(case_id):
    record = get_history(HISTORY_DIR, case_id)
    payload = request.get_json(silent=True) or {}
    if not record:
        return jsonify({"error": "Case not found"}), 404
    step_id = payload.get("step_id")
    if step_id is None or payload.get("status") not in {"pending", "done", "failed"}:
        return jsonify({"error": "step_id and a valid status are required"}), 400
    roadmap_steps = record.setdefault("diagnosis", {}).setdefault("roadmap", [])
    found = False
    for item in roadmap_steps:
        if str(item.get("step_id", item.get("id"))) == str(step_id):
            item["status"] = payload["status"]
            found = True
            break
    if not found:
        return jsonify({"error": "Roadmap step not found"}), 404
    save_history(HISTORY_DIR, record)
    return jsonify(record)


@app.post("/api/review/<case_id>")
def review(case_id):
    payload = request.get_json(silent=True) or {}
    if payload.get("status") == "rejected" and not payload.get("reviewer_note", "").strip():
        return jsonify({"error": "A note is required when rejecting a diagnosis"}), 400
    record = update_review(HISTORY_DIR, REVIEWS_DIR, case_id, payload)
    return jsonify(record) if record else (jsonify({"error": "Case not found"}), 404)


@app.get("/api/cases")
def cases():
    return jsonify(retriever.load())


@app.post("/api/cases")
def create_case():
    payload = request.get_json(silent=True) or {}
    cases = retriever.load()
    case_id = payload.get("case_id")
    if not case_id:
        return jsonify({"error": "case_id is required"}), 400
    cases = [case for case in cases if case.get("case_id") != case_id]
    cases.append(payload)
    KNOWLEDGE_FILE.write_text(json.dumps(cases, indent=2), encoding="utf-8")
    return jsonify(payload), 201


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
