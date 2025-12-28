# CANDLE DETECTOR - Pixel - OHLC generator (Benzer bir modül, feature_builder.py içinde de var kontrol etmek gerek)

import cv2
import numpy as np
from dataclasses import dataclass
from typing import List


# =================================================
# DATA STRUCTURE
# =================================================

@dataclass
class Candle:
    open: float   # pixel-space Y
    close: float  # pixel-space Y
    high: float   # pixel-space Y
    low: float    # pixel-space Y


# =================================================
# CANDLE DETECTOR
# =================================================

class CandleDetector:
    """
    Detects candlesticks from a chart image.
    Pixel-space only. No price logic.
    """

    def __init__(
        self,
        min_height_ratio: float = 0.05,
        min_aspect_ratio: float = 2.0
    ):
        self.min_height_ratio = min_height_ratio
        self.min_aspect_ratio = min_aspect_ratio

    # -------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------

    def detect(self, image: np.ndarray) -> List[Candle]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        _, binary = cv2.threshold(
            blur, 0, 255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        img_h, _ = gray.shape
        candles: List[Candle] = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

            if not self._is_valid_candle(w, h, img_h):
                continue

            candles.append(
                self._rect_to_candle(y, h, img_h)
            )

        # time order proxy: left→right assumed already cropped
        candles.reverse()
        return candles

    # =================================================
    # INTERNAL HELPERS
    # =================================================

    def _is_valid_candle(self, w: int, h: int, img_h: int) -> bool:
        if h < img_h * self.min_height_ratio:
            return False
        if h / max(w, 1) < self.min_aspect_ratio:
            return False
        return True

    def _rect_to_candle(
        self,
        y: int,
        height: int,
        img_h: int
    ) -> Candle:
        """
        Convert bounding rect to pixel-space OHLC.
        Higher price = smaller y, so invert via img_h - y.
        """

        high = img_h - y
        low = img_h - (y + height)

        # body approximation (center 50%)
        body_top = img_h - (y + int(height * 0.25))
        body_bottom = img_h - (y + int(height * 0.75))

        return Candle(
            open=body_top,
            close=body_bottom,
            high=high,
            low=low
        )

#   feature_builder.py içinde örnek kullanım:
#   from core.image_analysis.candle_detector import CandleDetector
#
#   detector = CandleDetector()
#   candles = detector.detect(image)
