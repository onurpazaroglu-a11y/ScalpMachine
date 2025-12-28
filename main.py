from pathlib import Path
from core.image_analysis.loader import Loader
from core.image_analysis.feature_builder import FeatureBuilder, PixelPriceCalibration
from core.engine import Engine

# =================================================
# PATHS
# =================================================
BASE_DIR = Path(__file__).parent
SESSION_DIR = BASE_DIR / "session"

IMAGE_PATH = SESSION_DIR / "chart.png"
CALIBRATION_PATH = SESSION_DIR / "calibration.json"
RISK_DB_PATH = BASE_DIR / "risk.db"  # risk DB yolunu ekledik

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
    # ENGINE
    # -------------------------------
    engine = Engine(
        risk_db_path=str(RISK_DB_PATH)
        # ai_manager parametresi varsa buraya ekleyebilirsin
    )

    # -------------------------------
    # PROCESS CYCLE
    # -------------------------------
    signal = engine.process(
        image=image,
        interval="1M",
        calibration=calibration
    )

    # -------------------------------
    # FEATURE TO DICT
    # -------------------------------
def feature_to_dict(feature):
    return {
        "candles": [
            {
                **c.__dict__,
                "candle_direction": c.direction
            } for c in feature.candles
        ],
        "indicators": feature.indicators,
        "volatility": feature.volatility
    }


    print("Run completed.")
    print("Signal:", signal)

if __name__ == "__main__":
    main()
