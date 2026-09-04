import json
import re
import subprocess
import threading
import pathlib

import requests

MODEL      = "llama3.2:3b"
OLLAMA_URL = "http://localhost:11434/api/chat"
EXEC_RE    = re.compile(r'EXEC:\s*([^\n]+)')

SYSTEM_PROMPT = (
    "You are CYBERVOID, an expert AI assistant for cybersecurity research and "
    "penetration testing. You have deep knowledge of offensive and defensive "
    "security, CTF challenges, network protocols, vulnerability assessment, "
    "and security tools (nmap, metasploit, burpsuite, sqlmap, etc.). "
    "When you recommend running a terminal command, prefix it with EXEC: on "
    "its own line (e.g. EXEC: nmap -sV 192.168.1.1). "
    "Keep responses concise and technical. You are running inside the "
    "CYBERVOID security research platform."
)

MAX_HISTORY = 6  # rolling window per side (user + assistant)


class AIChatEngine:
    """Non-blocking Ollama streaming chat client.

    Callbacks (on_token, on_done, on_exec) are called from a background thread
    and MUST only call queue.Queue.put() — never touch the Ursina scene graph.
    """

    def __init__(self, on_token, on_done, on_exec):
        self._on_token = on_token
        self._on_done  = on_done
        self._on_exec  = on_exec
        self._history  = []
        self._stop     = threading.Event()
        self._thread   = None

    def send(self, message: str):
        self._stop.clear()
        self._history.append({"role": "user", "content": message})
        # Trim rolling window
        if len(self._history) > MAX_HISTORY * 2:
            self._history = self._history[-(MAX_HISTORY * 2):]
        self._thread = threading.Thread(target=self._stream, daemon=True)
        self._thread.start()

    def _stream(self):
        messages   = [{"role": "system", "content": SYSTEM_PROMPT}] + self._history
        full_text  = ""
        exec_seen  = set()
        try:
            resp = requests.post(
                OLLAMA_URL,
                json={"model": MODEL, "messages": messages, "stream": True},
                stream=True,
                timeout=(15, 180),
            )
            resp.raise_for_status()
            for line in resp.iter_lines():
                if self._stop.is_set():
                    break
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                token = data.get("message", {}).get("content", "")
                if token:
                    full_text += token
                    self._on_token(token)
                    # Detect EXEC: commands as they accumulate
                    for m in EXEC_RE.finditer(full_text):
                        key = m.start()
                        if key not in exec_seen:
                            exec_seen.add(key)
                            self._on_exec(m.group(1).strip())
                if data.get("done", False):
                    break
        except Exception as exc:
            self._on_token(f"\n[ERROR: {exc}]")
        finally:
            if not self._stop.is_set():
                if full_text.strip():
                    self._history.append({"role": "assistant", "content": full_text})
                self._on_done(full_text)

    def stop(self):
        self._stop.set()

    def clear_history(self):
        self._history.clear()


def run_exec_engine(cmd: str, timeout: int = 30) -> dict:
    """Run a shell command via exec_engine binary.  Call from a thread only."""
    engine = pathlib.Path(__file__).parent / "exec_engine"
    if not engine.exists():
        return {"exit_code": -1, "stdout": "",
                "stderr": "exec_engine binary not found — run 'make'",
                "timed_out": False}
    try:
        result = subprocess.run(
            [str(engine), cmd, str(timeout)],
            capture_output=True, text=True,
            timeout=timeout + 5,
        )
        return json.loads(result.stdout)
    except Exception as exc:
        return {"exit_code": -1, "stdout": "", "stderr": str(exc),
                "timed_out": False}
