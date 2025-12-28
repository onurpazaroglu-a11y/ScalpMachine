# UTILS - yardımcı yığınlar

from datetime import datetime
from typing import Any, Dict
import json
import os


# =================================================
# TIME
# =================================================

def utc_now() -> datetime:
    """Returns current UTC datetime."""
    return datetime.utcnow()


def iso_now() -> str:
    """Returns current UTC time as ISO string."""
    return utc_now().isoformat()


def parse_iso(ts: str) -> datetime:
    """Parses ISO datetime string."""
    return datetime.fromisoformat(ts)


# =================================================
# SAFE DICT ACCESS
# =================================================

def get_nested(d: Dict[str, Any], path: str, default=None):
    """
    Safely get nested dict value.
    path example: 'signal.confidence'
    """
    keys = path.split(".")
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


# =================================================
# NUMERIC HELPERS
# =================================================

def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp value between min and max."""
    return max(min_value, min(value, max_value))


def pct(value: float, total: float) -> float:
    """Safe percentage calculation."""
    if total == 0:
        return 0.0
    return value / total


# =================================================
# FILE / JSON HELPERS
# =================================================

def ensure_dir(path: str):
    """Create directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


def read_json(path: str) -> Dict[str, Any]:
    """Read JSON file safely."""
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def write_json(path: str, data: Dict[str, Any], indent: int = 2):
    """Write JSON file."""
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w") as f:
        json.dump(data, f, indent=indent)


def append_jsonl(path: str, record: Dict[str, Any]):
    """Append record to JSONL file."""
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")


def read_jsonl(path: str):
    """Generator for JSONL records."""
    if not os.path.exists(path):
        return
    with open(path, "r") as f:
        for line in f:
            yield json.loads(line)


# =================================================
# DEBUG / FORMAT
# =================================================

def short_ts(ts: str) -> str:
    """ISO timestamp -> HH:MM:SS"""
    try:
        dt = parse_iso(ts)
        return dt.strftime("%H:%M:%S")
    except Exception:
        return ts


def pretty(obj: Any) -> str:
    """Pretty JSON string for debug panels."""
    try:
        return json.dumps(obj, indent=2)
    except Exception:
        return str(obj)
