#   FEATURE BUILDER Temel Yapı (Early stage)
#   GELİŞTİRME YOL HARİTASI (SONRA)
#   Sırayla:
#   1.OCR (sadece eksen için)
#   2.Multi-indicator katmanları
#   eklenecek


import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional


# =================================================
# DATA STRUCTURES
# =================================================

@dataclass
class Candle:
    open: float
    close: float
    high: float
    low: float


@dataclass
class Feature:
    candles: List[Candle]
    ema50: Optional[List[float]]
    ema200: Optional[List[float]]
    volatility: float


# =================================================
# CALIBRATION
# =================================================

@dataclass
class PixelPriceCalibration:
    pixel_top: int
    pixel_bottom: int
    price_top: float
    price_bottom: float

    def pixel_to_price(self, y_pixel: float) -> float:
        pixel_range = self.pixel_bottom - self.pixel_top
        if pixel_range == 0:
            raise ValueError("Invalid calibration")

        price_range = self.price_bottom - self.price_top
        scale = price_range / pixel_range
        return self.price_top + (y_pixel - self.pixel_top) * scale


# =================================================
# EMA COLOR CONFIG (THEME DEPENDENT)
# =================================================

EMA_CONFIG = {
    "ema50": {
        "hsv_lower": (20, 100, 100),
        "hsv_upper": (35, 255, 255)
    },
    "ema200": {
        "hsv_lower": (90, 100, 100),
        "hsv_upper": (130, 255, 255)
    }
}


# =================================================
# FEATURE BUILDER
# =================================================

class FeatureBuilder:
    """
    Image → numeric feature extractor
    No decisions, no strategy, no AI
    """

    # -------------------------------------------------
    # PUBLIC ENTRY
    # -------------------------------------------------

    def build(
        self,
        image: np.ndarray,
        interval: str,
        calibration: Optional[PixelPriceCalibration] = None
    ) -> Feature:

        candles = self._extract_candles(image)
        ema_data = self._extract_ema_lines(image)

        if calibration:
            candles = self._apply_price_calibration(candles, calibration)
            for k in ema_data:
                ema_data[k] = self._calibrate_series(ema_data[k], calibration)

        volatility = self._estimate_volatility(candles)

        return Feature(
            candles=candles,
            ema50=ema_data.get("ema50"),
            ema200=ema_data.get("ema200"),
            volatility=volatility
        )

    # =================================================
    # CANDLE DETECTION
    # =================================================

    def _extract_candles(self, image: np.ndarray) -> List[Candle]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        _, binary = cv2.threshold(
            blur, 0, 255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        h, _ = gray.shape
        candles = []

        for cnt in contours:
            x, y, w, ch = cv2.boundingRect(cnt)

            if ch < h * 0.05:
                continue
            if ch / max(w, 1) < 2:
                continue

            candles.append(
                self._build_candle_from_rect(y, ch, h)
            )

        # left → right (time order proxy)
        candles.reverse()
        return candles

    def _build_candle_from_rect(
        self,
        y: int,
        height: int,
        image_height: int
    ) -> Candle:

        high = image_height - y
        low = image_height - (y + height)

        body_top = image_height - (y + int(height * 0.25))
        body_bottom = image_height - (y + int(height * 0.75))

        # normalize (pixel space for now)
        return Candle(
            open=body_top,
            close=body_bottom,
            high=high,
            low=low
        )

    # =================================================
    # EMA DETECTION
    # =================================================

    def _extract_ema_lines(self, image: np.ndarray) -> Dict[str, List[float]]:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, w, _ = image.shape
        result = {}

        for name, cfg in EMA_CONFIG.items():
            mask = cv2.inRange(
                hsv,
                np.array(cfg["hsv_lower"]),
                np.array(cfg["hsv_upper"])
            )

            mask = self._clean_mask(mask)
            series = self._mask_to_series(mask, h, w)

            if series:
                result[name] = series

        return result

    def _clean_mask(self, mask: np.ndarray) -> np.ndarray:
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        return mask

    def _mask_to_series(
        self,
        mask: np.ndarray,
        height: int,
        width: int
    ) -> List[float]:

        series = []
        step = max(1, width // 120)

        for x in range(0, width, step):
            column = mask[:, x]
            ys = np.where(column > 0)[0]

            if len(ys) == 0:
                continue

            y = int(np.mean(ys))
            series.append(float(height - y))

        return series

    # =================================================
    # CALIBRATION HELPERS
    # =================================================

    def _apply_price_calibration(
        self,
        candles: List[Candle],
        calibration: PixelPriceCalibration
    ) -> List[Candle]:

        out = []
        for c in candles:
            out.append(
                Candle(
                    open=calibration.pixel_to_price(c.open),
                    close=calibration.pixel_to_price(c.close),
                    high=calibration.pixel_to_price(c.high),
                    low=calibration.pixel_to_price(c.low)
                )
            )
        return out

    def _calibrate_series(
        self,
        series: List[float],
        calibration: PixelPriceCalibration
    ) -> List[float]:
        return [calibration.pixel_to_price(v) for v in series]

    # =================================================
    # NUMERIC HELPERS
    # =================================================

    def _estimate_volatility(self, candles: List[Candle]) -> float:
        if len(candles) < 2:
            return 0.0

        closes = np.array([c.close for c in candles])
        returns = np.diff(closes)
        return float(np.std(returns))
