"""
應用程式統一樣式表管理
提供美觀、柔和的現代化界面設計
"""

# 主要樣式表 - 柔和現代化設計
MAIN_STYLE = """
/* 主視窗和基礎樣式 */
QMainWindow, QDialog, QWidget {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f8f9fa, stop:1 #e9ecef);
    color: #495057;
    font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif;
    font-size: 13px;
    line-height: 1.4;
}

/* 按鈕樣式 */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4dabf7, stop:1 #339af0);
    border: 1px solid #74c0fc;
    color: white;
    padding: 10px 18px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    min-height: 16px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #339af0, stop:1 #228be6);
    border-color: #339af0;
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #228be6, stop:1 #1c7ed6);
    border-color: #228be6;
}

QPushButton:disabled {
    background: #e9ecef;
    border-color: #dee2e6;
    color: #adb5bd;
}

/* 按鈕變體 */
QPushButton[class="success"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #81c784, stop:1 #66bb6a);
    border-color: #4caf50;
}

QPushButton[class="success"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #66bb6a, stop:1 #4caf50);
    border-color: #388e3c;
}

QPushButton[class="danger"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ff8a80, stop:1 #ff5722);
    border-color: #ff7043;
}

QPushButton[class="danger"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ff5722, stop:1 #e64a19);
    border-color: #ff5722;
}

QPushButton[class="warning"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffb74d, stop:1 #ff9800);
    border-color: #ffb74d;
}

QPushButton[class="warning"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ff9800, stop:1 #f57c00);
    border-color: #ff9800;
}

/* 下拉選單樣式 */
QComboBox {
    background-color: white;
    border: 2px solid #e9ecef;
    padding: 8px 12px;
    border-radius: 8px;
    min-width: 140px;
    min-height: 20px;
    font-size: 14px;
}

QComboBox:focus {
    border-color: #74c0fc;
    background-color: #f8f9ff;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
    background: transparent;
}

QComboBox::down-arrow {
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 8px solid #74c0fc;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: white;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    selection-background-color: #e3f2fd;
    selection-color: #1565c0;
    padding: 4px;
}

QComboBox QAbstractItemView::item {
    padding: 8px 12px;
    border-radius: 4px;
    margin: 1px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #f0f8ff;
}

/* 列表樣式 */
QListWidget {
    background-color: white;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 8px;
    font-size: 14px;
}

QListWidget::item {
    padding: 10px 12px;
    border-radius: 6px;
    margin: 2px 0px;
    color: #495057;
}

QListWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #e3f2fd, stop:1 #bbdefb);
    color: #1565c0;
    border: 1px solid #90caf9;
}

QListWidget::item:hover {
    background-color: #f8f9ff;
    border: 1px solid #e3f2fd;
}

/* 表格樣式 */
QTableWidget {
    background-color: white;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    gridline-color: #f1f3f4;
    selection-background-color: #e3f2fd;
    selection-color: #1565c0;
    font-size: 14px;
}

QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #f1f3f4;
}

QTableWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #e3f2fd, stop:1 #bbdefb);
    color: #1565c0;
}

QTableWidget::item:hover {
    background-color: #f8f9ff;
}

QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f8f9fa, stop:1 #e9ecef);
    color: #495057;
    padding: 8px 12px;
    border: 1px solid #dee2e6;
    font-weight: 600;
    font-size: 13px;
}

/* 輸入框樣式 */
QLineEdit {
    background-color: white;
    border: 2px solid #e9ecef;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 14px;
    color: #495057;
}

QLineEdit:focus {
    border-color: #74c0fc;
    background-color: #f8f9ff;
}

QTextEdit {
    background-color: white;
    border: 2px solid #e9ecef;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 14px;
    color: #495057;
}

QTextEdit:focus {
    border-color: #74c0fc;
    background-color: #f8f9ff;
}

/* 標籤樣式 */
QLabel {
    color: #495057;
    font-size: 14px;
    padding: 2px;
}

QLabel[class="title"] {
    font-size: 18px;
    font-weight: 600;
    color: #343a40;
    padding: 8px 0px;
}

QLabel[class="subtitle"] {
    font-size: 16px;
    font-weight: 500;
    color: #6c757d;
    padding: 4px 0px;
}

QLabel[class="color-label"] {
    border: 2px solid #dee2e6;
    border-radius: 6px;
    min-width: 80px;
    min-height: 30px;
}

/* 群組框樣式 */
QGroupBox {
    font-weight: 600;
    border: 2px solid #dee2e6;
    border-radius: 12px;
    margin: 12px 4px;
    padding-top: 12px;
    background-color: rgba(255, 255, 255, 0.9);
    font-size: 15px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 4px 12px;
    color: #495057;
    background-color: white;
    border-radius: 6px;
    border: 1px solid #dee2e6;
}

/* 核取方塊樣式 */
QCheckBox {
    color: #495057;
    font-size: 14px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #dee2e6;
    border-radius: 4px;
    background-color: white;
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4dabf7, stop:1 #339af0);
    border-color: #339af0;
}

QCheckBox::indicator:hover {
    border-color: #74c0fc;
}

/* 單選按鈕樣式 */
QRadioButton {
    color: #495057;
    font-size: 14px;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #dee2e6;
    border-radius: 9px;
    background-color: white;
}

QRadioButton::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4dabf7, stop:1 #339af0);
    border-color: #339af0;
}

QRadioButton::indicator:hover {
    border-color: #74c0fc;
}

/* 進度條樣式 */
QProgressBar {
    background-color: #e9ecef;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    text-align: center;
    color: #495057;
    font-weight: 500;
    min-height: 20px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4dabf7, stop:1 #339af0);
    border-radius: 6px;
    margin: 2px;
}

/* 滑桿樣式 */
QSlider::groove:horizontal {
    border: 1px solid #dee2e6;
    height: 8px;
    background: #e9ecef;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4dabf7, stop:1 #339af0);
    border: 1px solid #74c0fc;
    width: 18px;
    margin: -6px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #339af0, stop:1 #228be6);
    border-color: #339af0;
}

/* 數字輸入框樣式 */
QSpinBox {
    background-color: white;
    border: 2px solid #e9ecef;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 14px;
    color: #495057;
}

QSpinBox:focus {
    border-color: #74c0fc;
    background-color: #f8f9ff;
}

/* 狀態列樣式 */
QStatusBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f8f9fa, stop:1 #e9ecef);
    border-top: 1px solid #dee2e6;
    padding: 4px;
    font-size: 13px;
}

QStatusBar QLabel {
    padding: 4px 8px;
    background-color: transparent;
    border-radius: 4px;
    margin: 0px 2px;
}

/* 工具列樣式 */
QToolBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
    border: 1px solid #dee2e6;
    spacing: 6px;
    padding: 8px;
    min-height: 48px;
    border-radius: 8px;
    margin: 2px;
}

QToolBar::separator {
    background-color: #dee2e6;
    width: 1px;
    margin: 8px 4px;
    border-radius: 1px;
}

QToolBar QAction {
    padding: 10px 16px;
    margin: 2px;
    border-radius: 8px;
    color: #495057;
    font-size: 14px;
    font-weight: 500;
}

QToolBar QAction:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f0f8ff, stop:1 #e3f2fd);
    color: #1565c0;
}

QToolBar QAction:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #bbdefb, stop:1 #90caf9);
    color: #0d47a1;
}

/* 分頁樣式 */
QTabWidget::pane {
    border: 2px solid #dee2e6;
    border-radius: 8px;
    background-color: white;
    margin-top: 4px;
}

QTabWidget::tab-bar {
    alignment: center;
}

QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f8f9fa, stop:1 #e9ecef);
    border: 2px solid #dee2e6;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    color: #6c757d;
    font-weight: 500;
    font-size: 13px;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
    border-bottom-color: white;
    color: #495057;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #e3f2fd, stop:1 #bbdefb);
    color: #1565c0;
}

/* 捲軸樣式 */
QScrollArea {
    background-color: white;
    border: 2px solid #e9ecef;
    border-radius: 8px;
}

QScrollBar:vertical {
    background: #f8f9fa;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #adb5bd;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #6c757d;
}

QScrollBar:horizontal {
    background: #f8f9fa;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: #adb5bd;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background: #6c757d;
}

/* 框架樣式 */
QFrame {
    background-color: transparent;
    border: 1px solid #dee2e6;
    border-radius: 6px;
}

QFrame[class="separator"] {
    background-color: #dee2e6;
    border: none;
    max-height: 1px;
    margin: 8px 0px;
}

/* 對話框按鈕 */
QDialogButtonBox QPushButton {
    min-width: 80px;
    padding: 8px 16px;
}

QDialogButtonBox QPushButton[text="OK"],
QDialogButtonBox QPushButton[text="確定"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #81c784, stop:1 #66bb6a);
    border-color: #4caf50;
}

QDialogButtonBox QPushButton[text="Cancel"],
QDialogButtonBox QPushButton[text="取消"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #e0e0e0, stop:1 #bdbdbd);
    border-color: #9e9e9e;
    color: #424242;
}
"""

# 深色主題樣式表（備用）
DARK_STYLE = """
QMainWindow, QDialog, QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
    font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif;
}

QPushButton {
    background-color: #404040;
    border: 1px solid #606060;
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #4a90e2;
    border-color: #5aa3f0;
}

QLineEdit, QTextEdit {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    color: white;
    padding: 6px;
    border-radius: 4px;
}

QLabel {
    color: #ffffff;
}
"""

def get_main_style():
    """取得主要樣式表"""
    return MAIN_STYLE

def get_dark_style():
    """取得深色樣式表"""
    return DARK_STYLE

def apply_button_class(button, class_name):
    """為按鈕應用特定的樣式類別"""
    button.setProperty("class", class_name)
    button.style().unpolish(button)
    button.style().polish(button)

def apply_label_class(label, class_name):
    """為標籤應用特定的樣式類別"""
    label.setProperty("class", class_name)
    label.style().unpolish(label)
    label.style().polish(label)
