# INDICATOR SETUP - Default indicatorleri .json dosyasından alır, 
# kullanıcı isteğine göre düzenlenir ve indicatorlist.db veri tabanına kaydeder. 
# Daha sonra bu db içerisindeki liste, feature_builder içerisinde kullanılır.

import sys
import os
import sqlite3
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QListWidget, QListWidgetItem, QColorDialog, 
    QSpinBox, QMessageBox, QComboBox
)

# ==================== PATHS ====================
DB_PATH = "indicators/indicatorlist.db"
DB_FOLDER = os.path.dirname(DB_PATH)
DEFAULT_INDICATORS_PATH = "indicators/indicators_def.json"

if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# ==================== LOAD DEFAULT INDICATORS ====================
def load_default_indicators():
    if not os.path.exists(DEFAULT_INDICATORS_PATH):
        raise FileNotFoundError(
            f"{DEFAULT_INDICATORS_PATH} not found. "
            "Please create it with default indicator definitions."
        )
    with open(DEFAULT_INDICATORS_PATH, "r") as f:
        return json.load(f)

# ==================== DATABASE SETUP ====================
def setup_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tablo oluştur
    c.execute("""
        CREATE TABLE IF NOT EXISTS indicator_lists (
            id INTEGER PRIMARY KEY,
            session_id TEXT,
            indicator_name TEXT,
            indicator_type TEXT,
            params TEXT,
            color TEXT,
            line_thickness REAL,
            background_color TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    # list_name kolonunu ekle (eski DB varsa)
    c.execute("PRAGMA table_info(indicator_lists)")
    columns = [col[1] for col in c.fetchall()]
    if "list_name" not in columns:
        c.execute("ALTER TABLE indicator_lists ADD COLUMN list_name TEXT")
    conn.commit()
    conn.close()

# ==================== POPULATE DEFAULT INDICATORS ====================
def populate_default_indicators():
    indicators = load_default_indicators()
    return indicators

# ==================== LOAD / SAVE ====================
def load_saved_lists():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT session_id, list_name FROM indicator_lists WHERE list_name IS NOT NULL")
    rows = c.fetchall()
    conn.close()
    return [{"session_id": sid, "list_name": name} for sid, name in rows]

def load_indicator_list(session_id, list_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT indicator_name, indicator_type, params, color, line_thickness, background_color
        FROM indicator_lists WHERE session_id=? AND list_name=?
    """, (session_id, list_name))
    rows = c.fetchall()
    conn.close()
    result = []
    for name, typ, params, color, thickness, bg in rows:
        result.append({
            "name": name,
            "type": typ,
            "params": json.loads(params),
            "color": json.loads(color),
            "line_thickness": float(thickness),
            "background_color": json.loads(bg)
        })
    return result

