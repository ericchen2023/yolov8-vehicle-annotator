"""
YOLOv8 模型選擇對話框
提供五種不同版本的YOLOv8模型供用戶選擇，並自動下載不存在的模型
支援響應式設計，適應不同螢幕尺寸
"""

import os
import sys
from typing import Dict, Optional, Tuple
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QRadioButton, QButtonGroup, QProgressBar, QTextEdit,
    QGroupBox, QGridLayout, QFrame, QSizePolicy, QScrollArea,
    QWidget, QApplication, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QPalette

try:
    from ultralytics import YOLO
    import torch
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class ModelDownloadThread(QThread):
    """模型下載執行緒"""
    progress_updated = pyqtSignal(str, int)  # 模型名稱, 進度百分比
    download_completed = pyqtSignal(str, bool)  # 模型名稱, 是否成功
    status_updated = pyqtSignal(str)  # 狀態訊息
    
    def __init__(self, model_variant: str):
        super().__init__()
        self.model_variant = model_variant
        self.model_path = f"yolov8{model_variant}.pt"
        
    def run(self):
        """執行模型下載"""
        try:
            self.status_updated.emit(f"正在下載 YOLOv8{self.model_variant.upper()} 模型...")
            self.progress_updated.emit(self.model_variant, 10)
            
            # 使用YOLO的內建下載功能
            model = YOLO(self.model_path)
            
            self.progress_updated.emit(self.model_variant, 100)
            self.status_updated.emit(f"YOLOv8{self.model_variant.upper()} 模型下載完成")
            self.download_completed.emit(self.model_variant, True)
            
        except Exception as e:
            self.status_updated.emit(f"下載失敗: {str(e)}")
            self.download_completed.emit(self.model_variant, False)


