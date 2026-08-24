import json
import os
import shutil
import subprocess
from pathlib import Path
import urllib.error
import urllib.request

try:
    from .config import LLAMA_CLI_FALLBACK, LLAMA_SERVER_MODEL, LLAMA_SERVER_URL, OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_URL, ROOT_DIR
    from .classifier import fallback, parse_response
except ImportError:
    from config import LLAMA_CLI_FALLBACK, LLAMA_SERVER_MODEL, LLAMA_SERVER_URL, OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_URL, ROOT_DIR
    from classifier import fallback, parse_response


def run_server(prompt):
    payload = json.dumps({
        "model": LLAMA_SERVER_MODEL,
        "messages": [{"role": "system", "content": "You are NetSage. Return only valid JSON."}, {"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 900,
        "stream": False,
    }).encode("utf-8")
    request = urllib.request.Request(LLAMA_SERVER_URL, data=payload, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"]
        raw = content if isinstance(content, str) else json.dumps(content)
        return raw, parse_response(raw), True
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError):
        return None


def run_local(prompt):
    executable = os.getenv("LLAMA_CLI_PATH", "llama-cli.exe")
    model = os.getenv("MODEL_PATH", str(ROOT_DIR / "models" / "base" / "Qwen3-4B-Q4_K_M.gguf"))
    if not os.path.isabs(model):
        model = str(ROOT_DIR / model)
    executable_available = Path(executable).exists() or shutil.which(executable)
    if not executable_available or not Path(model).is_file():
        return None
    try:
        result = subprocess.run([executable, "-m", model, "-p", prompt, "--temp", "0.1", "-n", "512"], capture_output=True, text=True, timeout=120, check=False)
        raw = result.stdout or result.stderr
        if result.returncode == 0 and raw:
            parsed = parse_response(raw)
            if parsed["status"] != "UNKNOWN" or parsed["likely_root_cause"] != "Unable to determine":
                return raw, parsed, True
    except (OSError, subprocess.TimeoutExpired):
        pass


def run_free_api(prompt):
    if not OPENROUTER_API_KEY:
        return None
    payload = json.dumps({"model": OPENROUTER_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1, "max_tokens": 700}).encode("utf-8")
    request = urllib.request.Request(OPENROUTER_URL, data=payload, method="POST", headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json", "HTTP-Referer": "http://localhost:5173", "X-Title": "NetSage AI"})
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            body = json.loads(response.read().decode("utf-8"))
        raw = body["choices"][0]["message"]["content"]
        return raw, parse_response(raw), True
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError):
        return None


def run_llm(prompt):
    server_result = run_server(prompt)
    if server_result:
        return server_result
    if LLAMA_CLI_FALLBACK:
        local_result = run_local(prompt)
        if local_result:
            return local_result
    api_result = run_free_api(prompt)
    if api_result:
        return api_result
    return json.dumps(fallback()), fallback(), False