def save_indicator_list(session_id, list_name, indicators):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    for ind in indicators:
        try:
            c.execute("""
                INSERT INTO indicator_lists 
                (session_id, list_name, indicator_name, indicator_type, params, color, line_thickness, background_color, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                session_id,
                list_name,
                ind["name"],
                ind["type"],
                json.dumps(ind["params"]),
                json.dumps(ind["color"]),
                ind["line_thickness"],
                json.dumps(ind["background_color"]),
                now,
                now
            ))
        except sqlite3.IntegrityError:
            c.execute("""
                UPDATE indicator_lists 
                SET params=?, color=?, line_thickness=?, background_color=?, updated_at=?
                WHERE session_id=? AND list_name=? AND indicator_name=?
            """, (
                json.dumps(ind["params"]),
                json.dumps(ind["color"]),
                ind["line_thickness"],
                json.dumps(ind["background_color"]),
                now,
                session_id,
                list_name,
                ind["name"]
            ))
    conn.commit()
    conn.close()

# ==================== GUI ====================
class IndicatorSetupGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Indicator Setup")
        self.setGeometry(100, 100, 900, 500)
        self.session_id = f"session{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.selected_color = [0,0,0]
        self.selected_bg = [255,255,255]
        self.default_indicators = populate_default_indicators()
        self.current_list = []

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # ---------- LEFT PANEL ----------
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Indicators"))

        self.indicator_list_widget = QListWidget()
        for ind in self.default_indicators:
            item = QListWidgetItem(ind["name"])
            self.indicator_list_widget.addItem(item)
        self.indicator_list_widget.currentItemChanged.connect(self.on_indicator_select)
        left_layout.addWidget(self.indicator_list_widget)

        # Params for selected indicator
        self.type_input = QLineEdit()
        self.param_input = QLineEdit()
        self.line_thickness_input = QSpinBox()
        self.line_thickness_input.setRange(1,10)
        self.color_btn = QPushButton("Select Line Color"); self.color_btn.clicked.connect(self.select_color)
        self.bg_btn = QPushButton("Select Background Color"); self.bg_btn.clicked.connect(self.select_bg_color)

        left_layout.addWidget(QLabel("Type:")); left_layout.addWidget(self.type_input)
        left_layout.addWidget(QLabel("Params (JSON):")); left_layout.addWidget(self.param_input)
        left_layout.addWidget(QLabel("Line Thickness:")); left_layout.addWidget(self.line_thickness_input)
        left_layout.addWidget(self.color_btn); left_layout.addWidget(self.bg_btn)

        self.add_to_list_btn = QPushButton("Add to Indicator List")
        self.add_to_list_btn.clicked.connect(self.add_to_current_list)
        left_layout.addWidget(self.add_to_list_btn)

        main_layout.addLayout(left_layout)

        # ---------- RIGHT PANEL ----------
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Indicator Lists"))

        self.saved_lists_combo = QComboBox()
        self.saved_lists_combo.addItem("-- Select Saved List --")
        self.refresh_saved_lists()
        self.saved_lists_combo.currentIndexChanged.connect(self.on_saved_list_select)
        right_layout.addWidget(self.saved_lists_combo)

        self.current_list_widget = QListWidget()
        right_layout.addWidget(self.current_list_widget)

        self.list_name_input = QLineEdit()
        self.list_name_input.setPlaceholderText("Enter List Name")
        right_layout.addWidget(self.list_name_input)

        self.save_list_btn = QPushButton("Save List")
        self.save_list_btn.clicked.connect(self.save_current_list)
        right_layout.addWidget(self.save_list_btn)

        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    # ---------- COLOR PICKERS ----------
    def select_color(self):
        from PyQt5.QtGui import QColor
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = [color.red(), color.green(), color.blue()]

    def select_bg_color(self):
        from PyQt5.QtGui import QColor
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_bg = [color.red(), color.green(), color.blue()]

    # ---------- LEFT PANEL ACTIONS ----------
    def on_indicator_select(self, current, previous):
        if current:
            name = current.text()
            ind = next((i for i in self.default_indicators if i["name"]==name), None)
            if ind:
                self.type_input.setText(ind["type"])
                self.param_input.setText(json.dumps(ind["params"]))
                self.line_thickness_input.setValue(int(ind["line_thickness"]))
                self.selected_color = ind["color"]
                self.selected_bg = ind["background_color"]

    def add_to_current_list(self):
        if not self.indicator_list_widget.currentItem():
            return
        name = self.indicator_list_widget.currentItem().text()
        typ = self.type_input.text()
        try:
            params = json.loads(self.param_input.text())
        except:
            QMessageBox.warning(self,"Error","Params must be valid JSON")
            return
        thickness = self.line_thickness_input.value()
        indicator = {
            "name": name,
            "type": typ,
            "params": params,
            "color": self.selected_color,
            "line_thickness": thickness,
            "background_color": self.selected_bg
        }
        if any(i["name"]==name for i in self.current_list):
            QMessageBox.warning(self,"Error","Indicator already in list")
            return
        self.current_list.append(indicator)
        self.refresh_current_list_widget()

    def refresh_current_list_widget(self):
        self.current_list_widget.clear()
        for ind in self.current_list:
            self.current_list_widget.addItem(ind["name"])

    # ---------- RIGHT PANEL ACTIONS ----------
    def refresh_saved_lists(self):
        self.saved_lists_combo.clear()
        self.saved_lists_combo.addItem("-- Select Saved List --")
        for lst in load_saved_lists():
            display_name = f"{lst['list_name']} ({lst['session_id']})"
            self.saved_lists_combo.addItem(display_name, (lst['session_id'], lst['list_name']))

    def on_saved_list_select(self,index):
        if index==0:
            self.current_list=[]
            self.refresh_current_list_widget()
            return
        data = self.saved_lists_combo.itemData(index)
        session_id, list_name = data
        self.current_list = load_indicator_list(session_id,list_name)
        self.refresh_current_list_widget()
        self.list_name_input.setText(list_name)

    def save_current_list(self):
        list_name = self.list_name_input.text().strip()
        if not list_name:
            QMessageBox.warning(self,"Error","List name cannot be empty")
            return
        save_indicator_list(self.session_id,list_name,self.current_list)
        QMessageBox.information(self,"Saved",f"List '{list_name}' saved successfully")
        self.refresh_saved_lists()

# ==================== MAIN ====================
if __name__=="__main__":
    setup_db()
    app = QApplication(sys.argv)
    gui = IndicatorSetupGUI()
    gui.show()
    sys.exit(app.exec_())


# Genel olarak çalışıyor ancak line273 session_id, list_name = data hatası var.
# \indicators\indicators_def.json dosyası içerisinden default indikatör bilgisi çekiyor. 
# Update ile yeni indikatör sadece yeni .json ile eklenebilir