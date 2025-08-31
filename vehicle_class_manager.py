"""
車種類別管理器
提供自定義車種功能，包括新增、編輯、刪除車種類別
支援COCO數據集連動和智能快捷鍵分配
"""

import json
import os
from typing import List, Dict, Tuple, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QLineEdit, QColorDialog,
    QInputDialog, QMessageBox, QGroupBox, QFormLayout,
    QSpinBox, QCheckBox, QTextEdit, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDialogButtonBox, QFrame, QSplitter, QFileDialog, QApplication,
    QMenu, QAction, QShortcut, QListWidget, QAbstractItemView,
    QScrollArea, QGridLayout
)
from PyQt5.QtGui import QColor, QPixmap, QPainter, QIcon, QKeySequence, QFont
from PyQt5.QtCore import Qt, pyqtSignal


# COCO 80種類別定義
COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush"
]

# 車輛相關的COCO類別索引
VEHICLE_COCO_INDICES = [1, 2, 3, 5, 6, 7]  # bicycle, car, motorcycle, bus, train, truck

# 表情符號映射
COCO_EMOJI_MAP = {
    "person": "👤", "bicycle": "🚲", "car": "🚗", "motorcycle": "🏍",
    "airplane": "✈️", "bus": "🚌", "train": "🚂", "truck": "🚛",
    "boat": "🚢", "traffic light": "🚦", "fire hydrant": "🧯",
    "stop sign": "🛑", "parking meter": "🅿️", "bench": "🪑",
    "bird": "🐦", "cat": "🐱", "dog": "🐶", "horse": "🐴",
    "sheep": "🐑", "cow": "🐄", "elephant": "🐘", "bear": "🐻",
    "zebra": "🦓", "giraffe": "🦒", "backpack": "🎒", "umbrella": "☂️",
    "handbag": "👜", "tie": "👔", "suitcase": "🧳", "frisbee": "🥏",
    "skis": "🎿", "snowboard": "🏂", "sports ball": "⚽", "kite": "🪁",
    "baseball bat": "🏏", "baseball glove": "🧤", "skateboard": "🛼",
    "surfboard": "🏄", "tennis racket": "🎾", "bottle": "🍾",
    "wine glass": "🍷", "cup": "☕", "fork": "🍴", "knife": "🔪",
    "spoon": "🥄", "bowl": "🍜", "banana": "🍌", "apple": "🍎",
    "sandwich": "🥪", "orange": "🍊", "broccoli": "🥦", "carrot": "🥕",
    "hot dog": "🌭", "pizza": "🍕", "donut": "🍩", "cake": "🍰",
    "chair": "🪑", "couch": "🛋️", "potted plant": "🪴", "bed": "🛏️",
    "dining table": "🪑", "toilet": "🚽", "tv": "📺", "laptop": "💻",
    "mouse": "🖱️", "remote": "📺", "keyboard": "⌨️", "cell phone": "📱",
    "microwave": "🔥", "oven": "🔥", "toaster": "🔥", "sink": "🚰",
    "refrigerator": "🧊", "book": "📖", "clock": "🕐", "vase": "🏺",
    "scissors": "✂️", "teddy bear": "🧸", "hair drier": "💇", "toothbrush": "🪥"
}


# 導入樣式表
try:
    from styles import get_main_style
    STYLE_AVAILABLE = True
except ImportError:
    STYLE_AVAILABLE = False
    print("樣式表模組不可用，使用預設樣式")


class VehicleClass:
    """車種類別資料結構"""
    
    def __init__(self, class_id: int, name: str, color: QColor = None, 
                 description: str = "", enabled: bool = True, 
                 shortcut_key: str = "", emoji: str = "🚗",
                 coco_class_id: int = None):
        self.class_id = class_id
        self.name = name
        self.color = color or self._get_default_color(class_id)
        self.description = description
        self.enabled = enabled
        self.shortcut_key = shortcut_key or str(class_id + 1)  # 預設為ID+1
        self.emoji = emoji
        self.coco_class_id = coco_class_id  # 對應的COCO類別ID
    
    def _get_default_color(self, class_id: int) -> QColor:
        """根據 ID 生成預設顏色"""
        default_colors = [
            QColor(255, 75, 75),    # 紅色
            QColor(75, 255, 75),    # 綠色
            QColor(75, 150, 255),   # 藍色
            QColor(255, 215, 0),    # 金黃色
            QColor(255, 165, 0),    # 橙色
            QColor(147, 112, 219),  # 紫色
            QColor(255, 192, 203),  # 粉紅色
            QColor(0, 255, 255),    # 青色
            QColor(255, 255, 0),    # 黃色
            QColor(255, 20, 147),   # 深粉紅
        ]
        return default_colors[class_id % len(default_colors)]
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            'class_id': self.class_id,
            'name': self.name,
            'color': {
                'r': self.color.red(),
                'g': self.color.green(),
                'b': self.color.blue(),
                'a': self.color.alpha()
            },
            'description': self.description,
            'enabled': self.enabled,
            'shortcut_key': self.shortcut_key,
            'emoji': self.emoji,
            'coco_class_id': self.coco_class_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'VehicleClass':
        """從字典創建物件"""
        color_data = data.get('color', {})
        color = QColor(
            color_data.get('r', 255),
            color_data.get('g', 75),
            color_data.get('b', 75),
            color_data.get('a', 255)
        )
        
        return cls(
            class_id=data['class_id'],
            name=data['name'],
            color=color,
            description=data.get('description', ''),
            enabled=data.get('enabled', True),
            shortcut_key=data.get('shortcut_key', ''),
            emoji=data.get('emoji', '🚗'),
            coco_class_id=data.get('coco_class_id')
        )


