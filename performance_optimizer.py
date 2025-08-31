"""
效能優化模組 - 大圖片載入優化、記憶體管理、多執行緒處理
"""

import os
import gc
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Callable, Any, Dict
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import QPixmap
from PIL import Image
import cv2
import numpy as np


class ImageCache:
    """圖片快取管理器"""
    
    def __init__(self, max_cache_size: int = 100 * 1024 * 1024):  # 100MB
        self.max_cache_size = max_cache_size
        self.cache = {}
        self.access_order = []
        self.current_size = 0
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[QPixmap]:
        """取得快取的圖片"""
        with self.lock:
            if key in self.cache:
                # 更新訪問順序
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache[key]['pixmap']
            return None
    
    def put(self, key: str, pixmap: QPixmap, size: int):
        """加入圖片到快取"""
        with self.lock:
            # 如果已存在，更新
            if key in self.cache:
                old_size = self.cache[key]['size']
                self.current_size -= old_size
                self.access_order.remove(key)
            
            # 檢查是否需要清理快取
            while self.current_size + size > self.max_cache_size and self.access_order:
                self._evict_oldest()
            
            # 加入新項目
            self.cache[key] = {
                'pixmap': pixmap,
                'size': size
            }
            self.current_size += size
            self.access_order.append(key)
    
    def _evict_oldest(self):
        """移除最舊的快取項目"""
        if self.access_order:
            oldest_key = self.access_order.pop(0)
            if oldest_key in self.cache:
                old_size = self.cache[oldest_key]['size']
                self.current_size -= old_size
                del self.cache[oldest_key]
    
    def clear(self):
        """清空快取"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            self.current_size = 0
            gc.collect()
    
    def get_stats(self) -> Dict:
        """取得快取統計"""
        with self.lock:
            return {
                'cache_count': len(self.cache),
                'current_size_mb': self.current_size / (1024 * 1024),
                'max_size_mb': self.max_cache_size / (1024 * 1024),
                'hit_ratio': getattr(self, '_hit_count', 0) / max(getattr(self, '_total_requests', 1), 1)
            }


class ImageLoader(QThread):
    """非同步圖片載入器"""
    
    image_loaded = pyqtSignal(str, QPixmap)  # 路徑, 圖片
    loading_progress = pyqtSignal(int, int)  # 當前, 總數
    loading_error = pyqtSignal(str, str)     # 路徑, 錯誤訊息
    
    def __init__(self, cache: ImageCache):
        super().__init__()
        self.cache = cache
        self.load_queue = queue.Queue()
        self.is_running = False
        self.current_priority_path = None
        
        # 預設載入參數
        self.max_display_size = (2000, 2000)  # 顯示用的最大尺寸
        self.thumbnail_size = (400, 400)      # 縮略圖尺寸
        
    def add_load_request(self, image_path: str, priority: bool = False):
        """添加載入請求"""
        if priority:
            self.current_priority_path = image_path
        self.load_queue.put((image_path, priority))
        
        if not self.is_running:
            self.start()
    
    def run(self):
        """執行載入任務"""
        self.is_running = True
        processed = 0
        total = self.load_queue.qsize()
        
        while not self.load_queue.empty():
            try:
                image_path, priority = self.load_queue.get(timeout=1)
                
                # 檢查快取
                cached_pixmap = self.cache.get(image_path)
                if cached_pixmap:
                    self.image_loaded.emit(image_path, cached_pixmap)
                    processed += 1
                    self.loading_progress.emit(processed, total)
                    continue
                
                # 載入圖片
                pixmap = self.load_optimized_image(image_path)
                if pixmap:
                    # 計算大小並加入快取
                    size = pixmap.width() * pixmap.height() * 4  # RGBA
                    self.cache.put(image_path, pixmap, size)
                    self.image_loaded.emit(image_path, pixmap)
                else:
                    self.loading_error.emit(image_path, "無法載入圖片")
                
                processed += 1
                self.loading_progress.emit(processed, total)
                
            except queue.Empty:
                break
            except Exception as e:
                self.loading_error.emit(image_path, str(e))
        
        self.is_running = False
    
    def load_optimized_image(self, image_path: str) -> Optional[QPixmap]:
        """優化的圖片載入"""
        try:
            # 使用PIL檢查圖片資訊
            with Image.open(image_path) as img:
                original_size = img.size
                
                # 如果圖片太大，進行縮放
                if (original_size[0] > self.max_display_size[0] or 
                    original_size[1] > self.max_display_size[1]):
                    
                    # 計算縮放比例
                    scale_x = self.max_display_size[0] / original_size[0]
                    scale_y = self.max_display_size[1] / original_size[1]
                    scale = min(scale_x, scale_y)
                    
                    new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
                    
                    # 使用高品質重新取樣
                    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # 轉換為QPixmap
                    if img_resized.mode != 'RGB':
                        img_resized = img_resized.convert('RGB')
                    
                    # 轉換為numpy陣列然後到QPixmap
                    img_array = np.array(img_resized)
                    height, width, channel = img_array.shape
                    bytes_per_line = 3 * width
                    
                    # 使用OpenCV轉換顏色空間
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    
                    # 轉為QPixmap
                    pixmap = QPixmap()
                    pixmap.loadFromData(cv2.imencode('.jpg', img_array, [cv2.IMWRITE_JPEG_QUALITY, 95])[1].tobytes())
                    
                    return pixmap
                else:
                    # 直接載入小圖片
                    pixmap = QPixmap(image_path)
                    return pixmap if not pixmap.isNull() else None
                    
        except Exception as e:
            print(f"載入圖片錯誤: {image_path}, {e}")
            return None


class MemoryManager(QObject):
    """記憶體管理器"""
    
    memory_warning = pyqtSignal(int)  # 記憶體使用百分比
    
    def __init__(self):
        super().__init__()
        self.cache_managers = []
        self.monitoring = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_memory)
        
        # 記憶體閾值
        self.warning_threshold = 80  # 80%
        self.critical_threshold = 90  # 90%
        
    def register_cache(self, cache_manager):
        """註冊快取管理器"""
        self.cache_managers.append(cache_manager)
    
    def start_monitoring(self, interval: int = 5000):
        """開始記憶體監控"""
        self.monitoring = True
        self.timer.start(interval)
    
    def stop_monitoring(self):
        """停止記憶體監控"""
        self.monitoring = False
        self.timer.stop()
    
    def check_memory(self):
        """檢查記憶體使用"""
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent
            
            if memory_percent > self.critical_threshold:
                # 緊急清理
                self.emergency_cleanup()
                self.memory_warning.emit(memory_percent)
            elif memory_percent > self.warning_threshold:
                # 溫和清理
                self.gentle_cleanup()
                self.memory_warning.emit(memory_percent)
                
        except ImportError:
            # 如果沒有psutil，使用基本的垃圾回收
            gc.collect()
    
    def gentle_cleanup(self):
        """溫和的記憶體清理"""
        # 清理一半的快取
        for cache in self.cache_managers:
            if hasattr(cache, 'cache') and hasattr(cache, 'access_order'):
                with cache.lock:
                    cleanup_count = len(cache.access_order) // 2
                    for _ in range(cleanup_count):
                        if cache.access_order:
                            cache._evict_oldest()
        
        gc.collect()
    
    def emergency_cleanup(self):
        """緊急記憶體清理"""
        # 清空所有快取
        for cache in self.cache_managers:
            if hasattr(cache, 'clear'):
                cache.clear()
        
        # 強制垃圾回收
        gc.collect()
    
    def get_memory_stats(self) -> Dict:
        """取得記憶體統計"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            cache_stats = []
            for i, cache in enumerate(self.cache_managers):
                if hasattr(cache, 'get_stats'):
                    cache_stats.append(cache.get_stats())
                else:
                    cache_stats.append({'name': f'Cache_{i}', 'unknown': True})
            
            return {
                'system_memory': {
                    'total_gb': memory.total / (1024**3),
                    'available_gb': memory.available / (1024**3),
                    'used_percent': memory.percent
                },
                'cache_stats': cache_stats,
                'monitoring': self.monitoring
            }
        except ImportError:
            return {
                'system_memory': {'error': 'psutil not available'},
                'cache_stats': [],
                'monitoring': self.monitoring
            }


