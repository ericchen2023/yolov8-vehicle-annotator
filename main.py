

import sys
import os
import glob
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget,
    QHBoxLayout, QListWidget, QMessageBox, QComboBox, QProgressBar, QShortcut, 
    QSplitter, QFrame, QToolBar, QAction, QStatusBar, QGroupBox, QSlider, QSpinBox,
    QDialog, QDialogButtonBox, QCheckBox, QTextEdit, QTabWidget, QLineEdit, 
    QInputDialog, QListWidgetItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QPainter, QPen, QKeySequence, QIcon, QFont
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer

# 導入樣式表
from styles import get_main_style, apply_button_class

from annotator import AnnotatorLabel, VEHICLE_CLASSES
from advanced_exporter import AdvancedExporter
from file_manager import FileManager
from performance_optimizer import PerformanceOptimizer
from vehicle_class_manager import VehicleClassManager, VehicleClassManagerDialog

# AI輔助功能 (可選)
try:
    from ai_assistant import AIAssistant
    from ai_settings_dialog import AISettingsDialog
    from ai_prediction_dialog import PredictionResultDialog
    from model_selector_dialog import ModelSelectorDialog
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("AI輔助功能不可用，某些功能將被禁用")

# 模型訓練功能 (已移除)
# try:
#     from training_dialog import ModelTrainingDialog
#     from custom_model_trainer import TrainingConfig, DatasetPreparer, ModelTrainer
#     TRAINING_AVAILABLE = True
# except ImportError:
#     TRAINING_AVAILABLE = False
#     print("模型訓練功能不可用，某些功能將被禁用")

TRAINING_AVAILABLE = False
print("模型訓練功能已移除，專注於標註功能")

# 優化的柔和樣式表
MODERN_STYLE = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f8f9fa, stop:1 #e9ecef);
    color: #495057;
}

QWidget {
    background-color: #f8f9fa;
    color: #495057;
    font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif;
    font-size: 13px;
    line-height: 1.4;
}

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
    transform: translateY(-1px);
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

QLabel {
    color: #495057;
    font-size: 14px;
    padding: 2px;
}

QGroupBox {
    font-weight: 600;
    border: 2px solid #dee2e6;
    border-radius: 12px;
    margin: 12px 4px;
    padding-top: 12px;
    background-color: white;
    font-size: 15px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 4px 12px;
    color: #495057;
    background-color: white;
    border-radius: 6px;
}

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

QToolBar QAction:checked {
    background-color: #0078d4;
}

QToolBar QAction:disabled {
    color: #808080;
    background-color: transparent;
}

QSlider::groove:horizontal {
    border: 1px solid #3e3e42;
    height: 6px;
    background-color: #2d2d30;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #0078d4;
    border: 1px solid #005a9e;
    width: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background-color: #106ebe;
}

