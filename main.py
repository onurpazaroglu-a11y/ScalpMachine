from pathlib import Path
from core.image_analysis.loader import Loader
from core.image_analysis.feature_builder import FeatureBuilder, feature_to_dict, PixelPriceCalibration
from core.engine import Engine

BASE_DIR = Path(__file__).parent
SESSION_DIR = BASE_DIR / "session"

IMAGE_PATH = SESSION_DIR / "chart.png"
CALIBRATION_PATH = SESSION_DIR / "calibration.json"
RISK_DB_PATH = BASE_DIR / "risk.db"

def main():
    print("ScalpMachine starting...")

    # Load image & calibration
    image = Loader.load_image(IMAGE_PATH)
    calibration = Loader.load_calibration(CALIBRATION_PATH)

    # Feature build
    fb = FeatureBuilder()
    feature = fb.build(image=image, interval="1M", calibration=calibration)
    feature_dict = feature_to_dict(feature)

    # Engine
    engine = Engine(str(RISK_DB_PATH))

    # Process
    signal = engine.process(feature_dict=feature_dict, interval="1M")

    print("Run completed.")
    print("Signal:", signal)

if __name__ == "__main__":
    main()
