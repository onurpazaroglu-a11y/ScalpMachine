#AI MANAGER taslak

import json
import os
from typing import Dict, Any
from datetime import datetime

from core.signal_logic import Signal


class AIManager:
    """
    Passive learning and biasing module.
    Never generates signals. Never blocks trades.
    """

    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.active = False

        os.makedirs(self.model_dir, exist_ok=True)

        self.meta_path = os.path.join(self.model_dir, "meta.json")
        self.memory_path = os.path.join(self.model_dir, "experience.jsonl")

        self._load_or_init()

    # ------------------------------------------------
    # Lifecycle
    # ------------------------------------------------

    def _load_or_init(self):
        if not os.path.exists(self.meta_path):
            self._init_meta()
        else:
            self._load_meta()

    def _init_meta(self):
        self.meta = {
            "active": False,
            "created_at": datetime.utcnow().isoformat(),
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "last_updated": None
        }
        self._save_meta()

    def _load_meta(self):
        with open(self.meta_path, "r") as f:
            self.meta = json.load(f)
        self.active = self.meta.get("active", False)

    def _save_meta(self):
        self.meta["last_updated"] = datetime.utcnow().isoformat()
        with open(self.meta_path, "w") as f:
            json.dump(self.meta, f, indent=2)

    # ------------------------------------------------
    # Status
    # ------------------------------------------------

    def is_active(self) -> bool:
        return self.active

    def activate(self):
        self.active = True
        self.meta["active"] = True
        self._save_meta()

    def deactivate(self):
        self.active = False
        self.meta["active"] = False
        self._save_meta()

    # ------------------------------------------------
    # Bias Layer
    # ------------------------------------------------

    def adjust_signal(
        self,
        signal: Signal,
        feature: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Signal:
        """
        Soft confidence adjustment only.
        Action is NEVER changed.
        """

        confidence = signal.confidence

        # Example heuristic bias (replace later with ML)
        if analysis.get("trend_strength", 0) > 0.7:
            confidence *= 1.05

        if analysis.get("volatility", 0) > 0.8:
            confidence *= 0.90

        confidence = max(0.0, min(confidence, 1.0))

        return Signal(
            action=signal.action,
            confidence=confidence,
            reason=f"{signal.reason} | AI bias applied"
        )

    # ------------------------------------------------
    # Learning Loop
    # ------------------------------------------------

    def learn_from_result(
        self,
        signal: Signal,
        result: str
    ):
        """
        Stores experience. No online model update yet.
        """

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": signal.action,
            "confidence": signal.confidence,
            "result": result
        }

        with open(self.memory_path, "a") as f:
            f.write(json.dumps(record) + "\n")

        self.meta["total_trades"] += 1
        if result == "WIN":
            self.meta["wins"] += 1
        else:
            self.meta["losses"] += 1

        self._save_meta()
