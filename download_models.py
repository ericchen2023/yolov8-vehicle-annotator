#!/usr/bin/env python3
"""
YOLOv8 車輛標註工具 - 模型下載腳本
下載必要的 YOLOv8 模型檔案

使用方法:
python download_models.py

或者下載特定模型:
python download_models.py --model yolov8n
"""

import os
import sys
import argparse
import requests
from pathlib import Path
from tqdm import tqdm

# YOLOv8 模型下載連結
MODEL_URLS = {
    'yolov8n': 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt',
    'yolov8s': 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8s.pt',
    'yolov8m': 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8m.pt',
    'yolov8l': 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8l.pt',
    'yolov8x': 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8x.pt',
    'yolo11n': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt'
}

# 模型檔案大小（用於進度顯示）
MODEL_SIZES = {
    'yolov8n': 6549796,
    'yolov8s': 22588772,
    'yolov8m': 52136884,
    'yolov8l': 87792836,
    'yolov8x': 136890692,
    'yolo11n': 5613764
}

def download_file(url, filename, expected_size=None):
    """下載檔案並顯示進度"""
    print(f"下載 {filename}...")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        if expected_size and total_size == 0:
            total_size = expected_size

        with open(filename, 'wb') as file, tqdm(
            desc=filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                pbar.update(size)

        print(f"✅ {filename} 下載完成")
        return True

    except Exception as e:
        print(f"❌ 下載 {filename} 失敗: {e}")
        if os.path.exists(filename):
            os.remove(filename)
        return False

def main():
    parser = argparse.ArgumentParser(description='下載 YOLOv8 模型檔案')
    parser.add_argument('--model', choices=list(MODEL_URLS.keys()),
                       help='下載特定模型（預設下載所有模型）')
    parser.add_argument('--force', action='store_true',
                       help='強制重新下載已存在的檔案')

    args = parser.parse_args()

    print("🚗 YOLOv8 車輛標註工具 - 模型下載器")
    print("=" * 50)

    # 確定要下載的模型
    if args.model:
        models_to_download = [args.model]
    else:
        models_to_download = list(MODEL_URLS.keys())

    # 檢查並建立 models 目錄
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)

    print(f"將下載 {len(models_to_download)} 個模型到 {models_dir} 目錄")
    print()

    success_count = 0
    total_count = len(models_to_download)

    for model_name in models_to_download:
        filename = models_dir / f"{model_name}.pt"

        # 檢查檔案是否已存在
        if filename.exists() and not args.force:
            file_size = filename.stat().st_size
            expected_size = MODEL_SIZES.get(model_name, 0)

            if expected_size > 0 and abs(file_size - expected_size) < 1024:  # 允許1KB誤差
                print(f"⏭️  {model_name}.pt 已存在，跳過")
                success_count += 1
                continue
            else:
                print(f"⚠️  {model_name}.pt 檔案大小不正確，將重新下載")

        # 下載模型
        url = MODEL_URLS[model_name]
        if download_file(url, filename, MODEL_SIZES.get(model_name)):
            success_count += 1

    print()
    print("=" * 50)
    print(f"下載完成: {success_count}/{total_count} 個模型")

    if success_count == total_count:
        print("🎉 所有模型下載成功！")
        print()
        print("您現在可以運行:")
        print("python main.py")
    else:
        print("⚠️  部分模型下載失敗，請檢查網路連線後重試")
        print("或者手動下載失敗的模型")

    return success_count == total_count

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
