"""
AI輔助標註模組 - 使用YOLOv8進行自動預標註
支援功能：
- 自動車輛檢測與預標註
- 智慧邊界框優化
- 批次處理與確認
- 信心度過濾
"""

import os
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox

try:
    import torch
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("警告: YOLOv8未安裝，AI功能將被禁用")

class AIPredictor(QThread):
    """AI預測執行緒"""
    prediction_completed = pyqtSignal(str, list)  # 圖片路徑, 預測結果
    prediction_progress = pyqtSignal(int, int)     # 當前, 總數
    prediction_error = pyqtSignal(str, str)       # 圖片路徑, 錯誤訊息

    def __init__(self):
        super().__init__()
        self.model = None
        self.image_paths = []
        self.confidence_threshold = 0.5
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # 車種管理器引用
        self.vehicle_class_manager = None
        
        # 更嚴格的檢測參數
        self.iou_threshold = 0.3  # 降低IoU閾值，獲得更精確的框
        self.confidence_threshold = 0.3  # 降低信心度閾值，檢測更多目標
        self.agnostic_nms = True  # 啟用類別無關的NMS

    def set_vehicle_class_manager(self, manager):
        """設置車種管理器"""
        self.vehicle_class_manager = manager

    def load_model(self, model_path: str = None) -> bool:
        """載入YOLO模型"""
        try:
            if not YOLO_AVAILABLE:
                return False
                
            if model_path and os.path.exists(model_path):
                # 載入自訂模型
                self.model = YOLO(model_path)
            else:
                # 載入預訓練模型
                self.model = YOLO('yolov8x.pt')  # 使用nano版本，速度較快
                
            self.model.to(self.device)
            return True
            
        except Exception as e:
            print(f"載入模型失敗: {e}")
            return False

    def set_prediction_params(self, confidence: float = 0.5, iou: float = 0.45):
        """設定預測參數"""
        self.confidence_threshold = confidence
        self.iou_threshold = iou

    def add_images(self, image_paths: List[str]):
        """添加要處理的圖片"""
        self.image_paths = image_paths

    def run(self):
        """執行AI預測"""
        if not self.model or not self.image_paths:
            return

        total_images = len(self.image_paths)
        
        for i, image_path in enumerate(self.image_paths):
            try:
                # 執行預測 (使用更精確的參數)
                results = self.model.predict(
                    image_path, 
                    conf=self.confidence_threshold,  # 更低的信心度閾值
                    iou=self.iou_threshold,          # 更嚴格的IoU閾值
                    device=self.device,
                    verbose=False,
                    agnostic_nms=True,               # 類別無關的NMS
                    max_det=300,                     # 增加最大檢測數量
                    imgsz=640                        # 標準輸入尺寸
                )
                
                # 解析結果
                predictions = self.parse_predictions(results[0], image_path)
                
                # 發送結果
                self.prediction_completed.emit(image_path, predictions)
                self.prediction_progress.emit(i + 1, total_images)
                
            except Exception as e:
                self.prediction_error.emit(image_path, str(e))
                self.prediction_progress.emit(i + 1, total_images)

    def parse_predictions(self, result, image_path: str) -> List[Dict]:
        """解析YOLO預測結果"""
        predictions = []
        
        if result.boxes is None:
            return predictions
            
        boxes = result.boxes.xyxy.cpu().numpy()  # x1, y1, x2, y2
        confidences = result.boxes.conf.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy().astype(int)
        
        # 獲取COCO到車種的動態映射
        coco_to_vehicle_mapping = {}
        if self.vehicle_class_manager:
            coco_to_vehicle_mapping = self.vehicle_class_manager.get_coco_to_vehicle_mapping()
        
        for i, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
            # 只處理用戶設定了COCO ID的類別
            if cls not in coco_to_vehicle_mapping:
                continue
                
            x1, y1, x2, y2 = box
            width = x2 - x1
            height = y2 - y1
            
            # 過濾太小的檢測框 (可能是誤檢)
            if width < 20 or height < 20:
                continue
                    
            # 使用動態映射獲取車種ID
            vehicle_class_id = coco_to_vehicle_mapping[cls]
            
            # 獲取車種資訊
            vehicle_class = self.vehicle_class_manager.get_class(vehicle_class_id)
            if not vehicle_class:
                continue
                
            class_name = vehicle_class.name
            emoji = vehicle_class.emoji
            
            # 邊界框精細化 (使用邊緣檢測優化)
            optimized_bbox = SmartAnnotationOptimizer.optimize_bbox_with_edges(
                image_path, [int(x1), int(y1), int(width), int(height)]
            )
            
            prediction = {
                'bbox': optimized_bbox,
                'class_id': vehicle_class_id,
                'class_name': class_name,
                'emoji': emoji,
                'confidence': float(conf),
                'source': 'ai_prediction',
                'original_yolo_class': int(cls),
                'coco_class_id': int(cls)
            }
            predictions.append(prediction)
        
        return predictions