QSpinBox {
    background-color: #2d2d30;
    border: 1px solid #3e3e42;
    padding: 4px;
    border-radius: 4px;
    min-width: 60px;
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('YOLOv8 Vehicle Annotator - Professional Edition')
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)
        self.image_path = None
        self.image_list = []
        self.current_index = 0
        self.annotations_cache = {}  # 緩存每張圖片的標註 {image_path: annotations_list}
        
        # 初始化新模組
        self.advanced_exporter = AdvancedExporter()
        self.file_manager = FileManager()
        self.performance_optimizer = PerformanceOptimizer(os.getcwd())
        
        # 初始化車種管理器
        self.vehicle_class_manager = VehicleClassManager()
        self.current_vehicle_classes = self.vehicle_class_manager.get_classes_for_combo()
        
        # 初始化AI輔助功能 (如果可用)
        self.ai_assistant = None
        self.current_model_variant = 'm'  # 預設使用 medium 模型
        self.ai_settings = {
            'enabled': False,
            'confidence_threshold': 0.5,
            'iou_threshold': 0.45,
            'auto_optimize_bbox': True,
            'filter_overlapping': True,
            'model_path': f'yolov8{self.current_model_variant}.pt',
            'model_variant': self.current_model_variant,
            'use_custom_model': False,
            'batch_size': 1,
            'device': 'auto'
        }
        
        if AI_AVAILABLE:
            self.ai_assistant = AIAssistant()
            self.ai_assistant.set_vehicle_class_manager(self.vehicle_class_manager)
            self.ai_assistant.prediction_ready.connect(self.on_ai_prediction_ready)
            self.ai_assistant.status_updated.connect(self.on_ai_status_updated)
            
            # 嘗試初始化預設模型
            model_path = self.ai_settings['model_path']
            if self.ai_assistant.initialize(model_path):
                self.ai_settings['enabled'] = True
                self.statusBar().showMessage(f'AI功能已就緒，使用 YOLOv8{self.current_model_variant.upper()} 模型', 3000)
            else:
                self.statusBar().showMessage('AI模型未載入，請選擇模型', 3000)
        
        # 連接效能優化信號
        self.performance_optimizer.image_loader.image_loaded.connect(self.on_image_loaded_async)
        # 設定現代化樣式
        # 設定美觀的現代化樣式
        self.setStyleSheet(get_main_style())
        
        self.setup_ui()
        self.setup_shortcuts()
        self.setup_status_bar()
        self.setup_toolbar()

    def setup_toolbar(self):
        """設定專業工具列"""
        # 主工具列 - 檔案和基本操作
        main_toolbar = self.addToolBar('主要工具')
        main_toolbar.setMovable(False)
        main_toolbar.setFloatable(False)
        main_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        main_toolbar.setContextMenuPolicy(Qt.PreventContextMenu)  # 防止右鍵菜單
        
        # 檔案操作
        self.open_action = QAction('📁 載入圖片', self)
        self.open_action.setShortcut(QKeySequence.Open)  # 標準Ctrl+O
        self.open_action.setStatusTip('載入單張圖片 (Ctrl+O)')
        self.open_action.triggered.connect(self.load_image)
        main_toolbar.addAction(self.open_action)
        
        self.open_folder_action = QAction('📂 載入資料夾', self)
        self.open_folder_action.setShortcut(QKeySequence('Ctrl+Shift+O'))
        self.open_folder_action.setStatusTip('載入整個資料夾 (Ctrl+Shift+O)')
        self.open_folder_action.triggered.connect(self.load_folder)
        main_toolbar.addAction(self.open_folder_action)
        
        main_toolbar.addSeparator()
        
        # 導航控制
        self.prev_action = QAction('⬅ 上一張', self)
        self.prev_action.setShortcuts([QKeySequence('Left'), QKeySequence('A')])
        self.prev_action.setStatusTip('上一張圖片 (←, A)')
        self.prev_action.triggered.connect(self.prev_image)
        self.prev_action.setEnabled(False)
        main_toolbar.addAction(self.prev_action)
        
        self.next_action = QAction('➡ 下一張', self)
        self.next_action.setShortcuts([QKeySequence('Right'), QKeySequence('D')])
        self.next_action.setStatusTip('下一張圖片 (→, D)')
        self.next_action.triggered.connect(self.next_image)
        self.next_action.setEnabled(False)
        main_toolbar.addAction(self.next_action)
        
        main_toolbar.addSeparator()
        
        # 標註操作
        self.delete_selected_action = QAction('❌ 刪除選中', self)
        self.delete_selected_action.setShortcut(QKeySequence.Delete)
        self.delete_selected_action.setStatusTip('刪除選中標註 (Delete)')
        self.delete_selected_action.triggered.connect(self.delete_selected_annotation)
        self.delete_selected_action.setEnabled(False)
        main_toolbar.addAction(self.delete_selected_action)
        
        self.clear_action = QAction('🗑 清除所有', self)
        self.clear_action.setShortcut(QKeySequence('Ctrl+Delete'))
        self.clear_action.setStatusTip('清除所有標註 (Ctrl+Delete)')
        self.clear_action.triggered.connect(self.clear_rects)
        self.clear_action.setEnabled(False)
        main_toolbar.addAction(self.clear_action)
        self.delete_selected_action.setEnabled(False)
        main_toolbar.addAction(self.delete_selected_action)
        
        main_toolbar.addSeparator()
        
        # 匯出功能
        self.export_action = QAction('💾 匯出YOLO', self)
        self.export_action.setShortcut(QKeySequence.Save)  # 標準Ctrl+S
        self.export_action.setStatusTip('匯出當前圖片標註 (Ctrl+S)')
        self.export_action.triggered.connect(self.export_yolo)
        self.export_action.setEnabled(False)
        main_toolbar.addAction(self.export_action)
        
        self.export_all_action = QAction('📤 批次匯出', self)
        self.export_all_action.setShortcut(QKeySequence('Ctrl+Shift+S'))
        self.export_all_action.setStatusTip('批次匯出所有標註 (Ctrl+Shift+S)')
        self.export_all_action.triggered.connect(self.export_all)
        self.export_all_action.setEnabled(False)
        main_toolbar.addAction(self.export_all_action)
        
        self.advanced_export_action = QAction('🚀 進階匯出', self)
        self.advanced_export_action.setShortcut(QKeySequence('Ctrl+E'))
        self.advanced_export_action.setStatusTip('多格式進階匯出 (Ctrl+E)')
        self.advanced_export_action.triggered.connect(self.show_advanced_export_dialog)
        self.advanced_export_action.setEnabled(False)
        main_toolbar.addAction(self.advanced_export_action)
        
        # 第二工具列 - AI和專案管理
        ai_toolbar = self.addToolBar('AI 與專案管理')
        ai_toolbar.setMovable(False)
        ai_toolbar.setFloatable(False)
        ai_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        ai_toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        
        # AI輔助功能
        if AI_AVAILABLE:
            self.ai_predict_action = QAction('🤖 AI預測', self)
            self.ai_predict_action.setShortcut(QKeySequence('F5'))
            self.ai_predict_action.setStatusTip('AI自動標註當前圖片 (F5)')
            self.ai_predict_action.triggered.connect(self.ai_predict_current_image)
            self.ai_predict_action.setEnabled(False)
            ai_toolbar.addAction(self.ai_predict_action)
            
            self.ai_batch_action = QAction('🔄 批次AI', self)
            self.ai_batch_action.setShortcut(QKeySequence('Ctrl+F5'))
            self.ai_batch_action.setStatusTip('AI批次處理所有圖片 (Ctrl+F5)')
            self.ai_batch_action.triggered.connect(self.ai_predict_batch)
            self.ai_batch_action.setEnabled(False)
            ai_toolbar.addAction(self.ai_batch_action)
            
            ai_toolbar.addSeparator()
            
            self.model_select_action = QAction('🧠 選擇模型', self)
            self.model_select_action.setShortcut(QKeySequence('F4'))
            self.model_select_action.setStatusTip('選擇YOLOv8模型版本 (F4)')
            self.model_select_action.triggered.connect(self.show_model_selector)
            ai_toolbar.addAction(self.model_select_action)
            
            self.ai_settings_action = QAction('⚙ AI設定', self)
            self.ai_settings_action.setShortcut(QKeySequence('F6'))
            self.ai_settings_action.setStatusTip('AI參數設定 (F6)')
            self.ai_settings_action.triggered.connect(self.show_ai_settings)
            ai_toolbar.addAction(self.ai_settings_action)

            ai_toolbar.addSeparator()

        # 車種管理
        self.vehicle_class_action = QAction('🚗 車種管理', self)
        self.vehicle_class_action.setShortcut(QKeySequence('Ctrl+V'))
        self.vehicle_class_action.setStatusTip('管理車種類別 (Ctrl+V)')
        self.vehicle_class_action.triggered.connect(self.show_vehicle_class_manager)
        ai_toolbar.addAction(self.vehicle_class_action)
        
        ai_toolbar.addSeparator()
        
        # 專案管理
        self.recent_files_action = QAction('📋 最近檔案', self)
        self.recent_files_action.setShortcut(QKeySequence('Ctrl+H'))
        self.recent_files_action.setStatusTip('開啟最近使用的檔案 (Ctrl+H)')
        self.recent_files_action.triggered.connect(self.show_recent_files)
        ai_toolbar.addAction(self.recent_files_action)
        
        self.project_action = QAction('💼 專案管理', self)
        self.project_action.setShortcut(QKeySequence('Ctrl+P'))
        self.project_action.setStatusTip('專案管理與設定 (Ctrl+P)')
        self.project_action.triggered.connect(self.show_project_manager)
        ai_toolbar.addAction(self.project_action)
        
        ai_toolbar.addSeparator()
        
        # 系統工具
        self.cache_action = QAction('💾 快取管理', self)
        self.cache_action.setShortcut(QKeySequence('F7'))
        self.cache_action.setStatusTip('管理圖片快取 (F7)')
        self.cache_action.triggered.connect(self.manage_cache)
        ai_toolbar.addAction(self.cache_action)
        
        self.memory_action = QAction('🧠 記憶體監控', self)
        self.memory_action.setShortcut(QKeySequence('F8'))
        self.memory_action.setStatusTip('監控系統資源 (F8)')
        self.memory_action.triggered.connect(self.show_memory_monitor)
        ai_toolbar.addAction(self.memory_action)
        
        # 第三工具列 - 視圖控制
        view_toolbar = self.addToolBar('視圖控制')
        view_toolbar.setMovable(False)
        view_toolbar.setFloatable(False)
        view_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        view_toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        
        # 縮放控制
        self.zoom_in_action = QAction('🔍+ 放大', self)
        self.zoom_in_action.setShortcut(QKeySequence.ZoomIn)  # 標準Ctrl++
        self.zoom_in_action.setStatusTip('放大視圖 (Ctrl++)')
        self.zoom_in_action.triggered.connect(self.zoom_in)
        view_toolbar.addAction(self.zoom_in_action)
        
        self.zoom_out_action = QAction('🔍- 縮小', self)
        self.zoom_out_action.setShortcut(QKeySequence.ZoomOut)  # 標準Ctrl+-
        self.zoom_out_action.setStatusTip('縮小視圖 (Ctrl+-)')
        self.zoom_out_action.triggered.connect(self.zoom_out)
        view_toolbar.addAction(self.zoom_out_action)
        
        self.fit_action = QAction('📐 適應視窗', self)
        self.fit_action.setShortcut(QKeySequence('Ctrl+0'))
        self.fit_action.setStatusTip('適應視窗大小 (Ctrl+0)')
        self.fit_action.triggered.connect(self.fit_to_window)
        view_toolbar.addAction(self.fit_action)
        
        self.actual_action = QAction('1:1 實際大小', self)
        self.actual_action.setShortcut(QKeySequence('Ctrl+1'))
        self.actual_action.setStatusTip('顯示實際大小 (Ctrl+1)')
        self.actual_action.triggered.connect(self.actual_size)
        view_toolbar.addAction(self.actual_action)
        
        self.reset_view_action = QAction('🔄 重置視圖', self)
        self.reset_view_action.setShortcut(QKeySequence('Home'))
        self.reset_view_action.setStatusTip('重置視圖設定 (Home)')
        self.reset_view_action.triggered.connect(self.reset_view)
        view_toolbar.addAction(self.reset_view_action)
        
        # 分隔線
        view_toolbar.addSeparator()
        
        # 標籤顯示選項
        view_toolbar.addWidget(QLabel('標籤: '))
        
        # 顯示ID的checkbox
        self.show_ids_checkbox = QCheckBox('ID')
        self.show_ids_checkbox.setChecked(True)
        self.show_ids_checkbox.setStatusTip('顯示/隱藏標註框的ID編號')
        self.show_ids_checkbox.stateChanged.connect(self.toggle_show_ids)
        view_toolbar.addWidget(self.show_ids_checkbox)
        
        # 顯示分類的checkbox
        self.show_classes_checkbox = QCheckBox('分類')
        self.show_classes_checkbox.setChecked(True)
        self.show_classes_checkbox.setStatusTip('顯示/隱藏標註框的分類名稱')
        self.show_classes_checkbox.stateChanged.connect(self.toggle_show_classes)
        view_toolbar.addWidget(self.show_classes_checkbox)
        
        # 添加可伸縮空間，讓工具列更美觀
        # 添加可伸縮空間，讓工具列更美觀
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        view_toolbar.addWidget(spacer)

    def setup_status_bar(self):
        """設定狀態列"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.coord_label = QLabel('座標: -')
        self.scale_label = QLabel('縮放: 100%')
        self.image_size_label = QLabel('尺寸: -')
        
        # 效能狀態
        self.memory_label = QLabel('記憶體: -')
        self.cache_label = QLabel('快取: 0 項')
        
        self.status_bar.addWidget(self.coord_label)
        self.status_bar.addPermanentWidget(self.cache_label)
        self.status_bar.addPermanentWidget(self.memory_label)
        self.status_bar.addPermanentWidget(self.image_size_label)
        self.status_bar.addPermanentWidget(self.scale_label)
        
        # 啟動記憶體監控
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.update_memory_status)
        self.memory_timer.start(2000)  # 每2秒更新

    def setup_ui(self):
        """設定使用者介面"""
        # 中央 splitter
        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)
        
        # 左側面板
        self.left_panel = self.create_left_panel()
        main_splitter.addWidget(self.left_panel)
        
        # 圖片顯示區域
        self.annotator = AnnotatorLabel(self)
        self.annotator.rects_updated.connect(self.update_rect_list)
        self.annotator.rects_updated.connect(self.update_toolbar_states)  # 更新工具列狀態
        
        # 初始化車種顏色映射
        colors = self.vehicle_class_manager.get_class_colors()
        self.annotator.update_class_colors(colors)
        
        main_splitter.addWidget(self.annotator)
        
        # 右側面板
        self.right_panel = self.create_right_panel()
        main_splitter.addWidget(self.right_panel)
        
        # 設定分割比例
        main_splitter.setSizes([250, 800, 350])
        main_splitter.setStretchFactor(1, 1)  # 圖片區域可伸縮

    def create_left_panel(self):
        """建立左側控制面板"""
        left_widget = QWidget()
        left_widget.setFixedWidth(250)
        layout = QVBoxLayout(left_widget)
        
        # 檔案資訊群組
        file_group = QGroupBox("檔案資訊")
        file_layout = QVBoxLayout(file_group)
        
        self.image_info_label = QLabel('尚未載入圖片')
        self.image_info_label.setWordWrap(True)
        file_layout.addWidget(self.image_info_label)
        
        layout.addWidget(file_group)
        
        # 標註設定群組
        annotation_group = QGroupBox("標註設定")
        annotation_layout = QVBoxLayout(annotation_group)
        
        # 類別選擇
        class_label = QLabel('車種類型:')
        annotation_layout.addWidget(class_label)
        
        self.class_combo = QComboBox()
        self.update_class_combo()
        self.class_combo.currentIndexChanged.connect(self.change_class)
        annotation_layout.addWidget(self.class_combo)
        
        # 快捷鍵提示
        shortcuts_label = QLabel(
            "快捷鍵:\n"
            "• 1-4: 快速切換車種\n"
            "• A/D: 上/下一張圖片\n"
            "• Delete: 刪除選中標註\n"
            "• Ctrl+滑鼠拖拽: 平移\n"
            "• 滑鼠滾輪: 縮放"
        )
        shortcuts_label.setStyleSheet("color: #cccccc; font-size: 10px;")
        annotation_layout.addWidget(shortcuts_label)
        
        layout.addWidget(annotation_group)
        
        # 視圖控制群組
        view_group = QGroupBox("視圖控制")
        view_layout = QVBoxLayout(view_group)
        
        # 縮放控制
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("縮放:"))
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 500)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.zoom_changed)
        zoom_layout.addWidget(self.zoom_slider)
        
        self.zoom_spinbox = QSpinBox()
        self.zoom_spinbox.setRange(10, 500)
        self.zoom_spinbox.setValue(100)
        self.zoom_spinbox.setSuffix('%')
        self.zoom_spinbox.valueChanged.connect(self.zoom_value_changed)
        zoom_layout.addWidget(self.zoom_spinbox)
        
        view_layout.addLayout(zoom_layout)
        
        # 適應視窗按鈕
        fit_btn = QPushButton('🔍 適應視窗')
        fit_btn.clicked.connect(self.fit_to_window)
        view_layout.addWidget(fit_btn)
        
        # 實際大小按鈕
        actual_size_btn = QPushButton('1:1 實際大小')
        actual_size_btn.clicked.connect(self.actual_size)
        view_layout.addWidget(actual_size_btn)
        
        layout.addWidget(view_group)
        
        layout.addStretch()
        return left_widget

    def create_right_panel(self):
        """建立右側標註面板"""
        right_widget = QWidget()
        right_widget.setFixedWidth(350)
        layout = QVBoxLayout(right_widget)
        
        # 標註清單群組
        annotations_group = QGroupBox("標註清單")
        annotations_layout = QVBoxLayout(annotations_group)
        
        # 統計資訊
        self.stats_label = QLabel('統計: 尚無標註')
        self.stats_label.setStyleSheet("color: #4fc3f7; font-weight: bold;")
        annotations_layout.addWidget(self.stats_label)
        
        # 標註清單
        self.rect_list = QListWidget()
        self.rect_list.itemClicked.connect(self.delete_rect)
        self.rect_list.itemSelectionChanged.connect(self.on_list_selection_changed)
        annotations_layout.addWidget(self.rect_list)
        
        # 清單操作按鈕
        list_btn_layout = QHBoxLayout()
        select_all_btn = QPushButton('全選')
        select_all_btn.clicked.connect(self.select_all_annotations)
        clear_selection_btn = QPushButton('清除選擇')
        clear_selection_btn.clicked.connect(self.clear_selection)
        
        list_btn_layout.addWidget(select_all_btn)
        list_btn_layout.addWidget(clear_selection_btn)
        annotations_layout.addLayout(list_btn_layout)
        
        layout.addWidget(annotations_group)
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        return right_widget

    def zoom_changed(self, value):
        """縮放滑桿改變事件"""
        self.zoom_spinbox.blockSignals(True)
        self.zoom_spinbox.setValue(value)
        self.zoom_spinbox.blockSignals(False)
        
        if hasattr(self.annotator, 'scale_factor'):
            new_scale = value / 100.0
            self.annotator.scale_factor = new_scale
            self.annotator.update_scaled_image()
            self.annotator.repaint()
            self.update_scale_label()

    def zoom_value_changed(self, value):
        """縮放數值改變事件"""
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(value)
        self.zoom_slider.blockSignals(False)
        
        if hasattr(self.annotator, 'scale_factor'):
            new_scale = value / 100.0
            self.annotator.scale_factor = new_scale
            self.annotator.update_scaled_image()
            self.annotator.repaint()
            self.update_scale_label()

    def fit_to_window(self):
        """適應視窗大小"""
        if hasattr(self.annotator, 'fit_to_window'):
            self.annotator.fit_to_window()
            scale_percent = int(self.annotator.scale_factor * 100)
            self.zoom_slider.setValue(scale_percent)
            self.zoom_spinbox.setValue(scale_percent)
            self.update_scale_label()

    def actual_size(self):
        """設定為實際大小"""
        if hasattr(self.annotator, 'scale_factor'):
            self.annotator.scale_factor = 1.0
            self.annotator.image_offset = QPoint(0, 0)
            self.annotator.update_scaled_image()
            self.annotator.repaint()
            self.zoom_slider.setValue(100)
            self.zoom_spinbox.setValue(100)
            self.update_scale_label()

    def update_scale_label(self):
        """更新縮放標籤"""
        if hasattr(self.annotator, 'scale_factor'):
            scale_percent = int(self.annotator.scale_factor * 100)
            self.scale_label.setText(f'縮放: {scale_percent}%')

    def select_all_annotations(self):
        """選擇所有標註"""
        self.rect_list.selectAll()

    def clear_selection(self):
        """清除選擇"""
        self.rect_list.clearSelection()

    def on_list_selection_changed(self):
        """清單選擇改變事件"""
        selected_items = self.rect_list.selectedItems()
        if selected_items and hasattr(self.annotator, 'selected_rect_id'):
            # 獲取第一個選中項目的ID
            text = selected_items[0].text()
            try:
                rect_id = int(text.split(' ')[0].replace('ID:', ''))
                self.annotator.selected_rect_id = rect_id
                self.annotator.repaint()
            except:
                pass

    def setup_shortcuts(self):
        """設定完整快捷鍵系統"""
        # 註：工具列按鈕已包含快捷鍵，這裡是額外的快捷鍵補充
        
        # 圖片導航 - 額外快捷鍵
        QShortcut(QKeySequence('Space'), self, self.next_image)  # 空白鍵下一張
        QShortcut(QKeySequence('Shift+Space'), self, self.prev_image)  # Shift+空白鍵上一張
        QShortcut(QKeySequence('Up'), self, self.prev_image)  # 上箭頭
        QShortcut(QKeySequence('Down'), self, self.next_image)  # 下箭頭
        QShortcut(QKeySequence('Page_Up'), self, self.prev_image)  # Page Up
        QShortcut(QKeySequence('Page_Down'), self, self.next_image)  # Page Down
        
        # 標註操作額外快捷鍵
        QShortcut(QKeySequence('Ctrl+A'), self, self.select_all_annotations)  # 全選標註
        QShortcut(QKeySequence('Escape'), self, self.clear_selection)  # 清除選擇
        QShortcut(QKeySequence('Ctrl+Z'), self, self.undo_annotation)  # 撤銷 (如果實作)
        QShortcut(QKeySequence('Ctrl+Y'), self, self.redo_annotation)  # 重做 (如果實作)
        
        # 車種快速切換 - 數字鍵
        QShortcut(QKeySequence('1'), self, lambda: self.quick_change_class(0))
        QShortcut(QKeySequence('2'), self, lambda: self.quick_change_class(1))
        QShortcut(QKeySequence('3'), self, lambda: self.quick_change_class(2))
        QShortcut(QKeySequence('4'), self, lambda: self.quick_change_class(3))
        QShortcut(QKeySequence('5'), self, lambda: self.quick_change_class(4))
        QShortcut(QKeySequence('6'), self, lambda: self.quick_change_class(5))
        QShortcut(QKeySequence('7'), self, lambda: self.quick_change_class(6))
        QShortcut(QKeySequence('8'), self, lambda: self.quick_change_class(7))
        
        # 視圖控制額外快捷鍵
        QShortcut(QKeySequence('F'), self, self.fit_to_window)  # F鍵適應視窗
        QShortcut(QKeySequence('R'), self, self.reset_view)  # R鍵重置視圖
        QShortcut(QKeySequence('Ctrl+Shift+0'), self, self.reset_view)  # 完全重置
        
        # 功能快捷鍵
        QShortcut(QKeySequence('F9'), self, self.toggle_fullscreen)  # 全螢幕切換
        QShortcut(QKeySequence('F10'), self, self.toggle_annotations_visibility)  # 切換標註顯示
        QShortcut(QKeySequence('F11'), self, self.toggle_ui_visibility)  # 切換UI顯示
        QShortcut(QKeySequence('F12'), self, self.show_help_dialog)  # 顯示幫助
        
        # 匯出快捷鍵
        QShortcut(QKeySequence('Ctrl+Shift+E'), self, self.export_all)  # 快速全部匯出
        
        # 系統快捷鍵
        QShortcut(QKeySequence('Ctrl+Q'), self, self.close)  # 退出程式
        QShortcut(QKeySequence('Alt+F4'), self, self.close)  # Windows標準退出

    def reset_view(self):
        """重置視圖"""
        if hasattr(self.annotator, 'image') and self.annotator.image:
            self.annotator.scale_factor = 1.0
            self.annotator.image_offset = QPoint(0, 0)
            self.annotator.update_scaled_image()
            self.annotator.repaint()
            self.zoom_slider.setValue(100)
            self.zoom_spinbox.setValue(100)
            self.update_scale_label()

    def toggle_show_ids(self, state):
        """切換顯示ID"""
        show_ids = state == Qt.Checked
        self.annotator.set_show_ids(show_ids)
        status_msg = f"{'顯示' if show_ids else '隱藏'}標註框ID"
        self.statusBar().showMessage(status_msg, 2000)

    def toggle_show_classes(self, state):
        """切換顯示分類"""
        show_classes = state == Qt.Checked
        self.annotator.set_show_classes(show_classes)
        status_msg = f"{'顯示' if show_classes else '隱藏'}標註框分類"
        self.statusBar().showMessage(status_msg, 2000)

    def toggle_fullscreen(self):
        """切換全螢幕模式"""
        if self.isFullScreen():
            self.showNormal()
            self.statusBar().showMessage('退出全螢幕模式', 2000)
        else:
            self.showFullScreen()
            self.statusBar().showMessage('進入全螢幕模式 (按F9退出)', 3000)

    def toggle_annotations_visibility(self):
        """切換標註顯示/隱藏"""
        if hasattr(self.annotator, 'annotations_visible'):
            self.annotator.annotations_visible = not self.annotator.annotations_visible
            self.annotator.repaint()
            status = "顯示" if self.annotator.annotations_visible else "隱藏"
            self.statusBar().showMessage(f'{status}標註 (按F10切換)', 2000)
        else:
            # 如果annotator沒有此屬性，添加它
            self.annotator.annotations_visible = False
            self.annotator.repaint()
            self.statusBar().showMessage('隱藏標註 (按F10切換)', 2000)

    def toggle_ui_visibility(self):
        """切換UI面板顯示/隱藏"""
        # 切換左右面板的顯示狀態
        if hasattr(self, 'left_panel') and hasattr(self, 'right_panel'):
            visible = self.left_panel.isVisible()
            self.left_panel.setVisible(not visible)
            self.right_panel.setVisible(not visible)
            status = "隱藏" if visible else "顯示"
            self.statusBar().showMessage(f'{status}控制面板 (按F11切換)', 2000)

    def show_help_dialog(self):
        """顯示幫助對話框"""
        help_text = """
