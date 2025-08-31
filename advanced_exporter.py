"""
進階匯出模組 - 支援多種格式匯出
支援格式：YOLO、COCO、Pascal VOC、JSON
v2.1.3 更新：提升座標精確度至12位小數點
"""

import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from typing import List, Dict, Any


class AdvancedExporter:
    """進階匯出器，支援多種標註格式"""
    
    def __init__(self):
        self.vehicle_classes = {
            0: {'zh': '汽車', 'en': 'car'},
            1: {'zh': '卡車', 'en': 'truck'},
            2: {'zh': '巴士', 'en': 'bus'},
            3: {'zh': '機車', 'en': 'motorcycle'},
            4: {'zh': '腳踏車', 'en': 'bicycle'},
            5: {'zh': '貨車', 'en': 'van'},
            6: {'zh': '休旅車', 'en': 'suv'},
            7: {'zh': '跑車', 'en': 'sports_car'}
        }
        
    def export_yolo(self, image_path: str, annotations: List, output_dir: str) -> bool:
        """匯出YOLO格式"""
        try:
            from PIL import Image
            
            # 確保輸出目錄存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 取得圖片尺寸
            img = Image.open(image_path)
            img_width, img_height = img.size
            
            # 建立輸出檔案路徑
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}.txt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for rect in annotations:
                    class_id = rect['class']
                    x, y, w, h = rect['bbox']
                    
                    # 轉換為YOLO格式（中心點座標，相對尺寸）
                    center_x = (x + w / 2) / img_width
                    center_y = (y + h / 2) / img_height
                    width = w / img_width
                    height = h / img_height
                    
                    f.write(f"{class_id} {center_x:.12f} {center_y:.12f} {width:.12f} {height:.12f}\n")
                    
            return True
        except Exception as e:
            print(f"YOLO匯出錯誤: {e}")
            return False
    
    def export_coco(self, images_data: List[Dict], output_dir: str) -> bool:
        """匯出COCO格式"""
        try:
            # COCO格式結構
            coco_format = {
                "info": {
                    "description": "Vehicle Detection Dataset",
                    "version": "1.0",
                    "year": datetime.now().year,
                    "contributor": "YOLO Annotator",
                    "date_created": datetime.now().isoformat()
                },
                "licenses": [
                    {
                        "id": 1,
                        "name": "Custom License",
                        "url": ""
                    }
                ],
                "images": [],
                "annotations": [],
                "categories": []
            }
            
            # 添加類別
            for class_id, class_info in self.vehicle_classes.items():
                coco_format["categories"].append({
                    "id": class_id + 1,  # COCO類別ID從1開始
                    "name": class_info['en'],
                    "supercategory": "vehicle"
                })
            
            annotation_id = 1
            
            # 處理每張圖片
            for img_id, img_data in enumerate(images_data, 1):
                from PIL import Image
                
                image_path = img_data['path']
                annotations = img_data['annotations']
                
                # 取得圖片資訊
                img = Image.open(image_path)
                img_width, img_height = img.size
                
                # 添加圖片資訊
                coco_format["images"].append({
                    "id": img_id,
                    "width": img_width,
                    "height": img_height,
                    "file_name": os.path.basename(image_path)
                })
                
                # 添加標註
                for rect in annotations:
                    class_id = rect['class']
                    x, y, w, h = rect['bbox']
                    
                    coco_format["annotations"].append({
                        "id": annotation_id,
                        "image_id": img_id,
                        "category_id": class_id + 1,
                        "bbox": [round(x, 12), round(y, 12), round(w, 12), round(h, 12)],  # COCO格式：[x, y, width, height]
                        "area": round(w * h, 12),
                        "iscrowd": 0
                    })
                    annotation_id += 1
            
            # 儲存COCO檔案
            output_path = os.path.join(output_dir, "annotations.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(coco_format, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"COCO匯出錯誤: {e}")
            return False
    
    def export_pascal_voc(self, image_path: str, annotations: List, output_dir: str) -> bool:
        """匯出Pascal VOC格式"""
        try:
            from PIL import Image
            
            # 取得圖片資訊
            img = Image.open(image_path)
            img_width, img_height = img.size
            img_depth = 3  # RGB
            
            # 建立XML結構
            annotation = ET.Element("annotation")
            
            # 資料夾
            ET.SubElement(annotation, "folder").text = "images"
            
            # 檔案名稱
            filename = os.path.basename(image_path)
            ET.SubElement(annotation, "filename").text = filename
            
            # 路徑
            ET.SubElement(annotation, "path").text = image_path
            
            # 來源
            source = ET.SubElement(annotation, "source")
            ET.SubElement(source, "database").text = "Unknown"
            
            # 尺寸
            size = ET.SubElement(annotation, "size")
            ET.SubElement(size, "width").text = str(img_width)
            ET.SubElement(size, "height").text = str(img_height)
            ET.SubElement(size, "depth").text = str(img_depth)
            
            # 分割
            ET.SubElement(annotation, "segmented").text = "0"
            
            # 物件
            for rect in annotations:
                obj = ET.SubElement(annotation, "object")
                
                # 類別名稱
                class_id = rect['class']
                class_name = self.vehicle_classes[class_id]['en']
                ET.SubElement(obj, "name").text = class_name
                
                # 姿勢
                ET.SubElement(obj, "pose").text = "Unspecified"
                ET.SubElement(obj, "truncated").text = "0"
                ET.SubElement(obj, "difficult").text = "0"
                
                # 邊界框
                bbox = ET.SubElement(obj, "bndbox")
                x, y, w, h = rect['bbox']
                ET.SubElement(bbox, "xmin").text = str(int(x))
                ET.SubElement(bbox, "ymin").text = str(int(y))
                ET.SubElement(bbox, "xmax").text = str(int(x + w))
                ET.SubElement(bbox, "ymax").text = str(int(y + h))
            
            # 格式化XML並保存
            rough_string = ET.tostring(annotation, 'unicode')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")
            
            # 移除空行
            pretty_lines = [line for line in pretty_xml.split('\n') if line.strip()]
            pretty_xml = '\n'.join(pretty_lines)
            
            # 儲存XML檔案
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}.xml")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
                
            return True
        except Exception as e:
            print(f"Pascal VOC匯出錯誤: {e}")
            return False
    
    def export_json(self, image_path: str, annotations: List, output_dir: str) -> bool:
        """匯出JSON格式"""
        try:
            from PIL import Image
            
            # 取得圖片資訊
            img = Image.open(image_path)
            img_width, img_height = img.size
            
            # 建立JSON結構
            json_data = {
                "image": {
                    "file_name": os.path.basename(image_path),
                    "width": img_width,
                    "height": img_height,
                    "path": image_path
                },
                "annotations": [],
                "metadata": {
                    "created_date": datetime.now().isoformat(),
                    "created_by": "YOLO Annotator",
                    "format_version": "1.0"
                }
            }
            
            # 添加標註
            for idx, rect in enumerate(annotations):
                class_id = rect['class']
                x, y, w, h = rect['bbox']
                
                # 計算精確的中心點座標（保持高精確度）
                center_x = round(x + w / 2, 12)
                center_y = round(y + h / 2, 12)
                
                annotation_data = {
                    "id": idx + 1,
                    "class_id": class_id,
                    "class_name_zh": self.vehicle_classes[class_id]['zh'],
                    "class_name_en": self.vehicle_classes[class_id]['en'],
                    "bbox": {
                        "x": round(x, 12),
                        "y": round(y, 12),
                        "width": round(w, 12),
                        "height": round(h, 12)
                    },
                    "area": round(w * h, 12),
                    "center": {
                        "x": center_x,
                        "y": center_y
                    }
                }
                json_data["annotations"].append(annotation_data)
            
            # 儲存JSON檔案
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}.json")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"JSON匯出錯誤: {e}")
            return False
    
    def export_classes_file(self, output_dir: str, language: str = 'both') -> bool:
        """匯出類別檔案"""
        try:
            # 確保輸出目錄存在
            os.makedirs(output_dir, exist_ok=True)
            
            if language in ['zh', 'both']:
                # 中文類別檔案
                zh_path = os.path.join(output_dir, "classes.txt")
                with open(zh_path, 'w', encoding='utf-8') as f:
                    for class_id in sorted(self.vehicle_classes.keys()):
                        f.write(f"{self.vehicle_classes[class_id]['zh']}\n")
            
            if language in ['en', 'both']:
                # 英文類別檔案
                en_path = os.path.join(output_dir, "classes_en.txt")
                with open(en_path, 'w', encoding='utf-8') as f:
                    for class_id in sorted(self.vehicle_classes.keys()):
                        f.write(f"{self.vehicle_classes[class_id]['en']}\n")
                        
            return True
        except Exception as e:
            print(f"類別檔案匯出錯誤: {e}")
            return False
    
    def generate_export_report(self, export_results: Dict, output_dir: str) -> bool:
        """生成匯出統計報告"""
        try:
            report = {
                "export_summary": {
                    "export_date": datetime.now().isoformat(),
                    "total_images": export_results.get('total_images', 0),
                    "total_annotations": export_results.get('total_annotations', 0),
                    "export_formats": export_results.get('formats', []),
                    "output_directory": output_dir
                },
                "class_statistics": {},
                "format_results": export_results.get('format_results', {}),
                "errors": export_results.get('errors', [])
            }
            
            # 統計各類別數量
            class_counts = export_results.get('class_counts', {})
            for class_id, count in class_counts.items():
                class_info = self.vehicle_classes.get(class_id, {'zh': '未知', 'en': 'unknown'})
                report["class_statistics"][f"class_{class_id}"] = {
                    "name_zh": class_info['zh'],
                    "name_en": class_info['en'],
                    "count": count
                }
            
            # 儲存報告
            report_path = os.path.join(output_dir, "export_report.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"報告生成錯誤: {e}")
            return False
    
    def batch_export(self, images_data: List[Dict], output_dir: str, formats: List[str]) -> Dict:
        """批次匯出多種格式"""
        results = {
            'total_images': len(images_data),
            'total_annotations': 0,
            'formats': formats,
            'format_results': {},
            'class_counts': {},
            'errors': []
        }
        
        # 確保輸出目錄存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 為每種格式建立子目錄
        format_dirs = {}
        for fmt in formats:
            fmt_dir = os.path.join(output_dir, fmt.lower())
            os.makedirs(fmt_dir, exist_ok=True)
            format_dirs[fmt] = fmt_dir
        
        # 統計標註數量和類別
        for img_data in images_data:
            annotations = img_data['annotations']
            results['total_annotations'] += len(annotations)
            
            for ann in annotations:
                class_id = ann['class']
                results['class_counts'][class_id] = results['class_counts'].get(class_id, 0) + 1
        
        # 匯出各種格式
        for fmt in formats:
            success_count = 0
            fmt_dir = format_dirs[fmt]
            
            try:
                if fmt == 'YOLO':
                    for img_data in images_data:
                        if self.export_yolo(img_data['path'], img_data['annotations'], fmt_dir):
                            success_count += 1
                    # 匯出類別檔案
                    self.export_classes_file(fmt_dir)
                    
                elif fmt == 'COCO':
                    if self.export_coco(images_data, fmt_dir):
                        success_count = len(images_data)
                    
                elif fmt == 'Pascal VOC':
                    for img_data in images_data:
                        if self.export_pascal_voc(img_data['path'], img_data['annotations'], fmt_dir):
                            success_count += 1
                    # 匯出類別檔案
                    self.export_classes_file(fmt_dir)
                    
                elif fmt == 'JSON':
                    for img_data in images_data:
                        if self.export_json(img_data['path'], img_data['annotations'], fmt_dir):
                            success_count += 1
                    # 匯出類別檔案
                    self.export_classes_file(fmt_dir)
                
                results['format_results'][fmt] = {
                    'success': success_count,
                    'total': len(images_data),
                    'output_dir': fmt_dir
                }
                
            except Exception as e:
                error_msg = f"{fmt}格式匯出錯誤: {str(e)}"
                results['errors'].append(error_msg)
                results['format_results'][fmt] = {
                    'success': 0,
                    'total': len(images_data),
                    'error': error_msg
                }
        
        # 生成匯出報告
        self.generate_export_report(results, output_dir)
        
        return results
