from PyQt5.QtWidgets import QComboBox
from core.intervals import intervals_by_group, Interval


class IntervalSelector(QComboBox):
    """
    Read-only interval selector.
    Emits interval.code, not UI labels.
    """

    def __init__(self, default: str = "1M"):
        super().__init__()

        self._interval_map = {}

        self._populate()
        self.set_interval(default)

    def _populate(self):
        """
        Grouped intervals:
        SCALP / INTRADAY / SWING
        """
        for group in ["SCALP", "INTRADAY", "SWING"]:
            self.addItem(f"--- {group} ---")
            self.model().item(self.count() - 1).setEnabled(False)

            for interval in intervals_by_group(group):
                label = f"{interval.label} ({interval.code})"
                self.addItem(label)
                self._interval_map[label] = interval

    def current_interval(self) -> Interval:
        label = self.currentText()
        return self._interval_map.get(label)

    def current_code(self) -> str:
        interval = self.current_interval()
        return interval.code if interval else None

    def set_interval(self, code: str):
        for i in range(self.count()):
            interval = self._interval_map.get(self.itemText(i))
            if interval and interval.code == code:
                self.setCurrentIndex(i)
                return
