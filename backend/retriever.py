import json
import re
from pathlib import Path

try:
    from .test_cases import CASES
except ImportError:
    from test_cases import CASES


def _tokens(value):
    return set(re.findall(r"[a-z0-9]+", str(value).lower()))


class CaseRetriever:
    def __init__(self, knowledge_file):
        self.knowledge_file = Path(knowledge_file)

    def load(self):
        built_in = CASES
        if not self.knowledge_file.exists():
            return built_in
        try:
            data = json.loads(self.knowledge_file.read_text(encoding="utf-8"))
            stored = data if isinstance(data, list) else []
            by_id = {case.get("case_id"): case for case in built_in}
            by_id.update({case.get("case_id"): case for case in stored if case.get("case_id")})
            return list(by_id.values())
        except (json.JSONDecodeError, OSError):
            return built_in

    def search(self, query, limit=3):
        query_tokens = _tokens(query)
        scored = []
        for case in self.load():
            haystack = " ".join(str(case.get(key, "")) for key in case)
            tokens = _tokens(haystack)
            score = len(query_tokens & tokens) / max(len(query_tokens), 1)
            if score > 0:
                scored.append((score, case))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [{**case, "similarity_score": round(score, 2), "similarity": round(score, 2)} for score, case in scored[:limit]]
