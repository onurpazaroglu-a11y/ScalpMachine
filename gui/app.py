# APP taslak

import tkinter as tk

from core.engine import Engine
from ai.ai_manager import AIManager


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("ScalpMachine")

        self.ai = AIManager("models/default")
        self.engine = Engine("data/risk.db", self.ai)

        self.last_signal = None

        self.label = tk.Label(self, text="Action: -")
        self.label.pack()

        self.confidence = tk.Label(self, text="Confidence: -")
        self.confidence.pack()

        tk.Button(self, text="Analyze", command=self.on_analyze).pack()
        tk.Button(self, text="WIN", command=lambda: self.on_result("WIN")).pack()
        tk.Button(self, text="LOSS", command=lambda: self.on_result("LOSS")).pack()
        tk.Button(self, text="AI ON / OFF", command=self.on_ai_toggle).pack()

    def on_analyze(self):
        signal = self.engine.process(
            raw_analysis_inputs=self._collect_inputs(),
            interval="1M"
        )

        self.last_signal = signal
        self.label.config(text=f"Action: {signal.action}")
        self.confidence.config(text=f"Confidence: {signal.confidence:.2f}")

    def on_result(self, result):
        if self.last_signal:
            self.engine.register_trade_result(self.last_signal, result)

    def on_ai_toggle(self):
        if self.ai.is_active():
            self.ai.deactivate()
        else:
            self.ai.activate()

    def _collect_inputs(self):
        return {
            "candle": {},
            "trend": {},
            "indicator": {},
            "volatility": {}
        }


if __name__ == "__main__":
    App().mainloop()
