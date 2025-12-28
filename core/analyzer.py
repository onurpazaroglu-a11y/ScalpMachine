# analyzer.py

from typing import Dict, Any, List

class Analyzer:
    """
    Feature dict üzerinden analiz yapan modül.
    Candle yönü, trend ve diğer göstergeleri dikkate alır.
    """

    def analysis_to_dict(analysis):
        return {
        "bullish_pressure": getattr(analysis, "bullish_pressure", 0),
        "bearish_pressure": getattr(analysis, "bearish_pressure", 0),
        "signals": getattr(analysis, "signals", [])
    }


    def analyze(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """
        Feature dict -> analiz sonuçları dict
        """
        bullish_pressure, bearish_pressure = self._pressure(feature)
        # Diğer analiz adımları burada eklenebilir

        return {
            "bullish_pressure": bullish_pressure,
            "bearish_pressure": bearish_pressure,
            # İhtiyaca göre diğer metrikler eklenebilir
        }

    def _pressure(self, feature: Dict[str, Any]) -> tuple[int, int]:
        """
        Candle yönüne göre bullish/bearish baskıyı hesaplar
        """
        bullish = 0
        bearish = 0

        # Candles listesi feature dict’inde yer alıyor
        candles: List[Dict[str, Any]] = feature.get("candles", [])
        for f in candles:
            # candle_direction yoksa 0 kabul et
            direction = f.get("candle_direction", 0)
            if direction == 1:
                bullish += 1
            elif direction == -1:
                bearish += 1

        return bullish, bearish

    

    # Eğer başka analiz metrikleri varsa onları da feature dict ile uyumlu şekilde yazabilirsiniz
