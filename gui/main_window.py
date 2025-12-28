# MAIN WINDIW taslak

import sys
from datetime import datetime
from core.intervals import intervals_by_group
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QProgressBar
)
from PyQt5.QtCore import QTimer
from gui.widgets.interval_selector import IntervalSelector
from core.engine import Engine
from ai.ai_manager import AIManager
from gui.workers.analyze_worker import AnalyzeWorker


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # ----------------------------
        # Core
        # ----------------------------
        self.ai = AIManager("models/default")
        self.engine = Engine(
            risk_db_path="data/risk.db",
            ai_manager=self.ai
        )

        self.last_signal = None
        self.worker = None

        # ----------------------------
        # UI Setup
        # ----------------------------
        self.setWindowTitle("ScalpMachine")
        self._setup_ui()

        # ----------------------------
        # Risk status timer
        # ----------------------------
        self.risk_timer = QTimer()
        self.risk_timer.timeout.connect(self.update_risk_status)
        self.risk_timer.start(1000)

    # =================================================
    # UI
    # =================================================

    def _setup_ui(self):
        # Widgets
        self.signal_label = QLabel("Action: -")
        self.reason_label = QLabel("Reason: -")
        
        self.interval_selector = IntervalSelector(default="1M")


        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)

        self.risk_label = QLabel("Risk: OK")
        self.risk_label.setStyleSheet("color: green;")

        self.analyze_btn = QPushButton("Analyze")
        self.win_btn = QPushButton("WIN")
        self.loss_btn = QPushButton("LOSS")
        self.ai_btn = QPushButton("AI ON / OFF")

        # Events
        self.analyze_btn.clicked.connect(self.on_analyze)
        self.win_btn.clicked.connect(lambda: self.on_result("WIN"))
        self.loss_btn.clicked.connect(lambda: self.on_result("LOSS"))
        self.ai_btn.clicked.connect(self.on_ai_toggle)

        # ----------------------------
        # Layouts
        # ----------------------------

        main_layout = QVBoxLayout()

        # Top info
        main_layout.addWidget(self.signal_label)
        main_layout.addWidget(self.confidence_bar)
        main_layout.addWidget(self.reason_label)

        # Risk bar
        main_layout.addWidget(self.risk_label)

        # Button row
        button_row = QHBoxLayout()
        button_row.addWidget(self.analyze_btn)
        button_row.addWidget(self.win_btn)
        button_row.addWidget(self.loss_btn)
        button_row.addWidget(self.ai_btn)

        main_layout.addLayout(button_row)

        # Container
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        main_layout.addWidget(self.interval_selector)


    # =================================================
    # EVENTS
    # =================================================

    def on_analyze(self):
        self.analyze_btn.setEnabled(False)

        raw_data = self._collect_inputs()

        self.worker = AnalyzeWorker(
            engine=self.engine,
            raw_inputs=raw_data,
            interval="1M"
        )
        self.worker.finished.connect(self.on_analyze_finished)
        self.worker.start()

    def on_analyze_finished(self, signal):
        self.last_signal = signal
        self._update_view(signal)
        self.analyze_btn.setEnabled(True)

    def on_result(self, result: str):
        if self.last_signal:
            self.engine.register_trade_result(
                signal=self.last_signal,
                result=result
            )

    def on_ai_toggle(self):
        if self.ai.is_active():
            self.ai.deactivate()
        else:
            self.ai.activate()

    # =================================================
    # VIEW
    # =================================================

    def _update_view(self, signal):
        self.signal_label.setText(f"Action: {signal.action}")
        self.reason_label.setText(f"Reason: {signal.reason}")
        self.confidence_bar.setValue(int(signal.confidence * 100))

    def update_risk_status(self):
        if not self.engine.risk.is_blocked():
            self.risk_label.setText("Risk: OK")
            self.risk_label.setStyleSheet("color: green;")
            return

        blocked_until = self.engine.risk.blocked_until()
        if not blocked_until:
            return

        until_dt = datetime.fromisoformat(blocked_until)
        remaining = until_dt - datetime.utcnow()

        if remaining.total_seconds() <= 0:
            self.risk_label.setText("Risk: OK")
            self.risk_label.setStyleSheet("color: green;")
            return

        m, s = divmod(int(remaining.total_seconds()), 60)
        self.risk_label.setText(f"Risk: BLOCKED ({m:02d}:{s:02d})")
        self.risk_label.setStyleSheet("color: red;")

    # =================================================
    # INPUT STUB
    # =================================================

    def _collect_inputs(self):
        return {
            "candle": {},
            "trend": {},
            "indicator": {},
            "volatility": {}
        }


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