class VehicleClassManager:
    """車種類別管理器"""
    
    def __init__(self, config_file: str = "vehicle_classes.json"):
        self.config_file = config_file
        self.classes = {}  # {class_id: VehicleClass}
        self.next_id = 0
        self.coco_config_file = "coco_classes_config.json"
        self.selected_coco_classes = set(VEHICLE_COCO_INDICES)  # 預設選擇車輛相關類別
        self.load_classes()
        self.load_coco_config()
    
    def load_classes(self):
        """載入車種類別配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.classes = {}
                for class_data in data.get('classes', []):
                    vehicle_class = VehicleClass.from_dict(class_data)
                    self.classes[vehicle_class.class_id] = vehicle_class
                
                self.next_id = data.get('next_id', len(self.classes))
                
            except Exception as e:
                print(f"載入車種配置失敗: {e}")
                self._load_default_classes()
        else:
            self._load_default_classes()
        
        # 確保 next_id 正確
        if self.classes:
            self.next_id = max(self.classes.keys()) + 1
    
    def load_coco_config(self):
        """載入COCO類別配置"""
        if os.path.exists(self.coco_config_file):
            try:
                with open(self.coco_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.selected_coco_classes = set(data.get('selected_classes', VEHICLE_COCO_INDICES))
            except Exception as e:
                print(f"載入COCO配置失敗: {e}")
                self.selected_coco_classes = set(VEHICLE_COCO_INDICES)
        else:
            self.save_coco_config()
    
    def save_coco_config(self):
        """儲存COCO類別配置"""
        try:
            data = {
                'selected_classes': list(self.selected_coco_classes),
                'version': '1.0'
            }
            with open(self.coco_config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存COCO配置失敗: {e}")
    
    def _load_default_classes(self):
        """載入預設車種類別"""
        default_classes = [
            {'name': '機車', 'emoji': '🏍', 'shortcut_key': '1', 'description': '兩輪機車'},
            {'name': '汽車', 'emoji': '🚗', 'shortcut_key': '2', 'description': '一般乘用車'},
            {'name': '卡車', 'emoji': '🚛', 'shortcut_key': '3', 'description': '貨運卡車'},
            {'name': '公車', 'emoji': '🚌', 'shortcut_key': '4', 'description': '公共交通巴士'},
        ]
        
        self.classes = {}
        for i, cls_data in enumerate(default_classes):
            vehicle_class = VehicleClass(
                class_id=i,
                name=cls_data['name'],
                emoji=cls_data['emoji'],
                shortcut_key=cls_data['shortcut_key'],  # 已經是ID+1格式
                description=cls_data['description']
            )
            self.classes[i] = vehicle_class
        
        self.next_id = len(default_classes)
        self.save_classes()
    
    def save_classes(self):
        """儲存車種類別配置"""
        try:
            data = {
                'classes': [cls.to_dict() for cls in self.classes.values()],
                'next_id': self.next_id,
                'version': '1.0'
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"儲存車種配置失敗: {e}")
            raise
    
    def add_class(self, name: str, color: QColor = None, description: str = "", 
                  shortcut_key: str = "", emoji: str = "🚗", coco_class_id: int = None) -> int:
        """新增車種類別"""
        if not name.strip():
            raise ValueError("車種名稱不能為空")
        
        # 檢查名稱是否重複
        for cls in self.classes.values():
            if cls.name == name:
                raise ValueError(f"車種名稱 '{name}' 已存在")
        
        # 如果沒有指定快捷鍵，使用ID+1
        if not shortcut_key:
            shortcut_key = str(self.next_id + 1)
        
        # 檢查快捷鍵是否重複
        if shortcut_key:
            for cls in self.classes.values():
                if cls.shortcut_key == shortcut_key:
                    raise ValueError(f"快捷鍵 '{shortcut_key}' 已被使用")
        
        class_id = self.next_id
        vehicle_class = VehicleClass(
            class_id=class_id,
            name=name,
            color=color,
            description=description,
            shortcut_key=shortcut_key,
            emoji=emoji,
            coco_class_id=coco_class_id
        )
        
        self.classes[class_id] = vehicle_class
        self.next_id += 1
        self.save_classes()
        
        return class_id
    
    def update_class(self, class_id: int, name: str = None, color: QColor = None,
                     description: str = None, enabled: bool = None,
                     shortcut_key: str = None, emoji: str = None,
                     coco_class_id: int = None):
        """更新車種類別"""
        if class_id not in self.classes:
            raise ValueError(f"車種 ID {class_id} 不存在")
        
        vehicle_class = self.classes[class_id]
        
        if name is not None:
            if not name.strip():
                raise ValueError("車種名稱不能為空")
            # 檢查名稱是否與其他類別重複
            for cid, cls in self.classes.items():
                if cid != class_id and cls.name == name:
                    raise ValueError(f"車種名稱 '{name}' 已存在")
            vehicle_class.name = name
        
        if color is not None:
            vehicle_class.color = color
        
        if description is not None:
            vehicle_class.description = description
        
        if enabled is not None:
            vehicle_class.enabled = enabled
        
        if shortcut_key is not None:
            # 檢查快捷鍵是否與其他類別重複
            if shortcut_key:
                for cid, cls in self.classes.items():
                    if cid != class_id and cls.shortcut_key == shortcut_key:
                        raise ValueError(f"快捷鍵 '{shortcut_key}' 已被使用")
            vehicle_class.shortcut_key = shortcut_key
        
        if emoji is not None:
            vehicle_class.emoji = emoji
        
        if coco_class_id is not None:
            vehicle_class.coco_class_id = coco_class_id
        
        self.save_classes()
    
    def delete_class(self, class_id: int):
        """刪除車種類別"""
        if class_id not in self.classes:
            raise ValueError(f"車種 ID {class_id} 不存在")
        
        del self.classes[class_id]
        self.save_classes()
    
    def get_class(self, class_id: int) -> Optional[VehicleClass]:
        """取得車種類別"""
        return self.classes.get(class_id)
    
    def get_all_classes(self, enabled_only: bool = False) -> List[VehicleClass]:
        """取得所有車種類別"""
        classes = list(self.classes.values())
        if enabled_only:
            classes = [cls for cls in classes if cls.enabled]
        return sorted(classes, key=lambda x: x.class_id)
    
    def get_class_by_name(self, name: str) -> Optional[VehicleClass]:
        """根據名稱取得車種類別"""
        for cls in self.classes.values():
            if cls.name == name:
                return cls
        return None
    
    def get_classes_for_combo(self, enabled_only: bool = True) -> List[Tuple[str, int]]:
        """取得適用於下拉選單的車種清單"""
        classes = self.get_all_classes(enabled_only)
        return [(cls.name, cls.class_id) for cls in classes]
    
    def get_class_colors(self) -> Dict[int, QColor]:
        """取得所有車種的顏色映射"""
        return {class_id: cls.color for class_id, cls in self.classes.items()}
    
    def get_selected_coco_classes(self) -> List[int]:
        """取得選中的COCO類別ID列表"""
        return sorted(list(self.selected_coco_classes))
    
    def set_selected_coco_classes(self, selected_classes: List[int]):
        """設定選中的COCO類別"""
        self.selected_coco_classes = set(selected_classes)
        self.save_coco_config()
    
    def get_coco_class_name(self, coco_class_id: int) -> str:
        """取得COCO類別名稱"""
        if 0 <= coco_class_id < len(COCO_CLASSES):
            return COCO_CLASSES[coco_class_id]
        return f"Unknown ({coco_class_id})"
    
    def get_coco_class_emoji(self, coco_class_id: int) -> str:
        """取得COCO類別的表情符號"""
        class_name = self.get_coco_class_name(coco_class_id)
        return COCO_EMOJI_MAP.get(class_name, "❓")
    
    def import_from_coco(self, selected_coco_ids: List[int]):
        """從COCO數據集匯入選中的類別"""
        if not selected_coco_ids:
            return
        
        try:
            # 清除現有類別
            self.classes = {}
            self.next_id = 0
            
            # 添加選中的COCO類別
            for i, coco_id in enumerate(selected_coco_ids):
                class_name = self.get_coco_class_name(coco_id)
                emoji = self.get_coco_class_emoji(coco_id)
                
                vehicle_class = VehicleClass(
                    class_id=i,
                    name=class_name,
                    emoji=emoji,
                    shortcut_key=str(i + 1),  # ID+1
                    description=f"COCO類別: {class_name}",
                    coco_class_id=coco_id
                )
                self.classes[i] = vehicle_class
            
            self.next_id = len(selected_coco_ids)
            self.save_classes()
            
        except Exception as e:
            print(f"從COCO匯入失敗: {e}")
            raise
    
    def get_coco_to_vehicle_mapping(self) -> Dict[int, int]:
        """取得COCO類別ID到車種ID的映射"""
        mapping = {}
        for class_id, vehicle_class in self.classes.items():
            if vehicle_class.coco_class_id is not None:
                mapping[vehicle_class.coco_class_id] = class_id
        return mapping
    
    def export_classes_txt(self, filename: str = "classes.txt"):
        """匯出車種清單到文字檔案（YOLO格式）"""
        try:
            classes = self.get_all_classes(enabled_only=True)
            with open(filename, 'w', encoding='utf-8') as f:
                for cls in classes:
                    f.write(f"{cls.name}\n")
            return True
        except Exception as e:
            print(f"匯出車種清單失敗: {e}")
            return False
    
    def import_classes_txt(self, filename: str) -> bool:
        """從文字檔案匯入車種清單"""
        try:
            if not os.path.exists(filename):
                return False
            
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 清除現有類別
            self.classes = {}
            self.next_id = 0
            
            # 導入新類別
            for i, line in enumerate(lines):
                name = line.strip()
                if name:
                    # 生成預設表情符號
                    emoji_map = {
                        '機車': '🏍', '摩托車': '🏍',
                        '汽車': '🚗', '小客車': '🚗', '轎車': '🚗',
                        '卡車': '🚛', '貨車': '🚛', '載貨車': '🚛',
                        '公車': '🚌', '巴士': '🚌', '客運': '🚌',
                        '計程車': '🚕', '的士': '🚕',
                        '警車': '🚓',
                        '救護車': '🚑',
                        '消防車': '🚒',
                        '腳踏車': '🚲', '自行車': '🚲',
                        '三輪車': '🛺'
                    }
                    emoji = emoji_map.get(name, '🚗')
                    
                    vehicle_class = VehicleClass(
                        class_id=i,
                        name=name,
                        emoji=emoji,
                        shortcut_key=str(i+1),  # ID+1格式
                        description=""
                    )
                    self.classes[i] = vehicle_class
            
            self.next_id = len(self.classes)
            self.save_classes()
            return True
            
        except Exception as e:
            print(f"匯入車種清單失敗: {e}")
            return False
    
    def reorder_classes(self, new_order: List[int]):
        """重新排序車種類別
        
        Args:
            new_order: 新的順序，包含所有 class_id 的列表
        """
        if len(new_order) != len(self.classes):
            raise ValueError("新順序必須包含所有現有車種")
        
        # 檢查是否包含所有現有 class_id
        existing_ids = set(self.classes.keys())
        new_ids = set(new_order)
        if existing_ids != new_ids:
            raise ValueError("新順序必須包含所有現有車種 ID")
        
        # 創建新的映射
        old_classes = self.classes.copy()
        self.classes = {}
        
        # 重新分配 class_id
        for new_id, old_id in enumerate(new_order):
            old_class = old_classes[old_id]
            old_class.class_id = new_id
            self.classes[new_id] = old_class
        
        # 更新 next_id
        self.next_id = len(self.classes)
        self.save_classes()
    
    def move_class(self, class_id: int, direction: str):
        """移動車種位置
        
        Args:
            class_id: 要移動的車種 ID
            direction: 移動方向，'up' 或 'down'
        """
        if class_id not in self.classes:
            raise ValueError(f"車種 ID {class_id} 不存在")
        
        # 獲取當前排序
        sorted_classes = self.get_all_classes()
        current_index = None
        
        for i, cls in enumerate(sorted_classes):
            if cls.class_id == class_id:
                current_index = i
                break
        
        if current_index is None:
            return
        
        # 計算新位置
        if direction == 'up' and current_index > 0:
            new_index = current_index - 1
        elif direction == 'down' and current_index < len(sorted_classes) - 1:
            new_index = current_index + 1
        else:
            return  # 無法移動
        
        # 交換位置
        sorted_classes[current_index], sorted_classes[new_index] = \
            sorted_classes[new_index], sorted_classes[current_index]
        
        # 生成新的順序列表
        new_order = [cls.class_id for cls in sorted_classes]
        self.reorder_classes(new_order)
    
    def sort_classes_by_name(self, ascending: bool = True):
        """按名稱排序車種"""
        sorted_classes = sorted(
            self.get_all_classes(),
            key=lambda x: x.name,
            reverse=not ascending
        )
        new_order = [cls.class_id for cls in sorted_classes]
        self.reorder_classes(new_order)
    
    def sort_classes_by_id(self, ascending: bool = True):
        """按 ID 排序車種"""
        sorted_classes = sorted(
            self.get_all_classes(),
            key=lambda x: x.class_id,
            reverse=not ascending
        )
        new_order = [cls.class_id for cls in sorted_classes]
        self.reorder_classes(new_order)


class VehicleClassManagerDialog(QDialog):
    """車種管理對話框"""
    
    classes_updated = pyqtSignal()  # 車種更新信號
    
    def __init__(self, class_manager: VehicleClassManager, parent=None):
        super().__init__(parent)
        self.class_manager = class_manager
        self.setWindowTitle('車種類別管理')
        self.setMinimumSize(1000, 800)  # 改為最小尺寸以支援適應性視窗
        self.resize(1200, 900)  # 設定預設大小

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

                QTableWidget {
                    background-color: white;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                }

                QLineEdit, QComboBox {
                    padding: 6px 8px;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    background-color: white;
                }

                QLineEdit:focus, QComboBox:focus {
                    border-color: #339af0;
                }
            """)

        # 設置鍵盤快捷鍵
        self.setup_keyboard_shortcuts()

        self.setup_ui()
        self.load_classes_list()

    def setup_keyboard_shortcuts(self):
        """設置鍵盤快捷鍵"""
        # 新增車種 (Ctrl+N)
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.add_new_class)

        # 編輯車種 (F2 或 Enter)
        QShortcut(QKeySequence("F2"), self).activated.connect(self.edit_selected_class)
        QShortcut(QKeySequence("Return"), self).activated.connect(self.edit_selected_class)

        # 刪除車種 (Delete 或 Ctrl+D)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.delete_selected_class)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self.delete_selected_class)

        # 搜尋 (Ctrl+F)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.focus_search)

        # 全選 (Ctrl+A)
        QShortcut(QKeySequence("Ctrl+A"), self).activated.connect(self.select_all_classes)

        # 取消全選 (Escape)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self.select_none_classes)

        # 移動車種 (Ctrl+Up/Down)
        QShortcut(QKeySequence("Ctrl+Up"), self).activated.connect(self.move_class_up)
        QShortcut(QKeySequence("Ctrl+Down"), self).activated.connect(self.move_class_down)

        # 批次操作 (Ctrl+Shift+E/D)
        QShortcut(QKeySequence("Ctrl+Shift+E"), self).activated.connect(lambda: self.batch_edit_classes(True))
        QShortcut(QKeySequence("Ctrl+Shift+D"), self).activated.connect(lambda: self.batch_edit_classes(False))

        # 排序 (Ctrl+S)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.show_sort_menu)

        # 儲存變更 (Ctrl+Enter)
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.apply_changes)

        # 關閉對話框 (Ctrl+W)
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.reject)

    def focus_search(self):
        """聚焦到搜尋框"""
        if hasattr(self, 'search_edit'):
            self.search_edit.setFocus()
            self.search_edit.selectAll()

    def show_sort_menu(self):
        """顯示排序選單"""
        if hasattr(self, 'sort_menu_btn'):
            self.sort_menu_btn.showMenu()

    def keyPressEvent(self, event):
        """處理鍵盤事件"""
        # 方向鍵導航
        if event.key() == Qt.Key_Up:
            current_row = self.class_table.currentRow()
            if current_row > 0:
                self.class_table.selectRow(current_row - 1)
                event.accept()
                return
        elif event.key() == Qt.Key_Down:
            current_row = self.class_table.currentRow()
            if current_row < self.class_table.rowCount() - 1:
                self.class_table.selectRow(current_row + 1)
                event.accept()
                return

        # 呼叫父類方法處理其他按鍵
        super().keyPressEvent(event)
    
    def setup_ui(self):
        """設定使用者介面"""
        layout = QVBoxLayout(self)
        
        # 創建分頁介面
        tab_widget = QTabWidget()
        
        # 車種管理分頁
        manage_tab = self.create_manage_tab()
        tab_widget.addTab(manage_tab, "🚗 車種管理")
        
        # COCO設定分頁
        coco_tab = self.create_coco_tab()
        tab_widget.addTab(coco_tab, "🎯 COCO設定")
        
        # 匯入匯出分頁
        import_export_tab = self.create_import_export_tab()
        tab_widget.addTab(import_export_tab, "📁 匯入匯出")
        
        # 預設模板分頁
        templates_tab = self.create_templates_tab()
        tab_widget.addTab(templates_tab, "📋 預設模板")
        
        layout.addWidget(tab_widget)
        
        # 底部按鈕
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_changes)
        layout.addWidget(button_box)
    
    def create_manage_tab(self) -> QWidget:
        """創建車種管理分頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 搜尋和過濾區域
        search_layout = QHBoxLayout()

        # 搜尋框
        search_label = QLabel("🔍 搜尋:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("輸入車種名稱、表情或快捷鍵...")
        self.search_edit.textChanged.connect(self.filter_classes)

        # 過濾選項
        filter_label = QLabel("篩選:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部", "啟用的", "停用的"])
        self.filter_combo.currentTextChanged.connect(self.filter_classes)

        # 清除搜尋按鈕
        self.clear_search_btn = QPushButton("🗑️ 清除")
        self.clear_search_btn.clicked.connect(self.clear_search)
        self.clear_search_btn.setEnabled(False)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(filter_label)
        search_layout.addWidget(self.filter_combo)
        # 幫助按鈕
        help_btn = QPushButton("❓ 幫助")
        help_btn.clicked.connect(self.show_help_dialog)
        search_layout.addWidget(help_btn)

        search_layout.addStretch()

        layout.addLayout(search_layout)

        # 主內容區域
        content_layout = QHBoxLayout()

        # 左側：車種清單
        left_panel = QGroupBox("車種清單")
        left_layout = QVBoxLayout(left_panel)

        # 批次操作按鈕
        batch_layout = QHBoxLayout()

        self.select_all_btn = QPushButton("☑️ 全選")
        self.select_all_btn.clicked.connect(self.select_all_classes)
        batch_layout.addWidget(self.select_all_btn)

        self.select_none_btn = QPushButton("☐ 全不選")
        self.select_none_btn.clicked.connect(self.select_none_classes)
        batch_layout.addWidget(self.select_none_btn)

        self.batch_enable_btn = QPushButton("✅ 批次啟用")
        self.batch_enable_btn.clicked.connect(lambda: self.batch_edit_classes(True))
        batch_layout.addWidget(self.batch_enable_btn)

        self.batch_disable_btn = QPushButton("❌ 批次停用")
        self.batch_disable_btn.clicked.connect(lambda: self.batch_edit_classes(False))
        batch_layout.addWidget(self.batch_disable_btn)

        batch_layout.addStretch()

        left_layout.addLayout(batch_layout)

        # 車種表格
        self.class_table = QTableWidget()
        self.class_table.setColumnCount(6)
        self.class_table.setHorizontalHeaderLabels([
            "ID", "表情", "名稱", "快捷鍵", "顏色", "啟用"
        ])

        # 啟用拖放排序
        self.class_table.setDragDropMode(QTableWidget.InternalMove)
        self.class_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.class_table.setSelectionMode(QTableWidget.ExtendedSelection)  # 支援多選
        self.class_table.setDragDropOverwriteMode(False)

        # 設定欄寬
        header = self.class_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # 表情
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 名稱
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # 快捷鍵
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # 顏色
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # 啟用

        self.class_table.setColumnWidth(0, 50)   # ID
        self.class_table.setColumnWidth(1, 60)   # 表情
        self.class_table.setColumnWidth(3, 80)   # 快捷鍵
        self.class_table.setColumnWidth(4, 80)   # 顏色
        self.class_table.setColumnWidth(5, 60)   # 啟用

        self.class_table.itemSelectionChanged.connect(self.on_class_selected)

        # 連接拖放事件
        self.class_table.model().rowsMoved.connect(self.on_rows_moved)

        left_layout.addWidget(self.class_table)

        # 清單操作按鈕
        list_buttons = QHBoxLayout()

        self.add_btn = QPushButton("➕ 新增")
        self.add_btn.clicked.connect(self.add_new_class)
        list_buttons.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️ 編輯")
        self.edit_btn.clicked.connect(self.edit_selected_class)
        self.edit_btn.setEnabled(False)
        list_buttons.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑️ 刪除")
        self.delete_btn.clicked.connect(self.delete_selected_class)
        self.delete_btn.setEnabled(False)
        list_buttons.addWidget(self.delete_btn)

        list_buttons.addStretch()

        # 排序按鈕
        sort_menu_btn = QPushButton("📶 排序")
        sort_menu = self.create_sort_menu()
        sort_menu_btn.setMenu(sort_menu)
        list_buttons.addWidget(sort_menu_btn)

        self.move_up_btn = QPushButton("⬆️")
        self.move_up_btn.setToolTip("向上移動")
        self.move_up_btn.clicked.connect(self.move_class_up)
        self.move_up_btn.setEnabled(False)
        list_buttons.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton("⬇️")
        self.move_down_btn.setToolTip("向下移動")
        self.move_down_btn.clicked.connect(self.move_class_down)
        self.move_down_btn.setEnabled(False)
        list_buttons.addWidget(self.move_down_btn)

        left_layout.addLayout(list_buttons)

        # 右側：詳細設定
        right_panel = QGroupBox("車種詳細設定")
        right_layout = QFormLayout(right_panel)

        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self.on_detail_changed)
        right_layout.addRow("車種名稱:", self.name_edit)

        self.emoji_edit = QLineEdit()
        self.emoji_edit.setMaxLength(2)
        self.emoji_edit.textChanged.connect(self.on_detail_changed)
        right_layout.addRow("表情符號:", self.emoji_edit)

        self.shortcut_edit = QLineEdit()
        self.shortcut_edit.setMaxLength(1)
        self.shortcut_edit.textChanged.connect(self.on_detail_changed)
        right_layout.addRow("快捷鍵:", self.shortcut_edit)

        # 顏色選擇
        color_layout = QHBoxLayout()
        self.color_label = QLabel("    ")
        self.color_label.setStyleSheet("background-color: red; border: 1px solid black;")
        self.color_label.setFixedSize(30, 20)

        self.color_btn = QPushButton("選擇顏色")
        self.color_btn.clicked.connect(self.choose_color)

        color_layout.addWidget(self.color_label)
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()

        right_layout.addRow("標註顏色:", color_layout)

        self.enabled_cb = QCheckBox("啟用此車種")
        self.enabled_cb.stateChanged.connect(self.on_detail_changed)
        right_layout.addRow("", self.enabled_cb)

        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.textChanged.connect(self.on_detail_changed)
        right_layout.addRow("描述:", self.description_edit)

        # COCO類別資訊
        self.coco_info_label = QLabel("未關聯COCO類別")
        self.coco_info_label.setStyleSheet("color: #666; font-style: italic;")
        right_layout.addRow("COCO對應:", self.coco_info_label)
        
        # COCO類別選擇器
        coco_select_layout = QHBoxLayout()
        self.coco_select_combo = QComboBox()
        self.coco_select_combo.addItem("無", -1)
        for i, class_name in enumerate(COCO_CLASSES):
            emoji = COCO_EMOJI_MAP.get(class_name, "❓")
            self.coco_select_combo.addItem(f"{emoji} {class_name}", i)
        self.coco_select_combo.currentTextChanged.connect(self.on_coco_selection_changed)
        coco_select_layout.addWidget(self.coco_select_combo)
        coco_select_layout.addStretch()
        right_layout.addRow("更改COCO關聯:", coco_select_layout)

        # 將左右面板加入到分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 400])

        content_layout.addWidget(splitter)
        layout.addLayout(content_layout)

        # 追蹤是否有變更
        self.current_class_id = None
        self.details_changed = False

        # 搜尋和過濾相關變數
        self.all_classes_data = []  # 儲存所有車種資料用於過濾
        self.filtered_indices = []  # 過濾後的索引

        return widget

    def filter_classes(self):
        """過濾車種清單"""
        search_text = self.search_edit.text().strip().lower()
        filter_type = self.filter_combo.currentText()

        # 更新清除按鈕狀態
        self.clear_search_btn.setEnabled(bool(search_text or filter_type != "全部"))

        # 獲取所有車種資料
        if not self.all_classes_data:
            self.all_classes_data = []
            for row in range(self.class_table.rowCount()):
                row_data = []
                for col in range(self.class_table.columnCount()):
                    item = self.class_table.item(row, col)
                    if item:
                        row_data.append(item.text().lower())
                    else:
                        row_data.append("")
                # 添加啟用狀態
                enabled_item = self.class_table.item(row, 5)
                if enabled_item:
                    row_data.append(enabled_item.checkState() == Qt.Checked)
                else:
                    row_data.append(True)
                self.all_classes_data.append(row_data)

        # 應用過濾
        self.filtered_indices = []
        for i, row_data in enumerate(self.all_classes_data):
            # 搜尋過濾
            if search_text:
                searchable_text = " ".join(row_data[:-1])  # 不包含啟用狀態
                if search_text not in searchable_text:
                    continue

            # 類型過濾
            if filter_type == "啟用的" and not row_data[-1]:
                continue
            elif filter_type == "停用的" and row_data[-1]:
                continue

            self.filtered_indices.append(i)

        # 更新表格顯示
        self.update_filtered_display()

    def update_filtered_display(self):
        """更新過濾後的顯示"""
        # 隱藏所有行
        for row in range(self.class_table.rowCount()):
            self.class_table.setRowHidden(row, True)

        # 顯示過濾後的行
        for display_row, actual_row in enumerate(self.filtered_indices):
            self.class_table.setRowHidden(actual_row, False)

    def clear_search(self):
        """清除搜尋和過濾"""
        self.search_edit.clear()
        self.filter_combo.setCurrentText("全部")
        self.filter_classes()

    def select_all_classes(self):
        """全選車種"""
        self.class_table.setSelectionMode(QTableWidget.MultiSelection)
        for row in range(self.class_table.rowCount()):
            if not self.class_table.isRowHidden(row):
                self.class_table.selectRow(row)
        self.class_table.setSelectionMode(QTableWidget.SingleSelection)

    def select_none_classes(self):
        """取消全選"""
        self.class_table.clearSelection()

    def batch_edit_classes(self, enable: bool):
        """批次編輯車種啟用狀態"""
        selected_rows = set()
        for item in self.class_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.information(self, "沒有選擇", "請先選擇要批次編輯的車種")
            return

        # 確認操作
        action_text = "啟用" if enable else "停用"
        reply = QMessageBox.question(
            self, "批次編輯確認",
            f"確定要{action_text}選中的 {len(selected_rows)} 個車種嗎？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            updated_count = 0
            for row in selected_rows:
                # 獲取車種ID
                id_item = self.class_table.item(row, 0)
                if id_item:
                    class_id = id_item.data(Qt.UserRole)
                    try:
                        self.class_manager.update_class(class_id, enabled=enable)
                        # 更新表格顯示
                        enabled_item = self.class_table.item(row, 5)
                        if enabled_item:
                            enabled_item.setCheckState(Qt.Checked if enable else Qt.Unchecked)
                        updated_count += 1
                    except Exception as e:
                        print(f"更新車種 {class_id} 失敗: {e}")

            QMessageBox.information(
                self, "批次編輯完成",
                f"成功{action_text}了 {updated_count} 個車種"
            )

            # 重新載入以確保資料一致性
            self.load_classes_list()
            self.classes_updated.emit()

    def show_help_dialog(self):
        """顯示幫助對話框"""
        help_text = """
        <h3>🚗 車種類別管理 - 鍵盤快捷鍵</h3>

        <h4>📝 基本操作</h4>
        <ul>
        <li><b>Ctrl+N</b> - 新增車種</li>
        <li><b>F2</b> 或 <b>Enter</b> - 編輯選中的車種</li>
        <li><b>Delete</b> 或 <b>Ctrl+D</b> - 刪除選中的車種</li>
        <li><b>Ctrl+Enter</b> - 儲存變更</li>
        <li><b>Ctrl+W</b> - 關閉對話框</li>
        </ul>

        <h4>🔍 搜尋與過濾</h4>
        <ul>
        <li><b>Ctrl+F</b> - 聚焦到搜尋框</li>
        <li><b>Escape</b> - 清除搜尋並取消選擇</li>
        </ul>

        <h4>📋 選擇操作</h4>
        <ul>
        <li><b>Ctrl+A</b> - 全選車種</li>
        <li><b>↑/↓</b> - 方向鍵導航</li>
        </ul>

        <h4>🔄 排序與移動</h4>
        <ul>
        <li><b>Ctrl+Up</b> - 向上移動車種</li>
        <li><b>Ctrl+Down</b> - 向下移動車種</li>
        <li><b>Ctrl+S</b> - 開啟排序選單</li>
        </ul>

        <h4>⚡ 批次操作</h4>
        <ul>
        <li><b>Ctrl+Shift+E</b> - 批次啟用選中的車種</li>
        <li><b>Ctrl+Shift+D</b> - 批次停用選中的車種</li>
        </ul>

        <h4>💡 使用提示</h4>
        <ul>
        <li>支援多選進行批次操作</li>
        <li>拖拽行可以重新排序車種</li>
        <li>搜尋支援車種名稱、表情、快捷鍵</li>
        <li>所有變更都會自動儲存</li>
        </ul>
        """

        QMessageBox.information(self, "鍵盤快捷鍵幫助", help_text)

    def create_sort_menu(self) -> QMenu:
        """創建排序選單"""
        menu = QMenu()
        
        # 按名稱排序
        sort_name_asc = QAction("📝 按名稱排序 (A-Z)", self)
        sort_name_asc.triggered.connect(lambda: self.sort_classes_by_name(True))
        menu.addAction(sort_name_asc)
        
        sort_name_desc = QAction("📝 按名稱排序 (Z-A)", self)
        sort_name_desc.triggered.connect(lambda: self.sort_classes_by_name(False))
        menu.addAction(sort_name_desc)
        
        menu.addSeparator()
        
        # 按 ID 排序
        sort_id_asc = QAction("🔢 按 ID 排序 (0-9)", self)
        sort_id_asc.triggered.connect(lambda: self.sort_classes_by_id(True))
        menu.addAction(sort_id_asc)
        
        sort_id_desc = QAction("🔢 按 ID 排序 (9-0)", self)
        sort_id_desc.triggered.connect(lambda: self.sort_classes_by_id(False))
        menu.addAction(sort_id_desc)
        
        menu.addSeparator()
        
        # 重置為預設順序
        reset_order = QAction("🔄 重置為預設順序", self)
        reset_order.triggered.connect(self.reset_class_order)
        menu.addAction(reset_order)
        
        return menu
    
    def sort_classes_by_name(self, ascending: bool = True):
        """按名稱排序車種"""
        try:
            self.class_manager.sort_classes_by_name(ascending)
            self.load_classes_list()
            self.classes_updated.emit()
            
            order_text = "升序" if ascending else "降序"
            QMessageBox.information(
                self, "排序完成", 
                f"已按名稱 {order_text} 重新排序車種"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "排序失敗", f"排序過程發生錯誤：\n{str(e)}")
    
    def sort_classes_by_id(self, ascending: bool = True):
        """按 ID 排序車種"""
        try:
            self.class_manager.sort_classes_by_id(ascending)
            self.load_classes_list()
            self.classes_updated.emit()
            
            order_text = "升序" if ascending else "降序"
            QMessageBox.information(
                self, "排序完成", 
                f"已按 ID {order_text} 重新排序車種"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "排序失敗", f"排序過程發生錯誤：\n{str(e)}")
    
    def reset_class_order(self):
        """重置車種順序為預設"""
        reply = QMessageBox.question(
            self, "確認重置", 
            "確定要重置車種順序為預設順序嗎？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.class_manager.sort_classes_by_id(True)  # 按 ID 升序排列
                self.load_classes_list()
                self.classes_updated.emit()
                QMessageBox.information(self, "重置完成", "車種順序已重置為預設順序")
                
            except Exception as e:
                QMessageBox.critical(self, "重置失敗", f"重置過程發生錯誤：\n{str(e)}")
    
    def on_rows_moved(self, parent, start, end, destination, row):
        """處理行移動事件（拖放排序）"""
        try:
            # 獲取當前的車種順序
            classes = []
            for i in range(self.class_table.rowCount()):
                class_id = self.class_table.item(i, 0).data(Qt.UserRole)
                classes.append(class_id)
            
            # 使用新順序重新排列車種
            self.class_manager.reorder_classes(classes)
            
            # 重新載入以更新顯示
            self.load_classes_list()
            self.classes_updated.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "排序失敗", f"拖放排序時發生錯誤：\n{str(e)}")
            # 重新載入原始順序
            self.load_classes_list()
    
    def create_coco_tab(self) -> QWidget:
        """創建COCO設定分頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 說明文字
        info_label = QLabel(
            "設定要與YOLOv8 COCO模型連動的類別。\n"
            "選擇的類別將在AI辨識時被優先處理。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 10px; background-color: #f8f9fa; border-radius: 5px;")
        layout.addWidget(info_label)

        # 主要內容區域
        content_layout = QHBoxLayout()

        # 左側：COCO類別清單
        left_panel = QGroupBox("COCO 80種類別")
        left_layout = QVBoxLayout(left_panel)

        # 搜尋框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 搜尋:"))
        self.coco_search_edit = QLineEdit()
        self.coco_search_edit.setPlaceholderText("輸入類別名稱...")
        self.coco_search_edit.textChanged.connect(self.filter_coco_classes)
        search_layout.addWidget(self.coco_search_edit)
        left_layout.addLayout(search_layout)

        # 類別清單
        self.coco_list = QListWidget()
        self.coco_list.setSelectionMode(QAbstractItemView.MultiSelection)
        # self.load_coco_classes()  # 移到結尾執行
        left_layout.addWidget(self.coco_list)

        # 快速選擇按鈕
        quick_select_layout = QHBoxLayout()
        
        select_vehicle_btn = QPushButton("🚗 選擇車輛類別")
        select_vehicle_btn.clicked.connect(self.select_vehicle_classes)
        quick_select_layout.addWidget(select_vehicle_btn)
        
        select_all_btn = QPushButton("☑️ 全選")
        select_all_btn.clicked.connect(self.select_all_coco_classes)
        quick_select_layout.addWidget(select_all_btn)
        
        clear_selection_btn = QPushButton("☐ 清除選擇")
        clear_selection_btn.clicked.connect(self.clear_coco_selection)
        quick_select_layout.addWidget(clear_selection_btn)
        
        left_layout.addLayout(quick_select_layout)

        # 右側：選中類別和操作
        right_panel = QGroupBox("選中類別")
        right_layout = QVBoxLayout(right_panel)

        # 選中類別清單
        self.selected_coco_list = QListWidget()
        self.selected_coco_list.setMaximumHeight(200)
        right_layout.addWidget(self.selected_coco_list)

        # 操作按鈕
        operations_layout = QVBoxLayout()

        import_btn = QPushButton("📥 匯入選中類別")
        import_btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; padding: 10px; }")
        import_btn.clicked.connect(self.import_selected_coco_classes)
        operations_layout.addWidget(import_btn)

        sync_btn = QPushButton("🔄 同步到車種")
        sync_btn.setStyleSheet("QPushButton { background-color: #17a2b8; color: white; padding: 8px; }")
        sync_btn.clicked.connect(self.sync_coco_to_classes)
        operations_layout.addWidget(sync_btn)

        right_layout.addLayout(operations_layout)

        # 統計資訊
        stats_label = QLabel()
        self.update_coco_stats()
        right_layout.addWidget(stats_label)

        # 將左右面板加入分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 300])

        content_layout.addWidget(splitter)
        layout.addLayout(content_layout)

        # 儲存變數
        self.coco_stats_label = stats_label

        # 在所有UI元素創建完成後載入COCO類別
        self.load_coco_classes()

        return widget
    
    def load_coco_classes(self):
        """載入COCO類別到清單"""
        self.coco_list.clear()
        
        for i, class_name in enumerate(COCO_CLASSES):
            emoji = COCO_EMOJI_MAP.get(class_name, "❓")
            item_text = f"{emoji} {class_name} ({i})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, i)
            
            # 如果已經選中，預設選擇
            if i in self.class_manager.selected_coco_classes:
                item.setSelected(True)
            
            self.coco_list.addItem(item)
        
        self.update_selected_coco_display()
    
    def filter_coco_classes(self):
        """過濾COCO類別"""
        search_text = self.coco_search_edit.text().strip().lower()
        
        for i in range(self.coco_list.count()):
            item = self.coco_list.item(i)
            class_name = COCO_CLASSES[i]
            visible = search_text in class_name.lower()
            item.setHidden(not visible)
    
    def select_vehicle_classes(self):
        """選擇車輛相關的COCO類別"""
        self.coco_list.clearSelection()
        
        for i in range(self.coco_list.count()):
            item = self.coco_list.item(i)
            coco_id = item.data(Qt.UserRole)
            if coco_id in VEHICLE_COCO_INDICES:
                item.setSelected(True)
        
        self.update_selected_coco_display()
    
    def select_all_coco_classes(self):
        """全選COCO類別"""
        for i in range(self.coco_list.count()):
            item = self.coco_list.item(i)
            if not item.isHidden():
                item.setSelected(True)
        
        self.update_selected_coco_display()
    
    def clear_coco_selection(self):
        """清除COCO選擇"""
        self.coco_list.clearSelection()
        self.update_selected_coco_display()
    
    def update_selected_coco_display(self):
        """更新選中COCO類別的顯示"""
        self.selected_coco_list.clear()
        
        selected_items = []
        for i in range(self.coco_list.count()):
            item = self.coco_list.item(i)
            if item.isSelected():
                coco_id = item.data(Qt.UserRole)
                class_name = COCO_CLASSES[coco_id]
                emoji = COCO_EMOJI_MAP.get(class_name, "❓")
                selected_items.append(f"{emoji} {class_name}")
        
        for item_text in selected_items:
            self.selected_coco_list.addItem(item_text)
        
        self.update_coco_stats()
    
    def update_coco_stats(self):
        """更新COCO統計資訊"""
        selected_count = self.selected_coco_list.count()
        total_count = len(COCO_CLASSES)
        
        if hasattr(self, 'coco_stats_label'):
            self.coco_stats_label.setText(
                f"已選擇: {selected_count}/{total_count} 個類別\n"
                f"車輛類別: {len(VEHICLE_COCO_INDICES)} 個"
            )
    
    def import_selected_coco_classes(self):
        """匯入選中的COCO類別"""
        selected_coco_ids = []
        
        for i in range(self.coco_list.count()):
            item = self.coco_list.item(i)
            if item.isSelected():
                coco_id = item.data(Qt.UserRole)
                selected_coco_ids.append(coco_id)
        
        if not selected_coco_ids:
            QMessageBox.warning(self, "沒有選擇", "請先選擇要匯入的COCO類別")
            return
        
        reply = QMessageBox.question(
            self, "確認匯入",
            f"確定要匯入 {len(selected_coco_ids)} 個COCO類別嗎？\n\n"
            "這將覆蓋現有的車種設定。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.class_manager.import_from_coco(selected_coco_ids)
                self.class_manager.set_selected_coco_classes(selected_coco_ids)
                self.load_classes_list()
                self.clear_class_details()
                self.classes_updated.emit()
                
                QMessageBox.information(
                    self, "匯入成功", 
                    f"已成功匯入 {len(selected_coco_ids)} 個COCO類別！"
                )
                
            except Exception as e:
                QMessageBox.critical(self, "匯入失敗", f"匯入過程發生錯誤：\n{str(e)}")
    
    def sync_coco_to_classes(self):
        """同步COCO選擇到現有車種"""
        selected_coco_ids = []
        
        for i in range(self.coco_list.count()):
            item = self.coco_list.item(i)
            if item.isSelected():
                coco_id = item.data(Qt.UserRole)
                selected_coco_ids.append(coco_id)
        
        if not selected_coco_ids:
            QMessageBox.warning(self, "沒有選擇", "請先選擇要同步的COCO類別")
            return
        
        # 更新現有車種的COCO映射
        updated_count = 0
        for class_id, vehicle_class in self.class_manager.classes.items():
            # 嘗試找到匹配的COCO類別
            for coco_id in selected_coco_ids:
                coco_name = self.class_manager.get_coco_class_name(coco_id)
                if vehicle_class.name.lower() in coco_name.lower() or coco_name.lower() in vehicle_class.name.lower():
                    self.class_manager.update_class(class_id, coco_class_id=coco_id)
                    updated_count += 1
                    break
        
        self.class_manager.set_selected_coco_classes(selected_coco_ids)
        self.load_classes_list()
        self.classes_updated.emit()
        
        QMessageBox.information(
            self, "同步完成", 
            f"已同步 {updated_count} 個車種與COCO類別的對應關係"
        )
    
    def create_import_export_tab(self) -> QWidget:
        """創建匯入匯出分頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 匯出區域
        export_group = QGroupBox("匯出車種設定")
        export_layout = QVBoxLayout(export_group)
        
        export_info = QLabel(
            "匯出車種設定到不同格式的檔案，以便在其他專案中使用或備份。"
        )
        export_info.setWordWrap(True)
        export_layout.addWidget(export_info)
        
        export_buttons = QHBoxLayout()
        
        export_json_btn = QPushButton("📄 匯出 JSON 設定檔")
        export_json_btn.clicked.connect(self.export_json_config)
        export_buttons.addWidget(export_json_btn)
        
        export_txt_btn = QPushButton("📝 匯出 YOLO 類別檔")
        export_txt_btn.clicked.connect(self.export_txt_classes)
        export_buttons.addWidget(export_txt_btn)
        
        export_layout.addLayout(export_buttons)
        
        layout.addWidget(export_group)
        
        # 匯入區域
        import_group = QGroupBox("匯入車種設定")
        import_layout = QVBoxLayout(import_group)
        
        import_info = QLabel(
            "從其他檔案匯入車種設定。注意：匯入會覆蓋現有設定。"
        )
        import_info.setWordWrap(True)
        import_info.setStyleSheet("color: orange;")
        import_layout.addWidget(import_info)
        
        import_buttons = QHBoxLayout()
        
        import_json_btn = QPushButton("📁 匯入 JSON 設定檔")
        import_json_btn.clicked.connect(self.import_json_config)
        import_buttons.addWidget(import_json_btn)
        
        import_txt_btn = QPushButton("📂 匯入 YOLO 類別檔")
        import_txt_btn.clicked.connect(self.import_txt_classes)
        import_buttons.addWidget(import_txt_btn)
        
        import_layout.addLayout(import_buttons)
        
        layout.addWidget(import_group)
        
        layout.addStretch()
        
        return widget
    
    def create_templates_tab(self) -> QWidget:
        """創建預設模板分頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info_label = QLabel(
            "選擇預設的車種模板，快速設定常用的車種分類。"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 模板選項
        templates_group = QGroupBox("選擇模板")
        templates_layout = QVBoxLayout(templates_group)
        
        # 基本車種模板
        basic_btn = QPushButton("🚗 基本車種 (機車、汽車、卡車、公車)")
        basic_btn.clicked.connect(lambda: self.apply_template("basic"))
        templates_layout.addWidget(basic_btn)
        
        # 詳細車種模板
        detailed_btn = QPushButton("🚛 詳細車種 (包含特殊車輛)")
        detailed_btn.clicked.connect(lambda: self.apply_template("detailed"))
        templates_layout.addWidget(detailed_btn)
        
        # 交通工具模板
        transport_btn = QPushButton("🚲 所有交通工具 (包含非機動車)")
        transport_btn.clicked.connect(lambda: self.apply_template("transport"))
        templates_layout.addWidget(transport_btn)
        
        # 商用車模板
        commercial_btn = QPushButton("🚚 商用車專用")
        commercial_btn.clicked.connect(lambda: self.apply_template("commercial"))
        templates_layout.addWidget(commercial_btn)
        
        layout.addWidget(templates_group)
        
        # 預設模板說明
        template_info = QTextEdit()
        template_info.setReadOnly(True)
        template_info.setMaximumHeight(200)
        template_info.setText("""
模板說明：

🚗 基本車種：
• 機車、汽車、卡車、公車 (4類)
• 適合一般道路交通監控

🚛 詳細車種：
• 基本車種 + 計程車、警車、救護車、消防車 (8類)
• 適合城市交通分析

🚲 所有交通工具：
• 包含腳踏車、電動車、三輪車等 (12類)
• 適合完整的交通調查

🚚 商用車專用：
• 各種貨車、聯結車、工程車 (6類)
• 適合物流或工業區監控
        """)
        layout.addWidget(template_info)
        
        layout.addStretch()
        
        return widget
    
    def load_classes_list(self):
        """載入車種清單到表格"""
        classes = self.class_manager.get_all_classes()
        self.class_table.setRowCount(len(classes))

        # 重置搜尋和過濾相關變數
        self.all_classes_data = []
        self.filtered_indices = list(range(len(classes)))

        for row, vehicle_class in enumerate(classes):
            # ID
            id_item = QTableWidgetItem(str(vehicle_class.class_id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.class_table.setItem(row, 0, id_item)

            # 表情符號
            emoji_item = QTableWidgetItem(vehicle_class.emoji)
            self.class_table.setItem(row, 1, emoji_item)

            # 名稱
            name_item = QTableWidgetItem(vehicle_class.name)
            self.class_table.setItem(row, 2, name_item)

            # 快捷鍵
            shortcut_item = QTableWidgetItem(vehicle_class.shortcut_key)
            self.class_table.setItem(row, 3, shortcut_item)

            # 顏色
            color_item = QTableWidgetItem("■")
            color_item.setBackground(vehicle_class.color)
            color_item.setFlags(color_item.flags() & ~Qt.ItemIsEditable)
            self.class_table.setItem(row, 4, color_item)

            # 啟用狀態
            enabled_item = QTableWidgetItem("✓" if vehicle_class.enabled else "✗")
            enabled_item.setFlags(enabled_item.flags() & ~Qt.ItemIsEditable)
            self.class_table.setItem(row, 5, enabled_item)

            # 儲存類別 ID 到行資料
            self.class_table.item(row, 0).setData(Qt.UserRole, vehicle_class.class_id)

            # 收集搜尋資料
            self.all_classes_data.append([
                str(vehicle_class.class_id).lower(),
                vehicle_class.emoji.lower(),
                vehicle_class.name.lower(),
                vehicle_class.shortcut_key.lower(),
                "",  # 顏色不參與搜尋
                "啟用" if vehicle_class.enabled else "停用"
            ])

        # 確保所有行都顯示（重置過濾）
        for row in range(len(classes)):
            self.class_table.setRowHidden(row, False)
    
    def on_class_selected(self):
        """車種選擇變更"""
        selected_rows = set()
        for item in self.class_table.selectedItems():
            selected_rows.add(item.row())

        has_selection = len(selected_rows) > 0
        has_single_selection = len(selected_rows) == 1

        # 更新按鈕狀態
        self.edit_btn.setEnabled(has_single_selection)
        self.delete_btn.setEnabled(has_selection)
        self.batch_enable_btn.setEnabled(has_selection)
        self.batch_disable_btn.setEnabled(has_selection)

        # 移動按鈕只在單選時啟用
        if has_single_selection:
            current_row = list(selected_rows)[0]
            self.move_up_btn.setEnabled(current_row > 0)
            self.move_down_btn.setEnabled(current_row < self.class_table.rowCount() - 1)

            # 載入詳細資訊
            class_id = self.class_table.item(current_row, 0).data(Qt.UserRole)
            self.load_class_details(class_id)
        else:
            self.move_up_btn.setEnabled(False)
            self.move_down_btn.setEnabled(False)
            self.clear_details()

    def clear_details(self):
        """清除詳細資訊顯示"""
        self.name_edit.clear()
        self.emoji_edit.clear()
        self.shortcut_edit.clear()
        self.color_label.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6;")
        self.enabled_cb.setChecked(False)
        self.description_edit.clear()
        self.coco_info_label.setText("未關聯COCO類別")
        self.coco_info_label.setStyleSheet("color: #666; font-style: italic;")
        self.coco_select_combo.setCurrentIndex(0)  # 重置為"無"
        self.current_class_id = None
        self.details_changed = False

    def load_class_details(self, class_id: int):
        """載入車種詳細資訊"""
        vehicle_class = self.class_manager.get_class(class_id)
        if not vehicle_class:
            return
        
        self.current_class_id = class_id
        self.details_changed = False
        
        # 阻止信號避免觸發變更事件
        self.block_detail_signals(True)
        
        self.name_edit.setText(vehicle_class.name)
        self.emoji_edit.setText(vehicle_class.emoji)
        self.shortcut_edit.setText(vehicle_class.shortcut_key)
        self.enabled_cb.setChecked(vehicle_class.enabled)
        self.description_edit.setPlainText(vehicle_class.description)
        
        # 更新顏色顯示
        color_style = f"background-color: {vehicle_class.color.name()}; border: 1px solid black;"
        self.color_label.setStyleSheet(color_style)
        self.color_label.setProperty("color", vehicle_class.color)
        
        # 更新COCO資訊
        if vehicle_class.coco_class_id is not None:
            coco_name = self.class_manager.get_coco_class_name(vehicle_class.coco_class_id)
            emoji = self.class_manager.get_coco_class_emoji(vehicle_class.coco_class_id)
            self.coco_info_label.setText(f"{emoji} {coco_name} ({vehicle_class.coco_class_id})")
            self.coco_info_label.setStyleSheet("color: #28a745; font-weight: bold;")
        else:
            self.coco_info_label.setText("未關聯COCO類別")
            self.coco_info_label.setStyleSheet("color: #666; font-style: italic;")
        
        # 設定COCO選擇器
        if vehicle_class.coco_class_id is not None:
            # 找到對應的索引
            for i in range(self.coco_select_combo.count()):
                if self.coco_select_combo.itemData(i) == vehicle_class.coco_class_id:
                    self.coco_select_combo.setCurrentIndex(i)
                    break
        else:
            self.coco_select_combo.setCurrentIndex(0)  # 選擇"無"
        
        self.block_detail_signals(False)
    
    def clear_class_details(self):
        """清空車種詳細資訊"""
        self.current_class_id = None
        self.details_changed = False
        
        self.block_detail_signals(True)
        
        self.name_edit.clear()
        self.emoji_edit.clear()
        self.shortcut_edit.clear()
        self.enabled_cb.setChecked(False)
        self.description_edit.clear()
        self.color_label.setStyleSheet("background-color: red; border: 1px solid black;")
        self.coco_info_label.setText("未關聯COCO類別")
        self.coco_info_label.setStyleSheet("color: #666; font-style: italic;")
        self.coco_select_combo.setCurrentIndex(0)  # 重置為"無"
        
        self.block_detail_signals(False)
    
    def block_detail_signals(self, block: bool):
        """阻止詳細資訊的信號"""
        self.name_edit.blockSignals(block)
        self.emoji_edit.blockSignals(block)
        self.shortcut_edit.blockSignals(block)
        self.enabled_cb.blockSignals(block)
        self.description_edit.blockSignals(block)
        self.coco_select_combo.blockSignals(block)
    
    def on_detail_changed(self):
        """詳細資訊變更"""
        if self.current_class_id is not None:
            self.details_changed = True
    
    def on_coco_selection_changed(self):
        """COCO選擇器變更"""
        if self.current_class_id is not None:
            self.details_changed = True
    
    def choose_color(self):
        """選擇顏色"""
        current_color = self.color_label.property("color") or QColor(255, 75, 75)
        color = QColorDialog.getColor(current_color, self, "選擇標註顏色")
        
        if color.isValid():
            color_style = f"background-color: {color.name()}; border: 1px solid black;"
            self.color_label.setStyleSheet(color_style)
            self.color_label.setProperty("color", color)
            self.on_detail_changed()
    
    def add_new_class(self):
        """新增車種"""
        dialog = AddClassDialog(self.class_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_classes_list()
            self.classes_updated.emit()
    
    def edit_selected_class(self):
        """編輯選中的車種"""
        if self.current_class_id is not None:
            self.save_current_details()
    
    def save_current_details(self):
        """儲存當前的詳細資訊"""
        if self.current_class_id is None or not self.details_changed:
            return
        
        try:
            color = self.color_label.property("color") or QColor(255, 75, 75)
            
            # 獲取COCO選擇器的值
            coco_class_id = self.coco_select_combo.currentData()
            if coco_class_id == -1:
                coco_class_id = None
            
            self.class_manager.update_class(
                class_id=self.current_class_id,
                name=self.name_edit.text().strip(),
                emoji=self.emoji_edit.text(),
                shortcut_key=self.shortcut_edit.text(),
                color=color,
                enabled=self.enabled_cb.isChecked(),
                description=self.description_edit.toPlainText(),
                coco_class_id=coco_class_id
            )
            
            self.details_changed = False
            self.load_classes_list()
            self.classes_updated.emit()
            
        except ValueError as e:
            QMessageBox.warning(self, "更新失敗", str(e))
    
    def delete_selected_class(self):
        """刪除選中的車種"""
        if self.current_class_id is None:
            return
        
        vehicle_class = self.class_manager.get_class(self.current_class_id)
        if not vehicle_class:
            return
        
        reply = QMessageBox.question(
            self, "確認刪除",
            f"確定要刪除車種 '{vehicle_class.name}' 嗎？\n\n"
            "警告：這將影響已有的標註資料！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.class_manager.delete_class(self.current_class_id)
                self.load_classes_list()
                self.clear_class_details()
                self.classes_updated.emit()
                
            except ValueError as e:
                QMessageBox.critical(self, "刪除失敗", str(e))
    
    def move_class_up(self):
        """向上移動車種"""
        current_row = self.class_table.currentRow()
        if current_row <= 0:
            return
            
        # 獲取當前車種的 ID
        current_class_id = self.class_table.item(current_row, 0).data(Qt.UserRole)
        
        try:
            # 使用車種管理器的移動方法
            self.class_manager.move_class(current_class_id, 'up')
            
            # 重新載入列表並選擇移動後的位置
            self.load_classes_list()
            self.class_table.selectRow(current_row - 1)
            self.classes_updated.emit()
            
        except ValueError as e:
            QMessageBox.warning(self, "移動失敗", str(e))
    
    def move_class_down(self):
        """向下移動車種"""
        current_row = self.class_table.currentRow()
        if current_row < 0 or current_row >= self.class_table.rowCount() - 1:
            return
            
        # 獲取當前車種的 ID
        current_class_id = self.class_table.item(current_row, 0).data(Qt.UserRole)
        
        try:
            # 使用車種管理器的移動方法
            self.class_manager.move_class(current_class_id, 'down')
            
            # 重新載入列表並選擇移動後的位置
            self.load_classes_list()
            self.class_table.selectRow(current_row + 1)
            self.classes_updated.emit()
            
        except ValueError as e:
            QMessageBox.warning(self, "移動失敗", str(e))
    
    def _swap_classes(self, class_id1: int, class_id2: int):
        """交換兩個車種的 class_id"""
        if class_id1 not in self.class_manager.classes or class_id2 not in self.class_manager.classes:
            return
            
        # 獲取兩個車種物件
        class1 = self.class_manager.classes[class_id1]
        class2 = self.class_manager.classes[class_id2]
        
        # 交換 class_id
        class1.class_id, class2.class_id = class2.class_id, class1.class_id
        
        # 更新字典中的映射
        self.class_manager.classes[class1.class_id] = class1
        self.class_manager.classes[class2.class_id] = class2
        
        # 儲存變更
        self.class_manager.save_classes()
    
    def export_json_config(self):
        """匯出 JSON 設定檔"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "匯出車種設定", "vehicle_classes.json",
            "JSON 檔案 (*.json);;所有檔案 (*)"
        )
        
        if filename:
            try:
                # 直接複製配置檔案
                import shutil
                shutil.copy2(self.class_manager.config_file, filename)
                QMessageBox.information(self, "匯出成功", f"車種設定已匯出至：\n{filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "匯出失敗", f"匯出過程發生錯誤：\n{str(e)}")
    
    def export_txt_classes(self):
        """匯出 YOLO 類別檔"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "匯出類別清單", "classes.txt",
            "文字檔案 (*.txt);;所有檔案 (*)"
        )
        
        if filename:
            if self.class_manager.export_classes_txt(filename):
                QMessageBox.information(self, "匯出成功", f"類別清單已匯出至：\n{filename}")
            else:
                QMessageBox.critical(self, "匯出失敗", "匯出類別清單時發生錯誤")
    
    def import_json_config(self):
        """匯入 JSON 設定檔"""
        reply = QMessageBox.warning(
            self, "確認匯入",
            "匯入設定檔將覆蓋現有的車種設定！\n\n是否繼續？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        filename, _ = QFileDialog.getOpenFileName(
            self, "匯入車種設定", "",
            "JSON 檔案 (*.json);;所有檔案 (*)"
        )
        
        if filename:
            try:
                # 備份現有設定
                backup_file = self.class_manager.config_file + ".backup"
                import shutil
                shutil.copy2(self.class_manager.config_file, backup_file)
                
                # 替換設定檔
                shutil.copy2(filename, self.class_manager.config_file)
                
                # 重新載入
                self.class_manager.load_classes()
                self.load_classes_list()
                self.clear_class_details()
                self.classes_updated.emit()
                
                QMessageBox.information(
                    self, "匯入成功", 
                    f"車種設定已匯入成功！\n\n原設定已備份至：\n{backup_file}"
                )
                
            except Exception as e:
                QMessageBox.critical(self, "匯入失敗", f"匯入過程發生錯誤：\n{str(e)}")
    
    def import_txt_classes(self):
        """匯入 YOLO 類別檔"""
        reply = QMessageBox.warning(
            self, "確認匯入",
            "匯入類別檔將覆蓋現有的車種設定！\n\n是否繼續？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        filename, _ = QFileDialog.getOpenFileName(
            self, "匯入類別清單", "",
            "文字檔案 (*.txt);;所有檔案 (*)"
        )
        
        if filename:
            if self.class_manager.import_classes_txt(filename):
                self.load_classes_list()
                self.clear_class_details()
                self.classes_updated.emit()
                QMessageBox.information(self, "匯入成功", "類別清單已匯入成功！")
            else:
                QMessageBox.critical(self, "匯入失敗", "匯入類別清單時發生錯誤")
    
    def apply_template(self, template_name: str):
        """應用預設模板"""
        reply = QMessageBox.question(
            self, "確認套用模板",
            f"套用模板將覆蓋現有的車種設定！\n\n是否繼續？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        templates = {
            "basic": [
                {'name': '機車', 'emoji': '🏍', 'shortcut_key': '1'},
                {'name': '汽車', 'emoji': '🚗', 'shortcut_key': '2'},
                {'name': '卡車', 'emoji': '🚛', 'shortcut_key': '3'},
                {'name': '公車', 'emoji': '🚌', 'shortcut_key': '4'},
            ],
            "detailed": [
                {'name': '機車', 'emoji': '🏍', 'shortcut_key': '1'},
                {'name': '汽車', 'emoji': '🚗', 'shortcut_key': '2'},
                {'name': '卡車', 'emoji': '🚛', 'shortcut_key': '3'},
                {'name': '公車', 'emoji': '🚌', 'shortcut_key': '4'},
                {'name': '計程車', 'emoji': '🚕', 'shortcut_key': '5'},
                {'name': '警車', 'emoji': '🚓', 'shortcut_key': '6'},
                {'name': '救護車', 'emoji': '🚑', 'shortcut_key': '7'},
                {'name': '消防車', 'emoji': '🚒', 'shortcut_key': '8'},
            ],
            "transport": [
                {'name': '機車', 'emoji': '🏍', 'shortcut_key': '1'},
                {'name': '汽車', 'emoji': '🚗', 'shortcut_key': '2'},
                {'name': '卡車', 'emoji': '🚛', 'shortcut_key': '3'},
                {'name': '公車', 'emoji': '🚌', 'shortcut_key': '4'},
                {'name': '腳踏車', 'emoji': '🚲', 'shortcut_key': '5'},
                {'name': '電動車', 'emoji': '🔋', 'shortcut_key': '6'},
                {'name': '三輪車', 'emoji': '🛺', 'shortcut_key': '7'},
                {'name': '計程車', 'emoji': '🚕', 'shortcut_key': '8'},
            ],
            "commercial": [
                {'name': '小貨車', 'emoji': '🚚', 'shortcut_key': '1'},
                {'name': '中型貨車', 'emoji': '🚛', 'shortcut_key': '2'},
                {'name': '大型貨車', 'emoji': '🚛', 'shortcut_key': '3'},
                {'name': '聯結車', 'emoji': '🚛', 'shortcut_key': '4'},
                {'name': '工程車', 'emoji': '🚜', 'shortcut_key': '5'},
                {'name': '混凝土車', 'emoji': '🚚', 'shortcut_key': '6'},
            ]
        }
        
        template_classes = templates.get(template_name, [])
        if not template_classes:
            return
        
        try:
            # 清除現有類別
            self.class_manager.classes = {}
            self.class_manager.next_id = 0
            
            # 添加模板類別
            for i, cls_data in enumerate(template_classes):
                vehicle_class = VehicleClass(
                    class_id=i,
                    name=cls_data['name'],
                    emoji=cls_data['emoji'],
                    shortcut_key=cls_data['shortcut_key']
                )
                self.class_manager.classes[i] = vehicle_class
            
            self.class_manager.next_id = len(template_classes)
            self.class_manager.save_classes()
            
            self.load_classes_list()
            self.clear_class_details()
            self.classes_updated.emit()
            
            QMessageBox.information(self, "套用成功", f"已成功套用 {template_name} 模板！")
            
        except Exception as e:
            QMessageBox.critical(self, "套用失敗", f"套用模板時發生錯誤：\n{str(e)}")
    
    def apply_changes(self):
        """套用變更"""
        if self.details_changed:
            self.save_current_details()
        QMessageBox.information(self, "變更已套用", "所有變更已儲存")
    
    def accept(self):
        """接受對話框"""
        if self.details_changed:
            self.save_current_details()
        super().accept()


class AddClassDialog(QDialog):
    """新增車種對話框"""
    
    def __init__(self, class_manager: VehicleClassManager, parent=None):
        super().__init__(parent)
        self.class_manager = class_manager
        self.setWindowTitle('新增車種')
        self.setFixedSize(450, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QFormLayout(self)
        
        # 車種名稱
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如：電動車")
        layout.addRow("車種名稱 *:", self.name_edit)
        
        # 表情符號
        self.emoji_edit = QLineEdit()
        self.emoji_edit.setMaxLength(2)
        self.emoji_edit.setPlaceholderText("🚗")
        self.emoji_edit.setText("🚗")
        layout.addRow("表情符號:", self.emoji_edit)
        
        # 快捷鍵（自動生成ID+1）
        self.shortcut_edit = QLineEdit()
        self.shortcut_edit.setMaxLength(1)
        self.shortcut_edit.setPlaceholderText("自動生成 (ID+1)")
        self.shortcut_edit.setEnabled(False)  # 禁用手動輸入
        layout.addRow("快捷鍵:", self.shortcut_edit)
        
        # COCO類別選擇
        coco_layout = QHBoxLayout()
        self.coco_combo = QComboBox()
        self.coco_combo.addItem("無", -1)
        for i, class_name in enumerate(COCO_CLASSES):
            emoji = COCO_EMOJI_MAP.get(class_name, "❓")
            self.coco_combo.addItem(f"{emoji} {class_name}", i)
        self.coco_combo.currentTextChanged.connect(self.on_coco_selected)
        coco_layout.addWidget(self.coco_combo)
        coco_layout.addStretch()
        layout.addRow("對應COCO類別:", coco_layout)
        
        # 顏色選擇
        color_layout = QHBoxLayout()
        self.color_label = QLabel("    ")
        self.current_color = QColor(255, 75, 75)
        self.color_label.setStyleSheet(f"background-color: {self.current_color.name()}; border: 1px solid black;")
        self.color_label.setFixedSize(30, 20)
        
        self.color_btn = QPushButton("選擇顏色")
        self.color_btn.clicked.connect(self.choose_color)
        
        color_layout.addWidget(self.color_label)
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        
        layout.addRow("標註顏色:", color_layout)
        
        # 描述
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("車種描述（可選）")
        layout.addRow("描述:", self.description_edit)
        
        # 按鈕
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_dialog)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
    
    def on_coco_selected(self):
        """當選擇COCO類別時"""
        current_data = self.coco_combo.currentData()
        if current_data >= 0:
            class_name = COCO_CLASSES[current_data]
            emoji = COCO_EMOJI_MAP.get(class_name, "🚗")
            
            # 自動填入名稱和表情符號
            if not self.name_edit.text().strip():
                self.name_edit.setText(class_name)
            if not self.emoji_edit.text().strip() or self.emoji_edit.text() == "🚗":
                self.emoji_edit.setText(emoji)
    
    def choose_color(self):
        """選擇顏色"""
        color = QColorDialog.getColor(self.current_color, self, "選擇標註顏色")
        if color.isValid():
            self.current_color = color
            self.color_label.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
    
    def accept_dialog(self):
        """接受對話框"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "輸入錯誤", "請輸入車種名稱")
            return
        
        coco_class_id = self.coco_combo.currentData()
        if coco_class_id == -1:
            coco_class_id = None
        
        try:
            self.class_manager.add_class(
                name=name,
                color=self.current_color,
                description=self.description_edit.toPlainText(),
                emoji=self.emoji_edit.text() or "🚗",
                coco_class_id=coco_class_id
            )
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "新增失敗", str(e))


# 使用範例
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    # 創建車種管理器
    manager = VehicleClassManager()
    
    # 顯示管理對話框
    dialog = VehicleClassManagerDialog(manager)
    dialog.show()
    
    sys.exit(app.exec_())