class BackgroundProcessor(QThread):
    """背景處理器 - 用於預處理和批次任務"""
    
    task_completed = pyqtSignal(str, object)  # 任務ID, 結果
    progress_updated = pyqtSignal(str, int, int)  # 任務ID, 當前, 總數
    task_error = pyqtSignal(str, str)  # 任務ID, 錯誤訊息
    
    def __init__(self, max_workers: int = 4):
        super().__init__()
        self.max_workers = max_workers
        self.task_queue = queue.Queue()
        self.is_running = False
        self.executor = None
    
    def add_task(self, task_id: str, func: Callable, *args, **kwargs):
        """添加後台任務"""
        self.task_queue.put((task_id, func, args, kwargs))
        
        if not self.is_running:
            self.start()
    
    def run(self):
        """執行後台任務"""
        self.is_running = True
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        futures = {}
        
        while not self.task_queue.empty() or futures:
            # 添加新任務
            while not self.task_queue.empty() and len(futures) < self.max_workers:
                try:
                    task_id, func, args, kwargs = self.task_queue.get_nowait()
                    future = self.executor.submit(func, *args, **kwargs)
                    futures[future] = task_id
                except queue.Empty:
                    break
                except Exception as e:
                    self.task_error.emit(task_id, str(e))
            
            # 檢查完成的任務
            completed_futures = []
            for future, task_id in futures.items():
                if future.done():
                    try:
                        result = future.result()
                        self.task_completed.emit(task_id, result)
                    except Exception as e:
                        self.task_error.emit(task_id, str(e))
                    completed_futures.append(future)
            
            # 移除完成的任務
            for future in completed_futures:
                del futures[future]
            
            # 短暫休息
            self.msleep(100)
        
        self.executor.shutdown(wait=True)
        self.is_running = False


