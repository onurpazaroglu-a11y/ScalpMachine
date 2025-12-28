# ANALYZE WORKER taslak

from PyQt5.QtCore import QThread, pyqtSignal

class AnalyzeWorker(QThread):
    finished = pyqtSignal(object)

    def __init__(self, engine, raw_inputs, interval):
        super().__init__()
        self.engine = engine
        self.raw_inputs = raw_inputs
        self.interval = interval

    def run(self):
        signal = self.engine.process(
            raw_analysis_inputs=self.raw_inputs,
            interval=self.interval
        )
        self.finished.emit(signal)
