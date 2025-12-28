# SIGNAL LOGIC temel yapı

from dataclasses import dataclass


# ----------------------------------
# Signal Structure
# ----------------------------------

@dataclass
class Signal:
    action: str              # "CALL" | "PUT" | "WAIT"
    confidence: float        # 0.0 – 1.0
    reason: str              # human-readable explanation


# ----------------------------------
# Signal Logic
# ----------------------------------

class SignalLogic:
    """
    Converts AnalysisResult into a raw trading signal.
    This module is deterministic and rule-based.
    """

    def decide(self, analysis) -> Signal:
        """
        Entry point used by engine.
        """
        # Safety gate: very low quality setups
        if analysis.setup_quality < 0.25:
            return self._wait("Low setup quality")

        # Volatility filter
        if analysis.volatility_state == "high":
            return self._wait("High volatility")

        # Strong bullish scenario
        if self._bullish_setup(analysis):
            return self._call(analysis, "Bullish setup confirmed")

        # Strong bearish scenario
        if self._bearish_setup(analysis):
            return self._put(analysis, "Bearish setup confirmed")

        # Default
        return self._wait("No clear edge")

    # ----------------------------------
    # Setup definitions
    # ----------------------------------

    def _bullish_setup(self, a) -> bool:
        return (
            a.trend_bias == 1 and
            a.momentum_bias >= 0 and
            a.bullish_pressure > a.bearish_pressure and
            not a.overbought and
            a.setup_quality >= 0.45
        )

    def _bearish_setup(self, a) -> bool:
        return (
            a.trend_bias == -1 and
            a.momentum_bias <= 0 and
            a.bearish_pressure > a.bullish_pressure and
            not a.oversold and
            a.setup_quality >= 0.45
        )

    # ----------------------------------
    # Signal builders
    # ----------------------------------

    def _call(self, a, reason: str) -> Signal:
        confidence = self._confidence(a)
        return Signal(
            action="CALL",
            confidence=confidence,
            reason=reason
        )

    def _put(self, a, reason: str) -> Signal:
        confidence = self._confidence(a)
        return Signal(
            action="PUT",
            confidence=confidence,
            reason=reason
        )

    def _wait(self, reason: str) -> Signal:
        return Signal(
            action="WAIT",
            confidence=0.0,
            reason=reason
        )

    # ----------------------------------
    # Confidence scoring
    # ----------------------------------

    def _confidence(self, a) -> float:
        """
        Baseline confidence (AI may later adjust this).
        """
        base = a.setup_quality

        # Trend alignment bonus
        if a.trend_strength > 0.6:
            base += 0.1

        # Momentum confirmation bonus
        if abs(a.momentum_bias) == 1:
            base += 0.05

        return round(min(base, 1.0), 3)