class SmartAnnotationOptimizer:
    """智慧標註優化器"""
    
    @staticmethod
    def optimize_bbox_with_edges(image_path: str, bbox: List[int]) -> List[int]:
        """使用多重邊緣檢測技術優化邊界框，使其更貼緊車輛"""
        try:
            # 讀取圖片
            img = cv2.imread(image_path)
            if img is None:
                return bbox
                
            x, y, w, h = bbox
            
            # 先檢查當前邊界框是否已經足夠貼緊
            if SmartAnnotationOptimizer._is_bbox_already_tight(img, bbox):
                print(f"邊界框已經貼緊，跳過優化: {bbox}")
                return bbox
            
            # 設定搜索margin - 根據框大小動態調整
            margin_x = max(2, min(10, int(w * 0.08)))  # 2-10像素，最多8%
            margin_y = max(2, min(10, int(h * 0.08)))
            
            search_x1 = max(0, x - margin_x)
            search_y1 = max(0, y - margin_y)
            search_x2 = min(img.shape[1], x + w + margin_x)
            search_y2 = min(img.shape[0], y + h + margin_y)
            
            # 裁剪搜索區域
            roi = img[search_y1:search_y2, search_x1:search_x2]
            
            # 多重邊緣檢測方法
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # 方法1: 自適應Canny邊緣檢測
            blur = cv2.GaussianBlur(gray, (3, 3), 0)
            high_threshold = np.percentile(blur, 90)  # 降低閾值，更敏感
            low_threshold = high_threshold * 0.3
            edges1 = cv2.Canny(blur, low_threshold, high_threshold)
            
            # 方法2: 使用Sobel算子
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            edges2 = np.sqrt(sobel_x**2 + sobel_y**2).astype(np.uint8)
            edges2 = cv2.threshold(edges2, 40, 255, cv2.THRESH_BINARY)[1]
            
            # 結合兩種邊緣檢測結果
            edges = cv2.bitwise_or(edges1, edges2)
            
            # 形態學操作 - 更小的kernel避免過度擴張
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # 尋找輪廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 選擇最合適的輪廓
                original_area = w * h
                best_contour = None
                best_score = float('inf')
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    # 只考慮面積在原框30%-120%之間的輪廓
                    if 0.3 * original_area <= area <= 1.2 * original_area:
                        # 計算輪廓與原始框的重疊度
                        cx, cy, cw, ch = cv2.boundingRect(contour)
                        contour_bbox = [search_x1 + cx, search_y1 + cy, cw, ch]
                        overlap = SmartAnnotationOptimizer._calculate_bbox_overlap(bbox, contour_bbox)
                        
                        # 選擇重疊度高且面積合適的輪廓
                        score = abs(area - original_area) / original_area + (1 - overlap)
                        if score < best_score and overlap > 0.5:  # 至少50%重疊
                            best_score = score
                            best_contour = contour
                
                if best_contour is not None:
                    # 獲取緊密邊界框
                    cx, cy, cw, ch = cv2.boundingRect(best_contour)
                    
                    # 轉換回原圖座標
                    optimized_x = search_x1 + cx
                    optimized_y = search_y1 + cy
                    optimized_w = cw
                    optimized_h = ch
                    
                    # 嚴格驗證優化結果
                    if SmartAnnotationOptimizer._validate_optimized_bbox(bbox, [optimized_x, optimized_y, optimized_w, optimized_h]):
                        print(f"邊界框優化成功: {bbox} -> [{optimized_x}, {optimized_y}, {optimized_w}, {optimized_h}]")
                        return [optimized_x, optimized_y, optimized_w, optimized_h]
            
            print(f"邊界框無需優化，保持原狀: {bbox}")
            return bbox
            
        except Exception as e:
            print(f"邊界框優化失敗: {e}")
            return bbox
    
    @staticmethod
    def _is_bbox_already_tight(img, bbox: List[int]) -> bool:
        """檢查邊界框是否已經足夠貼緊"""
        try:
            x, y, w, h = bbox
            
            # 檢查邊界框周圍的像素變化
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 在邊界框邊緣取樣
            top_edge = gray[max(0, y-1):y+1, x:x+w] if y > 0 else None
            bottom_edge = gray[y+h-1:min(img.shape[0], y+h+1), x:x+w] if y+h < img.shape[0] else None
            left_edge = gray[y:y+h, max(0, x-1):x+1] if x > 0 else None
            right_edge = gray[y:y+h, x+w-1:min(img.shape[1], x+w+1)] if x+w < img.shape[1] else None
            
            # 計算邊緣變化
            edge_changes = 0
            total_pixels = 0
            
            for edge in [top_edge, bottom_edge, left_edge, right_edge]:
                if edge is not None and edge.size > 0:
                    # 計算梯度
                    if edge.shape[0] > 1 and edge.shape[1] > 1:
                        gradient = np.abs(np.gradient(edge.astype(float)))
                        edge_changes += np.sum(gradient[0] > 10) + np.sum(gradient[1] > 10)
                        total_pixels += edge.size
            
            # 如果邊緣變化足夠（表示框已經貼緊物體邊緣），則認為已經貼緊
            if total_pixels > 0:
                edge_ratio = edge_changes / total_pixels
                return edge_ratio > 0.15  # 15%以上的像素有明顯變化
            
            return False
            
        except Exception:
            return False
    
    @staticmethod
    def _calculate_bbox_overlap(bbox1: List[int], bbox2: List[int]) -> float:
        """計算兩個邊界框的重疊比例"""
        try:
            x1, y1, w1, h1 = bbox1
            x2, y2, w2, h2 = bbox2
            
            # 計算交集
            inter_x1 = max(x1, x2)
            inter_y1 = max(y1, y2)
            inter_x2 = min(x1 + w1, x2 + w2)
            inter_y2 = min(y1 + h1, y2 + h2)
            
            if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
                return 0.0
            
            inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
            area1 = w1 * h1
            
            return inter_area / area1 if area1 > 0 else 0.0
            
        except Exception:
            return 0.0
    
    @staticmethod
    def _validate_optimized_bbox(original_bbox: List[int], optimized_bbox: List[int]) -> bool:
        """驗證優化後的邊界框是否合理"""
        try:
            ox, oy, ow, oh = original_bbox
            nx, ny, nw, nh = optimized_bbox
            
            # 檢查尺寸變化是否合理（不應該變化太大）
            width_ratio = nw / ow if ow > 0 else 0
            height_ratio = nh / oh if oh > 0 else 0
            
            # 寬高比例應該在50%-150%之間
            if not (0.5 <= width_ratio <= 1.5) or not (0.5 <= height_ratio <= 1.5):
                return False
            
            # 檢查位置變化（中心點不應該偏移太遠）
            orig_center_x = ox + ow / 2
            orig_center_y = oy + oh / 2
            new_center_x = nx + nw / 2
            new_center_y = ny + nh / 2
            
            center_shift = ((new_center_x - orig_center_x) ** 2 + (new_center_y - orig_center_y) ** 2) ** 0.5
            max_shift = min(ow, oh) * 0.3  # 最大偏移不超過原框較小邊的30%
            
            if center_shift > max_shift:
                return False
            
            # 檢查重疊度
            overlap = SmartAnnotationOptimizer._calculate_bbox_overlap(original_bbox, optimized_bbox)
            if overlap < 0.6:  # 至少60%重疊
                return False
                
            return True
            
        except Exception:
            return False

    @staticmethod
    def filter_overlapping_predictions(predictions: List[Dict], iou_threshold: float = 0.5) -> List[Dict]:
        """過濾重疊的預測結果"""
        if len(predictions) <= 1:
            return predictions
            
        # 按信心度排序
        sorted_predictions = sorted(predictions, key=lambda x: x['confidence'], reverse=True)
        
        filtered = []
        for pred in sorted_predictions:
            # 檢查是否與已選擇的預測重疊
            is_duplicate = False
            for selected in filtered:
                if SmartAnnotationOptimizer.calculate_iou(pred['bbox'], selected['bbox']) > iou_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(pred)
                
        return filtered

    @staticmethod
    def calculate_iou(box1: List[int], box2: List[int]) -> float:
        """計算兩個邊界框的IoU"""
        x1_1, y1_1, w1, h1 = box1
        x2_1 = x1_1 + w1
        y2_1 = y1_1 + h1
        
        x1_2, y1_2, w2, h2 = box2
        x2_2 = x1_2 + w2
        y2_2 = y1_2 + h2
        
        # 計算交集區域
        inter_x1 = max(x1_1, x1_2)
        inter_y1 = max(y1_1, y1_2)
        inter_x2 = min(x2_1, x2_2)
        inter_y2 = min(y2_1, y2_2)
        
        if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
            return 0.0
            
        inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
        
        # 計算聯集區域
        area1 = w1 * h1
        area2 = w2 * h2
        union_area = area1 + area2 - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0


