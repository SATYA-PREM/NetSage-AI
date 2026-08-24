import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
source = ROOT / "data" / "cases.csv"
target = ROOT / "data" / "knowledge" / "cases.json"
history_dir = ROOT / "data" / "history"
training_target = ROOT / "data" / "training.jsonl"

existing = {}
if target.exists() and target.read_text(encoding="utf-8").strip():
	existing = {case.get("case_id"): case for case in json.loads(target.read_text(encoding="utf-8"))}

if source.exists() and source.read_text(encoding="utf-8").strip():
	with source.open(newline="", encoding="utf-8") as handle:
		for case in csv.DictReader(handle):
			if case.get("case_id"):
				existing[case["case_id"]] = case

target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(list(existing.values()), indent=2), encoding="utf-8")
print(f"Wrote {len(existing)} cases to {target}")

# Export reviewed investigations for future evaluation or fine-tuning.
reviewed = []
for path in history_dir.glob("CASE-*.json"):
	try:
		record = json.loads(path.read_text(encoding="utf-8"))
	except (OSError, json.JSONDecodeError):
		continue
	if record.get("human_review", {}).get("status") in {"accepted", "edited", "rejected"}:
		reviewed.append({"messages": [{"role": "system", "content": "You are NetSage, a Cisco networking troubleshooting assistant."}, {"role": "user", "content": record.get("input", "")}, {"role": "assistant", "content": json.dumps(record.get("diagnosis", {}))}]})

training_target.write_text("\n".join(json.dumps(item) for item in reviewed) + ("\n" if reviewed else ""), encoding="utf-8")
print(f"Exported {len(reviewed)} reviewed cases to {training_target}")
