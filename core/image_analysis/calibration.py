from dataclasses import dataclass

@dataclass
class PixelPriceCalibration:
    pixel_top: int
    pixel_bottom: int
    price_top: float
    price_bottom: float

    def pixel_to_price(self, y_pixel: float) -> float:
        """
        Convert pixel Y coordinate to price
        """
        if self.pixel_bottom == self.pixel_top:
            raise ValueError("Invalid calibration: zero pixel range")

        price_range = self.price_bottom - self.price_top
        pixel_range = self.pixel_bottom - self.pixel_top

        scale = price_range / pixel_range

        return self.price_top + (y_pixel - self.pixel_top) * scale