class ModelInfoCard(QFrame):
    """模型資訊卡片元件 - 響應式設計"""
    
    def __init__(self, model_variant: str, model_info: Dict):
        super().__init__()
        self.model_variant = model_variant
        self.model_info = model_info
        self.radio_button = None
        self.setup_ui()
        
    def setup_ui(self):
        """設置卡片UI"""
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)
        self.setStyleSheet("""
            QFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ffffff, stop:1 #f8f9fa);
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 8px;
                margin: 4px;
            }
            QFrame:hover {
                border-color: #74c0fc;
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #f0f8ff, stop:1 #e3f2fd);
            }
            QRadioButton {
                font-size: 16px;
                font-weight: bold;
                color: #1565c0;
                padding: 4px;
            }
            QRadioButton:checked {
                color: #0d47a1;
            }
            QLabel {
                color: #495057;
                padding: 2px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # 模型名稱和選擇按鈕
        header_layout = QHBoxLayout()
        
        self.radio_button = QRadioButton(f"YOLOv8{self.model_variant.upper()}")
        self.radio_button.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(self.radio_button)
        
        header_layout.addStretch()
        
        # 模型大小標籤
        size_label = QLabel(f"📦 {self.model_info['size']}")
        size_label.setStyleSheet("color: #28a745; font-weight: bold;")
        header_layout.addWidget(size_label)
        
        layout.addLayout(header_layout)
        
        # 模型描述
        desc_label = QLabel(self.model_info['description'])
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 13px; color: #6c757d; line-height: 1.4;")
        layout.addWidget(desc_label)
        
        # 性能指標網格
        metrics_layout = QGridLayout()
        metrics_layout.setSpacing(4)
        
        # 速度指標
        speed_label = QLabel("⚡ 速度:")
        speed_label.setStyleSheet("font-weight: bold; color: #495057;")
        speed_value = QLabel(self.model_info['speed'])
        speed_value.setStyleSheet("color: #17a2b8;")
        metrics_layout.addWidget(speed_label, 0, 0)
        metrics_layout.addWidget(speed_value, 0, 1)
        
        # 精確度指標
        accuracy_label = QLabel("🎯 精確度:")
        accuracy_label.setStyleSheet("font-weight: bold; color: #495057;")
        accuracy_value = QLabel(self.model_info['accuracy'])
        accuracy_value.setStyleSheet("color: #dc3545;")
        metrics_layout.addWidget(accuracy_label, 1, 0)
        metrics_layout.addWidget(accuracy_value, 1, 1)
        
        # 記憶體使用
        memory_label = QLabel("🧠 記憶體:")
        memory_label.setStyleSheet("font-weight: bold; color: #495057;")
        memory_value = QLabel(self.model_info['memory'])
        memory_value.setStyleSheet("color: #fd7e14;")
        metrics_layout.addWidget(memory_label, 2, 0)
        metrics_layout.addWidget(memory_value, 2, 1)
        
        layout.addLayout(metrics_layout)
        
        # 使用場景
        scenario_label = QLabel("💡 適用場景:")
        scenario_label.setStyleSheet("font-weight: bold; color: #495057; margin-top: 4px;")
        layout.addWidget(scenario_label)
        
        scenario_text = QLabel(self.model_info['use_case'])
        scenario_text.setWordWrap(True)
        scenario_text.setStyleSheet("font-size: 12px; color: #6c757d; font-style: italic; margin-bottom: 4px;")
        layout.addWidget(scenario_text)
        
        # 檔案狀態
        self.status_label = QLabel()
        self.update_status()
        layout.addWidget(self.status_label)
        
        # 設置最小和最大尺寸以支援響應式
        self.setMinimumSize(280, 220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
    def update_status(self):
        """更新模型檔案狀態"""
        model_path = f"yolov8{self.model_variant}.pt"
        if os.path.exists(model_path):
            file_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
            self.status_label.setText(f"✅ 已下載 ({file_size:.1f} MB)")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
        else:
            self.status_label.setText("📥 需要下載")
            self.status_label.setStyleSheet("color: #ffc107; font-weight: bold;")
    
    def get_radio_button(self):
        """獲取單選按鈕"""
        return self.radio_button


class ModelSelectorDialog(QDialog):
    """YOLOv8 模型選擇對話框 - 響應式設計"""
    
    # 模型資訊定義
    MODEL_INFO = {
        'n': {
            'name': 'Nano',
            'size': '6.2 MB',
            'description': '超輕量級模型，適合移動設備和嵌入式系統',
            'speed': '極快',
            'accuracy': '中等',
            'memory': '極低',
            'use_case': '移動應用、即時處理、資源受限環境',
            'parameters': '3.2M',
            'gflops': '8.7'
        },
        's': {
            'name': 'Small',
            'size': '21.5 MB',
            'description': '輕量級模型，平衡速度和精確度',
            'speed': '很快',
            'accuracy': '良好',
            'memory': '低',
            'use_case': '快速原型開發、即時應用、一般車輛檢測',
            'parameters': '11.2M',
            'gflops': '28.6'
        },
        'm': {
            'name': 'Medium',
            'size': '49.7 MB',
            'description': '中等模型，在速度和精確度間取得平衡',
            'speed': '快',
            'accuracy': '很好',
            'memory': '中等',
            'use_case': '標準應用、批次處理、品質要求較高的檢測',
            'parameters': '25.9M',
            'gflops': '78.9'
        },
        'l': {
            'name': 'Large',
            'size': '87.7 MB',
            'description': '大型模型，提供高精確度檢測',
            'speed': '中等',
            'accuracy': '高',
            'memory': '高',
            'use_case': '高精度要求、複雜場景、專業應用',
            'parameters': '43.7M',
            'gflops': '165.2'
        },
        'x': {
            'name': 'Extra Large',
            'size': '136.7 MB',
            'description': '最大模型，提供最高精確度，適合研究和高端應用',
            'speed': '慢',
            'accuracy': '最高',
            'memory': '很高',
            'use_case': '研究項目、最高精度要求、離線批次處理',
            'parameters': '68.2M',
            'gflops': '257.8'
        }
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_model = None
        self.model_cards = {}
        self.button_group = QButtonGroup()
        self.download_thread = None
        
        self.setup_ui()
        self.setup_responsive_design()
        
        # 預設選擇 medium 模型
        if 'm' in self.model_cards:
            self.model_cards['m'].get_radio_button().setChecked(True)
            self.selected_model = 'm'
    
    def setup_ui(self):
        """設置用戶介面"""
        self.setWindowTitle('YOLOv8 模型選擇')
        self.setModal(True)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 標題
        title_label = QLabel('🤖 選擇 YOLOv8 模型')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #1565c0;
                padding: 10px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 說明文字
        desc_label = QLabel(
            '請選擇適合您需求的 YOLOv8 模型版本。如果選擇的模型不存在，系統將自動下載。'
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #6c757d;
                padding: 5px;
                margin-bottom: 15px;
                line-height: 1.4;
            }
        """)
        main_layout.addWidget(desc_label)
        
        # 創建滾動區域以支援響應式設計
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # 模型卡片容器
        cards_widget = QWidget()
        self.cards_layout = QGridLayout(cards_widget)
        self.cards_layout.setSpacing(10)
        
        # 創建模型卡片
        row, col = 0, 0
        max_cols = 2  # 預設每行2個卡片
        
        for variant, info in self.MODEL_INFO.items():
            card = ModelInfoCard(variant, info)
            self.model_cards[variant] = card
            self.button_group.addButton(card.get_radio_button())
            
            # 連接信號
            card.get_radio_button().toggled.connect(
                lambda checked, v=variant: self.on_model_selected(v) if checked else None
            )
            
            self.cards_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 如果最後一行只有一個卡片，讓它跨越兩列
        if len(self.MODEL_INFO) % max_cols == 1:
            last_card = list(self.model_cards.values())[-1]
            self.cards_layout.addWidget(last_card, row, 0, 1, max_cols)
        
        scroll_area.setWidget(cards_widget)
        main_layout.addWidget(scroll_area)
        
        # 系統要求說明
        sys_req_group = QGroupBox("💻 系統要求和建議")
        sys_req_layout = QVBoxLayout(sys_req_group)
        
        sys_req_text = QTextEdit()
        sys_req_text.setReadOnly(True)
        sys_req_text.setMaximumHeight(100)
        sys_req_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                color: #495057;
            }
        """)
        
        device_info = self.get_device_info()
        sys_req_text.setText(
            f"🖥️ 當前設備: {device_info}\n\n"
            "💡 建議選擇:\n"
            "• CPU 或低階 GPU: Nano (n) 或 Small (s)\n"
            "• 中階 GPU: Medium (m) 或 Large (l)\n"
            "• 高階 GPU 或大記憶體: Extra Large (x)\n\n"
            "⚠️ 注意: 較大的模型需要更多記憶體和計算時間"
        )
        
        sys_req_layout.addWidget(sys_req_text)
        main_layout.addWidget(sys_req_group)
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #4dabf7, stop:1 #339af0);
                border-radius: 6px;
                margin: 2px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # 狀態標籤
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #495057;
                padding: 5px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
        # 按鈕
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.ok_button = QPushButton('✅ 確定')
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept_selection)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #28a745, stop:1 #1e7e34);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #34ce57, stop:1 #28a745);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #1e7e34, stop:1 #155724);
            }
            QPushButton:disabled {
                background: #6c757d;
                color: #adb5bd;
            }
        """)
        
        cancel_button = QPushButton('❌ 取消')
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #6c757d, stop:1 #5a6268);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #7c848a, stop:1 #6c757d);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #5a6268, stop:1 #495057);
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.ok_button)
        
        main_layout.addLayout(button_layout)
    
    def setup_responsive_design(self):
        """設置響應式設計"""
        # 設置最小尺寸
        self.setMinimumSize(700, 600)
        
        # 根據螢幕大小調整視窗尺寸
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        
        # 計算適當的視窗大小
        width = min(1000, int(screen_size.width() * 0.8))
        height = min(800, int(screen_size.height() * 0.8))
        
        self.resize(width, height)
        
        # 居中顯示
        self.move(
            (screen_size.width() - width) // 2,
            (screen_size.height() - height) // 2
        )
    
    def resizeEvent(self, event):
        """響應視窗大小變化"""
        super().resizeEvent(event)
        
        # 根據視窗寬度調整卡片布局
        if hasattr(self, 'cards_layout'):
            width = self.width()
            
            # 計算每行的卡片數量
            if width < 800:
                max_cols = 1
            elif width < 1200:
                max_cols = 2
            else:
                max_cols = 3
            
            # 重新排列卡片
            for i, (variant, card) in enumerate(self.model_cards.items()):
                row = i // max_cols
                col = i % max_cols
                self.cards_layout.addWidget(card, row, col)
    
    def get_device_info(self) -> str:
        """獲取設備資訊"""
        try:
            if YOLO_AVAILABLE and torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                return f"GPU: {gpu_name} ({gpu_memory:.1f} GB)"
            else:
                return "CPU (建議使用 Nano 或 Small 模型)"
        except:
            return "未知設備"
    
    def on_model_selected(self, variant: str):
        """處理模型選擇"""
        self.selected_model = variant
        model_info = self.MODEL_INFO[variant]
        self.status_label.setText(f"已選擇 YOLOv8{variant.upper()} ({model_info['name']})")
        
        # 更新OK按鈕狀態
        self.ok_button.setEnabled(True)
    
    def accept_selection(self):
        """確認選擇並處理模型下載"""
        if not self.selected_model:
            QMessageBox.warning(self, '未選擇', '請選擇一個模型')
            return
        
        model_path = f"yolov8{self.selected_model}.pt"
        
        # 檢查模型是否存在
        if os.path.exists(model_path):
            self.accept()
            return
        
        # 模型不存在，需要下載
        reply = QMessageBox.question(
            self, '下載模型',
            f'YOLOv8{self.selected_model.upper()} 模型不存在，是否立即下載？\n\n'
            f'檔案大小: {self.MODEL_INFO[self.selected_model]["size"]}\n'
            '下載可能需要幾分鐘時間。',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.download_model()
        else:
            self.reject()
    
    def download_model(self):
        """下載選擇的模型"""
        if not YOLO_AVAILABLE:
            QMessageBox.critical(
                self, '錯誤',
                'YOLOv8 未安裝，無法下載模型。\n請先安裝 ultralytics 套件。'
            )
            return
        
        # 禁用按鈕
        self.ok_button.setEnabled(False)
        self.ok_button.setText('⏳ 下載中...')
        
        # 顯示進度條
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 開始下載
        self.download_thread = ModelDownloadThread(self.selected_model)
        self.download_thread.progress_updated.connect(self.on_download_progress)
        self.download_thread.download_completed.connect(self.on_download_completed)
        self.download_thread.status_updated.connect(self.on_download_status)
        self.download_thread.start()
    
    def on_download_progress(self, model_variant: str, progress: int):
        """處理下載進度"""
        self.progress_bar.setValue(progress)
    
    def on_download_status(self, status: str):
        """處理下載狀態"""
        self.status_label.setText(status)
    
    def on_download_completed(self, model_variant: str, success: bool):
        """處理下載完成"""
        self.progress_bar.setVisible(False)
        self.ok_button.setEnabled(True)
        self.ok_button.setText('✅ 確定')
        
        if success:
            # 更新模型卡片狀態
            if model_variant in self.model_cards:
                self.model_cards[model_variant].update_status()
            
            QMessageBox.information(
                self, '下載完成',
                f'YOLOv8{model_variant.upper()} 模型下載成功！'
            )
            self.accept()
        else:
            QMessageBox.critical(
                self, '下載失敗',
                f'YOLOv8{model_variant.upper()} 模型下載失敗，請檢查網路連接。'
            )
    
    def get_selected_model(self) -> Optional[str]:
        """獲取選擇的模型"""
        return self.selected_model
    
    def get_model_path(self) -> Optional[str]:
        """獲取模型檔案路徑"""
        if self.selected_model:
            return f"yolov8{self.selected_model}.pt"
        return None
    
    def validate_selection(self) -> bool:
        """驗證選擇的有效性"""
        if not self.selected_model:
            return False
            
        if self.selected_model not in self.MODEL_INFO:
            return False
            
        return True
    
    def closeEvent(self, event):
        """處理關閉事件"""
        if self.download_thread and self.download_thread.isRunning():
            reply = QMessageBox.question(
                self, '確認關閉',
                '模型正在下載中，確定要關閉嗎？',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.download_thread.quit()
                self.download_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


# 測試程式
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 設置應用程式樣式
    app.setStyle('Fusion')
    
    dialog = ModelSelectorDialog()
    
    if dialog.exec_() == QDialog.Accepted:
        selected_model = dialog.get_selected_model()
        model_path = dialog.get_model_path()
        print(f"選擇的模型: YOLOv8{selected_model.upper()}")
        print(f"模型路徑: {model_path}")
    else:
        print("用戶取消選擇")
    
    sys.exit()
