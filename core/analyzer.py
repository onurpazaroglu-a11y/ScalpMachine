# ANALYZER temel yapı (Veri analiz eder (görüntü değil!))

from dataclasses import dataclass, asdict
from typing import Dict, Any


# ----------------------------------
# Analysis Result Structure
# ----------------------------------

@dataclass
class AnalysisResult:
    # Candle / price action
    bullish_pressure: float     # 0.0 – 1.0
    bearish_pressure: float     # 0.0 – 1.0

    # Trend
    trend_bias: int             # -1 bearish, 0 neutral, 1 bullish
    trend_strength: float       # 0.0 – 1.0

    # Indicator states
    momentum_bias: int          # -1 / 0 / 1
    overbought: bool
    oversold: bool

    # Volatility
    volatility_state: str       # "low" | "normal" | "high"

    # Overall quality
    setup_quality: float        # 0.0 – 1.0


# ----------------------------------
# Analyzer
# ----------------------------------

class Analyzer:
    """
    Converts feature vectors into interpretable
    technical analysis states.
    """

    def analyze(self, feature: Dict[str, Any]) -> AnalysisResult:
        bullish_pressure, bearish_pressure = self._pressure(feature)
        trend_bias, trend_strength = self._trend(feature)
        momentum_bias = self._momentum(feature)
        overbought, oversold = self._rsi_state(feature)
        volatility_state = self._volatility(feature)
        setup_quality = self._quality(
            bullish_pressure,
            bearish_pressure,
            trend_strength,
            volatility_state
        )

        return AnalysisResult(
            bullish_pressure=bullish_pressure,
            bearish_pressure=bearish_pressure,
            trend_bias=trend_bias,
            trend_strength=trend_strength,
            momentum_bias=momentum_bias,
            overbought=overbought,
            oversold=oversold,
            volatility_state=volatility_state,
            setup_quality=setup_quality
        )

    # ----------------------------------
    # Internal logic blocks
    # ----------------------------------

    def _pressure(self, f: Dict[str, Any]) -> tuple[float, float]:
        """
        Candle + momentum pressure
        """
        bullish = 0.0
        bearish = 0.0

        if f["candle_direction"] == 1:
            bullish += f["body_ratio"]
        elif f["candle_direction"] == -1:
            bearish += f["body_ratio"]

        if f["macd_histogram"] > 0:
            bullish += min(abs(f["macd_histogram"]) / 5.0, 1.0)
        else:
            bearish += min(abs(f["macd_histogram"]) / 5.0, 1.0)

        return min(bullish, 1.0), min(bearish, 1.0)

    def _trend(self, f: Dict[str, Any]) -> tuple[int, float]:
        """
        Trend direction & strength
        """
        if f["trend_slope"] > 0.1:
            bias = 1
        elif f["trend_slope"] < -0.1:
            bias = -1
        else:
            bias = 0

        strength = f["trend_strength"]
        return bias, strength

    def _momentum(self, f: Dict[str, Any]) -> int:
        """
        Momentum bias from RSI + EMA
        """
        score = 0

        if f["ema_fast_above_slow"]:
            score += 1
        else:
            score -= 1

        if f["rsi_zone"] == 1:
            score -= 1
        elif f["rsi_zone"] == -1:
            score += 1

        if score > 0:
            return 1
        if score < 0:
            return -1
        return 0

    def _rsi_state(self, f: Dict[str, Any]) -> tuple[bool, bool]:
        return f["rsi_zone"] == 1, f["rsi_zone"] == -1

    def _volatility(self, f: Dict[str, Any]) -> str:
        if f["volatility_score"] < 0.3:
            return "low"
        if f["volatility_score"] > 0.7:
            return "high"
        return "normal"

    def _quality(
        self,
        bullish: float,
        bearish: float,
        trend_strength: float,
        volatility_state: str
    ) -> float:
        """
        Overall setup quality (confidence baseline)
        """
        base = max(bullish, bearish) * trend_strength

        if volatility_state == "high":
            base *= 0.7
        elif volatility_state == "low":
            base *= 0.85

        return round(min(base, 1.0), 3)


# ----------------------------------
# Utility
# ----------------------------------

def analysis_to_dict(result: AnalysisResult) -> Dict[str, Any]:
    return asdict(result)
