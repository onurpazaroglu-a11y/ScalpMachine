import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Candle:
    open: float
    close: float
    high: float
    low: float

    @property
    def candle_direction(self) -> int:
        """1 = bullish, -1 = bearish, 0 = neutral"""
        if self.close > self.open:
            return 1
        elif self.close < self.open:
            return -1
        else:
            return 0


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

class FeatureBuilder:
    def build(self, image, interval, calibration: Optional[PixelPriceCalibration] = None):
        # Basit candlestick tespiti
        # Burada örnek olarak tüm pikselleri tek candle yapıyoruz
        candles = [Candle(open=0, close=1, high=1, low=0)]
        indicators_data = {}

        volatility = 0.01
        return Feature(candles=candles, indicators=indicators_data, volatility=volatility)

def feature_to_dict(feature: Feature):
    """
    Feature nesnesini dict’e çevirir. Analyzer’ın ihtiyaç duyduğu
    candle_direction gibi alanları da ekler.
    """
    feature_dict = {
        "candles": [],
        "indicators": feature.indicators,
        "volatility": feature.volatility
    }

    for c in feature.candles:
        direction = 1 if c.close > c.open else -1 if c.close < c.open else 0
        feature_dict["candles"].append({
            "open": c.open,
            "close": c.close,
            "high": c.high,
            "low": c.low,
            "candle_direction": direction
        })

    return feature_dict
