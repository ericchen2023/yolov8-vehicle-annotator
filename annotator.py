from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor, QCursor, QFont, QBrush
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QPoint

# 預設車種類別（向後相容）
VEHICLE_CLASSES = [
    ('機車', 0),
    ('汽車', 1),
    ('卡車', 2),
    ('公車', 3)
]

# 預設車種顏色映射
DEFAULT_CLASS_COLORS = {
    0: QColor(255, 75, 75),    # 機車 - 亮紅色
    1: QColor(75, 255, 75),    # 汽車 - 亮綠色
    2: QColor(75, 150, 255),   # 卡車 - 亮藍色
    3: QColor(255, 215, 0),    # 公車 - 金黃色
}

class AnnotatorLabel(QLabel):
    rects_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.image = None
        self.scaled_image = None
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.rects = []  # [{'id': int, 'rect': QRect, 'class_id': int, 'class_name': str}]
        self.current_rect = None
        self.setMouseTracking(True)
        self.next_id = 1
        self.class_id = 0
        self.class_name = VEHICLE_CLASSES[0][0]
        
        # 縮放和拖拽相關
        self.scale_factor = 1.0
        self.min_scale = 0.1
        self.max_scale = 5.0
        self.image_offset = QPoint(0, 0)
        self.last_pan_point = None
        self.panning = False
        
        # 選中的標註
        self.selected_rect_id = None
        self.hover_rect_id = None
        
        # 車種顏色映射（可動態更新）
        self.class_colors = DEFAULT_CLASS_COLORS.copy()
        
        # 顯示選項
        self.show_labels = True  # 顯示ID和分類標籤
        self.show_ids = True     # 顯示ID
        self.show_classes = True # 顯示分類名稱
        
        # 標註框編輯功能
        self.editing_mode = None  # None, 'move', 'resize_tl', 'resize_tr', 'resize_bl', 'resize_br', 'resize_t', 'resize_b', 'resize_l', 'resize_r'
        self.edit_start_point = None
        self.edit_original_rect = None
        self.resize_handle_size = 6  # 調整手柄大小
        
        # 設定背景
        self.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                border: 1px solid #555;
            }
        """)

    def update_class_colors(self, color_mapping):
        """更新車種顏色映射"""
        self.class_colors.update(color_mapping)
        self.repaint()  # 重新繪製以應用新顏色
    
    def get_class_color(self, class_id):
        """取得車種顏色"""
        return self.class_colors.get(class_id, QColor(255, 75, 75))
    
    def set_show_labels(self, show_labels):
        """設定是否顯示標籤"""
        self.show_labels = show_labels
        self.repaint()
    
    def set_show_ids(self, show_ids):
        """設定是否顯示ID"""
        self.show_ids = show_ids
        self.repaint()
    
    def set_show_classes(self, show_classes):
        """設定是否顯示分類名稱"""
        self.show_classes = show_classes
        self.repaint()
    
    def set_image(self, image_input, image_path=None):
        # 支持兩種輸入：圖片路徑字符串或QPixmap/QImage對象
        if isinstance(image_input, str):
            # 如果是字符串，當作圖片路徑處理
            self.image = QPixmap(image_input)
            if self.image.isNull():
                raise Exception(f"無法載入圖片: {image_input}")
        elif isinstance(image_input, QPixmap):
            # 如果是QPixmap，直接使用
            self.image = image_input
        elif hasattr(image_input, 'size'):
            # 如果是QImage，轉換為QPixmap
            self.image = QPixmap.fromImage(image_input)
        else:
            raise Exception("不支援的圖片輸入類型")
        
        # 檢查圖片是否有效
        if self.image.isNull():
            raise Exception("圖片載入失敗或圖片為空")
        
        self.rects = []
        self.current_rect = None
        self.next_id = 1
        self.scale_factor = 1.0
        self.image_offset = QPoint(0, 0)
        self.selected_rect_id = None
        self.hover_rect_id = None
        self.fit_to_window()
        self.repaint()

    def fit_to_window(self):
        if self.image:
            widget_size = self.size()
            image_size = self.image.size()
            
            # 檢查是否有有效的尺寸
            if (widget_size.width() <= 0 or widget_size.height() <= 0 or 
                image_size.width() <= 0 or image_size.height() <= 0):
                self.scale_factor = 1.0
                self.image_offset = QPoint(0, 0)
                self.update_scaled_image()
                return
            
            scale_x = widget_size.width() / image_size.width()
            scale_y = widget_size.height() / image_size.height()
            self.scale_factor = min(scale_x, scale_y) * 0.95  # 留一些邊距
            
            self.image_offset = QPoint(0, 0)
            self.update_scaled_image()

    def update_scaled_image(self):
        if self.image:
            # 確保scale_factor是有效的
            if self.scale_factor <= 0:
                self.scale_factor = 1.0
                
            scaled_size = self.image.size() * self.scale_factor
            self.scaled_image = self.image.scaled(scaled_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def get_image_rect(self):
        if not self.scaled_image:
            return QRect()
        
        widget_rect = self.rect()
        image_rect = self.scaled_image.rect()
        
        # 圖片在 widget 中央，加上偏移
        x = (widget_rect.width() - image_rect.width()) // 2 + self.image_offset.x()
        y = (widget_rect.height() - image_rect.height()) // 2 + self.image_offset.y()
        
        return QRect(x, y, image_rect.width(), image_rect.height())

    def widget_to_image_coords(self, widget_point):
        """將 widget 座標轉換為原始圖片座標"""
        if not self.image or not self.scaled_image:
            return widget_point
        
        image_rect = self.get_image_rect()
        if not image_rect.contains(widget_point):
            return None
        
        # 相對於縮放圖片的座標
        relative_x = (widget_point.x() - image_rect.x()) / self.scale_factor
        relative_y = (widget_point.y() - image_rect.y()) / self.scale_factor
        
        return QPoint(int(relative_x), int(relative_y))

    def image_to_widget_coords(self, image_point):
        """將原始圖片座標轉換為 widget 座標"""
        if not self.image or not self.scaled_image:
            return image_point
        
        image_rect = self.get_image_rect()
        
        widget_x = int(image_point.x() * self.scale_factor + image_rect.x())
        widget_y = int(image_point.y() * self.scale_factor + image_rect.y())
        
        return QPoint(widget_x, widget_y)

    def set_class(self, class_id, class_name):
        self.class_id = class_id
        self.class_name = class_name

    def wheelEvent(self, event):
        if self.image:
            # 滑鼠滾輪縮放
            delta = event.angleDelta().y()
            zoom_factor = 1.15 if delta > 0 else 1/1.15
            
            old_scale = self.scale_factor
            self.scale_factor = max(self.min_scale, min(self.max_scale, self.scale_factor * zoom_factor))
            
            if self.scale_factor != old_scale:
                # 以滑鼠位置為中心縮放
                mouse_pos = event.pos()
                self.zoom_at_point(mouse_pos, self.scale_factor / old_scale)
                
    def zoom_at_point(self, point, zoom_factor):
        # 計算縮放前的圖片中心
        old_image_rect = self.get_image_rect()
        
        # 更新縮放圖片
        self.update_scaled_image()
        
        # 計算新的偏移，使縮放中心保持在滑鼠位置
        new_image_rect = self.get_image_rect()
        
        # 調整偏移
        scale_diff = zoom_factor - 1.0
        offset_x = (point.x() - old_image_rect.center().x()) * scale_diff
        offset_y = (point.y() - old_image_rect.center().y()) * scale_diff
        
        self.image_offset.setX(self.image_offset.x() - int(offset_x))
        self.image_offset.setY(self.image_offset.y() - int(offset_y))
        
        self.repaint()

    def mousePressEvent(self, event):
        if not self.image:
            return
            
        if event.button() == Qt.LeftButton:
            image_point = self.widget_to_image_coords(event.pos())
            if image_point:
                # 優先檢查是否點擊了選中標註的調整手柄
                selected_item = self.get_selected_rect_item()
                if selected_item:
                    handle_type = self.get_resize_handle_at_point(event.pos(), selected_item)
                    if handle_type:
                        # 開始編輯模式
                        self.editing_mode = handle_type
                        self.edit_start_point = image_point
                        self.edit_original_rect = QRect(selected_item['rect'])
                        self.setCursor(self.get_cursor_for_handle(handle_type))
                        return
                
                # 檢查是否點擊了現有標註
                clicked_rect_id = self.get_rect_at_point(image_point)
                if clicked_rect_id:
                    self.selected_rect_id = clicked_rect_id
                    self.editing_mode = None
                    self.repaint()
                else:
                    # 開始繪製新標註
                    self.drawing = True
                    self.start_point = image_point
                    self.end_point = image_point
                    self.current_rect = None
                    self.selected_rect_id = None
                    self.editing_mode = None
        
        elif event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier):
            # 開始拖拽圖片
            self.panning = True
            self.last_pan_point = event.pos()
            self.setCursor(QCursor(Qt.ClosedHandCursor))

    def mouseMoveEvent(self, event):
        if not self.image:
            return
            
        if self.panning and self.last_pan_point:
            # 拖拽圖片
            delta = event.pos() - self.last_pan_point
            self.image_offset += delta
            self.last_pan_point = event.pos()
            self.repaint()
            return
            
        if self.editing_mode and self.edit_start_point:
            # 編輯標註框
            image_point = self.widget_to_image_coords(event.pos())
            if image_point:
                self.update_rect_during_edit(image_point)
                self.repaint()
            return
            
        if self.drawing and self.start_point:
            # 繪製新標註框
            image_point = self.widget_to_image_coords(event.pos())
            if image_point:
                self.end_point = image_point
                self.current_rect = QRect(self.start_point, self.end_point).normalized()
                self.repaint()
        else:
            # 檢查滑鼠懸停和游標更新
            image_point = self.widget_to_image_coords(event.pos())
            if image_point:
                # 優先檢查選中標註的調整手柄
                selected_item = self.get_selected_rect_item()
                if selected_item:
                    handle_type = self.get_resize_handle_at_point(event.pos(), selected_item)
                    if handle_type:
                        self.setCursor(self.get_cursor_for_handle(handle_type))
                        return
                
                # 檢查其他標註
                hover_id = self.get_rect_at_point(image_point)
                if hover_id != self.hover_rect_id:
                    self.hover_rect_id = hover_id
                    self.setCursor(QCursor(Qt.PointingHandCursor) if hover_id else QCursor(Qt.ArrowCursor))
                    self.repaint()
            else:
                # 滑鼠在圖片外
                if self.hover_rect_id is not None:
                    self.hover_rect_id = None
                    self.setCursor(QCursor(Qt.ArrowCursor))
                    self.repaint()
    
    def update_rect_during_edit(self, current_point):
        """在編輯過程中更新標註框"""
        selected_item = self.get_selected_rect_item()
        if not selected_item or not self.edit_original_rect:
            return
            
        original_rect = self.edit_original_rect
        dx = current_point.x() - self.edit_start_point.x()
        dy = current_point.y() - self.edit_start_point.y()
        
        new_rect = QRect(original_rect)
        
        if self.editing_mode == 'move':
            # 移動整個標註框
            new_rect.translate(dx, dy)
            
        elif self.editing_mode == 'resize_tl':
            # 左上角調整
            new_rect.setTopLeft(original_rect.topLeft() + QPoint(dx, dy))
            
        elif self.editing_mode == 'resize_tr':
            # 右上角調整
            new_rect.setTopRight(original_rect.topRight() + QPoint(dx, dy))
            
        elif self.editing_mode == 'resize_bl':
            # 左下角調整  
            new_rect.setBottomLeft(original_rect.bottomLeft() + QPoint(dx, dy))
            
        elif self.editing_mode == 'resize_br':
            # 右下角調整
            new_rect.setBottomRight(original_rect.bottomRight() + QPoint(dx, dy))
            
        elif self.editing_mode == 'resize_t':
            # 上邊調整
            new_rect.setTop(original_rect.top() + dy)
            
        elif self.editing_mode == 'resize_b':
            # 下邊調整
            new_rect.setBottom(original_rect.bottom() + dy)
            
        elif self.editing_mode == 'resize_l':
            # 左邊調整
            new_rect.setLeft(original_rect.left() + dx)
            
        elif self.editing_mode == 'resize_r':
            # 右邊調整
            new_rect.setRight(original_rect.right() + dx)
        
        # 確保標註框最小尺寸
        if new_rect.width() < 10:
            if self.editing_mode in ['resize_l', 'resize_tl', 'resize_bl']:
                new_rect.setLeft(new_rect.right() - 10)
            else:
                new_rect.setRight(new_rect.left() + 10)
                
        if new_rect.height() < 10:
            if self.editing_mode in ['resize_t', 'resize_tl', 'resize_tr']:
                new_rect.setTop(new_rect.bottom() - 10)
            else:
                new_rect.setBottom(new_rect.top() + 10)
        
        # 確保標註框在圖片範圍內
        if self.image:
            image_bounds = QRect(0, 0, self.image.width(), self.image.height())
            new_rect = new_rect.intersected(image_bounds)
        
        # 更新標註框
        new_rect = new_rect.normalized()
        selected_item['rect'] = new_rect

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.panning:
                self.panning = False
                self.last_pan_point = None
                self.setCursor(QCursor(Qt.ArrowCursor))
                
            elif self.editing_mode and self.edit_start_point:
                # 完成編輯
                self.editing_mode = None
                self.edit_start_point = None
                self.edit_original_rect = None
                self.setCursor(QCursor(Qt.ArrowCursor))
                self.repaint()
                # 通知父窗口標註已改變
                self.rects_updated.emit()
                
            elif self.drawing and self.image and self.start_point and self.end_point:
                rect = QRect(self.start_point, self.end_point).normalized()
                if rect.width() > 10 and rect.height() > 10:
                    self.rects.append({
                        'id': self.next_id,
                        'rect': rect,
                        'class_id': self.class_id,
                        'class_name': self.class_name
                    })
                    self.selected_rect_id = self.next_id
                    self.next_id += 1
                    self.rects_updated.emit()
                
                self.drawing = False
                self.current_rect = None
                self.repaint()
            
        elif event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier):
            # 結束拖拽
            self.panning = False
            self.setCursor(QCursor(Qt.ArrowCursor))
            
        elif event.button() == Qt.RightButton:
            if self.editing_mode:
                # 取消編輯
                self.editing_mode = None
                self.edit_start_point = None
                self.edit_original_rect = None
                self.setCursor(QCursor(Qt.ArrowCursor))
                self.repaint()

    def get_rect_at_point(self, point):
        """獲取在指定點的標註ID"""
        for item in reversed(self.rects):  # 從最後繪製的開始檢查
            if item['rect'].contains(point):
                return item['id']
        return None
    
    def get_resize_handle_at_point(self, point, rect_item):
        """獲取調整手柄類型"""
        if not rect_item:
            return None
            
        # 獲取圖片顯示區域
        image_rect = self.get_image_rect()
        widget_rect = self.image_rect_to_widget_rect(rect_item['rect'], image_rect)
        
        handle_size = self.resize_handle_size
        x, y, w, h = widget_rect.x(), widget_rect.y(), widget_rect.width(), widget_rect.height()
        px, py = point.x(), point.y()
        
        # 檢查八個調整手柄
        handles = {
            'resize_tl': QRect(x - handle_size//2, y - handle_size//2, handle_size, handle_size),         # 左上
            'resize_tr': QRect(x + w - handle_size//2, y - handle_size//2, handle_size, handle_size),    # 右上  
            'resize_bl': QRect(x - handle_size//2, y + h - handle_size//2, handle_size, handle_size),    # 左下
            'resize_br': QRect(x + w - handle_size//2, y + h - handle_size//2, handle_size, handle_size), # 右下
            'resize_t': QRect(x + w//2 - handle_size//2, y - handle_size//2, handle_size, handle_size),  # 上中
            'resize_b': QRect(x + w//2 - handle_size//2, y + h - handle_size//2, handle_size, handle_size), # 下中
            'resize_l': QRect(x - handle_size//2, y + h//2 - handle_size//2, handle_size, handle_size),  # 左中
            'resize_r': QRect(x + w - handle_size//2, y + h//2 - handle_size//2, handle_size, handle_size), # 右中
        }
        
        for handle_type, handle_rect in handles.items():
            if handle_rect.contains(point):
                return handle_type
                
        # 檢查是否在標註框內部（移動模式）
        if widget_rect.contains(point):
            return 'move'
            
        return None
    
    def get_cursor_for_handle(self, handle_type):
        """根據調整手柄類型獲取對應的游標"""
        cursor_map = {
            'resize_tl': Qt.SizeFDiagCursor,    # 左上到右下
            'resize_tr': Qt.SizeBDiagCursor,    # 右上到左下
            'resize_bl': Qt.SizeBDiagCursor,    # 左下到右上  
            'resize_br': Qt.SizeFDiagCursor,    # 右下到左上
            'resize_t': Qt.SizeVerCursor,       # 垂直
            'resize_b': Qt.SizeVerCursor,       # 垂直
            'resize_l': Qt.SizeHorCursor,       # 水平
            'resize_r': Qt.SizeHorCursor,       # 水平
            'move': Qt.SizeAllCursor            # 移動
        }
        return QCursor(cursor_map.get(handle_type, Qt.ArrowCursor))
    
    def get_selected_rect_item(self):
        """獲取當前選中的標註項"""
        if self.selected_rect_id:
            for item in self.rects:
                if item['id'] == self.selected_rect_id:
                    return item
        return None

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.scaled_image:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 繪製圖片
        image_rect = self.get_image_rect()
        painter.drawPixmap(image_rect, self.scaled_image)
        
        # 繪製標註框
        for item in self.rects:
            self.draw_annotation(painter, item, image_rect)
        
        # 繪製正在繪製的標註框
        if self.current_rect:
            color = self.get_class_color(self.class_id)
            pen = QPen(color, 2, Qt.DashLine)
            painter.setPen(pen)
            # 確保正在繪製的標註框也不填充
            painter.setBrush(QBrush(Qt.NoBrush))
            widget_rect = self.image_rect_to_widget_rect(self.current_rect, image_rect)
            painter.drawRect(widget_rect)

    def draw_annotation(self, painter, item, image_rect):
        """繪製單個標註"""
        base_color = self.get_class_color(item['class_id'])
        
        # 判斷標註狀態
        is_selected = item['id'] == self.selected_rect_id
        is_hover = item['id'] == self.hover_rect_id
        
        # 為邊框創建專用顏色（避免影響標籤）
        border_color = QColor(base_color)
        
        # 設定邊框樣式
        if is_selected:
            pen = QPen(border_color, 3)
        elif is_hover:
            pen = QPen(border_color, 2)
        else:
            # 只對邊框顏色設透明度，不影響原始顏色
            border_color.setAlpha(180)
            pen = QPen(border_color, 2)
        
        painter.setPen(pen)
        # 確保不填充標註框內部
        painter.setBrush(QBrush(Qt.NoBrush))
        
        # 轉換座標並繪製標註框（只繪製邊框，不填充）
        widget_rect = self.image_rect_to_widget_rect(item['rect'], image_rect)
        painter.drawRect(widget_rect)
        
        # 如果是選中的標註，繪製調整手柄
        if is_selected:
            self.draw_resize_handles(painter, widget_rect, base_color)
        
        # 繪製標籤背景（使用原始顏色，確保標籤清晰）
        if self.show_labels and (self.show_ids or self.show_classes):
            # 構建標籤文字
            label_parts = []
            if self.show_ids:
                label_parts.append(f"ID:{item['id']}")
            if self.show_classes:
                label_parts.append(item['class_name'])
            
            if label_parts:  # 只有當有內容要顯示時才繪製標籤
                label_text = " ".join(label_parts)
                
                font = QFont("Arial", max(8, int(10 * self.scale_factor)))
                painter.setFont(font)
                
                text_rect = painter.fontMetrics().boundingRect(label_text)
                
                # 標籤背景位置
                label_bg = QRect(
                    widget_rect.x(),
                    widget_rect.y() - text_rect.height() - 4,
                    text_rect.width() + 8,
                    text_rect.height() + 4
                )
                
                # 使用原始顏色繪製標籤背景（確保不透明）
                label_color = QColor(base_color)
                label_color.setAlpha(255)  # 確保標籤背景完全不透明
                painter.fillRect(label_bg, label_color)
                
                # 繪製標籤文字
                painter.setPen(QPen(Qt.white, 1))
                text_x = label_bg.x() + 4
                text_y = label_bg.y() + text_rect.height() + 2
                painter.drawText(text_x, text_y, label_text)
        
    def draw_resize_handles(self, painter, rect, color):
        """繪製調整手柄"""
        handle_size = self.resize_handle_size
        handle_color = QColor(color)
        handle_color.setAlpha(255)  # 確保手柄完全不透明
        
        painter.setPen(QPen(Qt.white, 1))
        painter.setBrush(QBrush(handle_color))
        
        # 8個調整手柄的位置
        handles = [
            # 四個角
            QRect(rect.left() - handle_size // 2, rect.top() - handle_size // 2, handle_size, handle_size),  # 左上
            QRect(rect.right() - handle_size // 2, rect.top() - handle_size // 2, handle_size, handle_size),  # 右上
            QRect(rect.left() - handle_size // 2, rect.bottom() - handle_size // 2, handle_size, handle_size),  # 左下
            QRect(rect.right() - handle_size // 2, rect.bottom() - handle_size // 2, handle_size, handle_size),  # 右下
            # 四個邊中點
            QRect(rect.center().x() - handle_size // 2, rect.top() - handle_size // 2, handle_size, handle_size),  # 上
            QRect(rect.center().x() - handle_size // 2, rect.bottom() - handle_size // 2, handle_size, handle_size),  # 下
            QRect(rect.left() - handle_size // 2, rect.center().y() - handle_size // 2, handle_size, handle_size),  # 左
            QRect(rect.right() - handle_size // 2, rect.center().y() - handle_size // 2, handle_size, handle_size),  # 右
        ]
        
        for handle in handles:
            painter.drawRect(handle)

    def image_rect_to_widget_rect(self, image_rect, image_display_rect):
        """將圖片座標的矩形轉換為 widget 座標"""
        x = int(image_rect.x() * self.scale_factor + image_display_rect.x())
        y = int(image_rect.y() * self.scale_factor + image_display_rect.y())
        w = int(image_rect.width() * self.scale_factor)
        h = int(image_rect.height() * self.scale_factor)
        return QRect(x, y, w, h)

    def get_rects(self):
        return self.rects

    def clear_rects(self):
        self.rects = []
        self.next_id = 1
        self.selected_rect_id = None
        self.hover_rect_id = None
        self.repaint()

    def delete_rect_by_id(self, rect_id):
        self.rects = [r for r in self.rects if r['id'] != rect_id]
        if self.selected_rect_id == rect_id:
            self.selected_rect_id = None
        if self.hover_rect_id == rect_id:
            self.hover_rect_id = None
        self.repaint()
        
    def delete_selected_rect(self):
        """刪除選中的標註"""
        if self.selected_rect_id:
            self.delete_rect_by_id(self.selected_rect_id)
            self.rects_updated.emit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image:
            self.update_scaled_image()
