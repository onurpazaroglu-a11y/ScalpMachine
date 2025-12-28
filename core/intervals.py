# INTERVALS - TEMEL (Sözlük gibi kullanım / MTF içine modül olarak import edilecek)

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Interval:
    code: str        # "15S", "1M", "5M"
    seconds: int     # 15, 60, 300
    label: str       # UI display
    group: str       # "SCALP", "INTRADAY", "SWING"


# -------------------------------------------------
# INTERVAL DEFINITIONS
# -------------------------------------------------

INTERVALS: Dict[str, Interval] = {
    # --- Seconds (Scalp) ---
    "5S":  Interval("5S", 5, "5 Seconds", "SCALP"),
    "15S": Interval("15S", 15, "15 Seconds", "SCALP"),
    "30S": Interval("30S", 30, "30 Seconds", "SCALP"),

    # --- Minutes (Intraday) ---
    "1M":  Interval("1M", 60, "1 Minute", "INTRADAY"),
    "2M":  Interval("2M", 120, "2 Minutes", "INTRADAY"),
    "3M":  Interval("3M", 180, "3 Minutes", "INTRADAY"),
    "5M":  Interval("5M", 300, "5 Minutes", "INTRADAY"),
    "15M": Interval("15M", 900, "15 Minutes", "INTRADAY"),

    # --- Higher (Context / Oracle) ---
    "30M": Interval("30M", 1800, "30 Minutes", "SWING"),
    "1H":  Interval("1H", 3600, "1 Hour", "SWING"),
}


# -------------------------------------------------
# PUBLIC API
# -------------------------------------------------

def is_valid_interval(code: str) -> bool:
    return code in INTERVALS


def get_interval(code: str) -> Interval:
    if code not in INTERVALS:
        raise ValueError(f"Unsupported interval: {code}")
    return INTERVALS[code]


def all_intervals() -> List[Interval]:
    return list(INTERVALS.values())


def intervals_by_group(group: str) -> List[Interval]:
    return [i for i in INTERVALS.values() if i.group == group]


def to_seconds(code: str) -> int:
    return get_interval(code).seconds


def higher_interval(code: str) -> List[Interval]:
    """
    Returns higher timeframe intervals (for oracle / confirmation logic).
    """
    base = get_interval(code).seconds
    return sorted(
        [i for i in INTERVALS.values() if i.seconds > base],
        key=lambda x: x.seconds
    )
