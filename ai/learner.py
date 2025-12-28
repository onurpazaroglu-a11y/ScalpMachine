# LEARNER MODUL - AI train için gerekli bilgileri hazırlar (db implemenatasyonu henüz yok)

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List


class Learner:
    """
    Converts decisions and outcomes into learnable knowledge.
    Rule-based now, ML-ready later.
    """

    def __init__(self):
        # key: pattern_id
        # value: stats + samples
        self._memory: Dict[str, Dict[str, Any]] = {}

    # -------------------------------------------------
    # PATTERN IDENTIFICATION
    # -------------------------------------------------

    def build_pattern_id(self, features: Dict[str, Any]) -> str:
        """
        Create a stable hash for a given feature snapshot.
        """
        payload = json.dumps(features, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    # -------------------------------------------------
    # RECORD LEARNING EVENT
    # -------------------------------------------------

    def record(
        self,
        features: Dict[str, Any],
        action: str,
        result: str,
        reward: float
    ) -> None:
        """
        action: BUY / SELL / SKIP
        result: WIN / LOSS / BREAKEVEN
        reward: normalized outcome (-1.0 .. +1.0)
        """

        pattern_id = self.build_pattern_id(features)

        if pattern_id not in self._memory:
            self._memory[pattern_id] = {
                "count": 0,
                "win": 0,
                "loss": 0,
                "total_reward": 0.0,
                "samples": []
            }

        entry = self._memory[pattern_id]
        entry["count"] += 1
        entry["total_reward"] += reward

        if result == "WIN":
            entry["win"] += 1
        elif result == "LOSS":
            entry["loss"] += 1

        entry["samples"].append({
            "action": action,
            "result": result,
            "reward": reward
        })

    # -------------------------------------------------
    # QUERY (ENGINE / AI READY)
    # -------------------------------------------------

    def get_pattern_score(self, pattern_id: str) -> float:
        """
        Returns confidence score in range [-1, +1]
        """
        entry = self._memory.get(pattern_id)
        if not entry or entry["count"] == 0:
            return 0.0

        avg_reward = entry["total_reward"] / entry["count"]
        return max(-1.0, min(1.0, avg_reward))

    def is_reliable(self, pattern_id: str, min_samples: int=10) -> bool:
        entry = self._memory.get(pattern_id)
        return bool(entry and entry["count"] >= min_samples)

    # -------------------------------------------------
    # EXPORT (FOR AI MODULE)
    # -------------------------------------------------

    def export_dataset(self) -> List[Dict[str, Any]]:
        dataset = []
        for pid, entry in self._memory.items():
            dataset.append({
                "pattern_id": pid,
                "count": entry["count"],
                "win": entry["win"],
                "loss": entry["loss"],
                "avg_reward": (
                    entry["total_reward"] / entry["count"]
                    if entry["count"] > 0 else 0.0
                )
            })
        return dataset

    # -------------------------------------------------
    # PERSISTENCE
    # -------------------------------------------------

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._memory, f, indent=2)

    def load(self, path: str | Path) -> None:
        path = Path(path)
        if not path.exists():
            return

        with open(path, "r", encoding="utf-8") as f:
            self._memory = json.load(f)



#   Öğrenme Zinciri:
#   Feature snapshot
#   +Action (BUY / SELL)
#   +Result (WIN / LOSS)
#       ↓
#   learner.py
#       ↓
#   pattern memory

#   Bu şunları sağlar:
#   “Bu yapı genelde işe yarıyor mu?”
#   “Kaç kere denendi?”
#   “Ödül ortalaması ne?”

#   ENGINE ENTEGRASYONU (ÖRNEK)
#   pattern_id = learner.build_pattern_id(feature_snapshot)

#   if learner.is_reliable(pattern_id):
#       score = learner.get_pattern_score(pattern_id)
#       confidence *= (1 + score * 0.3)
