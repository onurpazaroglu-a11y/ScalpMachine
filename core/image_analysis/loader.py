import json
import cv2
import numpy as np
from pathlib import Path
from typing import Optional

from core.image_analysis.feature_builder import PixelPriceCalibration


class Loader:
    """
    Centralized loader for images, calibration, and session artifacts.
    Deterministic, replay-safe.
    """

    # -------------------------------------------------
    # IMAGE
    # -------------------------------------------------

    @staticmethod
    def load_image(path: str | Path) -> np.ndarray:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"Failed to load image: {path}")

        return image

    # -------------------------------------------------
    # CALIBRATION
    # -------------------------------------------------

    @staticmethod
    def load_calibration(path: str | Path) -> Optional[PixelPriceCalibration]:
        path = Path(path)
        if not path.exists():
            return None

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return PixelPriceCalibration(
            pixel_top=data["pixel_top"],
            pixel_bottom=data["pixel_bottom"],
            price_top=data["price_top"],
            price_bottom=data["price_bottom"],
        )

    @staticmethod
    def save_calibration(
        calibration: PixelPriceCalibration,
        path: str | Path
    ) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "pixel_top": calibration.pixel_top,
                    "pixel_bottom": calibration.pixel_bottom,
                    "price_top": calibration.price_top,
                    "price_bottom": calibration.price_bottom,
                },
                f,
                indent=2
            )

    # -------------------------------------------------
    # SESSION LOG / FEATURES
    # -------------------------------------------------

    @staticmethod
    def load_json(path: str | Path) -> dict:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"JSON not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_json(data: dict, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
