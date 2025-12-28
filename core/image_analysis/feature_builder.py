# feature_builder.py
import sys
import os
import cv2
import numpy as np
import sqlite3
import json
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

# =================== IMPORT INDICATORS ===================
# indicators klasörünü path’e ekle
INDICATORS_PATH = Path(__file__).parent.parent / "indicators"
if str(INDICATORS_PATH) not in sys.path:
    sys.path.append(str(INDICATORS_PATH))

try:
    from indicator_setup import DB_PATH, load_indicators_from_db
except ModuleNotFoundError:
    raise ModuleNotFoundError(py modülü bulunamadı. indicators klasörün
        "indicator_setup.py modülü bulunamadı. indicators klasöründe olduğundan emin ol."
    )

# =================== DATA STRUCTURES ===================
@dataclass
class Candle:
    open: float
    close: float
    high: float
    low: float

@dataclass
class Feature:
    candles: List[Candle]
    indicators: dict
    volatility: float

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

# =================== FEATURE BUILDER ===================
class FeatureBuilder:
    def __init__(self, session_id=None, list_name=None):
        self.session_id = session_id
        self.list_name = list_name
        self.indicators = []
        if session_id and list_name:
            try:
                self.indicators = load_indicators_from_db(session_id, list_name)
            except Exception as e:
                print(f"DB’den indikatör yüklenemedi: {e}")
                self.indicators = []

    def build(self, image: np.ndarray, interval: str, calibration: Optional[PixelPriceCalibration] = None):
        candles = self._extract_candles(image)
        indicators_data = self._extract_indicator_layers(image)

        if calibration:
            candles = self._apply_price_calibration(candles, calibration)
            for k in indicators_data:
                indicators_data[k] = self._calibrate_series(indicators_data[k], calibration)

        volatility = self._estimate_volatility(candles)

        return Feature(
            candles=candles,
            indicators=indicators_data,
            volatility=volatility
        )

    # ----------------- CANDLE DETECTION -----------------
    def _extract_candles(self, image: np.ndarray) -> List[Candle]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5),0)
        _, binary = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        h, _ = gray.shape
        candles = []
        for cnt in contours:
            x, y, w, ch = cv2.boundingRect(cnt)
            if ch < h*0.05: continue
            if ch/max(w,1) < 2: continue
            candles.append(self._build_candle_from_rect(y,ch,h))
        candles.reverse()
        return candles

    def _build_candle_from_rect(self, y, height, image_height):
        high = image_height - y
        low = image_height - (y + height)
        body_top = image_height - (y + int(height*0.25))
        body_bottom = image_height - (y + int(height*0.75))
        return Candle(open=body_top, close=body_bottom, high=high, low=low)

    # ----------------- INDICATOR LAYER DETECTION -----------------
    def _extract_indicator_layers(self, image: np.ndarray):
        h, w, _ = image.shape
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        result = {}
        for ind in self.indicators:
            color = np.array(ind.get("color",[0,0,0]), dtype=np.uint8)
            lower = np.clip(color - 10, 0, 255)
            upper = np.clip(color + 10, 0, 255)
            mask = cv2.inRange(hsv, lower, upper)
            mask = self._clean_mask(mask)
            series = self._mask_to_series(mask, h, w)
            if series:
                result[ind["name"]] = series
        return result

    def _clean_mask(self, mask: np.ndarray) -> np.ndarray:
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        return mask

    def _mask_to_series(self, mask: np.ndarray, height: int, width: int):
        series = []
        step = max(1, width//120)
        for x in range(0, width, step):
            column = mask[:,x]
            ys = np.where(column>0)[0]
            if len(ys)==0: continue
            y = int(np.mean(ys))
            series.append(float(height - y))
        return series

    # ----------------- CALIBRATION HELPERS -----------------
    def _apply_price_calibration(self, candles, calibration):
        out=[]
        for c in candles:
            out.append(Candle(
                open=calibration.pixel_to_price(c.open),
                close=calibration.pixel_to_price(c.close),
                high=calibration.pixel_to_price(c.high),
                low=calibration.pixel_to_price(c.low)
            ))
        return out

    def _calibrate_series(self, series, calibration):
        return [calibration.pixel_to_price(v) for v in series]

    # ----------------- NUMERIC HELPERS -----------------
    def _estimate_volatility(self, candles):
        if len(candles)<2: return 0.0
        closes = np.array([c.close for c in candles])
        returns = np.diff(closes)
        return float(np.std(returns))

# ==================== ÖRNEK KULLANIM ====================
if __name__=="__main__":
    session_id = "session20251228_142900"
    list_name = "MyDefaultList"
    fb = FeatureBuilder(session_id=session_id, list_name=list_name)
    # image = cv2.imread("test_chart.png")
    # calibration = PixelPriceCalibration(pixel_top=0, pixel_bottom=500, price_top=100, price_bottom=200)
    # feature = fb.build(image, interval="1M", calibration=calibration)
    # print(feature)
