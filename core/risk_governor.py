# RISK GOVERNOR temel yapı

import sqlite3
from datetime import datetime, timedelta
from typing import Optional


# ----------------------------------
# Risk Governor
# ----------------------------------

class RiskGovernor:
    """
    Behavioral risk protection module.
    Controls loss streaks and temporary trading blocks.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    # ----------------------------------
    # Public API (Engine calls these)
    # ----------------------------------

    def is_blocked(self) -> bool:
        state = self._get_state()
        if not state["blocked_until"]:
            return False

        blocked_until = datetime.fromisoformat(state["blocked_until"])
        return datetime.utcnow() < blocked_until

    def blocked_until(self) -> Optional[str]:
        state = self._get_state()
        return state["blocked_until"]

    def register_trade_result(self, result: str):
        """
        result: "WIN" | "LOSS"
        """
        state = self._get_state()

        if result == "LOSS":
            consecutive = state["consecutive_losses"] + 1
            self._update_losses(consecutive)

            self._check_and_apply_block(consecutive)

        elif result == "WIN":
            self._reset_losses()

    def allow_signal(self, signal_action: str) -> bool:
        """
        Final gate before signal is shown to user.
        """
        if self.is_blocked():
            return False

        # Optional: WAIT always allowed
        if signal_action == "WAIT":
            return True

        return True

    # ----------------------------------
    # Internal logic
    # ----------------------------------

    def _check_and_apply_block(self, consecutive_losses: int):
        """
        Applies progressive blocking rules.
        """
        block_minutes = None

        if consecutive_losses >= 10:
            block_minutes = 60
        elif consecutive_losses >= 7:
            block_minutes = 30
        elif consecutive_losses >= 5:
            block_minutes = 15

        if block_minutes:
            blocked_until = datetime.utcnow() + timedelta(minutes=block_minutes)
            self._set_block(blocked_until, f"{consecutive_losses} consecutive losses")

    # ----------------------------------
    # Database
    # ----------------------------------

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS risk_state (
                    id INTEGER PRIMARY KEY,
                    consecutive_losses INTEGER,
                    last_loss_time TEXT,
                    blocked_until TEXT,
                    block_reason TEXT
                )
            """)
            cur = conn.execute("SELECT COUNT(*) FROM risk_state")
            if cur.fetchone()[0] == 0:
                conn.execute("""
                    INSERT INTO risk_state (
                        consecutive_losses,
                        last_loss_time,
                        blocked_until,
                        block_reason
                    ) VALUES (0, NULL, NULL, NULL)
                """)

    def _get_state(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                SELECT consecutive_losses, last_loss_time,
                       blocked_until, block_reason
                FROM risk_state
                LIMIT 1
            """)
            row = cur.fetchone()

        return {
            "consecutive_losses": row[0],
            "last_loss_time": row[1],
            "blocked_until": row[2],
            "block_reason": row[3]
        }

    def _update_losses(self, count: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE risk_state
                SET consecutive_losses = ?,
                    last_loss_time = ?
            """, (count, datetime.utcnow().isoformat()))

    def _reset_losses(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE risk_state
                SET consecutive_losses = 0,
                    last_loss_time = NULL,
                    blocked_until = NULL,
                    block_reason = NULL
            """)

    def _set_block(self, until: datetime, reason: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE risk_state
                SET blocked_until = ?,
                    block_reason = ?
            """, (until.isoformat(), reason))