🚗 YOLOv8 車輛標註工具 - 快捷鍵指南

📁 檔案操作:
• Ctrl+O: 載入圖片
• Ctrl+Shift+O: 載入資料夾
• Ctrl+S: 匯出當前標註
• Ctrl+Shift+S: 批次匯出
• Ctrl+E: 進階匯出

🖱 導航操作:
• ←/→ 或 A/D: 上/下一張圖片
• Space: 下一張圖片
• Shift+Space: 上一張圖片
• Page Up/Down: 上/下一張圖片

🏷 標註操作:
• 1-8: 快速切換車種類型
• Delete: 刪除選中標註
• Ctrl+Delete: 清除所有標註
• Ctrl+A: 全選標註
• Escape: 清除選擇

🔍 視圖控制:
• Ctrl+0: 適應視窗
• Ctrl+1: 實際大小
• Ctrl++/-: 放大/縮小
• F: 適應視窗
• R: 重置視圖
• Home: 重置視圖

🤖 AI功能:
• F3: 自訂模型訓練
• F4: 選擇YOLOv8模型
• F5: AI預測當前圖片
• Ctrl+F5: AI批次處理
• F6: AI設定

🛠 系統功能:
• F7: 快取管理
• F8: 記憶體監控
• F9: 全螢幕切換
• F10: 切換標註顯示
• F11: 切換UI顯示
• F12: 顯示此幫助
• Ctrl+Q: 退出程式