class PerformanceOptimizer:
    """效能優化管理器"""
    
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        
        # 初始化元件
        self.image_cache = ImageCache(max_cache_size=200 * 1024 * 1024)  # 200MB
        self.image_loader = ImageLoader(self.image_cache)
        self.memory_manager = MemoryManager()
        self.background_processor = BackgroundProcessor()
        
        # 註冊快取到記憶體管理器
        self.memory_manager.register_cache(self.image_cache)
        
        # 啟動記憶體監控
        self.memory_manager.start_monitoring()
        
        # 效能統計
        self.stats = {
            'images_loaded': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'load_times': [],
            'memory_cleanups': 0
        }
        
        # 連接信號
        self.memory_manager.memory_warning.connect(self.on_memory_warning)
        self.image_loader.image_loaded.connect(self.on_image_loaded)
        self.background_processor.task_completed.connect(self.on_background_task_completed)
    
    def load_image_async(self, image_path: str, priority: bool = False):
        """非同步載入圖片"""
        # 檢查快取
        cached = self.image_cache.get(image_path)
        if cached:
            self.stats['cache_hits'] += 1
            return cached
        
        self.stats['cache_misses'] += 1
        self.image_loader.add_load_request(image_path, priority)
        return None
    
    def preload_images(self, image_paths: list, current_index: int = 0):
        """預載入圖片"""
        # 優先載入當前圖片
        if 0 <= current_index < len(image_paths):
            self.image_loader.add_load_request(image_paths[current_index], priority=True)
        
        # 預載入前後圖片
        preload_range = 3  # 前後各3張
        for i in range(max(0, current_index - preload_range), 
                       min(len(image_paths), current_index + preload_range + 1)):
            if i != current_index:
                self.image_loader.add_load_request(image_paths[i], priority=False)
    
    def add_background_task(self, task_id: str, func: Callable, *args, **kwargs):
        """添加背景任務"""
        self.background_processor.add_task(task_id, func, *args, **kwargs)
    
    def on_memory_warning(self, memory_percent: int):
        """處理記憶體警告"""
        print(f"記憶體使用警告: {memory_percent}%")
        self.stats['memory_cleanups'] += 1
        
        # 根據記憶體使用情況調整快取大小
        if memory_percent > 90:
            # 緊急情況：減少快取大小到50MB
            self.image_cache.max_cache_size = 50 * 1024 * 1024
            self.memory_manager.emergency_cleanup()
        elif memory_percent > 80:
            # 警告情況：減少快取大小到100MB
            self.image_cache.max_cache_size = 100 * 1024 * 1024
            self.memory_manager.gentle_cleanup()
    
    def on_image_loaded(self, image_path: str, pixmap: QPixmap):
        """處理圖片載入完成"""
        self.stats['images_loaded'] += 1
    
    def on_background_task_completed(self, task_id: str, result: Any):
        """處理背景任務完成"""
        print(f"背景任務完成: {task_id}")
    
    def get_performance_stats(self) -> Dict:
        """取得效能統計"""
        return {
            'cache_stats': self.image_cache.get_stats(),
            'memory_stats': self.memory_manager.get_memory_stats(),
            'loader_stats': {
                'images_loaded': self.stats['images_loaded'],
                'cache_hits': self.stats['cache_hits'],
                'cache_misses': self.stats['cache_misses'],
                'hit_ratio': self.stats['cache_hits'] / max(self.stats['cache_hits'] + self.stats['cache_misses'], 1),
                'memory_cleanups': self.stats['memory_cleanups']
            }
        }
    
    def get_cache_info(self) -> Dict:
        """取得快取資訊 (供主程式使用)"""
        try:
            cache_stats = self.image_cache.get_stats()
            
            # 模擬快取項目列表
            items = []
            if hasattr(self.image_cache, 'cache') and self.image_cache.cache:
                for path in list(self.image_cache.cache.keys())[:10]:  # 只顯示前10項
                    items.append({
                        'path': path,
                        'size': cache_stats['current_size_mb'] / max(cache_stats['cache_count'], 1)  # 估算每項大小
                    })
            
            return {
                'size': cache_stats['cache_count'],  # main.py期望的鍵
                'memory_usage': cache_stats['current_size_mb'],  # main.py期望的鍵
                'max_size_mb': cache_stats['max_size_mb'],
                'hit_rate': cache_stats['hit_ratio'],
                'usage_percent': (cache_stats['current_size_mb'] / max(cache_stats['max_size_mb'], 1)) * 100,
                'items': items  # main.py期望的快取項目列表
            }
        except Exception as e:
            return {
                'error': f'無法取得快取資訊: {str(e)}',
                'size': 0,  # main.py期望的鍵
                'memory_usage': 0.0,  # main.py期望的鍵
                'max_size_mb': 0,
                'hit_rate': 0.0,
                'usage_percent': 0.0,
                'items': []  # main.py期望的快取項目列表
            }
    
    def get_memory_info(self) -> Dict:
        """取得記憶體資訊 (供主程式使用)"""
        try:
            memory_stats = self.memory_manager.get_memory_stats()
            process_memory = self._get_process_memory()
            
            # 計算已使用的記憶體
            total_gb = memory_stats['system_memory']['total_gb']
            available_gb = memory_stats['system_memory']['available_gb']
            used_gb = total_gb - available_gb
            
            # 生成記憶體建議
            recommendations = []
            if memory_stats['system_memory']['used_percent'] > 85:
                recommendations.append("系統記憶體使用率過高，建議關閉其他應用程式")
            if process_memory['memory_mb'] > 500:
                recommendations.append("程式記憶體使用量較高，建議清理快取")
                
            # 格式化為main.py期望的格式
            return {
                'system': {
                    'total': total_gb,
                    'used': used_gb,  # main.py期望的鍵
                    'available': available_gb, 
                    'percent': memory_stats['system_memory']['used_percent']
                },
                'process': {
                    'memory': process_memory['memory_mb']  # main.py期望的鍵
                },
                'cache': memory_stats.get('cache_stats', []),
                'recommendations': recommendations  # main.py期望的建議列表
            }
        except Exception as e:
            return {
                'error': f'無法取得記憶體資訊: {str(e)}',
                'system': {
                    'total': 0, 
                    'used': 0,  # main.py期望的鍵
                    'available': 0, 
                    'percent': 0
                },
                'process': {
                    'memory': 0  # main.py期望的鍵
                },
                'cache': [],
                'recommendations': []  # main.py期望的建議列表
            }
    
    def _get_process_memory(self) -> Dict:
        """取得當前程序記憶體使用量"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            return {
                'memory_mb': memory_info.rss / (1024 * 1024)
            }
        except Exception:
            return {'memory_mb': 0}
    
    def cleanup(self):
        """清理資源"""
        self.memory_manager.stop_monitoring()
        self.image_loader.quit()
        self.image_loader.wait()
        self.background_processor.quit()
        self.background_processor.wait()
        self.image_cache.clear()
        
    def clear_cache(self):
        """清除所有快取 - main.py介面使用"""
        self.image_cache.clear()
        self.stats['cache_hits'] = 0
        self.stats['cache_misses'] = 0
        self.stats['memory_cleanups'] += 1
        
    def optimize_cache(self):
        """優化快取 - main.py介面使用"""
        # 執行溫和清理
        self.memory_manager.gentle_cleanup()
        # 清理統計資料
        self.stats['load_times'] = self.stats['load_times'][-100:]  # 保留最近100次
        
    def get_cache_size(self) -> int:
        """取得快取項目數量 - main.py介面使用"""
        return len(self.image_cache.cache)


# 輔助函數
def install_performance_dependencies():
    """安裝效能相關的依賴庫"""
    try:
        import subprocess
        import sys
        
        packages = ['psutil', 'pillow', 'opencv-python', 'numpy']
        
        for package in packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                print(f"安裝 {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        
        return True
    except Exception as e:
        print(f"安裝依賴庫錯誤: {e}")
        return False
