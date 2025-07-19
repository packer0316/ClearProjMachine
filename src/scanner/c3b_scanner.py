#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C3B檔案掃描器 - 負責解析.c3b檔案中引用的圖片檔案
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional

# 添加專案根目錄到路徑以導入c3b_parser
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from c3b_parser import C3BParser
from src.utils.logger import ScannerLogger


class C3BScanner:
    """C3B檔案掃描器 - 負責解析.c3b檔案中引用的圖片檔案"""
    
    def __init__(self, project_path: str, image_types: Set[str], progress_callback=None):
        """
        初始化C3B掃描器
        
        Args:
            project_path: 專案根目錄路徑
            image_types: 要搜尋的圖片類型集合
            progress_callback: 進度回調函數，接收 (current, total, message) 參數
        """
        self.project_path = Path(project_path)
        self.image_types = image_types
        self.c3b_files = []
        self.results = {}
        self.logger = ScannerLogger()
        self.successful_scans = 0
        self.failed_scans = 0
        self.progress_callback = progress_callback
        self.c3b_parser = C3BParser()
    
    def _report_progress(self, current: int, total: int, message: str):
        """報告進度"""
        if self.progress_callback:
            self.progress_callback(current, total, message)
    
    def scan_c3b_files(self) -> Dict[str, List[str]]:
        """
        掃描專案中的所有.c3b檔案並分析其引用的圖片檔案
        
        Returns:
            Dict[str, List[str]]: 以檔案路徑為key，引用圖片列表為value的字典
        """
        try:
            self.logger.info(f"開始掃描專案: {self.project_path}")
            
            # 尋找所有C3B檔案
            self._find_all_c3b_files()
            total_files = len(self.c3b_files)
            
            # 報告找到的檔案數量
            self.logger.info(f"找到 {len(self.c3b_files)} 個C3B檔案")
            
            # 如果沒有檔案要分析，直接返回
            if total_files == 0:
                self._report_progress(0, 0, "未找到任何C3B檔案")
                return self.results
            
            # 分析每個C3B檔案
            for i, c3b_file in enumerate(self.c3b_files, 1):
                try:
                    # 報告當前分析進度
                    progress_msg = f"正在分析C3B檔案: {c3b_file.name}"
                    self._report_progress(i, total_files, progress_msg)
                    self.logger.info(f"分析C3B檔案 ({i}/{total_files}): {c3b_file.name}")
                    
                    # 解析C3B檔案
                    referenced_images = self._analyze_c3b_file(c3b_file)
                    if referenced_images:
                        self.results[str(c3b_file)] = referenced_images
                        self.successful_scans += 1
                        self.logger.info(f"成功解析C3B檔案，找到 {len(referenced_images)} 個圖片引用")
                    else:
                        self.successful_scans += 1
                        self.logger.warning(f"C3B檔案解析完成，但未找到圖片引用")
                        
                except Exception as e:
                    self.failed_scans += 1
                    error_msg = str(e)
                    self.logger.error(f"分析C3B檔案 {c3b_file} 時發生錯誤: {error_msg}")
                    continue
            
            # 報告分析完成
            self._report_progress(total_files, total_files, "C3B檔案分析完成")
            
            # 記錄掃描摘要
            self.logger.log_scan_summary(total_files, self.successful_scans, self.failed_scans)
            self.logger.info(f"掃描完成，總共解析出 {len(self.results)} 個有效結果")
            
            return self.results
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"掃描過程中發生錯誤: {error_msg}")
            return self.results
    
    def _find_all_c3b_files(self):
        """尋找專案中的所有.c3b檔案"""
        self.c3b_files = []
        
        try:
            for root, dirs, files in os.walk(self.project_path):
                for file in files:
                    if file.lower().endswith('.c3b'):
                        file_path = Path(root) / file
                        self.c3b_files.append(file_path)
        except Exception as e:
            print(f"掃描檔案時發生錯誤: {str(e)}")
    
    def _analyze_c3b_file(self, c3b_file_path: Path) -> List[str]:
        """
        分析單個C3B檔案中引用的圖片檔案
        
        Args:
            c3b_file_path: C3B檔案路徑
            
        Returns:
            List[str]: 引用圖片檔案的路徑列表
        """
        referenced_images = []
        
        try:
            # 檢查檔案是否存在且可讀
            if not c3b_file_path.exists():
                print(f"檔案不存在: {c3b_file_path}")
                return referenced_images
            
            if not c3b_file_path.is_file():
                print(f"不是檔案: {c3b_file_path}")
                return referenced_images
            
            # 檢查檔案大小
            file_size = c3b_file_path.stat().st_size
            if file_size > 50 * 1024 * 1024:  # 50MB限制
                print(f"檔案太大，跳過: {c3b_file_path} ({file_size} bytes)")
                return referenced_images
            
            # 使用C3BParser解析檔案
            result = self.c3b_parser.parse_c3b_file(str(c3b_file_path))
            
            if 'error' in result:
                print(f"解析C3B檔案時發生錯誤: {result['error']}")
                return referenced_images
            
            # 提取圖片引用
            if 'referenced_images' in result:
                for image_name in result['referenced_images']:
                    # 過濾出支援的圖片格式
                    if any(image_name.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                        # 尋找對應的檔案路徑
                        full_path = self._find_image_file(image_name, c3b_file_path.parent)
                        if full_path:
                            referenced_images.append(full_path)
                        else:
                            # 如果找不到完整路徑，直接使用檔案名
                            referenced_images.append(image_name)
            
            # 清除parser的狀態，為下一個檔案準備
            self.c3b_parser.referenced_images.clear()
            
        except PermissionError:
            print(f"沒有權限讀取檔案: {c3b_file_path}")
        except Exception as e:
            print(f"解析C3B檔案 {c3b_file_path} 時發生錯誤: {str(e)}")
        
        return referenced_images
    
    def _find_image_file(self, image_name: str, base_path: Path) -> Optional[str]:
        """
        在專案中尋找圖片檔案的完整路徑
        
        Args:
            image_name: 圖片檔案名稱
            base_path: 基礎搜尋路徑
            
        Returns:
            Optional[str]: 找到的完整路徑，未找到則返回None
        """
        # 方法1: 在C3B檔案同一目錄下尋找
        same_dir_path = base_path / image_name
        if same_dir_path.exists():
            return str(same_dir_path)
        
        # 方法2: 在專案根目錄下遞迴搜尋
        try:
            for root, dirs, files in os.walk(self.project_path):
                for file in files:
                    if file.lower() == image_name.lower():
                        return os.path.join(root, file)
        except Exception:
            pass
        
        return None
    
    def get_statistics(self) -> Dict[str, any]:
        """
        取得掃描統計資訊
        
        Returns:
            Dict[str, any]: 統計資訊字典
        """
        total_files = len(self.c3b_files)
        total_referenced_files = sum(len(files) for files in self.results.values())
        
        return {
            'total_files': total_files,
            'analyzed_files': self.successful_scans,
            'failed_scans': self.failed_scans,
            'total_referenced_files': total_referenced_files,
            'total_c3b_files': len(self.c3b_files)
        } 