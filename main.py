#   ScalpMachine Main entry

from pathlib import Path
from core.image_analysis.loader import Loader
from core.image_analysis.feature_builder import FeatureBuilder, PixelPriceCalibration
from core.image_analysis.candle_detector import CandleDetector
from ai.decision_bias import DecisionBias
from ai.learner import Learner
from core.engine import Engine

# =================================================
# PATHS
# =================================================

BASE_DIR = Path(__file__).parent
SESSION_DIR = BASE_DIR / "session"

IMAGE_PATH = SESSION_DIR / "chart.png"
CALIBRATION_PATH = SESSION_DIR / "calibration.json"
DECISION_BIAS_PATH = SESSION_DIR / "decision_bias.json"
LEARNER_PATH = SESSION_DIR / "learner.json"


# =================================================
# MAIN BOOTSTRAP
# =================================================

def main():
    print("ScalpMachine starting...")

    # -------------------------------
    # LOADERS
    # -------------------------------
    image = Loader.load_image(IMAGE_PATH)
    calibration = Loader.load_calibration(CALIBRATION_PATH)

    # -------------------------------
    # CORE MODULES
    # -------------------------------
    feature_builder = FeatureBuilder()
    candle_detector = CandleDetector()
    decision_bias = DecisionBias()
    learner = Learner()

    decision_bias.load(DECISION_BIAS_PATH)
    learner.load(LEARNER_PATH)

    # -------------------------------
    # ENGINE
    # -------------------------------
    engine = Engine(
        feature_builder=feature_builder,
        candle_detector=candle_detector,
        decision_bias=decision_bias,
        learner=learner
    )

    # -------------------------------
    # RUN SINGLE CYCLE
    # -------------------------------
    result = engine.run(
        image=image,
        interval="1M",
        calibration=calibration
    )

    # -------------------------------
    # PERSIST LEARNING
    # -------------------------------
    decision_bias.save(DECISION_BIAS_PATH)
    learner.save(LEARNER_PATH)

    print("Run completed.")
    print("Result:", result)


# =================================================
# ENTRY POINT
# =================================================

if __name__ == "__main__":
    main()
