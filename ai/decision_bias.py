# DECISION BIAS - Engine skorlar, doğru - yanlış sonucunu verir (db'e sonuç girme bölümü eklenecek)

import json
from pathlib import Path
from typing import Dict


class DecisionBias:
    """
    Tracks historical decision performance and produces
    bias scores for future decisions.

    Not AI. Not ML.
    Deterministic statistical memory.
    """

    def __init__(self):
        # key: condition hash / signature
        # value: {"win": int, "loss": int}
        self._stats: Dict[str, Dict[str, int]] = {}

    # -------------------------------------------------
    # UPDATE (AFTER TRADE RESULT)
    # -------------------------------------------------

    def record_result(
        self,
        condition_id: str,
        success: bool
    ) -> None:
        if condition_id not in self._stats:
            self._stats[condition_id] = {"win": 0, "loss": 0}

        if success:
            self._stats[condition_id]["win"] += 1
        else:
            self._stats[condition_id]["loss"] += 1

    # -------------------------------------------------
    # QUERY (BEFORE DECISION)
    # -------------------------------------------------

    def get_bias(self, condition_id: str) -> float:
        """
        Returns bias score in range [-1, +1]

        +1   → always successful
         0   → neutral / unknown
        -1   → always failing
        """

        stat = self._stats.get(condition_id)
        if not stat:
            return 0.0

        wins = stat["win"]
        losses = stat["loss"]
        total = wins + losses

        if total == 0:
            return 0.0

        return (wins - losses) / total

    # -------------------------------------------------
    # ENGINE INTEGRATION HELP
    # -------------------------------------------------

    def adjust_confidence(
        self,
        raw_confidence: float,
        condition_id: str,
        weight: float = 0.5
    ) -> float:
        """
        Adjusts confidence based on historical bias.

        weight: how much bias affects final confidence
        """

        bias = self.get_bias(condition_id)
        adjusted = raw_confidence + bias * weight

        return max(0.0, min(1.0, adjusted))

    # -------------------------------------------------
    # PERSISTENCE
    # -------------------------------------------------

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._stats, f, indent=2)

    def load(self, path: str | Path) -> None:
        path = Path(path)
        if not path.exists():
            return

        with open(path, "r", encoding="utf-8") as f:
            self._stats = json.load(f)