class AIAssistant(QObject):
    """AI輔助標註管理器"""
    
    prediction_ready = pyqtSignal(str, list)  # 圖片路徑, 建議標註
    batch_completed = pyqtSignal(dict)        # 批次處理結果
    status_updated = pyqtSignal(str)          # 狀態更新
    
    def __init__(self, vehicle_class_manager=None):
        super().__init__()
        self.predictor = AIPredictor()
        self.optimizer = SmartAnnotationOptimizer()
        
        # 設置車種管理器
        if vehicle_class_manager:
            self.set_vehicle_class_manager(vehicle_class_manager)
        
        # 連接信號
        self.predictor.prediction_completed.connect(self.on_prediction_completed)
        self.predictor.prediction_progress.connect(self.on_prediction_progress)
        self.predictor.prediction_error.connect(self.on_prediction_error)
        
        # 設定參數 (更精確的預設值)
        self.auto_optimize_bbox = True
        self.filter_overlapping = True
        self.min_confidence = 0.4        # 降低最小信心度，捕捉更多目標
        self.max_detections = 100        # 增加最大檢測數量
        self.iou_filter_threshold = 0.4  # IoU過濾閾值
        
        # 車輛特定優化參數
        self.vehicle_size_filters = {
            'min_width': 15,   # 最小寬度像素
            'min_height': 15,  # 最小高度像素
            'max_width': 2000, # 最大寬度像素
            'max_height': 1500 # 最大高度像素
        }
        
        # 統計資料
        self.stats = {
            'total_predictions': 0,
            'accepted_predictions': 0,
            'rejected_predictions': 0,
            'optimized_boxes': 0
        }

    def set_vehicle_class_manager(self, manager):
        """設置車種管理器"""
        self.vehicle_class_manager = manager
        self.predictor.set_vehicle_class_manager(manager)

    def is_available(self) -> bool:
        """檢查AI功能是否可用"""
        return YOLO_AVAILABLE

    def initialize(self, model_path: str = None) -> bool:
        """初始化AI助手"""
        if not YOLO_AVAILABLE:
            return False
            
        success = self.predictor.load_model(model_path)
        if success:
            self.status_updated.emit("AI輔助功能已就緒")
        else:
            self.status_updated.emit("AI模型載入失敗")
        return success

    def predict_single_image(self, image_path: str, confidence: float = 0.4):
        """對單張圖片進行預測 (增強的車輛檢測)"""
        if not self.predictor.model:
            return
            
        # 車輛專用預處理
        if not self.preprocess_single_image(image_path):
            return
            
        # 設置更精確的參數
        self.predictor.set_prediction_params(confidence, iou=0.3)
        self.predictor.add_images([image_path])
        
        if not self.predictor.isRunning():
            self.predictor.start()
            
    def preprocess_single_image(self, image_path: str) -> bool:
        """單張圖片的車輛檢測預處理"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                self.status_updated.emit(f"無法讀取圖片: {image_path}")
                return False
                
            height, width = img.shape[:2]
            if width < 100 or height < 100:
                self.status_updated.emit(f"圖片尺寸過小: {width}x{height}")
                return False
                
            return True
        except Exception as e:
            self.status_updated.emit(f"圖片預處理錯誤: {e}")
            return False

    def predict_batch(self, image_paths: List[str], confidence: float = 0.4):
        """批次預測 (車輛專用優化)"""
        if not self.predictor.model or not image_paths:
            return
            
        # 預處理圖片列表，過濾無效圖片
        valid_images = []
        for image_path in image_paths:
            if self.preprocess_single_image(image_path):
                valid_images.append(image_path)
                
        if not valid_images:
            self.status_updated.emit("沒有有效的圖片可供處理")
            return
            
        # 設置更精確的參數
        self.predictor.set_prediction_params(confidence, iou=0.3)
        self.predictor.add_images(valid_images)
        
        if not self.predictor.isRunning():
            self.status_updated.emit(f"開始AI批次處理 {len(valid_images)} 張圖片...")
            self.predictor.start()

    def on_prediction_completed(self, image_path: str, predictions: List[Dict]):
        """處理預測完成"""
        self.stats['total_predictions'] += len(predictions)
        
        # 過濾重疊預測
        if self.filter_overlapping and predictions:
            predictions = self.optimizer.filter_overlapping_predictions(predictions)
        
        # 優化邊界框
        optimized_predictions = []
        for pred in predictions:
            if self.auto_optimize_bbox:
                original_bbox = pred['bbox']
                optimized_bbox = self.optimizer.optimize_bbox_with_edges(image_path, original_bbox)
                
                if optimized_bbox != original_bbox:
                    pred['bbox'] = optimized_bbox
                    pred['optimized'] = True
                    self.stats['optimized_boxes'] += 1
                else:
                    pred['optimized'] = False
            
            optimized_predictions.append(pred)
        
        # 發送結果
        self.prediction_ready.emit(image_path, optimized_predictions)

    def on_prediction_progress(self, current: int, total: int):
        """處理進度更新"""
        progress = int((current / total) * 100)
        self.status_updated.emit(f"AI處理進度: {current}/{total} ({progress}%)")

    def on_prediction_error(self, image_path: str, error: str):
        """處理預測錯誤"""
        self.status_updated.emit(f"AI預測錯誤: {os.path.basename(image_path)} - {error}")

    def accept_prediction(self, prediction: Dict):
        """接受AI預測"""
        self.stats['accepted_predictions'] += 1

    def reject_prediction(self, prediction: Dict):
        """拒絕AI預測"""
        self.stats['rejected_predictions'] += 1

    def get_stats(self) -> Dict:
        """獲取統計資料"""
        return self.stats.copy()

    def set_parameters(self, confidence: float = 0.5, auto_optimize: bool = True, 
                      filter_overlap: bool = True):
        """設定AI參數"""
        self.min_confidence = confidence
        self.auto_optimize_bbox = auto_optimize
        self.filter_overlapping = filter_overlap
        self.predictor.set_prediction_params(confidence)

    def cleanup(self):
        """清理資源"""
        if self.predictor.isRunning():
            self.predictor.quit()
            self.predictor.wait()
