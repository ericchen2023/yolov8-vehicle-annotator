"""
檔案管理模組 - 專案檔案管理、最近開啟清單、自動備份
"""

import os
import json
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class FileManager:
    """檔案管理器"""
    
    def __init__(self, config_dir: str = None):
        # 備份設定（先設定這些屬性）
        self.max_recent_files = 20
        self.max_backups = 10
        self.backup_interval_hours = 1
        
        # 設定檔案目錄
        if config_dir is None:
            self.config_dir = os.path.expanduser("~/.yolo_annotator")
        else:
            self.config_dir = config_dir
            
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 設定檔案路徑
        self.recent_files_path = os.path.join(self.config_dir, "recent_files.json")
        self.projects_dir = os.path.join(self.config_dir, "projects")
        self.backups_dir = os.path.join(self.config_dir, "backups")
        
        # 建立目錄
        os.makedirs(self.projects_dir, exist_ok=True)
        os.makedirs(self.backups_dir, exist_ok=True)
        
        # 載入最近開啟的檔案
        self.recent_files = self.load_recent_files()
    
    def load_recent_files(self) -> List[Dict]:
        """載入最近開啟的檔案清單"""
        try:
            if os.path.exists(self.recent_files_path):
                with open(self.recent_files_path, 'r', encoding='utf-8') as f:
                    recent_files = json.load(f)
                    
                # 過濾掉不存在的檔案
                valid_files = []
                for file_info in recent_files:
                    if os.path.exists(file_info.get('path', '')):
                        valid_files.append(file_info)
                        
                return valid_files[:self.max_recent_files]
            return []
        except Exception as e:
            print(f"載入最近檔案錯誤: {e}")
            return []
    
    def save_recent_files(self):
        """保存最近開啟的檔案清單"""
        try:
            with open(self.recent_files_path, 'w', encoding='utf-8') as f:
                json.dump(self.recent_files, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存最近檔案錯誤: {e}")
    
    def add_recent_file(self, file_path: str, file_type: str = 'image'):
        """添加檔案到最近開啟清單"""
        try:
            file_info = {
                'path': os.path.abspath(file_path),
                'name': os.path.basename(file_path),
                'type': file_type,
                'last_opened': datetime.now().isoformat(),
                'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
            
            # 移除相同路徑的舊記錄
            self.recent_files = [f for f in self.recent_files if f['path'] != file_info['path']]
            
            # 添加到清單開頭
            self.recent_files.insert(0, file_info)
            
            # 限制清單長度
            self.recent_files = self.recent_files[:self.max_recent_files]
            
            # 保存
            self.save_recent_files()
            
        except Exception as e:
            print(f"添加最近檔案錯誤: {e}")
    
    def get_recent_files(self, file_type: str = None) -> List[Dict]:
        """取得最近開啟的檔案清單"""
        if file_type is None:
            return self.recent_files
        return [f for f in self.recent_files if f.get('type') == file_type]
    
    def clear_recent_files(self):
        """清空最近開啟的檔案清單"""
        self.recent_files = []
        self.save_recent_files()
    
    def create_project(self, project_name: str, project_data: Dict) -> str:
        """創建新專案"""
        try:
            # 專案檔案路徑
            project_filename = f"{project_name}.json"
            project_path = os.path.join(self.projects_dir, project_filename)
            
            # 專案資料結構
            project_info = {
                'project_name': project_name,
                'created_date': datetime.now().isoformat(),
                'modified_date': datetime.now().isoformat(),
                'version': '1.0',
                'settings': project_data.get('settings', {}),
                'images': project_data.get('images', []),
                'annotations': project_data.get('annotations', {}),
                'statistics': project_data.get('statistics', {})
            }
            
            # 保存專案檔案
            with open(project_path, 'w', encoding='utf-8') as f:
                json.dump(project_info, f, indent=2, ensure_ascii=False)
            
            # 添加到最近檔案
            self.add_recent_file(project_path, 'project')
            
            return project_path
            
        except Exception as e:
            print(f"創建專案錯誤: {e}")
            return None
    
    def load_project(self, project_path: str) -> Optional[Dict]:
        """載入專案檔案"""
        try:
            if not os.path.exists(project_path):
                return None
                
            with open(project_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # 添加到最近檔案
            self.add_recent_file(project_path, 'project')
            
            return project_data
            
        except Exception as e:
            print(f"載入專案錯誤: {e}")
            return None
    
    def save_project(self, project_path: str, project_data: Dict) -> bool:
        """保存專案檔案"""
        try:
            # 更新修改時間
            project_data['modified_date'] = datetime.now().isoformat()
            
            # 備份現有檔案
            if os.path.exists(project_path):
                self.create_backup(project_path)
            
            # 保存專案檔案
            with open(project_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            # 添加到最近檔案
            self.add_recent_file(project_path, 'project')
            
            return True
            
        except Exception as e:
            print(f"保存專案錯誤: {e}")
            return False
    
    def get_project_list(self) -> List[Dict]:
        """取得專案清單"""
        try:
            projects = []
            
            if os.path.exists(self.projects_dir):
                for filename in os.listdir(self.projects_dir):
                    if filename.endswith('.json'):
                        project_path = os.path.join(self.projects_dir, filename)
                        
                        try:
                            with open(project_path, 'r', encoding='utf-8') as f:
                                project_data = json.load(f)
                                
                            project_info = {
                                'name': project_data.get('project_name', filename[:-5]),
                                'path': project_path,
                                'created_date': project_data.get('created_date', ''),
                                'modified_date': project_data.get('modified_date', ''),
                                'images_count': len(project_data.get('images', [])),
                                'annotations_count': sum(len(anns) for anns in project_data.get('annotations', {}).values())
                            }
                            projects.append(project_info)
                            
                        except Exception as e:
                            print(f"讀取專案 {filename} 錯誤: {e}")
            
            # 按修改時間排序
            projects.sort(key=lambda x: x.get('modified_date', ''), reverse=True)
            return projects
            
        except Exception as e:
            print(f"取得專案清單錯誤: {e}")
            return []
    
    def delete_project(self, project_path: str) -> bool:
        """刪除專案"""
        try:
            if os.path.exists(project_path):
                # 創建備份
                self.create_backup(project_path, backup_type='deleted')
                
                # 刪除檔案
                os.remove(project_path)
                
                # 從最近檔案中移除
                self.recent_files = [f for f in self.recent_files if f['path'] != project_path]
                self.save_recent_files()
                
                return True
            return False
            
        except Exception as e:
            print(f"刪除專案錯誤: {e}")
            return False
    
    def create_backup(self, file_path: str, backup_type: str = 'auto') -> bool:
        """創建檔案備份"""
        try:
            if not os.path.exists(file_path):
                return False
            
            # 建立備份檔案名稱
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            backup_filename = f"{name}_{backup_type}_{timestamp}{ext}"
            backup_path = os.path.join(self.backups_dir, backup_filename)
            
            # 複製檔案
            shutil.copy2(file_path, backup_path)
            
            # 清理舊備份
            self.cleanup_old_backups()
            
            return True
            
        except Exception as e:
            print(f"創建備份錯誤: {e}")
            return False
    
    def cleanup_old_backups(self):
        """清理舊備份檔案"""
        try:
            if not os.path.exists(self.backups_dir):
                return
            
            # 取得所有備份檔案
            backup_files = []
            for filename in os.listdir(self.backups_dir):
                file_path = os.path.join(self.backups_dir, filename)
                if os.path.isfile(file_path):
                    backup_files.append({
                        'path': file_path,
                        'name': filename,
                        'mtime': os.path.getmtime(file_path)
                    })
            
            # 按修改時間排序
            backup_files.sort(key=lambda x: x['mtime'], reverse=True)
            
            # 刪除超過限制的備份
            if len(backup_files) > self.max_backups:
                for backup in backup_files[self.max_backups:]:
                    try:
                        os.remove(backup['path'])
                    except:
                        pass
            
            # 刪除超過30天的備份
            cutoff_time = datetime.now() - timedelta(days=30)
            for backup in backup_files:
                backup_time = datetime.fromtimestamp(backup['mtime'])
                if backup_time < cutoff_time:
                    try:
                        os.remove(backup['path'])
                    except:
                        pass
                        
        except Exception as e:
            print(f"清理備份錯誤: {e}")
    
    def get_backup_list(self) -> List[Dict]:
        """取得備份清單"""
        try:
            backups = []
            
            if os.path.exists(self.backups_dir):
                for filename in os.listdir(self.backups_dir):
                    file_path = os.path.join(self.backups_dir, filename)
                    if os.path.isfile(file_path):
                        backup_info = {
                            'name': filename,
                            'path': file_path,
                            'size': os.path.getsize(file_path),
                            'created_date': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                            'modified_date': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                        }
                        backups.append(backup_info)
            
            # 按修改時間排序
            backups.sort(key=lambda x: x['modified_date'], reverse=True)
            return backups
            
        except Exception as e:
            print(f"取得備份清單錯誤: {e}")
            return []
    
    def auto_backup_check(self, project_path: str) -> bool:
        """檢查是否需要自動備份"""
        try:
            if not os.path.exists(project_path):
                return False
            
            # 取得檔案修改時間
            file_mtime = datetime.fromtimestamp(os.path.getmtime(project_path))
            
            # 檢查是否有最近的備份
            filename = os.path.basename(project_path)
            name = os.path.splitext(filename)[0]
            
            latest_backup_time = None
            for backup_name in os.listdir(self.backups_dir):
                if backup_name.startswith(f"{name}_auto_"):
                    backup_path = os.path.join(self.backups_dir, backup_name)
                    backup_time = datetime.fromtimestamp(os.path.getmtime(backup_path))
                    if latest_backup_time is None or backup_time > latest_backup_time:
                        latest_backup_time = backup_time
            
            # 如果沒有備份或備份太舊，創建新備份
            if (latest_backup_time is None or 
                file_mtime - latest_backup_time > timedelta(hours=self.backup_interval_hours)):
                return self.create_backup(project_path, 'auto')
            
            return False
            
        except Exception as e:
            print(f"自動備份檢查錯誤: {e}")
            return False
    
    def export_project_summary(self, output_dir: str) -> bool:
        """匯出專案摘要報告"""
        try:
            projects = self.get_project_list()
            recent_files = self.get_recent_files()
            backups = self.get_backup_list()
            
            summary = {
                "generated_date": datetime.now().isoformat(),
                "total_projects": len(projects),
                "recent_files_count": len(recent_files),
                "backups_count": len(backups),
                "projects": projects,
                "recent_files": recent_files[:10],  # 只顯示前10個
                "storage_info": {
                    "config_dir": self.config_dir,
                    "projects_dir": self.projects_dir,
                    "backups_dir": self.backups_dir
                }
            }
            
            report_path = os.path.join(output_dir, "project_summary.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"匯出專案摘要錯誤: {e}")
            return False
