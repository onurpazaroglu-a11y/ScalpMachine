# ENGINE - interval doğrulaması, risk pre-check + final gate, AI sadece bias + learning, 
# session log +replay için snapshot, GUI/CLI/Replay uyumlu

from typing import Dict, Any, Optional
from core.intervals import is_valid_interval
from core.risk_governor import RiskGovernor
from core.signal_logic import SignalLogic, Signal
from core.analyzer import Analyzer, analysis_to_dict
from core.image_analysis.feature_builder import FeatureBuilder, feature_to_dict
from core.session_logger import SessionLogger


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
        raw_analysis_inputs: Dict[str, Dict[str, Any]],
        interval: str
    ) -> Signal:
        """
        raw inputs -> feature -> analysis -> signal
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
                risk_blocked=True,
                chart_snapshot=None
            )
            return signal

        # -----------------------------
        # Feature building
        # -----------------------------
        feature = self.feature_builder.build(
            candle_data=raw_analysis_inputs.get("candle", {}),
            trend_data=raw_analysis_inputs.get("trend", {}),
            indicator_data=raw_analysis_inputs.get("indicator", {}),
            volatility_data=raw_analysis_inputs.get("volatility", {}),
            interval=interval
            )
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
            signal = self.ai.adjust_signal(
                signal=signal,
                feature=feature_dict,
                analysis=analysis_dict
            )

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
        # Session log (snapshot only)
        # -----------------------------
        self.logger.log_signal(
            interval=interval,
            signal=signal,
            risk_blocked=self.risk.is_blocked(),
            chart_snapshot={
                "close": feature.close_series[-50:],
                "ema50": feature.ema50[-50:],
                "ema200": feature.ema200[-50:]
            } if hasattr(feature, "close_series") else None
        )

        return signal

    # =================================================
    # FEEDBACK LOOP
    # =================================================

    def register_trade_result(
        self,
        signal: Signal,
        result: str
    ):
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
            self.ai.learn_from_result(
                signal=signal,
                result=result
            )

        # -----------------------------
        # Session log update
        # -----------------------------
        self.logger.log_result(result)
