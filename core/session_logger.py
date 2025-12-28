import json
import os
from datetime import datetime


class SessionLogger:

    def __init__(self, session_dir="sessions"):
        os.makedirs(session_dir, exist_ok=True)

        name = datetime.utcnow().strftime("%Y-%m-%d_%H-%M")
        self.path = os.path.join(session_dir, f"{name}.jsonl")

    def log_signal(self, interval, signal, risk_blocked):
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "interval": interval,
            "signal": {
                "action": signal.action,
                "confidence": signal.confidence,
                "reason": signal.reason
            },
            "result": None,
            "risk_blocked": risk_blocked
        }
        self._write(record)

    def log_result(self, result):
        with open(self.path, "rb+") as f:
            f.seek(0, os.SEEK_END)
            pos = f.tell()

            while pos > 0:
                pos -= 1
                f.seek(pos)
                if f.read(1) == b"\n":
                    break

            last = json.loads(f.readline())
            last["result"] = result

            f.seek(pos)
            f.truncate()
            f.write((json.dumps(last) + "\n").encode())

    def _write(self, record):
        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")
