from core.analyzer import Analyzer, analysis_to_dict
from core.image_analysis.feature_builder import feature_to_dict, FeatureBuilder
from core.signal_logic import SignalLogic, Signal
from core.risk_governor import RiskGovernor

class Engine:
    def __init__(self, risk_db_path: str, ai_manager=None):
        self.feature_builder = FeatureBuilder()
        self.analyzer = Analyzer()
        self.signal_logic = SignalLogic()
        self.risk = RiskGovernor(risk_db_path)
        self.ai = ai_manager

    def process(self, feature_dict: dict, interval: str):
        # Interval kontrolü
        if not interval in ["1M","5M","15M"]:
            raise ValueError(f"Invalid interval: {interval}")

        # Risk check
        if self.risk.is_blocked():
            return Signal(action="WAIT", confidence=0.0, reason="Risk blocked")

        # Analysis
        analysis = self.analyzer.analyze(feature_dict)
        signal = self.signal_logic.decide(analysis)

        # AI bias (opsiyonel)
        if self.ai and self.ai.is_active():
            signal = self.ai.adjust_signal(signal, feature_dict, analysis_to_dict(analysis))

        # Risk gate
        if not self.risk.allow_signal(signal.action):
            signal = Signal(action="WAIT", confidence=0.0, reason="Blocked by risk governor")

        return signal