📋 專案管理:
• Ctrl+H: 最近檔案
• Ctrl+P: 專案管理

        """
        
        QMessageBox.information(self, '快捷鍵指南', help_text)

    def undo_annotation(self):
        """撤銷標註 (預留功能)"""
        self.statusBar().showMessage('撤銷功能開發中...', 2000)

    def redo_annotation(self):
        """重做標註 (預留功能)"""
        self.statusBar().showMessage('重做功能開發中...', 2000)

    def update_toolbar_states(self):
        """更新工具列按鈕狀態"""
        has_image = bool(self.image_path)
        has_images = len(self.image_list) > 0
        has_annotations = bool(self.annotator.rects) if hasattr(self.annotator, 'rects') else False
        has_selected_annotation = bool(hasattr(self.annotator, 'selected_rect_id') and 
                                     getattr(self.annotator, 'selected_rect_id', None) is not None)
        
        # 更新按鈕啟用狀態
        if hasattr(self, 'clear_action'):
            self.clear_action.setEnabled(has_annotations)
        if hasattr(self, 'delete_selected_action'):
            # 刪除選中只在有選中標註時啟用，沒有選中時在有標註的情況下也可用
            self.delete_selected_action.setEnabled(has_annotations)
        if hasattr(self, 'export_action'):
            self.export_action.setEnabled(has_image and has_annotations)
        if hasattr(self, 'export_all_action'):
            self.export_all_action.setEnabled(has_images)
        if hasattr(self, 'advanced_export_action'):
            self.advanced_export_action.setEnabled(has_images)
        
        # AI功能狀態
        if AI_AVAILABLE:
            if hasattr(self, 'ai_predict_action'):
                self.ai_predict_action.setEnabled(has_image and self.ai_settings.get('enabled', False))
            if hasattr(self, 'ai_batch_action'):
                self.ai_batch_action.setEnabled(has_images and self.ai_settings.get('enabled', False))
        
        # 導航狀態
        self.update_navigation_buttons()

    def zoom_in(self):
        """放大"""
        current = self.zoom_slider.value()
        new_value = min(500, current + 10)
        self.zoom_slider.setValue(new_value)

    def zoom_out(self):
        """縮小"""
        current = self.zoom_slider.value()
        new_value = max(10, current - 10)
        self.zoom_slider.setValue(new_value)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '選擇圖片', './images', 
            'Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;All Files (*)'
        )
        if file_path:
            # 載入單張圖片時，檢查同資料夾的其他圖片
            folder_path = os.path.dirname(file_path)
            supported_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'}
            self.image_list = []
            
            # 載入同資料夾的所有圖片
            for filename in os.listdir(folder_path):
                full_path = os.path.join(folder_path, filename)
                if os.path.isfile(full_path):
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in supported_extensions:
                        self.image_list.append(full_path)
            
            self.image_list.sort()
            # 找到當前選中圖片的索引
            self.current_index = 0
            if file_path in self.image_list:
                self.current_index = self.image_list.index(file_path)
            
            self.load_current_image()
            # 記錄資料夾到最近檔案
            self.file_manager.add_recent_file(folder_path, 'folder')

    def load_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, '選擇圖片資料夾', './images')
        if folder_path:
            # 支援的圖片副檔名（不區分大小寫）
            supported_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'}
            self.image_list = []
            
            # 遍歷資料夾中的所有檔案
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    # 取得副檔名（轉為小寫）
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in supported_extensions:
                        self.image_list.append(file_path)
            
            self.image_list.sort()
            if self.image_list:
                self.current_index = 0
                self.load_current_image()
                # 記錄資料夾到最近檔案（而不是第一張圖片）
                self.file_manager.add_recent_file(folder_path, 'folder')
                QMessageBox.information(self, '載入成功', f'已載入 {len(self.image_list)} 張圖片')
            else:
                QMessageBox.warning(self, '警告', '資料夾中沒有找到支援的圖片檔案')

    def load_current_image(self):
        if self.image_list and 0 <= self.current_index < len(self.image_list):
            # 儲存當前圖片的標註到緩存
            if self.image_path and self.annotator.get_rects():
                self.annotations_cache[self.image_path] = self.annotator.get_rects().copy()
            
            # 載入新圖片
            self.image_path = self.image_list[self.current_index]
            
            # 檢查檔案是否存在
            if not os.path.exists(self.image_path):
                QMessageBox.warning(self, '檔案不存在', f'圖片檔案不存在: {self.image_path}')
                return
            
            try:
                self.annotator.set_image(self.image_path)
            except Exception as e:
                QMessageBox.critical(self, '載入錯誤', f'無法載入圖片: {str(e)}')
                return
            
            # 從緩存恢復標註
            if self.image_path in self.annotations_cache:
                self.annotator.rects = self.annotations_cache[self.image_path].copy()
                # 更新next_id為最大ID+1
                if self.annotator.rects:
                    max_id = max(item['id'] for item in self.annotator.rects)
                    self.annotator.next_id = max_id + 1
                self.annotator.repaint()
            
            self.update_rect_list()
            self.update_image_info()
            self.update_image_size_info()
            self.update_toolbar_states()  # 更新工具列狀態
            self.fit_to_window()

    def save_current_annotations(self):
        """儲存當前圖片的標註到緩存"""
        if self.image_path:
            self.annotations_cache[self.image_path] = self.annotator.get_rects().copy()

    def prev_image(self):
        if len(self.image_list) > 1 and self.current_index > 0:
            self.save_current_annotations()  # 儲存當前標註
            self.current_index -= 1
            self.load_current_image()

    def next_image(self):
        if len(self.image_list) > 1 and self.current_index < len(self.image_list) - 1:
            self.save_current_annotations()  # 儲存當前標註
            self.current_index += 1
            self.load_current_image()

    def update_navigation_buttons(self):
        """更新導航按鈕狀態"""
        has_prev = len(self.image_list) > 1 and self.current_index > 0
        has_next = len(self.image_list) > 1 and self.current_index < len(self.image_list) - 1
        
        if hasattr(self, 'prev_action'):
            self.prev_action.setEnabled(has_prev)
        if hasattr(self, 'next_action'):
            self.next_action.setEnabled(has_next)

    def update_image_info(self):
        """更新圖片資訊顯示"""
        if self.image_path and self.image_list:
            filename = os.path.basename(self.image_path)
            info = f'檔案: {filename}\n進度: {self.current_index + 1}/{len(self.image_list)}'
            if len(self.image_list) > 1:
                info += f'\n上一張: {os.path.basename(self.image_list[self.current_index-1]) if self.current_index > 0 else "無"}'
                info += f'\n下一張: {os.path.basename(self.image_list[self.current_index+1]) if self.current_index < len(self.image_list)-1 else "無"}'
            self.image_info_label.setText(info)
            self.update_navigation_buttons()  # 更新按鈕狀態
        else:
            self.image_info_label.setText('尚未載入圖片')
            if hasattr(self, 'prev_action'):
                self.prev_action.setEnabled(False)
            if hasattr(self, 'next_action'):
                self.next_action.setEnabled(False)

    def update_image_size_info(self):
        if hasattr(self.annotator, 'image') and self.annotator.image:
            size = self.annotator.image.size()
            self.image_size_label.setText(f'尺寸: {size.width()}×{size.height()}')
        else:
            self.image_size_label.setText('尺寸: -')

    def quick_change_class(self, class_index):
        if 0 <= class_index < len(self.current_vehicle_classes):
            self.class_combo.setCurrentIndex(class_index)

    def change_class(self, idx):
        if idx < len(self.current_vehicle_classes):
            class_name, class_id = self.current_vehicle_classes[idx]
            self.annotator.set_class(class_id, class_name)
    
    def update_class_combo(self):
        """更新車種下拉選單"""
        self.class_combo.clear()
        self.current_vehicle_classes = self.vehicle_class_manager.get_classes_for_combo()
        
        for name, class_id in self.current_vehicle_classes:
            # 取得車種物件以獲取表情符號
            vehicle_class = self.vehicle_class_manager.get_class(class_id)
            if vehicle_class:
                display_name = f"{vehicle_class.emoji} {name}"
                self.class_combo.addItem(display_name, class_id)
            else:
                self.class_combo.addItem(name, class_id)
        
        # 更新 annotator 的顏色映射（如果已經初始化）
        if hasattr(self, 'annotator') and hasattr(self.annotator, 'update_class_colors'):
            colors = self.vehicle_class_manager.get_class_colors()
            self.annotator.update_class_colors(colors)
    
    def show_vehicle_class_manager(self):
        """顯示車種管理對話框"""
        dialog = VehicleClassManagerDialog(self.vehicle_class_manager, self)
        dialog.classes_updated.connect(self.on_vehicle_classes_updated)
        dialog.exec_()
    
    def on_vehicle_classes_updated(self):
        """車種類別更新時的回調函數"""
        # 更新下拉選單
        self.update_class_combo()
        
        # 更新 annotator 的顏色映射（如果已經初始化）
        if hasattr(self, 'annotator') and hasattr(self.annotator, 'update_class_colors'):
            colors = self.vehicle_class_manager.get_class_colors()
            self.annotator.update_class_colors(colors)
        
        # 匯出更新的 classes.txt
        self.vehicle_class_manager.export_classes_txt('classes.txt')
        
        # 更新快捷鍵（如果需要）
        self.update_class_shortcuts()
        
        self.statusBar().showMessage('車種類別已更新', 3000)
    
    def update_class_shortcuts(self):
        """更新車種快捷鍵"""
        # 移除舊的快捷鍵
        for i in range(10):  # 支援0-9的快捷鍵
            shortcut_key = str(i) if i > 0 else "0"
            shortcuts = [s for s in self.findChildren(QShortcut) 
                        if s.key().toString() == shortcut_key]
            for shortcut in shortcuts:
                shortcut.deleteLater()
        
        # 添加新的快捷鍵
        classes = self.vehicle_class_manager.get_all_classes(enabled_only=True)
        for vehicle_class in classes:
            if vehicle_class.shortcut_key and vehicle_class.shortcut_key.isdigit():
                index = None
                for i, (name, class_id) in enumerate(self.current_vehicle_classes):
                    if class_id == vehicle_class.class_id:
                        index = i
                        break
                
                if index is not None:
                    shortcut = QShortcut(QKeySequence(vehicle_class.shortcut_key), self)
                    shortcut.activated.connect(lambda idx=index: self.quick_change_class(idx))

    def delete_selected_annotation(self):
        """刪除選中的標註"""
        # 優先處理標註器中的選中標註
        if hasattr(self.annotator, 'delete_selected_rect') and callable(self.annotator.delete_selected_rect):
            result = self.annotator.delete_selected_rect()
            if result:  # 如果成功刪除，更新狀態
                self.update_rect_list()
                self.update_toolbar_states()
                return
        
        # 如果標註器沒有選中的，嘗試從清單刪除當前選中項
        current_item = self.rect_list.currentItem()
        if current_item:
            self.delete_rect(current_item)
            return
            
        # 如果沒有選中的標註，顯示提示
        if hasattr(self.annotator, 'rects') and self.annotator.rects:
            self.statusBar().showMessage('請先選擇要刪除的標註', 2000)
        else:
            self.statusBar().showMessage('沒有標註可刪除', 2000)

    def clear_rects(self):
        self.annotator.clear_rects()
        self.update_rect_list()
    
    def on_image_loaded_async(self, image_path, qimage):
        """異步圖片載入完成的回調"""
        try:
            self.image_path = image_path
            self.annotator.set_image(qimage, image_path)
            
            # 恢復該圖片的標註從快取
            if image_path in self.annotations_cache:
                self.annotator.rects = self.annotations_cache[image_path].copy()
                # 更新next_id為最大ID+1
                if self.annotator.rects:
                    max_id = max(item['id'] for item in self.annotator.rects)
                    self.annotator.next_id = max_id + 1
                self.annotator.repaint()
            
            # 更新UI
            self.update_rect_list()
            self.update_image_info()
            self.update_image_size_info()
            self.fit_to_window()
            
        except Exception as e:
            print(f"異步載入圖片失敗: {e}")
            QMessageBox.critical(self, '錯誤', f'載入圖片失敗: {str(e)}')
    
    def update_memory_status(self):
        """更新記憶體狀態"""
        try:
            memory_info = self.performance_optimizer.get_memory_info()
            memory_text = f"記憶體: {memory_info['process']['memory']:.0f} MB"
            self.memory_label.setText(memory_text)
        except:
            # 如果獲取記憶體資訊失敗，顯示默認值
            self.memory_label.setText("記憶體: - MB")

    def manage_cache(self):
        """管理圖片快取"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QListWidget
        
        dialog = QDialog(self)
        dialog.setWindowTitle('快取管理')
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 快取統計
        cache_info = self.performance_optimizer.get_cache_info()
        info_label = QLabel(f"快取項目: {cache_info['size']} 項\n記憶體使用: {cache_info['memory_usage']:.1f} MB")
        layout.addWidget(info_label)
        
        # 快取項目列表
        cache_list = QListWidget()
        for item in cache_info['items']:
            cache_list.addItem(f"{os.path.basename(item['path'])} - {item['size']:.1f} MB")
        layout.addWidget(cache_list)
        
        # 按鈕
        buttons_layout = QHBoxLayout()
        clear_button = QPushButton('清除快取')
        optimize_button = QPushButton('優化快取')
        close_button = QPushButton('關閉')
        
        def clear_cache():
            self.performance_optimizer.clear_cache()
            cache_size = self.performance_optimizer.get_cache_size()
            self.cache_label.setText(f'快取: {cache_size} 項')
            QMessageBox.information(self, '成功', '快取已清除')
            dialog.close()
        
        def optimize_cache():
            self.performance_optimizer.optimize_cache()
            QMessageBox.information(self, '成功', '快取已優化')
            dialog.close()
        
        clear_button.clicked.connect(clear_cache)
        optimize_button.clicked.connect(optimize_cache)
        close_button.clicked.connect(dialog.close)
        
        buttons_layout.addWidget(clear_button)
        buttons_layout.addWidget(optimize_button)
        buttons_layout.addWidget(close_button)
        layout.addLayout(buttons_layout)
        
        dialog.exec_()
    
    def show_memory_monitor(self):
        """顯示記憶體監控"""
        memory_info = self.performance_optimizer.get_memory_info()
        
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar
        
        dialog = QDialog(self)
        dialog.setWindowTitle('記憶體監控')
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # 系統記憶體
        system_label = QLabel(f"系統記憶體: {memory_info['system']['used']:.1f} GB / {memory_info['system']['total']:.1f} GB")
        layout.addWidget(system_label)
        
        system_bar = QProgressBar()
        system_bar.setMaximum(100)
        system_bar.setValue(int(memory_info['system']['percent']))
        layout.addWidget(system_bar)
        
        # 關閉按鈕
        close_button = QPushButton('關閉')
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        dialog.exec_()

    def update_rect_list(self):
        self.rect_list.clear()
        annotations = self.annotator.get_rects()
        
        for item in annotations:
            rect = item['rect']
            class_id = item['class_id']
            class_name = item['class_name']
            
            # 取得車種的表情符號
            vehicle_class = self.vehicle_class_manager.get_class(class_id)
            emoji = vehicle_class.emoji if vehicle_class else '🚗'
            
            list_text = f"ID:{item['id']} {emoji} {class_name} ({rect.x()}, {rect.y()}, {rect.width()}×{rect.height()})"
            self.rect_list.addItem(list_text)
        
        # 更新統計資訊
        if annotations:
            class_counts = {}
            for item in annotations:
                class_id = item['class_id']
                class_name = item['class_name']
                class_counts[class_id] = class_counts.get(class_id, 0) + 1
            
            stats_parts = []
            for class_id, count in class_counts.items():
                vehicle_class = self.vehicle_class_manager.get_class(class_id)
                emoji = vehicle_class.emoji if vehicle_class else '🚗'
                stats_parts.append(f'{emoji}{count}')
            
            stats_text = f'統計: {" | ".join(stats_parts)} (總計: {len(annotations)})'
            self.stats_label.setText(stats_text)
        else:
            self.stats_label.setText('統計: 尚無標註')

    def delete_rect(self, item):
        text = item.text()
        try:
            rect_id = int(text.split(' ')[0].replace('ID:', ''))
            self.annotator.delete_rect_by_id(rect_id)
            self.update_rect_list()
        except:
            pass

    def export_yolo(self):
        if not self.image_path or not self.annotator.get_rects():
            QMessageBox.warning(self, '警告', '請先載入圖片並標註至少一個車輛！')
            return
        
        try:
            # 確保exports/yolo目錄存在
            output_dir = os.path.join('exports', 'yolo')
            os.makedirs(output_dir, exist_ok=True)
            
            # 轉換標註格式
            annotations = []
            for rect_data in self.annotator.get_rects():
                if hasattr(rect_data, 'get'):  # 字典格式
                    if 'rect' in rect_data and 'class_id' in rect_data:
                        qrect = rect_data['rect']
                        annotations.append({
                            'class': rect_data['class_id'],
                            'bbox': [qrect.x(), qrect.y(), qrect.width(), qrect.height()]
                        })
                    elif 'class' in rect_data and 'x' in rect_data:
                        annotations.append({
                            'class': rect_data['class'],
                            'bbox': [rect_data['x'], rect_data['y'], rect_data['width'], rect_data['height']]
                        })
            
            if not annotations:
                QMessageBox.warning(self, '警告', '沒有找到有效的標註資料！')
                return
            
            exporter = AdvancedExporter()
            success = exporter.export_yolo(
                self.image_path, 
                annotations, 
                output_dir
            )
            
            # 同時匯出類別檔案
            classes_success = exporter.export_classes_file(output_dir)
            classes_path = os.path.join(output_dir, 'classes.txt')
            
            if success and classes_success:
                base_name = os.path.splitext(os.path.basename(self.image_path))[0]
                label_file = os.path.join(output_dir, f'{base_name}.txt')
                QMessageBox.information(
                    self, '匯出成功', 
                    f'標註已匯出至: {label_file}\n類別檔案: {classes_path}\n\n'
                    f'標註數量: {len(annotations)}'
                )
            else:
                QMessageBox.warning(self, '匯出警告', '部分檔案匯出失敗，請檢查控制台輸出')
        except Exception as e:
            QMessageBox.critical(self, '匯出失敗', f'匯出過程發生錯誤：{str(e)}')

    def export_all(self):
        if not self.image_list:
            QMessageBox.warning(self, '警告', '請先載入圖片！')
            return
        
        # 儲存當前標註
        self.save_current_annotations()
        
        reply = QMessageBox.question(
            self, '批次匯出', 
            f'確定要匯出所有 {len(self.image_list)} 張圖片的標註嗎？\n'
            '（只會匯出有標註的圖片）', 
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        # 確保exports/yolo目錄存在
        output_dir = os.path.join('exports', 'yolo')
        os.makedirs(output_dir, exist_ok=True)
        
        # 顯示進度條
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.image_list))
        
        exported_count = 0
        total_annotations = 0
        
        try:
            for i, image_path in enumerate(self.image_list):
                self.progress_bar.setValue(i + 1)
                QApplication.processEvents()
                
                # 從緩存獲取標註
                annotations_raw = self.annotations_cache.get(image_path, [])
                if annotations_raw:
                    try:
                        # 轉換標註格式
                        annotations = []
                        for rect_data in annotations_raw:
                            if hasattr(rect_data, 'get'):  # 字典格式
                                if 'rect' in rect_data and 'class_id' in rect_data:
                                    qrect = rect_data['rect']
                                    annotations.append({
                                        'class': rect_data['class_id'],
                                        'bbox': [qrect.x(), qrect.y(), qrect.width(), qrect.height()]
                                    })
                                elif 'class' in rect_data and 'x' in rect_data:
                                    annotations.append({
                                        'class': rect_data['class'],
                                        'bbox': [rect_data['x'], rect_data['y'], rect_data['width'], rect_data['height']]
                                    })
                        
                        if annotations:
                            exporter = AdvancedExporter()
                            success = exporter.export_yolo(image_path, annotations, output_dir)
                            if success:
                                exported_count += 1
                                total_annotations += len(annotations)
                    except Exception as e:
                        print(f"匯出 {image_path} 時發生錯誤: {e}")
                        continue
            
            # 匯出類別檔案
            exporter = AdvancedExporter()
            classes_success = exporter.export_classes_file(output_dir)
            
        finally:
            self.progress_bar.setVisible(False)
            
        classes_path = os.path.join(output_dir, 'classes.txt')
        QMessageBox.information(
            self, '批次匯出完成', 
            f'已匯出 {exported_count} 個標註檔案\n'
            f'總標註數量: {total_annotations}\n'
            f'輸出目錄: {output_dir}\n'
            f'類別檔案: {classes_path}'
        )
    
    def show_advanced_export_dialog(self):
        """顯示進階匯出對話框"""
        dialog = AdvancedExportDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            formats = dialog.get_selected_formats()
            output_dir = dialog.get_output_directory()
            if formats and output_dir:
                self.perform_advanced_export(formats, output_dir)
    
    def perform_advanced_export(self, formats, output_dir):
        """執行進階匯出"""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # 先保存當前圖片的標註
            self.save_current_annotations()
            
            # 準備圖片資料
            images_data = []
            for image_path in self.image_list:
                annotations = self.annotations_cache.get(image_path, [])
                if annotations:
                    # 轉換標註格式
                    formatted_annotations = []
                    for rect in annotations:
                        # 檢查標註資料格式
                        if 'rect' in rect and 'class_id' in rect:
                            # annotator.py格式：{'id': int, 'rect': QRect, 'class_id': int, 'class_name': str}
                            qrect = rect['rect']
                            formatted_annotations.append({
                                'class': rect['class_id'],
                                'bbox': [qrect.x(), qrect.y(), qrect.width(), qrect.height()]
                            })
                        elif 'class' in rect and 'x' in rect:
                            # 已經是正確格式
                            formatted_annotations.append({
                                'class': rect['class'],
                                'bbox': [rect['x'], rect['y'], rect['width'], rect['height']]
                            })
                    
                    if formatted_annotations:  # 只添加有標註的圖片
                        images_data.append({
                            'path': image_path,
                            'annotations': formatted_annotations
                        })
            
            if not images_data:
                QMessageBox.warning(self, '警告', '沒有找到可匯出的標註資料')
                return
            
            # 執行批次匯出
            results = self.advanced_exporter.batch_export(images_data, output_dir, formats)
            
            # 顯示結果
            self.show_export_results(results, output_dir)
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"進階匯出錯誤詳細資訊: {error_detail}")
            QMessageBox.critical(self, '匯出錯誤', f'進階匯出失敗: {str(e)}\n\n詳細錯誤請查看控制台輸出。')
        finally:
            self.progress_bar.setVisible(False)
    
    def show_export_results(self, results, output_dir):
        """顯示匯出結果"""
        dialog = ExportResultsDialog(results, output_dir, self)
        dialog.exec_()
    
    def show_recent_files(self):
        """顯示最近檔案"""
        dialog = RecentFilesDialog(self.file_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_file = dialog.get_selected_file()
            if selected_file:
                file_type = selected_file.get('type', 'image')
                file_path = selected_file['path']
                
                if not os.path.exists(file_path):
                    QMessageBox.warning(self, '檔案不存在', f'路徑不存在: {file_path}')
                    # 從最近檔案中移除不存在的檔案
                    self.file_manager.recent_files = [f for f in self.file_manager.recent_files if f['path'] != file_path]
                    self.file_manager.save_recent_files()
                    return
                
                if file_type == 'project':
                    self.load_project_file(file_path)
                elif file_type == 'folder':
                    # 載入資料夾中的所有圖片
                    self.load_folder_from_path(file_path)
                else:
                    # 載入單張圖片（但實際載入整個資料夾）
                    if os.path.isfile(file_path):
                        folder_path = os.path.dirname(file_path)
                        self.load_folder_from_path(folder_path, selected_file=file_path)
                    else:
                        QMessageBox.warning(self, '檔案錯誤', f'不是有效的圖片檔案: {file_path}')
    
    def load_folder_from_path(self, folder_path, selected_file=None):
        """從指定路徑載入資料夾中的所有圖片"""
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            QMessageBox.warning(self, '資料夾不存在', f'資料夾不存在: {folder_path}')
            return
        
        # 支援的圖片副檔名（不區分大小寫）
        supported_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'}
        self.image_list = []
        
        # 遍歷資料夾中的所有檔案
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                # 取得副檔名（轉為小寫）
                ext = os.path.splitext(filename)[1].lower()
                if ext in supported_extensions:
                    self.image_list.append(file_path)
        
        self.image_list.sort()
        if self.image_list:
            # 如果指定了特定檔案，設定為當前檔案
            self.current_index = 0
            if selected_file and selected_file in self.image_list:
                self.current_index = self.image_list.index(selected_file)
            
            self.load_current_image()
            QMessageBox.information(self, '載入成功', f'已載入 {len(self.image_list)} 張圖片')
        else:
            QMessageBox.warning(self, '警告', '資料夾中沒有找到支援的圖片檔案')
    
    def show_project_manager(self):
        """顯示專案管理器"""
        dialog = ProjectManagerDialog(self.file_manager, self)
        dialog.exec_()
    
    def load_project_file(self, project_path):
        """載入專案檔案"""
        project_data = self.file_manager.load_project(project_path)
        if project_data:
            # 載入專案設定
            self.image_list = project_data.get('images', [])
            self.annotations_cache = project_data.get('annotations', {})
            
            if self.image_list:
                self.current_index = 0
                self.load_current_image()
                QMessageBox.information(self, '專案載入', f'成功載入專案: {project_data.get("project_name", "未命名")}')
            else:
                QMessageBox.warning(self, '警告', '專案中沒有圖片檔案')
        else:
            QMessageBox.critical(self, '錯誤', '載入專案檔案失敗')
    
    def save_current_project(self):
        """保存當前專案"""
        if not self.image_list:
            QMessageBox.warning(self, '警告', '沒有可保存的專案內容')
            return
        
        project_name, ok = QInputDialog.getText(self, '保存專案', '請輸入專案名稱:')
        if ok and project_name:
            project_data = {
                'settings': {},
                'images': self.image_list,
                'annotations': self.annotations_cache,
                'statistics': self.get_project_statistics()
            }
            
            project_path = self.file_manager.create_project(project_name, project_data)
            if project_path:
                QMessageBox.information(self, '保存成功', f'專案已保存: {project_path}')
            else:
                QMessageBox.critical(self, '保存失敗', '無法保存專案檔案')
    
    def get_project_statistics(self):
        """取得專案統計資訊"""
        total_images = len(self.image_list)
        total_annotations = sum(len(anns) for anns in self.annotations_cache.values())
        
        # 統計各類別數量
        class_counts = {}
        for annotations in self.annotations_cache.values():
            for ann in annotations:
                class_id = ann['class']
                class_counts[class_id] = class_counts.get(class_id, 0) + 1
        
        return {
            'total_images': total_images,
            'total_annotations': total_annotations,
            'class_counts': class_counts,
            'last_updated': datetime.now().isoformat()
        }
    
    def show_model_selector(self):
        """顯示模型選擇對話框"""
        if not AI_AVAILABLE:
            QMessageBox.warning(
                self, '功能不可用',
                'AI功能不可用，請先安裝 ultralytics 套件。\n\n'
                '安裝命令: pip install ultralytics'
            )
            return
        
        dialog = ModelSelectorDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            selected_model = dialog.get_selected_model()
            model_path = dialog.get_model_path()
            
            if selected_model and model_path:
                # 更新AI設定
                self.current_model_variant = selected_model
                self.ai_settings['model_variant'] = selected_model
                self.ai_settings['model_path'] = model_path
                
                # 重新初始化AI助手
                if self.ai_assistant:
                    success = self.ai_assistant.initialize(model_path)
                    if success:
                        self.ai_settings['enabled'] = True
                        self.statusBar().showMessage(
                            f'已切換至 YOLOv8{selected_model.upper()} 模型', 3000
                        )
                        
                        # 更新AI功能按鈕狀態
                        self.update_ai_button_states()
                        
                        # 顯示模型資訊
                        model_info = dialog.MODEL_INFO[selected_model]
                        QMessageBox.information(
                            self, '模型切換成功',
                            f'✅ 已成功切換至 YOLOv8{selected_model.upper()} 模型\n\n'
                            f'📋 模型名稱: {model_info["name"]}\n'
                            f'📦 檔案大小: {model_info["size"]}\n'
                            f'⚡ 執行速度: {model_info["speed"]}\n'
                            f'🎯 檢測精確度: {model_info["accuracy"]}\n'
                            f'🧠 記憶體需求: {model_info["memory"]}\n\n'
                            f'💡 適用場景: {model_info["use_case"]}'
                        )
                    else:
                        QMessageBox.critical(
                            self, '模型載入失敗',
                            f'❌ 無法載入 YOLOv8{selected_model.upper()} 模型\n\n'
                            '可能原因:\n'
                            '• 模型檔案損壞或不完整\n'
                            '• 記憶體不足\n'
                            '• CUDA 驅動問題\n\n'
                            '建議: 嘗試重新下載模型或選擇較小的模型版本'
                        )
                else:
                    # 如果AI助手未初始化，先初始化
                    if AI_AVAILABLE:
                        from ai_assistant import AIAssistant
                        self.ai_assistant = AIAssistant()
                        self.ai_assistant.set_vehicle_class_manager(self.vehicle_class_manager)
                        self.ai_assistant.prediction_ready.connect(self.on_ai_prediction_ready)
                        self.ai_assistant.status_updated.connect(self.on_ai_status_updated)
                        
                        success = self.ai_assistant.initialize(model_path)
                        if success:
                            self.ai_settings['enabled'] = True
                            self.statusBar().showMessage(
                                f'AI功能已啟用，使用 YOLOv8{selected_model.upper()} 模型', 3000
                            )
                            self.update_ai_button_states()
                        else:
                            QMessageBox.critical(
                                self, '初始化失敗',
                                '❌ AI功能初始化失敗\n\n'
                                '請檢查:\n'
                                '• 模型檔案是否存在\n'
                                '• 是否有足夠記憶體\n'
                                '• ultralytics 套件是否正確安裝'
                            )
    
    def update_ai_button_states(self):
        """更新AI功能按鈕狀態"""
        has_image = bool(self.image_path)
        has_images = len(self.image_list) > 0
        ai_enabled = self.ai_settings.get('enabled', False)
        
        if hasattr(self, 'ai_predict_action'):
            self.ai_predict_action.setEnabled(has_image and ai_enabled)
        if hasattr(self, 'ai_batch_action'):
            self.ai_batch_action.setEnabled(has_images and ai_enabled)
    
    def get_current_model_info(self):
        """獲取當前模型資訊"""
        return {
            'variant': self.current_model_variant,
            'path': self.ai_settings.get('model_path', ''),
            'enabled': self.ai_settings.get('enabled', False)
        }


# 對話框類別定義
class AdvancedExportDialog(QDialog):
    """進階匯出對話框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('進階匯出設定')
        self.setFixedSize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 匯出格式選擇
        format_group = QGroupBox('選擇匯出格式')
        format_layout = QVBoxLayout(format_group)
        
        self.yolo_cb = QCheckBox('YOLO (YOLOv8標準格式)')
        self.yolo_cb.setChecked(True)
        self.coco_cb = QCheckBox('COCO (通用物件偵測格式)')
        self.pascal_cb = QCheckBox('Pascal VOC (XML格式)')
        self.json_cb = QCheckBox('JSON (自訂格式)')
        
        format_layout.addWidget(self.yolo_cb)
        format_layout.addWidget(self.coco_cb)
        format_layout.addWidget(self.pascal_cb)
        format_layout.addWidget(self.json_cb)
        
        layout.addWidget(format_group)
        
        # 輸出目錄選擇
        dir_group = QGroupBox('輸出目錄')
        dir_layout = QHBoxLayout(dir_group)
        
        self.dir_line = QLineEdit('./exports')
        self.dir_button = QPushButton('瀏覽...')
        self.dir_button.clicked.connect(self.select_directory)
        
        dir_layout.addWidget(self.dir_line)
        dir_layout.addWidget(self.dir_button)
        
        layout.addWidget(dir_group)
        
        # 說明文字
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(100)
        info_text.setText(
            "• YOLO: 適用於YOLOv8訓練的標準格式\n"
            "• COCO: 通用的物件偵測標註格式\n"
            "• Pascal VOC: XML格式，適用於多種框架\n"
            "• JSON: 包含完整資訊的自訂格式"
        )
        layout.addWidget(info_text)
        
        # 按鈕
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, '選擇輸出目錄')
        if dir_path:
            self.dir_line.setText(dir_path)
    
    def get_selected_formats(self):
        formats = []
        if self.yolo_cb.isChecked():
            formats.append('YOLO')
        if self.coco_cb.isChecked():
            formats.append('COCO')
        if self.pascal_cb.isChecked():
            formats.append('Pascal VOC')
        if self.json_cb.isChecked():
            formats.append('JSON')
        return formats
    
    def get_output_directory(self):
        return self.dir_line.text()


class ExportResultsDialog(QDialog):
    """匯出結果對話框"""
    
    def __init__(self, results, output_dir, parent=None):
        super().__init__(parent)
        self.results = results
        self.output_dir = output_dir
        self.setWindowTitle('匯出結果')
        self.setFixedSize(600, 500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 結果摘要
        summary_text = f"""
匯出完成！

總計圖片: {self.results['total_images']} 張
總計標註: {self.results['total_annotations']} 個
匯出格式: {', '.join(self.results['formats'])}
輸出目錄: {self.output_dir}
        """
        
        summary_label = QLabel(summary_text)
        layout.addWidget(summary_label)
        
        # 詳細結果
        results_text = QTextEdit()
        results_text.setReadOnly(True)
        
        details = "格式匯出結果:\n\n"
        for fmt, result in self.results['format_results'].items():
            if 'error' in result:
                details += f"❌ {fmt}: {result['error']}\n\n"
            else:
                details += f"✅ {fmt}: 成功匯出 {result['success']}/{result['total']} 個檔案\n"
                details += f"   輸出目錄: {result['output_dir']}\n\n"
        
        if self.results.get('errors'):
            details += "錯誤訊息:\n"
            for error in self.results['errors']:
                details += f"• {error}\n"
        
        results_text.setText(details)
        layout.addWidget(results_text)
        
        # 按鈕
        button_box = QDialogButtonBox()
        
        open_button = QPushButton('開啟輸出目錄')
        open_button.clicked.connect(self.open_output_dir)
        button_box.addButton(open_button, QDialogButtonBox.ActionRole)
        
        close_button = QPushButton('關閉')
        close_button.clicked.connect(self.accept)
        button_box.addButton(close_button, QDialogButtonBox.AcceptRole)
        
        layout.addWidget(button_box)
    
    def open_output_dir(self):
        import subprocess
        import platform
        
        if platform.system() == 'Windows':
            subprocess.run(['explorer', self.output_dir], shell=True)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', self.output_dir])
        else:  # Linux
            subprocess.run(['xdg-open', self.output_dir])


class RecentFilesDialog(QDialog):
    """最近檔案對話框"""
    
    def __init__(self, file_manager, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.selected_file = None
        self.setWindowTitle('最近開啟的檔案')
        self.setFixedSize(700, 500)
        self.setup_ui()
        self.load_recent_files()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 檔案清單
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        layout.addWidget(self.file_list)
        
        # 按鈕
        button_layout = QHBoxLayout()
        
        clear_button = QPushButton('清空清單')
        clear_button.clicked.connect(self.clear_recent_files)
        button_layout.addWidget(clear_button)
        
        button_layout.addStretch()
        
        open_button = QPushButton('開啟選中檔案')
        open_button.clicked.connect(self.open_selected_file)
        button_layout.addWidget(open_button)
        
        cancel_button = QPushButton('取消')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addWidget(QWidget())  # spacer
        layout.addLayout(button_layout)
    
    def load_recent_files(self):
        recent_files = self.file_manager.get_recent_files()
        
        for file_info in recent_files:
            file_type = file_info['type']
            type_icons = {
                'folder': '📁',
                'project': '💼',
                'image': '🖼️'
            }
            type_names = {
                'folder': '資料夾',
                'project': '專案檔案',
                'image': '圖片檔案'
            }
            
            icon = type_icons.get(file_type, '📄')
            type_name = type_names.get(file_type, file_type)
            
            item_text = f"{icon} {file_info['name']} ({type_name})\n"
            item_text += f"路徑: {file_info['path']}\n"
            item_text += f"最後開啟: {file_info['last_opened'][:19]}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, file_info)
            self.file_list.addItem(item)
    
    def clear_recent_files(self):
        reply = QMessageBox.question(
            self, '確認清空', '確定要清空最近檔案清單嗎？',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.file_manager.clear_recent_files()
            self.file_list.clear()
    
    def on_file_double_clicked(self, item):
        self.selected_file = item.data(Qt.UserRole)
        self.accept()
    
    def open_selected_file(self):
        current_item = self.file_list.currentItem()
        if current_item:
            self.selected_file = current_item.data(Qt.UserRole)
            self.accept()
    
    def get_selected_file(self):
        return self.selected_file


class ProjectManagerDialog(QDialog):
    """專案管理對話框"""
    
    def __init__(self, file_manager, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.setWindowTitle('專案管理')
        self.setFixedSize(800, 600)
        self.setup_ui()
        self.load_projects()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 專案清單
        self.project_list = QListWidget()
        self.project_list.itemDoubleClicked.connect(self.on_project_double_clicked)
        layout.addWidget(self.project_list)
        
        # 按鈕區域
        button_layout = QHBoxLayout()
        
        new_button = QPushButton('新建專案')
        new_button.clicked.connect(self.create_new_project)
        button_layout.addWidget(new_button)
        
        load_button = QPushButton('載入專案')
        load_button.clicked.connect(self.load_selected_project)
        button_layout.addWidget(load_button)
        
        delete_button = QPushButton('刪除專案')
        delete_button.clicked.connect(self.delete_selected_project)
        button_layout.addWidget(delete_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton('關閉')
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def load_projects(self):
        projects = self.file_manager.get_project_list()
        
        self.project_list.clear()
        for project in projects:
            item_text = f"{project['name']}\n"
            item_text += f"圖片: {project['images_count']} 張, "
            item_text += f"標註: {project['annotations_count']} 個\n"
            item_text += f"修改時間: {project['modified_date'][:19] if project['modified_date'] else '未知'}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, project)
            self.project_list.addItem(item)
    
    def create_new_project(self):
        # 這裡可以添加新建專案的邏輯
        QMessageBox.information(self, '新建專案', '請先載入圖片後再建立專案')
    
    def load_selected_project(self):
        current_item = self.project_list.currentItem()
        if current_item:
            project = current_item.data(Qt.UserRole)
            if hasattr(self.parent(), 'load_project_file'):
                self.parent().load_project_file(project['path'])
                self.accept()
    
    def delete_selected_project(self):
        current_item = self.project_list.currentItem()
        if current_item:
            project = current_item.data(Qt.UserRole)
            reply = QMessageBox.question(
                self, '確認刪除', 
                f'確定要刪除專案 "{project["name"]}" 嗎？',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if self.file_manager.delete_project(project['path']):
                    self.load_projects()  # 重新載入清單
                    QMessageBox.information(self, '刪除成功', '專案已刪除')
                else:
                    QMessageBox.critical(self, '刪除失敗', '無法刪除專案')
    
    def on_project_double_clicked(self, item):
        self.load_selected_project()


# === 效能優化功能擴充 ===
def extend_main_window():
    """為 MainWindow 類添加效能優化功能"""

    # 效能優化功能
    def manage_cache(self):
        """管理圖片快取"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QListWidget
        
        dialog = QDialog(self)
        dialog.setWindowTitle('快取管理')
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 快取統計
        cache_info = self.performance_optimizer.get_cache_info()
        info_label = QLabel(f"快取項目: {cache_info['size']} 項\n記憶體使用: {cache_info['memory_usage']:.1f} MB")
        layout.addWidget(info_label)
        
        # 快取項目列表
        cache_list = QListWidget()
        for item in cache_info['items']:
            cache_list.addItem(f"{os.path.basename(item['path'])} - {item['size']:.1f} MB")
        layout.addWidget(cache_list)
        
        # 按鈕
        buttons_layout = QHBoxLayout()
        clear_button = QPushButton('清除快取')
        optimize_button = QPushButton('優化快取')
        close_button = QPushButton('關閉')
        
        def clear_cache():
            self.performance_optimizer.clear_cache()
            cache_size = self.performance_optimizer.get_cache_size()
            self.cache_label.setText(f'快取: {cache_size} 項')
            QMessageBox.information(self, '成功', '快取已清除')
            dialog.close()
        
        def optimize_cache():
            self.performance_optimizer.optimize_cache()
            QMessageBox.information(self, '成功', '快取已優化')
            dialog.close()
        
        clear_button.clicked.connect(clear_cache)
        optimize_button.clicked.connect(optimize_cache)
        close_button.clicked.connect(dialog.close)
        
        buttons_layout.addWidget(clear_button)
        buttons_layout.addWidget(optimize_button)
        buttons_layout.addWidget(close_button)
        layout.addLayout(buttons_layout)
        
        dialog.exec_()
    
    def show_memory_monitor(self):
        """顯示記憶體監控"""
        memory_info = self.performance_optimizer.get_memory_info()
        
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar
        
        dialog = QDialog(self)
        dialog.setWindowTitle('記憶體監控')
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # 系統記憶體
        system_label = QLabel(f"系統記憶體: {memory_info['system']['used']:.1f} GB / {memory_info['system']['total']:.1f} GB")
        layout.addWidget(system_label)
        
        system_bar = QProgressBar()
        system_bar.setMaximum(100)
        system_bar.setValue(int(memory_info['system']['percent']))
        layout.addWidget(system_bar)
        
        # 程序記憶體
        process_label = QLabel(f"程序記憶體: {memory_info['process']['memory']:.1f} MB")
        layout.addWidget(process_label)
        
        # 建議
        recommendations = memory_info.get('recommendations', [])
        if recommendations:
            recommendations_label = QLabel("建議:")
            layout.addWidget(recommendations_label)
            
            for rec in recommendations:
                rec_label = QLabel(f"• {rec}")
                layout.addWidget(rec_label)
        
        # 關閉按鈕
        close_button = QPushButton('關閉')
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        dialog.exec_()
    
    def update_memory_status(self):
        """更新記憶體狀態"""
        try:
            memory_info = self.performance_optimizer.get_memory_info()
            memory_text = f"記憶體: {memory_info['process']['memory']:.0f} MB"
            self.memory_label.setText(memory_text)
        except:
            # 如果獲取記憶體資訊失敗，顯示默認值
            self.memory_label.setText("記憶體: - MB")

# =============== AI輔助功能方法 ===============
# =============== AI輔助功能方法 ===============

def ai_predict_current_image(self):
    """AI預測當前圖片"""
    if not AI_AVAILABLE or not self.ai_assistant:
        QMessageBox.warning(self, 'AI功能不可用', 
                          '請安裝必要套件：pip install torch ultralytics')
        return
        
    if not self.image_path:
        QMessageBox.warning(self, '沒有圖片', '請先載入圖片')
        return
    
    if not self.ai_settings['enabled']:
        reply = QMessageBox.question(self, 'AI功能未啟用', 
                                   'AI功能未啟用，是否要開啟設定？',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.show_ai_settings()
        return
    
    # 初始化AI助手 (如果尚未初始化)
    if not self.ai_assistant.is_available():
        QMessageBox.warning(self, 'AI初始化失敗', 
                          'AI模型載入失敗，請檢查設定')
        return
    
    # 如果AI助手還沒初始化，先初始化
    if not hasattr(self.ai_assistant, 'predictor') or not self.ai_assistant.predictor.model:
        model_path = self.ai_settings['model_path'] if self.ai_settings['use_custom_model'] else None
        if not self.ai_assistant.initialize(model_path):
            QMessageBox.critical(self, 'AI初始化失敗', 'AI模型初始化失敗')
            return
    
    # 設定AI參數
    self.ai_assistant.set_parameters(
        confidence=self.ai_settings['confidence_threshold'],
        auto_optimize=self.ai_settings['auto_optimize_bbox'],
        filter_overlap=self.ai_settings['filter_overlapping']
    )
    
    # 開始預測
    self.statusBar().showMessage('AI正在分析圖片...')
    self.ai_assistant.predict_single_image(
        self.image_path, 
        confidence=self.ai_settings['confidence_threshold']
    )

def ai_predict_batch(self):
    """AI批次預測"""
    if not AI_AVAILABLE or not self.ai_assistant:
        QMessageBox.warning(self, 'AI功能不可用', 
                          '請安裝必要套件：pip install torch ultralytics')
        return
        
    if not self.image_list:
        QMessageBox.warning(self, '沒有圖片', '請先載入圖片或資料夾')
        return
    
    if not self.ai_settings['enabled']:
        reply = QMessageBox.question(self, 'AI功能未啟用', 
                                   'AI功能未啟用，是否要開啟設定？',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.show_ai_settings()
        return
    
    # 確認批次處理
    reply = QMessageBox.question(
        self, '批次AI預測',
        f'將對 {len(self.image_list)} 張圖片進行AI預測。\n\n'
        '這可能需要一些時間，是否繼續？',
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if reply != QMessageBox.Yes:
        return
    
    # 初始化AI助手
    if not hasattr(self.ai_assistant, 'predictor') or not self.ai_assistant.predictor.model:
        model_path = self.ai_settings['model_path'] if self.ai_settings['use_custom_model'] else None
        if not self.ai_assistant.initialize(model_path):
            QMessageBox.critical(self, 'AI初始化失敗', 'AI模型初始化失敗')
            return
    
    # 設定AI參數
    self.ai_assistant.set_parameters(
        confidence=self.ai_settings['confidence_threshold'],
        auto_optimize=self.ai_settings['auto_optimize_bbox'],
        filter_overlap=self.ai_settings['filter_overlapping']
    )
    
    # 開始批次預測
    self.statusBar().showMessage(f'AI批次處理 {len(self.image_list)} 張圖片...')
    self.ai_assistant.predict_batch(
        self.image_list,
        confidence=self.ai_settings['confidence_threshold']
    )

def show_ai_settings(self):
    """顯示AI設定對話框"""
    if not AI_AVAILABLE:
        QMessageBox.warning(self, 'AI功能不可用', 
                          '請安裝必要套件：pip install torch ultralytics')
        return
        
    dialog = AISettingsDialog(self.ai_settings, self)
    dialog.settings_changed.connect(self.on_ai_settings_changed)
    dialog.exec_()

def on_ai_settings_changed(self, new_settings):
    """處理AI設定變更"""
    self.ai_settings.update(new_settings)
    
    # 如果AI助手存在且設定有重大變更，重新初始化
    if self.ai_assistant:
        # 檢查是否需要重新載入模型
        if (new_settings.get('use_custom_model') != self.ai_settings.get('use_custom_model') or
            new_settings.get('model_path') != self.ai_settings.get('model_path')):
            
            model_path = new_settings['model_path'] if new_settings['use_custom_model'] else None
            self.ai_assistant.initialize(model_path)
    
    self.statusBar().showMessage('AI設定已更新', 3000)

def on_ai_prediction_ready(self, image_path, predictions):
    """處理AI預測完成"""
    if not predictions:
        QMessageBox.information(self, 'AI預測結果', '在此圖片中未檢測到車輛')
        self.statusBar().showMessage('AI預測完成：未檢測到車輛', 3000)
        return
    
    # 確保切換到對應的圖片
    if image_path != self.image_path and image_path in self.image_list:
        # 儲存當前標註
        if self.image_path:
            self.save_current_annotations()
        
        # 切換到AI處理的圖片
        target_index = self.image_list.index(image_path)
        self.current_index = target_index
        self.load_current_image()
    
    # 載入當前圖片作為預覽
    image_pixmap = None
    if hasattr(self.annotator, 'image') and self.annotator.image:
        image_pixmap = self.annotator.image
    else:
        # 如果annotator中沒有圖片，嘗試直接載入
        try:
            image_pixmap = QPixmap(image_path)
        except Exception as e:
            print(f"載入圖片預覽失敗: {e}")
    
    # 顯示預測結果對話框
    dialog = PredictionResultDialog(image_path, predictions, image_pixmap, self)
    dialog.predictions_accepted.connect(
        lambda preds, path=image_path: self.on_ai_predictions_accepted(path, preds)
    )
    dialog.predictions_rejected.connect(
        lambda preds, path=image_path: self.on_ai_predictions_rejected(path, preds)
    )
    
    result = dialog.exec_()
    
    if result == QDialog.Accepted:
        self.statusBar().showMessage(f'AI預測完成：處理了 {len(predictions)} 個檢測結果', 3000)
    else:
        self.statusBar().showMessage('AI預測被取消', 3000)

def on_ai_predictions_accepted(self, image_path, accepted_predictions):
    """處理接受的AI預測"""
    if not accepted_predictions:
        return
    
    # 將AI預測轉換為標註格式
    new_annotations = []
    for pred in accepted_predictions:
        bbox = pred['bbox']
        x, y, w, h = bbox
        
        annotation = {
            'id': self.annotator.next_id,
            'rect': QRect(x, y, w, h),
            'class_id': pred['class_id'],
            'class_name': pred['class_name']
        }
        
        new_annotations.append(annotation)
        self.annotator.next_id += 1
        
        # 更新AI統計
        if self.ai_assistant:
            self.ai_assistant.accept_prediction(pred)
    
    # 如果是當前圖片，直接添加到標註器
    if image_path == self.image_path:
        self.annotator.rects.extend(new_annotations)
        self.annotator.repaint()
        self.update_rect_list()
    
    # 更新快取
    if image_path not in self.annotations_cache:
        self.annotations_cache[image_path] = []
    
    self.annotations_cache[image_path].extend(new_annotations)
    
    # 發送更新信號
    self.annotator.rects_updated.emit()

def on_ai_predictions_rejected(self, image_path, rejected_predictions):
    """處理拒絕的AI預測"""
    # 更新AI統計
    if self.ai_assistant:
        for pred in rejected_predictions:
            self.ai_assistant.reject_prediction(pred)

def on_ai_status_updated(self, status_message):
    """處理AI狀態更新"""
    self.statusBar().showMessage(status_message, 5000)

# 將AI功能方法添加到 MainWindow 類
if AI_AVAILABLE:
    MainWindow.ai_predict_current_image = ai_predict_current_image
    MainWindow.ai_predict_batch = ai_predict_batch
    MainWindow.show_ai_settings = show_ai_settings
    MainWindow.on_ai_settings_changed = on_ai_settings_changed
    MainWindow.on_ai_prediction_ready = on_ai_prediction_ready
    MainWindow.on_ai_predictions_accepted = on_ai_predictions_accepted
    MainWindow.on_ai_predictions_rejected = on_ai_predictions_rejected
    MainWindow.on_ai_status_updated = on_ai_status_updated

# 訓練功能已移除，專注於標註功能


if __name__ == '__main__':
    # 啟用高DPI支援 (必須在創建 QApplication 之前設定)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # 設定應用程式屬性
    app.setApplicationName('YOLOv8 Vehicle Annotator')
    app.setApplicationVersion('2.0')
    app.setOrganizationName('AI Tools')
    
    # 擴充主視窗功能
    extend_main_window()
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
