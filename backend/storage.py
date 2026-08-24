import json
from datetime import datetime, timezone
from pathlib import Path


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_history(history_dir, record):
    path = Path(history_dir) / f"{record['case_id']}.json"
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


def list_history(history_dir):
    records = []
    for path in sorted(Path(history_dir).glob("CASE-*.json"), reverse=True):
        try:
            records.append(_read(path))
        except (OSError, json.JSONDecodeError):
            continue
    return records


def get_history(history_dir, case_id):
    path = Path(history_dir) / f"{case_id}.json"
    return _read(path) if path.exists() else None


def update_review(history_dir, reviews_dir, case_id, review):
    record = get_history(history_dir, case_id)
    if not record:
        return None
    record["human_review"] = {**record.get("human_review", {}), **review, "updated_at": datetime.now(timezone.utc).isoformat()}
    save_history(history_dir, record)
    Path(reviews_dir).mkdir(parents=True, exist_ok=True)
    (Path(reviews_dir) / f"{case_id}.json").write_text(json.dumps(record["human_review"], indent=2), encoding="utf-8")
    return record
