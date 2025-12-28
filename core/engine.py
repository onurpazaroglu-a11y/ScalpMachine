# ENGINE - interval doğrulaması, risk pre-check + final gate, AI sadece bias + learning, 
# session log + replay için snapshot, GUI/CLI/Replay uyumlu

from typing import Dict, Any, Optional
from core.intervals import is_valid_interval
from core.risk_governor import RiskGovernor
from core.signal_logic import SignalLogic, Signal
from core.analyzer import Analyzer, analysis_to_dict
from core.image_analysis.feature_builder import FeatureBuilder
from core.image_analysis.feature_builder import PixelPriceCalibration
from core.session_logger import SessionLogger


def feature_to_dict(feature):
    """Feature objectunu dict'e çevirir"""
    return {
        "candles": [c.__dict__ for c in feature.candles],
        "indicators": feature.indicators,
        "volatility": feature.volatility
    }


class Engine:
    """
    Central decision orchestrator.
    GUI, CLI, Replay all talk ONLY to this class.
    """

    def __init__(
        self,
        risk_db_path: str,
        ai_manager: Optional[Any] = None,
        session_dir: str = "sessions"
    ):
        # Core modules
        self.feature_builder = FeatureBuilder()
        self.analyzer = Analyzer()
        self.signal_logic = SignalLogic()
        self.risk = RiskGovernor(risk_db_path)

        # Optional AI
        self.ai = ai_manager

        # Session logger (read-only for replay)
        self.logger = SessionLogger(session_dir=session_dir)

    # =================================================
    # MAIN PIPELINE
    # =================================================
    def process(
        self,
        image: Any,
        interval: str,
        calibration: Optional[PixelPriceCalibration] = None
    ) -> Signal:
        """
        image -> feature -> analysis -> signal
        -> AI bias (optional) -> risk gate
        """

        # -----------------------------
        # Interval validation
        # -----------------------------
        if not is_valid_interval(interval):
            raise ValueError(f"Invalid interval: {interval}")

        # -----------------------------
        # Risk pre-check (hard stop)
        # -----------------------------
        if self.risk.is_blocked():
            signal = Signal(
                action="WAIT",
                confidence=0.0,
                reason="Risk protection active"
            )
            # Log blocked state
            self.logger.log_signal(
                interval=interval,
                signal=signal,
                risk_blocked=True
            )
            return signal

        # -----------------------------
        # Feature building
        # -----------------------------
        feature = self.feature_builder.build(image=image, interval=interval, calibration=calibration)
        feature_dict = feature_to_dict(feature)

        # -----------------------------
        # Analysis
        # -----------------------------
        analysis = self.analyzer.analyze(feature_dict)
        analysis_dict = analysis_to_dict(analysis)

        # -----------------------------
        # Rule-based signal
        # -----------------------------
        signal = self.signal_logic.decide(analysis)

        # -----------------------------
        # AI bias (optional, soft only)
        # -----------------------------
        if self.ai is not None and self.ai.is_active():
            signal = self.ai.adjust_signal(signal=signal, feature=feature_dict, analysis=analysis_dict)

        # -----------------------------
        # Final risk gate
        # -----------------------------
        if not self.risk.allow_signal(signal.action):
            signal = Signal(
                action="WAIT",
                confidence=0.0,
                reason="Blocked by risk governor"
            )

        # -----------------------------
        # Session log
        # -----------------------------
        self.logger.log_signal(
            interval=interval,
            signal=signal,
            risk_blocked=self.risk.is_blocked()
        )

        return signal

    # =================================================
    # FEEDBACK LOOP
    # =================================================
    def register_trade_result(self, signal: Signal, result: str):
        """
        result: "WIN" | "LOSS"
        """

        # -----------------------------
        # Risk update
        # -----------------------------
        self.risk.register_trade_result(result)

        # -----------------------------
        # AI learning (optional)
        # -----------------------------
        if self.ai is not None and self.ai.is_active():
            self.ai.learn_from_result(signal=signal, result=result)

        # -----------------------------
        # Session log update
        # -----------------------------
        self.logger.log_result(result)
