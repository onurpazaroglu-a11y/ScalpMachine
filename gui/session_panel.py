# SESSION PANEL taslak (session.json okur, adım adım replay yapar, her adımda grafik + sonuç gösterir,)

import json
from PyQt5.QtWidgets import (
    QWidget, QListWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton
)

from gui.chart_overlay import ChartOverlay


class SessionPanel(QWidget):
    """
    Read-only session replay panel.
    No Engine calls. No learning. No trading.
    """

    def __init__(self, session_file: str):
        super().__init__()

        self.records = self._load(session_file)
        self.index = 0

        # ----------------------------
        # Widgets
        # ----------------------------
        self.info_label = QLabel()
        self.info_label.setMinimumHeight(120)

        self.chart = ChartOverlay()

        self.prev_btn = QPushButton("Prev")
        self.next_btn = QPushButton("Next")

        self.prev_btn.clicked.connect(self.prev)
        self.next_btn.clicked.connect(self.next)

        # ----------------------------
        # Layout
        # ----------------------------
        control_row = QHBoxLayout()
        control_row.addWidget(self.prev_btn)
        control_row.addWidget(self.next_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.info_label)
        main_layout.addWidget(self.chart)
        main_layout.addLayout(control_row)

        self.setLayout(main_layout)

        # Initial render
        if self.records:
            self._render()

    # =================================================
    # DATA
    # =================================================

    def _load(self, path):
        with open(path, "r") as f:
            return [json.loads(line) for line in f]

    # =================================================
    # RENDER
    # =================================================

    def _render(self):
        r = self.records[self.index]

        signal = r.get("signal", {})
        result = r.get("result")
        risk = "BLOCKED" if r.get("risk_blocked") else "OK"

        self.info_label.setText(
            f"""
Time      : {r.get('timestamp')}
Interval  : {r.get('interval')}

Action    : {signal.get('action')}
Confidence: {signal.get('confidence', 0):.2f}
Reason    : {signal.get('reason')}

Result    : {result}
Risk      : {risk}
"""
        )

        chart_data = r.get("chart")
        if chart_data:
            self.chart.render(
                chart_data=chart_data,
                signal=signal
            )

    # =================================================
    # NAVIGATION
    # =================================================

    def next(self):
        if self.index < len(self.records) - 1:
            self.index += 1
            self._render()

    def prev(self):
        if self.index > 0:
            self.index -= 1
            self._render()

#Hierarchy problemi var, çözülmesi gerekiyor (Saat sabahın 4'ü çözmeyeceğim bu saatte)