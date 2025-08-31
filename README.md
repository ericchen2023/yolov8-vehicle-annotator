# 🚗 YOLOv8 車輛標註工具 v1.0.0 - 完整使用說明書

<div align="center">

![YOLOv8 Vehicle Annotator](https://img.shields.io/badge/YOLOv8-車輛標註工具-blue?style=for-the-badge&logo=python)
![Version](https://img.shields.io/badge/版本-v1.0.0-green?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square)
![License](https://img.shields.io/badge/授權-MIT-orange?style=flat-square)

**專業級車輛檢測標註工具，集成AI自動預標註、自定義車種管理、高效能圖像處理**

[📥 下載](#-安裝指南) • [🚀 快速開始](#-快速入門) • [📖 詳細說明](#-功能詳解) • [❓ 疑難排解](#-疑難排解)

</div>

---

## 📋 目錄

- [🚗 產品概述](#-產品概述)
- [✨ 核心功能特色](#-核心功能特色)
- [📋 系統需求](#-系統需求)
- [🛠 安裝指南](#-安裝指南)
- [🚀 快速入門](#-快速入門)
- [📖 功能詳解](#-功能詳解)
- [⌨️ 完整快捷鍵指南](#️-完整快捷鍵指南)
- [📤 匯出格式說明](#-匯出格式說明)
- [🔧 疑難排解](#-疑難排解)
- [📞 技術支援](#-技術支援)
- [📜 授權條款](#-授權條款)

---

## 🚗 產品概述

YOLOv8 車輛標註工具是一款專為車輛檢測任務設計的專業級標註軟體，結合了人工智慧自動預標註技術與人性化的操作介面，為使用者提供高效、精準的圖像標註體驗。

### 🎯 主要應用場景

- **🚗 車輛檢測資料集製作**：為自動駕駛、智慧交通系統準備訓練資料
- **📊 交通流量分析**：標註道路上的各類車輛進行流量統計
- **🔍 安全監控系統**：標註監控畫面中的車輛目標
- **📈 研究與開發**：學術研究中的車輛檢測資料標註
- **🏭 工業應用**：工廠車輛、叉車等工業車輛的檢測標註

### 💡 產品優勢

- **🤖 AI智慧輔助**：集成YOLOv8模型，一鍵自動檢測車輛
- **🎨 完全自定義**：不受限於固定車種，可自由定義車輛類別
- **⚡ 高效率處理**：支援批次處理，節省大量人工時間
- **🎯 像素級精準**：八手柄編輯器支援精確到像素的調整
- **📊 多格式匯出**：支援YOLO、COCO、Pascal VOC等多種業界標準格式
- **💾 智慧快取**：優化大圖片處理，節省系統資源

---

## ✨ 核心功能特色

### 🎯 核心功能

#### 1. 智慧車輛分類系統
- **完全自定義車種**：不限於固定類型，可自由新增/編輯/刪除車種
- **表情符號標識**：每個車種可設定獨特的表情符號，方便識別
- **快捷鍵支援**：支援自定義快捷鍵，快速切換車種
- **COCO資料集整合**：可選擇80種COCO類別進行AI辨識

#### 2. AI自動預標註
- **YOLOv8模型集成**：使用最新的YOLOv8目標檢測模型
- **多模型選擇**：Nano、Small、Medium、Large、X-Large五種模型
- **動態COCO映射**：根據配置的車種動態映射AI辨識結果
- **批次處理支援**：支援整個資料夾的批次AI預測

#### 3. 精確標註工具
- **八手柄編輯器**：支援八個方向的精確調整
- **像素級精準度**：支援12位小數點精確度
- **即時視覺回饋**：標註框變更即時顯示
- **多選操作**：支援多個標註框的同時操作

#### 4. 批次處理能力
- **資料夾批次載入**：一次載入整個資料夾的圖片
- **AI批次預測**：對多張圖片進行批次AI預測
- **批次匯出**：支援多格式批次匯出功能
- **進度顯示**：即時顯示處理進度

#### 5. 多格式匯出
- **YOLO格式**：標準YOLOv8訓練格式
- **COCO格式**：業界標準的JSON結構化格式
- **Pascal VOC格式**：XML標註格式
- **JSON格式**：包含完整資訊的自訂格式

### 🚀 進階功能

#### 效能優化系統
- **智慧快取管理**：自動快取已處理的圖片
- **記憶體監控**：即時監控系統記憶體使用情況
- **大圖片優化**：針對大尺寸圖片進行特殊優化處理
- **異步載入**：非同步圖片載入，提升使用者體驗

#### 專案管理系統
- **專案保存**：支援專案檔案的保存和載入
- **最近檔案記錄**：自動記錄最近開啟的檔案
- **自動備份**：重要操作自動備份標註資料
- **專案統計**：提供專案的詳細統計資訊

#### 專業UI設計
- **現代化介面**：採用深色主題的現代化設計
- **可調整佈局**：支援視窗分割比例調整
- **工具列自訂**：可自訂工具列的顯示和位置
- **多解析度支援**：支援高DPI顯示器

#### 完整快捷鍵系統
- **100+快捷鍵**：涵蓋所有主要操作
- **自定義支援**：支援部分功能的快捷鍵自定義
- **鍵盤導航**：支援鍵盤完整操作軟體
- **快速操作**：一鍵完成複雜操作流程

---

## 📋 系統需求

### 💻 最低系統需求

| 組件 | 需求 | 說明 |
|------|------|------|
| **作業系統** | Windows 10/11<br>macOS 10.14+<br>Ubuntu 18.04+ | 支援主流桌面作業系統 |
| **Python版本** | 3.8 或以上 | 建議使用3.9+以獲得最佳效能 |
| **記憶體** | 4GB RAM | 基本標註功能所需 |
| **硬碟空間** | 2GB | 程式安裝和基本快取空間 |
| **顯示器** | 1920x1080 | 支援高DPI顯示器 |

### 🚀 建議系統配置

| 組件 | 建議配置 | 說明 |
|------|----------|------|
| **處理器** | Intel i5 / AMD Ryzen 5 以上 | 多核心處理器可提升批次處理速度 |
| **記憶體** | 8GB RAM 或以上 | 處理大圖片和批次操作的理想配置 |
| **儲存空間** | 10GB SSD | 存放圖片資料集和快取檔案 |
| **顯示卡** | 獨立顯示卡（可選） | 提升圖像處理和UI渲染效能 |
| **網路** | 穩定網路連線 | 下載AI模型和軟體更新 |

### 📊 效能基準測試

| 操作類型 | 4GB RAM | 8GB RAM | 16GB RAM |
|----------|---------|---------|----------|
| 單張圖片載入 | < 2秒 | < 1秒 | < 0.5秒 |
| AI預測（單張） | 3-8秒 | 2-5秒 | 1-3秒 |
| 批次AI預測 | 30-120秒 | 15-60秒 | 8-30秒 |
| 大圖片處理 | 支援 | 良好 | 最佳 |

---

## 🛠 安裝指南

### 方法一：自動安裝（推薦）

#### Windows 系統
```batch
# 1. 下載專案
git clone https://github.com/ericchen2023/yolov8-vehicle-annotator.git
cd yolo-vehicle-annotator

# 2. 執行自動安裝
install.bat
```

#### macOS/Linux 系統
```bash
# 1. 下載專案
git clone https://github.com/ericchen2023/yolov8-vehicle-annotator.git
cd yolo-vehicle-annotator

# 2. 給予執行權限
chmod +x install.sh

# 3. 執行自動安裝
./install.sh
```

### 方法二：手動安裝

#### 步驟1：環境準備
```bash
# 建立專用虛擬環境
python -m venv yolo_annotator_env

# 啟動虛擬環境
# Windows
yolo_annotator_env\Scripts\activate
# macOS/Linux
source yolo_annotator_env/bin/activate
```

#### 步驟2：安裝依賴套件
```bash
# 安裝所有必要套件
pip install -r requirements.txt
```

#### 步驟3：驗證安裝
```bash
# 檢查Python版本
python --version

# 檢查關鍵套件
python -c "import PyQt5, torch, ultralytics; print('所有套件安裝成功')"
```

#### 步驟4：啟動程式
```bash
# 啟動主程式
python main.py
```

### 🔍 安裝驗證

安裝完成後，您應該能夠：

1. **成功啟動程式**：雙擊 `main.py` 或執行 `python main.py`
2. **載入圖片**：使用 `Ctrl+O` 開啟圖片檔案
3. **AI功能測試**：按 `F5` 測試AI預測功能
4. **匯出功能**：使用 `Ctrl+S` 測試標註匯出

### ⚠️ 常見安裝問題

#### 問題1：PyQt5安裝失敗
```bash
# 解決方案：使用系統套件管理器
# Ubuntu/Debian
sudo apt-get install python3-pyqt5

# macOS
brew install pyqt5
```

#### 問題2：記憶體不足
- 關閉其他大型應用程式
- 使用較小的AI模型（YOLOv8n）
- 增加系統虛擬記憶體

#### 問題3：網路問題
- 檢查網路連線
- 使用代理伺服器（如果需要）
- 手動下載大檔案套件

---

## 🚀 快速入門

### 5分鐘上手指南

#### 步驟1：準備圖片資料
1. 建立一個資料夾存放您的車輛圖片
2. 支援格式：PNG、JPG、JPEG、BMP、TIFF
3. 建議圖片尺寸：1920x1080 或以上
4. 檔案命名：使用有意義的名稱

#### 步驟2：啟動程式
```bash
cd yolo-vehicle-annotator
python main.py
```

#### 步驟3：載入圖片
- **單張圖片**：`Ctrl+O` 或點擊 📁 載入圖片
- **整個資料夾**：`Ctrl+Shift+O` 或點擊 📂 載入資料夾

#### 步驟4：設定車種
1. 按 `Ctrl+V` 開啟車種管理器
2. 點擊 ➕ 新增按鈕新增車種
3. 設定車種名稱、表情符號、快捷鍵
4. 選擇對應的COCO類別（用於AI辨識）

#### 步驟5：AI自動標註
1. 按 `F4` 選擇AI模型（建議使用Medium）
2. 按 `F5` 執行AI預測
3. 程式會自動檢測並標註車輛
4. 檢查並調整AI標註結果

#### 步驟6：手動調整
- **移動標註框**：點擊並拖拽標註框
- **調整大小**：拖拽八個手柄調整大小
- **刪除標註**：選中標註後按 `Delete`
- **切換車種**：使用數字鍵1-4或自定義快捷鍵

#### 步驟7：匯出標註
- **單張匯出**：`Ctrl+S` 匯出當前圖片
- **批次匯出**：`Ctrl+Shift+S` 匯出所有圖片
- **進階匯出**：`Ctrl+E` 選擇多種格式

### 📊 工作流程圖

```
開始
  ↓
載入圖片資料夾
  ↓
設定車種分類
  ↓
選擇AI模型
  ↓
執行AI預測
  ↓
檢查/調整標註
  ↓
匯出標註資料
  ↓
完成
```

---

## 📖 功能詳解

### 🎯 車種管理系統

#### 基本操作
1. **開啟車種管理器**：`Ctrl+V`
2. **新增車種**：點擊 ➕ 按鈕
3. **編輯車種**：雙擊車種或按 `F2`
4. **刪除車種**：選中車種後按 `Delete`

#### 進階設定
- **表情符號**：為每個車種選擇獨特圖示
- **快捷鍵**：設定1-9的數字快捷鍵
- **COCO映射**：選擇對應的COCO類別
- **啟用/停用**：控制車種是否在AI辨識中啟用

#### 批次操作
- **全選**：`Ctrl+A` 選擇所有車種
- **批次啟用**：`Ctrl+Shift+E`
- **批次停用**：`Ctrl+Shift+D`
- **搜尋過濾**：`Ctrl+F` 開啟搜尋

### 🤖 AI預測系統

#### 模型選擇
| 模型 | 大小 | 速度 | 精確度 | 適用場景 |
|------|------|------|--------|----------|
| Nano | 6MB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 快速原型 |
| Small | 22MB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 一般應用 |
| Medium | 50MB | ⭐⭐⭐ | ⭐⭐⭐⭐ | 平衡選擇 |
| Large | 88MB | ⭐⭐ | ⭐⭐⭐⭐⭐ | 高精度 |
| X-Large | 137MB | ⭐ | ⭐⭐⭐⭐⭐ | 研究用途 |

#### 預測參數設定
- **信心閾值**：0.1-0.9，建議0.3-0.5
- **自動優化**：自動調整標註框大小
- **重疊過濾**：移除重疊的標註框
- **批次大小**：1-16，根據記憶體調整

#### 批次處理
1. 載入圖片資料夾
2. 設定AI參數
3. 選擇批次處理模式
4. 監控處理進度
5. 檢查處理結果

### 🎨 標註編輯器

#### 基本操作
- **建立標註**：點擊滑鼠左鍵開始拖拽
- **選中標註**：點擊標註框
- **移動標註**：拖拽標註框中心
- **調整大小**：拖拽八個手柄

#### 進階功能
- **多選操作**：按住Ctrl點擊多個標註
- **精確調整**：使用方向鍵微調位置
- **複製標註**：`Ctrl+C` / `Ctrl+V`
- **貼齊網格**：自動貼齊像素網格

#### 視覺輔助
- **ID顯示**：顯示標註框的編號
- **分類顯示**：顯示車種名稱
- **顏色編碼**：不同車種使用不同顏色
- **透明度調整**：調整標註框透明度

### 📊 專案管理

#### 專案檔案結構
```
專案名稱/
├── images/          # 原始圖片
├── labels/          # YOLO格式標註
├── annotations.json # 完整標註資料
└── project.json     # 專案設定
```

#### 專案操作
- **新建專案**：`Ctrl+N`
- **開啟專案**：`Ctrl+O`
- **儲存專案**：`Ctrl+S`
- **專案統計**：查看標註統計資訊

#### 備份與恢復
- **自動備份**：每10分鐘自動備份
- **手動備份**：`Ctrl+B`
- **恢復備份**：從備份檔案恢復

---

## ⌨️ 完整快捷鍵指南

### 📁 檔案操作

| 功能 | 快捷鍵 | 說明 | 替代鍵 |
|------|--------|------|--------|
| 載入圖片 | `Ctrl+O` | 開啟單張圖片 | - |
| 載入資料夾 | `Ctrl+Shift+O` | 載入整個資料夾 | - |
| 儲存標註 | `Ctrl+S` | 匯出當前標註 | - |
| 批次匯出 | `Ctrl+Shift+S` | 批次匯出所有標註 | - |
| 進階匯出 | `Ctrl+E` | 多格式匯出 | - |
| 最近檔案 | `Ctrl+H` | 開啟最近檔案 | - |
| 專案管理 | `Ctrl+P` | 專案管理器 | - |

### 🤖 AI功能

| 功能 | 快捷鍵 | 說明 | 替代鍵 |
|------|--------|------|--------|
| 選擇模型 | `F4` | 選擇YOLOv8模型 | - |
| AI預測 | `F5` | 當前圖片AI標註 | - |
| 批次AI | `Ctrl+F5` | 批次AI處理 | - |
| AI設定 | `F6` | AI參數設定 | - |
| 停止AI | `Esc` | 停止當前AI處理 | - |

### 🖼 圖片導航

| 功能 | 快捷鍵 | 說明 | 替代鍵 |
|------|--------|------|--------|
| 上一張 | `←` | 前一張圖片 | `A` |
| 下一張 | `→` | 下一張圖片 | `D` |
| 第一張 | `Home` | 跳到第一張 | `Ctrl+Home` |
| 最後一張 | `End` | 跳到最後一張 | `Ctrl+End` |
| 上一頁 | `Page Up` | 上一頁圖片 | - |
| 下一頁 | `Page Down` | 下一頁圖片 | - |
| 空白鍵 | `Space` | 下一張 | - |
| Shift+空白 | `Shift+Space` | 上一張 | - |

### 🏷 標註操作

| 功能 | 快捷鍵 | 說明 | 替代鍵 |
|------|--------|------|--------|
| 刪除選中 | `Delete` | 刪除選中標註 | - |
| 清除所有 | `Ctrl+Delete` | 清除所有標註 | - |
| 全選標註 | `Ctrl+A` | 選擇所有標註 | - |
| 取消選擇 | `Escape` | 取消所有選擇 | - |
| 複製標註 | `Ctrl+C` | 複製選中標註 | - |
| 貼上標註 | `Ctrl+V` | 貼上標註 | - |
| 撤銷 | `Ctrl+Z` | 撤銷上一步操作 | - |
| 重做 | `Ctrl+Y` | 重做上一步操作 | - |

### 🚗 車種切換

| 功能 | 快捷鍵 | 說明 | 替代鍵 |
|------|--------|------|--------|
| 車種1 | `1` | 切換到第一個車種 | - |
| 車種2 | `2` | 切換到第二個車種 | - |
| 車種3 | `3` | 切換到第三個車種 | - |
| 車種4 | `4` | 切換到第四個車種 | - |
| 車種5 | `5` | 切換到第五個車種 | - |
| 車種6 | `6` | 切換到第六個車種 | - |
| 車種7 | `7` | 切換到第七個車種 | - |
| 車種8 | `8` | 切換到第八個車種 | - |
| 車種管理 | `Ctrl+V` | 開啟車種管理器 | - |

### 🔍 視圖控制

| 功能 | 快捷鍵 | 說明 | 替代鍵 |
|------|--------|------|--------|
| 放大 | `Ctrl++` | 放大視圖 | 滑鼠滾輪上 |
| 縮小 | `Ctrl+-` | 縮小視圖 | 滑鼠滾輪下 |
| 適應視窗 | `Ctrl+0` | 適應視窗大小 | `F` |
| 實際大小 | `Ctrl+1` | 顯示實際大小 | - |
| 適應寬度 | `Ctrl+2` | 適應視窗寬度 | - |
| 適應高度 | `Ctrl+3` | 適應視窗高度 | - |
| 重置視圖 | `Home` | 重置視圖設定 | `R` |
| 全螢幕 | `F9` | 切換全螢幕 | - |

### 🛠 系統功能

| 功能 | 快捷鍵 | 說明 | 替代鍵 |
|------|--------|------|--------|
| 快取管理 | `F7` | 管理圖片快取 | - |
| 記憶體監控 | `F8` | 監控系統資源 | - |
| 幫助 | `F12` | 顯示幫助 | - |
| 偏好設定 | `F10` | 開啟偏好設定 | - |
| 退出程式 | `Ctrl+Q` | 退出應用程式 | `Alt+F4` |

### ⌨️ 鍵盤導航

| 功能 | 快捷鍵 | 說明 |
|------|--------|------|
| 焦點切換 | `Tab` | 在不同區域間切換焦點 |
| 上一項 | `↑` | 清單中選擇上一項 |
| 下一項 | `↓` | 清單中選擇下一項 |
| 展開/摺疊 | `Enter` | 展開或摺疊項目 |
| 快速搜尋 | `Ctrl+F` | 在清單中搜尋 |

---

## 📤 匯出格式說明

### YOLO格式 (推薦)

#### 檔案結構
```
data/
├── images/          # 原始圖片
│   ├── image1.jpg
│   └── image2.jpg
└── labels/          # YOLO標註檔案
    ├── image1.txt
    └── image2.txt
```

#### 標註格式
```text
# 格式：class_id center_x center_y width height
# 座標為相對值（0-1之間），12位小數精度
0 0.123456789012 0.987654321098 0.300000000000 0.400000000000
1 0.456789012345 0.654321098765 0.250000000000 0.350000000000
```

#### 座標計算
- `center_x` = (x_min + x_max) / 2 / image_width
- `center_y` = (y_min + y_max) / 2 / image_height
- `width` = (x_max - x_min) / image_width
- `height` = (y_max - y_min) / image_height

### COCO格式

#### JSON結構
```json
{
  "info": {
    "description": "YOLO Vehicle Annotation Dataset",
    "version": "1.0",
    "year": 2025
  },
  "images": [
    {
      "id": 1,
      "file_name": "image1.jpg",
      "width": 1920,
      "height": 1080
    }
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 0,
      "bbox": [100.0, 200.0, 300.0, 400.0],
      "area": 120000.0,
      "iscrowd": 0
    }
  ],
  "categories": [
    {
      "id": 0,
      "name": "car",
      "supercategory": "vehicle"
    }
  ]
}
```

#### 座標格式
- `bbox`: [x_min, y_min, width, height]
- 座標為絕對像素值
- 支援小數點精確度

### Pascal VOC格式

#### XML結構
```xml
<annotation>
  <folder>images</folder>
  <filename>image1.jpg</filename>
  <path>/path/to/image1.jpg</path>
  <source>
    <database>YOLO Vehicle Annotator</database>
  </source>
  <size>
    <width>1920</width>
    <height>1080</height>
    <depth>3</depth>
  </size>
  <segmented>0</segmented>
  <object>
    <name>car</name>
    <pose>Unspecified</pose>
    <truncated>0</truncated>
    <difficult>0</difficult>
    <bndbox>
      <xmin>100</xmin>
      <ymin>200</ymin>
      <xmax>400</xmax>
      <ymax>600</ymax>
    </bndbox>
  </object>
</annotation>
```

#### 座標格式
- 使用絕對像素座標
- `xmin`, `ymin`: 左上角座標
- `xmax`, `ymax`: 右下角座標

### 自訂JSON格式

#### 完整資訊格式
```json
{
  "image_path": "image1.jpg",
  "image_size": {
    "width": 1920,
    "height": 1080
  },
  "annotations": [
    {
      "id": 1,
      "class_id": 0,
      "class_name": "car",
      "bbox": {
        "x": 100.0,
        "y": 200.0,
        "width": 300.0,
        "height": 400.0
      },
      "confidence": 0.95,
      "timestamp": "2025-08-31T10:30:00Z"
    }
  ],
  "metadata": {
    "annotator": "YOLO Vehicle Annotator v2.2.0",
    "created": "2025-08-31T10:30:00Z",
    "last_modified": "2025-08-31T10:35:00Z"
  }
}
```

---

## 🔧 疑難排解

### 🚀 效能問題

#### 程式運行緩慢
**問題現象**：
- 圖片載入慢
- AI預測速度慢
- 介面卡頓

**解決方案**：
1. **檢查系統資源**
   ```bash
   # Windows
   taskmgr
   # macOS
   Activity Monitor
   # Linux
   htop
   ```

2. **優化設定**
   - 減少快取大小（F7）
   - 使用較小的AI模型
   - 關閉不必要的背景程式

3. **硬體升級建議**
   - 增加記憶體至8GB以上
   - 使用SSD硬碟
   - 升級處理器

#### 記憶體不足
**問題現象**：
- 程式崩潰
- "Out of Memory"錯誤
- 系統變慢

**解決方案**：
1. **增加虛擬記憶體**
   - Windows：系統設定 > 系統 > 關於 > 相關設定 > 進階系統設定
   - 設定虛擬記憶體為實體記憶體的1.5-2倍

2. **優化程式設定**
   - 使用YOLOv8n模型
   - 減少批次處理大小
   - 定期清理快取

### 🤖 AI功能問題

#### AI預測失敗
**問題現象**：
- AI無法啟動
- 預測結果為空
- 模型載入錯誤

**解決方案**：
1. **檢查網路連線**
   ```bash
   ping google.com
   ```

2. **重新安裝套件**
   ```bash
   pip uninstall torch torchvision ultralytics
   pip install torch torchvision ultralytics
   ```

3. **檢查模型檔案**
   - 刪除 `.cache` 資料夾
   - 重新下載模型檔案

#### 模型載入錯誤
**常見錯誤訊息**：
- "CUDA out of memory"
- "Model not found"
- "Network error"

**解決步驟**：
1. 檢查網路連線
2. 清理快取檔案
3. 重新安裝ultralytics
4. 嘗試離線模型

### 📁 檔案處理問題

#### 圖片載入失敗
**問題現象**：
- 無法開啟圖片檔案
- 顯示格式不支援
- 圖片顯示異常

**支援格式**：
- PNG, JPG, JPEG, BMP, GIF, TIFF
- RGB/RGBA色彩模式
- 最大支援4096x4096像素

**解決方案**：
1. **檢查檔案格式**
   ```bash
   file image.jpg
   ```

2. **轉換圖片格式**
   ```bash
   # 使用Python轉換
   from PIL import Image
   img = Image.open('image.jpg')
   img.save('image.png')
   ```

3. **檢查檔案損壞**
   - 使用其他圖片檢視器開啟
   - 重新下載或匯出圖片

#### 匯出檔案問題
**問題現象**：
- 匯出檔案為空
- 格式錯誤
- 編碼問題

**檢查清單**：
1. 確認有標註資料
2. 檢查輸出目錄權限
3. 確認磁碟空間充足
4. 檢查檔案路徑長度

### 🔧 系統相容性問題

#### Windows特定問題
**常見問題**：
- 路徑長度限制
- 權限問題
- 編碼問題

**解決方案**：
1. **啟用長路徑支援**
   ```cmd
   reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f
   ```

2. **以管理員身份執行**
   - 右鍵程式 > 以管理員身份執行

#### macOS特定問題
**常見問題**：
- 權限問題
- Gatekeeper阻擋
- 路徑問題

**解決方案**：
1. **允許應用程式執行**
   ```bash
   xattr -d com.apple.quarantine /path/to/application
   ```

2. **檢查權限**
   ```bash
   ls -la /path/to/directory
   ```

#### Linux特定問題
**常見問題**：
- 依賴套件缺失
- 權限問題
- 顯示問題

**解決方案**：
1. **安裝系統依賴**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-pyqt5 python3-opencv
   
   # CentOS/RHEL
   sudo yum install python3-qt5 python3-opencv
   ```

2. **檢查顯示設定**
   ```bash
   echo $DISPLAY
   ```

### 📞 技術支援

#### 聯絡方式
- **GitHub Issues**: [提交問題](https://github.com/ericchen2023/yolo-vehicle-annotator/issues)
- **Email**: <ericchen20050329@gmail.com>
- **討論區**: [GitHub Discussions](https://github.com/ericchen2023/yolo-vehicle-annotator/discussions)

#### 回報問題時請提供
1. **系統資訊**
   - 作業系統版本
   - Python版本
   - 硬體配置

2. **錯誤訊息**
   - 完整的錯誤訊息
   - 錯誤發生時的螢幕截圖

3. **重現步驟**
   - 詳細的操作步驟
   - 使用的圖片樣本
   - 設定檔案

4. **日誌檔案**
   - 程式執行日誌
   - 系統事件日誌

---

## 📜 授權條款

### MIT License

Copyright (c) 2025 Eric Chen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FORA PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

### 第三方授權

本專案使用了以下開源套件：

- **PyQt5**: GPL v3
- **PyTorch**: BSD-3-Clause
- **Ultralytics YOLOv8**: AGPL-3.0
- **OpenCV**: BSD-3-Clause
- **Pillow**: MIT
- **NumPy**: BSD-3-Clause

---

<div align="center">

**YOLOv8 車輛標註工具 v1.0.0**

*讓車輛標註工作變得簡單而高效*

[⬆️ 返回頂部](#-yolov8-車輛標註工具-v100---完整使用說明書)

最後更新: 2025年8月31日

</div>

#### 🎯 使用指南
- 按 **F4** 或點擊 **"🧠 選擇模型"** 開啟模型選擇器
- 根據硬體配置選擇適合的模型版本
- 系統自動下載不存在的模型檔案
- 支援即時模型切換，無需重啟程式

### 🎯 高精度座標匯出
極致精確的標註座標匯出功能：
- **12位小數精度**：從6位提升至12位小數點精確度
- **精度提升594,000倍**：大幅減少座標誤差
- **格式全覆蓋**：YOLO、JSON、COCO格式全面支援高精度

### 🚗 進階車種管理系統
全新升級的車種管理功能，提供專業級的車種管理體驗：

#### 🔍 智慧搜尋與過濾

- **即時搜尋**：支援車種名稱、表情符號、快捷鍵的即時搜尋
- **多重篩選**：按啟用狀態篩選（全部/啟用/停用）
- **一鍵清除**：快速清除搜尋條件和篩選器

#### ⚡ 批次操作功能

- **多選支援**：支援多個車種同時選擇
- **批次啟用/停用**：一次操作多個車種的啟用狀態
- **全選/取消全選**：快速選擇所有車種或取消選擇

#### ⌨️ 完整鍵盤快捷鍵系統

- **基本操作**：Ctrl+N新增、F2編輯、Delete刪除
- **搜尋操作**：Ctrl+F聚焦搜尋框、Escape清除搜尋
- **選擇操作**：Ctrl+A全選、方向鍵導航
- **排序操作**：Ctrl+Up/Down移動、Ctrl+S排序選單
- **批次操作**：Ctrl+Shift+E啟用、Ctrl+Shift+D停用
- **視窗操作**：Ctrl+Enter儲存、Ctrl+W關閉

#### 🎨 適應性UI設計

- **智慧分割**：QSplitter實現左右面板適應性調整
- **最小尺寸保護**：防止視窗過小導致文字截斷
- **拖拽排序**：支援拖拽行進行車種重新排序
- **即時預覽**：詳細設定面板即時反映變更

## 📋 系統需求

### 最低需求

- **作業系統**：Windows 10/11、macOS 10.14+、Ubuntu 18.04+
- **Python**：3.8 或以上版本
- **記憶體**：4GB RAM
- **硬碟空間**：2GB 可用空間

### 建議配置

- **記憶體**：8GB RAM 或以上
- **顯示卡**：支援CUDA的NVIDIA GPU（AI功能加速，建議 4GB+ VRAM）
- **處理器**：Intel i5 或 AMD Ryzen 5 以上
- **CUDA**：CUDA 11.8 或以上版本（GPU 加速必需）

## 🛠 安裝指南

### 方法一：一鍵安裝

```bash
# 1. 下載專案
git clone https://github.com/ericchen2023/yolov8-vehicle-annotator.git
cd yolo-vehicle-annotator

# 2. 執行安裝腳本
# Windows
install.bat
# macOS/Linux
./install.sh
```

### 方法二：手動安裝

```bash
# 1. 建立虛擬環境
py -m venv .venv
.venv\Scripts\activate

# 2. 安裝依賴
pip install -r requirements.txt

# 3. GPU 支援（可選，但強烈建議）
# 安裝 GPU 版本 PyTorch（CUDA 11.8）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 4. 啟動程式
python main.py
```

## 🚀 快速入門

### 基本使用流程

1. **載入圖片**：`Ctrl+O` 載入單張圖片或 `Ctrl+Shift+O` 載入資料夾
2. **選擇AI模型**：`F4` 選擇適合的YOLOv8模型版本
3. **AI自動標註**：`F5` 執行AI預測或 `Ctrl+F5` 批次處理
4. **手動調整**：使用八手柄編輯器精確調整標註
5. **匯出結果**：`Ctrl+S` 匯出YOLO格式或 `Ctrl+E` 多格式匯出

### 車種管理

- **管理車種**：`Ctrl+V` 開啟車種管理器
- **自定義車種**：新增、編輯、刪除車種類別
- **快速切換**：使用數字鍵 1-4 或自定義快捷鍵

## ⌨️ 主要快捷鍵

### 檔案操作

| 功能 | 快捷鍵 | 說明 |
|------|--------|------|
| 載入圖片 | `Ctrl+O` | 開啟單張圖片 |
| 載入資料夾 | `Ctrl+Shift+O` | 載入整個資料夾 |
| 儲存標註 | `Ctrl+S` | 匯出當前標註 |
| 進階匯出 | `Ctrl+E` | 多格式匯出 |

### AI功能

| 功能 | 快捷鍵 | 說明 |
|------|--------|------|
| 選擇模型 | `F4` | 選擇YOLOv8模型版本 |
| AI預測 | `F5` | 當前圖片AI標註 |
| 批次AI | `Ctrl+F5` | 批次AI處理 |
| AI設定 | `F6` | AI參數設定 |

### 圖片導航

| 功能 | 快捷鍵 | 說明 |
|------|--------|------|
| 上一張 | `←` `A` | 前一張圖片 |
| 下一張 | `→` `D` | 下一張圖片 |
| 車種切換 | `1-4` | 快速切換車輛類型 |

### 視圖控制

| 功能 | 快捷鍵 | 說明 |
|------|--------|------|
| 適應視窗 | `Ctrl+0` `F` | 適應視窗大小 |
| 全螢幕 | `F9` | 切換全螢幕 |
| 車種管理 | `Ctrl+V` | 車種類別管理 |

## 📤 匯出格式

### YOLO格式

標準YOLOv8訓練格式，12位小數精度座標：

```text
# 格式：class_id center_x center_y width height
0 0.123456789012 0.987654321098 0.300000000000 0.400000000000
```

### COCO格式

JSON結構化資料，支援高精度座標：

```json
{
  "images": [...],
  "annotations": [...],
  "categories": [
    {"id": 0, "name": "motorcycle"},
    {"id": 1, "name": "car"}
  ]
}
```

### Pascal VOC格式

XML結構化標註格式：

```xml
<annotation>
  <filename>image.jpg</filename>
  <object>
    <name>car</name>
    <bndbox>
      <xmin>100</xmin>
      <ymin>200</ymin>
      <xmax>300</xmax>
      <ymax>400</ymax>
    </bndbox>
  </object>
</annotation>
```

## 🔧 疑難排解

### GPU 使用教學

#### 🚀 GPU 加速設定

使用 GPU 可以大幅提升 AI 預測和模型訓練速度（比 CPU 快 5-20 倍）：

**1. 檢查 GPU 支援**

```bash
# 檢查是否有 NVIDIA GPU
nvidia-smi

# 檢查 CUDA 版本
nvcc --version
```

**2. 安裝 GPU 版本的 PyTorch**

```bash
# 停用虛擬環境（如果已啟動）
deactivate

# 重新啟動虛擬環境
.venv\Scripts\activate

# 安裝 GPU 版本 PyTorch（根據 CUDA 版本選擇）
# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 或直接安裝最新版
pip install torch torchvision torchaudio
```

**3. 驗證 GPU 設定**

在程式中會自動顯示使用的設備：

```text
🚀 使用 GPU 訓練：cuda:0    # GPU 可用
💻 使用 CPU 訓練（未檢測到可用的 GPU）    # 僅 CPU
```

**4. GPU 使用指標**

- **AI 預測**：GPU 加速 5-10 倍
- **模型訓練**：GPU 加速 10-20 倍
- **記憶體需求**：建議 4GB+ VRAM

#### 🎯 GPU 效能優化

- **批次大小調整**：GPU 記憶體充足時可增加 batch_size
- **模型選擇**：GPU 環境建議使用 YOLOv8m 或 YOLOv8l
- **訓練參數**：GPU 訓練時可增加 epochs 和 workers 數量

#### ⚠️ 常見 GPU 問題

**Q: 顯示 "CUDA out of memory"**

- 減小批次大小（batch_size）
- 選擇較小的模型（YOLOv8n 或 YOLOv8s）
- 關閉其他使用 GPU 的程式

**Q: GPU 不被識別**

- 確認已安裝正確版本的 CUDA 和 cuDNN
- 重新安裝 GPU 版本的 PyTorch
- 檢查 NVIDIA 驅動程式是否最新

**Q: 訓練速度仍然很慢**

- 確認正在使用 GPU（查看訓練日誌）
- 檢查 GPU 使用率（nvidia-smi）
- 嘗試增加批次大小和 workers 數量

### 常見問題

**Q: AI預測速度慢**

- 選擇較小的模型（YOLOv8n 或 YOLOv8s）
- 檢查CUDA是否正確安裝
- 調整批次大小設定

**Q: 記憶體不足**

- 使用較小的AI模型
- 調整快取大小設定（F7）
- 關閉其他大型應用程式

**Q: 匯出檔案為空**

- 確認已建立標註
- 檢查輸出目錄權限
- 確認圖片已正確載入

### 效能優化

- **記憶體監控**：按 F8 開啟記憶體監控
- **快取管理**：按 F7 管理圖片快取
- **模型選擇**：根據硬體選擇適合的AI模型

## � 支援與貢獻

### 技術支援

- **Github Issues**: [提交問題](https://github.com/ericchen2023/yolo-vehicle-annotator/issues)
- **Email**: <ericchen20050329@gmail.com>

### 授權條款

本專案採用 MIT 授權條款，歡迎貢獻與使用。

---

版本: v2.2.0 | 最後更新: 2025-08-27
