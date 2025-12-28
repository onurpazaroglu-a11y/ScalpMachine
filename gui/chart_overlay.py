from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class ChartOverlay(QWidget):

    def __init__(self):
        super().__init__()

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvasQTAgg(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def rendery(self, chart_data, signal=None):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.plot(chart_data["close"], label="Close", linewidth=1.5)
        ax.plot(chart_data["ema50"], label="EMA50", linestyle="--")
        ax.plot(chart_data["ema200"], label="EMA200", linestyle=":")

        if signal:
            ax.set_title(
                f"{signal['action']} | conf={signal['confidence']:.2f}"
            )

        ax.legend()
        ax.grid(True)

        self.canvas.draw()


# Modüller sorunlu kontrol edilecek
# Line18 def render(self, chart_data, ...) tanımı; komut çakışmaması için def rendery olarak değiştirildi.