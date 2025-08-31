"""
AI設定對話框 - 配置AI輔助功能參數
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QCheckBox, QSlider, QSpinBox, QGroupBox, QTextEdit,
    QProgressBar, QMessageBox, QTabWidget, QWidget,
    QComboBox, QLineEdit, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

# 導入樣式表
try:
    from styles import get_main_style
    STYLE_AVAILABLE = True
except ImportError:
    STYLE_AVAILABLE = False
    print("樣式表模組不可用，使用預設樣式")

class AISettingsDialog(QDialog):
    """AI設定對話框"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, current_settings=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('AI輔助設定')
        self.setFixedSize(500, 600)
        
        # 設定美觀的現代化樣式
        if STYLE_AVAILABLE:
            self.setStyleSheet(get_main_style())
        else:
            # 備用樣式
            self.setStyleSheet("""
                QDialog {
                    background-color: #f8f9fa;
                    color: #495057;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                QPushButton {
                    background-color: #339af0;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: 500;
                }
                
                QPushButton:hover {
                    background-color: #228be6;
                }
                
                QGroupBox {
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    font-weight: 600;
                    margin: 8px 0;
                    padding-top: 10px;
                    background-color: white;
                }
            """)
        
        # 預設設定 (針對車輛檢測優化)
        self.settings = {
            'enabled': True,
            'confidence_threshold': 0.4,    # 降低閾值，檢測更多車輛
            'iou_threshold': 0.3,           # 更嚴格的IoU，減少重疊
            'auto_optimize_bbox': True,     # 啟用邊界框優化
            'filter_overlapping': True,     # 過濾重疊檢測
            'model_path': '',
            'use_custom_model': False,
            'batch_size': 1,
            'device': 'auto',
            'max_detections': 100,          # 增加最大檢測數量
            'min_vehicle_size': 20,         # 最小車輛尺寸(像素)
            'edge_optimization': True,      # 啟用邊緣優化
            'vehicle_classes_only': True    # 只檢測車輛類別
        }
        
        if current_settings:
            self.settings.update(current_settings)
            
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 標題
        title_label = QLabel('AI輔助標註設定')
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 建立標籤頁
        tab_widget = QTabWidget()
        
        # 基本設定標籤
        basic_tab = QWidget()
        tab_widget.addTab(basic_tab, '基本設定')
        self.setup_basic_tab(basic_tab)
        
        # 進階設定標籤
        advanced_tab = QWidget()
        tab_widget.addTab(advanced_tab, '進階設定')
        self.setup_advanced_tab(advanced_tab)
        
        # 模型設定標籤
        model_tab = QWidget()
        tab_widget.addTab(model_tab, '模型設定')
        self.setup_model_tab(model_tab)
        
        layout.addWidget(tab_widget)
        
        # 狀態顯示
        status_group = QGroupBox('系統狀態')
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(80)
        self.status_text.setPlainText('檢查AI功能可用性...')
        status_layout.addWidget(self.status_text)
        
        layout.addWidget(status_group)
        
        # 按鈕
        button_layout = QHBoxLayout()
        
        self.test_button = QPushButton('測試AI功能')
        self.test_button.clicked.connect(self.test_ai_functionality)
        button_layout.addWidget(self.test_button)
        
        button_layout.addStretch()
        
        self.reset_button = QPushButton('重置預設')
        self.reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_button)
        
        self.cancel_button = QPushButton('取消')
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.apply_button = QPushButton('套用')
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)

    def setup_basic_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # AI功能啟用
        self.enable_ai_cb = QCheckBox('啟用AI輔助功能')
        self.enable_ai_cb.setToolTip('啟用或停用所有AI輔助功能')
        layout.addWidget(self.enable_ai_cb)
        
        # 信心度閾值
        conf_group = QGroupBox('預測信心度設定')
        conf_layout = QVBoxLayout(conf_group)
        
        conf_info = QLabel('只有超過此信心度的預測才會顯示')
        conf_info.setWordWrap(True)
        conf_layout.addWidget(conf_info)
        
        conf_slider_layout = QHBoxLayout()
        conf_slider_layout.addWidget(QLabel('信心度:'))
        
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(1, 99)
        self.confidence_slider.setValue(40)  # 預設40%，更適合車輛檢測
        self.confidence_slider.valueChanged.connect(self.update_confidence_label)
        conf_slider_layout.addWidget(self.confidence_slider)
        
        self.confidence_label = QLabel('0.50')
        self.confidence_label.setMinimumWidth(40)
        conf_slider_layout.addWidget(self.confidence_label)
        
        conf_layout.addLayout(conf_slider_layout)
        layout.addWidget(conf_group)
        
        # 智慧優化選項
        optimize_group = QGroupBox('智慧優化')
        optimize_layout = QVBoxLayout(optimize_group)
        
        self.auto_optimize_cb = QCheckBox('自動優化邊界框')
        self.auto_optimize_cb.setToolTip('使用邊緣檢測自動調整AI預測的邊界框')
        optimize_layout.addWidget(self.auto_optimize_cb)
        
        self.filter_overlap_cb = QCheckBox('過濾重疊預測')
        self.filter_overlap_cb.setToolTip('自動移除重疊度過高的預測結果')
        optimize_layout.addWidget(self.filter_overlap_cb)
        
        layout.addWidget(optimize_group)
        
        layout.addStretch()

    def setup_advanced_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # IOU閾值設定
        iou_group = QGroupBox('重疊過濾設定')
        iou_layout = QVBoxLayout(iou_group)
        
        iou_info = QLabel('用於過濾重疊預測的IoU閾值')
        iou_layout.addWidget(iou_info)
        
        iou_slider_layout = QHBoxLayout()
        iou_slider_layout.addWidget(QLabel('IoU閾值:'))
        
        self.iou_slider = QSlider(Qt.Horizontal)
        self.iou_slider.setRange(1, 90)
        self.iou_slider.setValue(30)  # 預設30%，更嚴格的重疊過濾
        self.iou_slider.valueChanged.connect(self.update_iou_label)
        iou_slider_layout.addWidget(self.iou_slider)
        
        self.iou_label = QLabel('0.45')
        self.iou_label.setMinimumWidth(40)
        iou_slider_layout.addWidget(self.iou_label)
        
        iou_layout.addLayout(iou_slider_layout)
        layout.addWidget(iou_group)
        
        # 效能設定
        performance_group = QGroupBox('效能設定')
        performance_layout = QVBoxLayout(performance_group)
        
        # 裝置選擇
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel('運算裝置:'))
        
        self.device_combo = QComboBox()
        self.device_combo.addItems(['auto', 'cpu', 'cuda', 'mps'])
        self.device_combo.setToolTip('選擇AI運算使用的裝置\nauto: 自動選擇\ncpu: 使用CPU\ncuda: 使用NVIDIA GPU\nmps: 使用Apple GPU')
        device_layout.addWidget(self.device_combo)
        
        performance_layout.addLayout(device_layout)
        
        # 批次大小
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel('批次大小:'))
        
        self.batch_spinbox = QSpinBox()
        self.batch_spinbox.setRange(1, 32)
        self.batch_spinbox.setValue(1)
        self.batch_spinbox.setToolTip('一次處理的圖片數量，較大值可能提高速度但需要更多記憶體')
        batch_layout.addWidget(self.batch_spinbox)
        
        performance_layout.addLayout(batch_layout)
        layout.addWidget(performance_group)
        
        layout.addStretch()

    def setup_model_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # 模型選擇
        model_group = QGroupBox('模型設定')
        model_layout = QVBoxLayout(model_group)
        
        # 預設模型選項
        self.default_model_rb = QCheckBox('使用預設YOLOv8模型')
        self.default_model_rb.setToolTip('使用YOLOv8預訓練模型 (yolov8x.pt)')
        model_layout.addWidget(self.default_model_rb)
        
        # 自訂模型選項
        self.custom_model_cb = QCheckBox('使用自訂模型')
        self.custom_model_cb.toggled.connect(self.toggle_custom_model)
        model_layout.addWidget(self.custom_model_cb)
        
        # 模型路徑選擇
        model_path_layout = QHBoxLayout()
        
        self.model_path_edit = QLineEdit()
        self.model_path_edit.setPlaceholderText('選擇自訂模型檔案 (.pt)')
        self.model_path_edit.setEnabled(False)
        model_path_layout.addWidget(self.model_path_edit)
        
        self.browse_button = QPushButton('瀏覽...')
        self.browse_button.clicked.connect(self.browse_model_file)
        self.browse_button.setEnabled(False)
        model_path_layout.addWidget(self.browse_button)
        
        model_layout.addLayout(model_path_layout)
        layout.addWidget(model_group)
        
        # 模型資訊
        info_group = QGroupBox('模型資訊')
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel(
            "• 預設模型: YOLOv8nano，檔案小速度快，適合一般使用\n"
            "• 自訂模型: 可載入針對特定場景訓練的模型\n"
            "• 支援格式: .pt (PyTorch模型檔案)\n"
            "• 建議: 首次使用請選用預設模型"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        layout.addStretch()

    def toggle_custom_model(self, checked):
        """切換自訂模型選項"""
        self.model_path_edit.setEnabled(checked)
        self.browse_button.setEnabled(checked)
        
        if checked:
            self.default_model_rb.setChecked(False)
        else:
            self.default_model_rb.setChecked(True)

    def browse_model_file(self):
        """瀏覽模型檔案"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '選擇YOLOv8模型檔案',
            '',
            'PyTorch模型 (*.pt);;所有檔案 (*.*)'
        )
        
        if file_path:
            self.model_path_edit.setText(file_path)

    def update_confidence_label(self, value):
        """更新信心度標籤"""
        self.confidence_label.setText(f'{value / 100:.2f}')

    def update_iou_label(self, value):
        """更新IoU標籤"""
        self.iou_label.setText(f'{value / 100:.2f}')

    def load_settings(self):
        """載入設定到UI"""
        self.enable_ai_cb.setChecked(self.settings['enabled'])
        
        conf_value = int(self.settings['confidence_threshold'] * 100)
        self.confidence_slider.setValue(conf_value)
        self.update_confidence_label(conf_value)
        
        iou_value = int(self.settings['iou_threshold'] * 100)
        self.iou_slider.setValue(iou_value)
        self.update_iou_label(iou_value)
        
        self.auto_optimize_cb.setChecked(self.settings['auto_optimize_bbox'])
        self.filter_overlap_cb.setChecked(self.settings['filter_overlapping'])
        
        # 進階設定
        device_index = self.device_combo.findText(self.settings['device'])
        if device_index >= 0:
            self.device_combo.setCurrentIndex(device_index)
            
        self.batch_spinbox.setValue(self.settings['batch_size'])
        
        # 模型設定
        if self.settings['use_custom_model'] and self.settings['model_path']:
            self.custom_model_cb.setChecked(True)
            self.model_path_edit.setText(self.settings['model_path'])
        else:
            self.default_model_rb.setChecked(True)

    def get_settings(self) -> dict:
        """獲取當前設定"""
        settings = {
            'enabled': self.enable_ai_cb.isChecked(),
            'confidence_threshold': self.confidence_slider.value() / 100.0,
            'iou_threshold': self.iou_slider.value() / 100.0,
            'auto_optimize_bbox': self.auto_optimize_cb.isChecked(),
            'filter_overlapping': self.filter_overlap_cb.isChecked(),
            'device': self.device_combo.currentText(),
            'batch_size': self.batch_spinbox.value(),
            'use_custom_model': self.custom_model_cb.isChecked(),
            'model_path': self.model_path_edit.text() if self.custom_model_cb.isChecked() else ''
        }
        return settings

    def test_ai_functionality(self):
        """測試AI功能"""
        self.status_text.setPlainText('正在測試AI功能...')
        
        try:
            # 檢查依賴套件
            try:
                import torch
                torch_version = torch.__version__
                torch_available = True
            except ImportError:
                torch_version = "未安裝"
                torch_available = False
            
            try:
                from ultralytics import YOLO
                yolo_available = True
            except ImportError:
                yolo_available = False
            
            # 檢查GPU可用性
            gpu_available = torch.cuda.is_available() if torch_available else False
            
            # 生成狀態報告
            status_lines = [
                "=== AI功能狀態檢查 ===",
                f"PyTorch: {'✓' if torch_available else '✗'} {torch_version}",
                f"Ultralytics: {'✓' if yolo_available else '✗'}",
                f"CUDA GPU: {'✓' if gpu_available else '✗'}",
                "",
            ]
            
            if torch_available and yolo_available:
                status_lines.append("✅ AI功能完全可用")
                if gpu_available:
                    status_lines.append("🚀 GPU加速可用，建議使用cuda裝置")
                else:
                    status_lines.append("💻 將使用CPU運算，速度較慢")
            else:
                status_lines.append("❌ AI功能不可用")
                status_lines.append("")
                status_lines.append("安裝指令:")
                if not torch_available:
                    status_lines.append("pip install torch torchvision")
                if not yolo_available:
                    status_lines.append("pip install ultralytics")
            
            self.status_text.setPlainText('\n'.join(status_lines))
            
        except Exception as e:
            self.status_text.setPlainText(f'測試AI功能時發生錯誤: {str(e)}')

    def reset_to_defaults(self):
        """重置為預設值"""
        reply = QMessageBox.question(
            self,
            '重置確認',
            '確定要重置所有AI設定為預設值嗎？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 重置設定
            self.settings = {
                'enabled': True,
                'confidence_threshold': 0.5,
                'iou_threshold': 0.45,
                'auto_optimize_bbox': True,
                'filter_overlapping': True,
                'model_path': '',
                'use_custom_model': False,
                'batch_size': 1,
                'device': 'auto'
            }
            self.load_settings()

    def apply_settings(self):
        """套用設定"""
        new_settings = self.get_settings()
        
        # 驗證設定
        if new_settings['use_custom_model'] and not new_settings['model_path']:
            QMessageBox.warning(self, '設定錯誤', '請選擇自訂模型檔案或使用預設模型')
            return
        
        if new_settings['use_custom_model'] and not os.path.exists(new_settings['model_path']):
            QMessageBox.warning(self, '檔案錯誤', f'模型檔案不存在：{new_settings["model_path"]}')
            return
        
        # 發送設定變更信號
        self.settings_changed.emit(new_settings)
        self.accept()

    def showEvent(self, event):
        """對話框顯示時自動測試AI功能"""
        super().showEvent(event)
        self.test_ai_functionality()
