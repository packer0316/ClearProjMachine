import os
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
import struct
from src.utils.logger import ScannerLogger


class EFKScanner:
    """EFK檔案掃描器 - 負責解析.efk檔案中的引用檔案"""
    
    def __init__(self, project_path: str, image_types: Set[str]):
        """
        初始化EFK掃描器
        
        Args:
            project_path: 專案根目錄路徑
            image_types: 要搜尋的圖片類型集合
        """
        self.project_path = Path(project_path)
        self.image_types = image_types
        self.efk_files = []
        self.results = {}
        self.logger = ScannerLogger()
        self.successful_scans = 0
        self.failed_scans = 0
    
    def scan_efk_files(self) -> Dict[str, List[str]]:
        """
        掃描專案中的所有.efk檔案並分析其引用的檔案
        
        Returns:
            Dict[str, List[str]]: 以EFK檔案路徑為key，引用檔案列表為value的字典
        """
        try:
            self.logger.info(f"開始掃描專案: {self.project_path}")
            
            # 尋找所有.efk檔案
            self._find_efk_files()
            self.logger.info(f"找到 {len(self.efk_files)} 個EFK檔案")
            
            # 分析每個EFK檔案
            for i, efk_file in enumerate(self.efk_files, 1):
                try:
                    self.logger.info(f"分析檔案 {i}/{len(self.efk_files)}: {efk_file.name}")
                    referenced_files = self._analyze_efk_file(efk_file)
                    if referenced_files:
                        self.results[str(efk_file)] = referenced_files
                        self.successful_scans += 1
                        self.logger.info(f"成功解析檔案，找到 {len(referenced_files)} 個引用")
                    else:
                        self.successful_scans += 1
                        self.logger.warning(f"檔案解析完成，但未找到引用")
                except Exception as e:
                    self.failed_scans += 1
                    error_msg = str(e)
                    self.logger.error(f"分析檔案 {efk_file} 時發生錯誤: {error_msg}")
                    self.logger.log_file_scan(str(efk_file), False, error_msg)
                    continue
            
            # 記錄掃描摘要
            self.logger.log_scan_summary(len(self.efk_files), self.successful_scans, self.failed_scans)
            self.logger.info(f"掃描完成，總共解析出 {len(self.results)} 個有效結果")
            
            return self.results
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"掃描過程中發生錯誤: {error_msg}")
            return self.results
    
    def _find_efk_files(self):
        """尋找專案中的所有.efk檔案"""
        self.efk_files = []
        
        try:
            for root, dirs, files in os.walk(self.project_path):
                for file in files:
                    if file.lower().endswith('.efk'):
                        file_path = Path(root) / file
                        self.efk_files.append(file_path)
        except Exception as e:
            print(f"掃描檔案時發生錯誤: {str(e)}")
            # 確保即使出錯也能返回已找到的檔案
            pass
    
    def _analyze_efk_file(self, efk_file_path: Path) -> List[str]:
        """
        分析單個EFK檔案中的引用檔案
        
        Args:
            efk_file_path: EFK檔案路徑
            
        Returns:
            List[str]: 引用檔案的路徑列表
        """
        referenced_files = []
        
        try:
            # 檢查檔案是否存在且可讀
            if not efk_file_path.exists():
                print(f"檔案不存在: {efk_file_path}")
                return referenced_files
            
            if not efk_file_path.is_file():
                print(f"不是檔案: {efk_file_path}")
                return referenced_files
            
            # 檢查檔案大小
            file_size = efk_file_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB限制
                print(f"檔案太大，跳過: {efk_file_path} ({file_size} bytes)")
                return referenced_files
            
            # 讀取EFK檔案內容
            with open(efk_file_path, 'rb') as f:
                content = f.read()
            
            # 嘗試解析EFK檔案結構
            referenced_files = self._parse_efk_content(content, efk_file_path)
            
        except PermissionError:
            print(f"沒有權限讀取檔案: {efk_file_path}")
        except Exception as e:
            # 使用更安全的錯誤處理
            try:
                print(f"解析EFK檔案 {efk_file_path} 時發生錯誤: {str(e)}")
            except Exception:
                print(f"解析EFK檔案時發生未知錯誤")
        
        return referenced_files
    
    def _parse_efk_content(self, content: bytes, efk_file_path: Path) -> List[str]:
        """
        解析EFK檔案內容，尋找引用的檔案
        
        Args:
            content: EFK檔案的二進制內容
            efk_file_path: EFK檔案路徑
            
        Returns:
            List[str]: 引用檔案的路徑列表
        """
        referenced_files = []
        
        # 使用精確的EFK解析邏輯
        try:
            # 解析UTF-16字串
            strings = self._parse_utf16_strings(content)
            
            # 從字串中提取檔案路徑
            for string_info in strings:
                string = string_info['string']
                
                # 檢查是否包含檔案路徑
                if any(ext in string.lower() for ext in ['.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.efk', '.efkmat', '.efkmodel']):
                    # 提取個別檔案路徑
                    individual_paths = self._extract_file_paths_from_string(string)
                    referenced_files.extend(individual_paths)
            
            # 移除重複
            referenced_files = list(set(referenced_files))
            
        except Exception as e:
            self.logger.error(f"解析EFK檔案內容時發生錯誤: {str(e)}")
        
        return referenced_files
    
    def _parse_utf16_strings(self, content: bytes) -> List[Dict[str, any]]:
        """
        解析EFK檔案中的UTF-16字串
        
        Args:
            content: EFK檔案的二進制內容
            
        Returns:
            List[Dict[str, any]]: 字串資訊列表
        """
        strings = []
        
        # 跳過檔案頭（4 bytes）
        pos = 4
        
        while pos < len(content):
            # 嘗試讀取長度
            if pos + 4 <= len(content):
                try:
                    length = struct.unpack('<I', content[pos:pos+4])[0]
                    
                    # 檢查長度是否合理
                    if 0 < length < 1000 and pos + 4 + length * 2 <= len(content):
                        # 讀取UTF-16字串
                        string_data = content[pos+4:pos+4+length*2]
                        
                        try:
                            # 嘗試UTF-16LE解碼
                            string = string_data.decode('utf-16le')
                            strings.append({
                                'position': pos,
                                'length': length,
                                'string': string
                            })
                            
                            # 移動到下一個位置
                            pos += 4 + length * 2
                            continue
                        except:
                            pass
                except:
                    pass
            
            pos += 1
        
        return strings
    
    def _extract_file_paths_from_string(self, combined_string: str) -> List[str]:
        """
        從連在一起的字串中提取個別檔案路徑
        
        Args:
            combined_string: 連在一起的檔案路徑字串
            
        Returns:
            List[str]: 提取的檔案路徑列表
        """
        # 檔案副檔名模式
        file_extensions = [
            '.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp',
            '.efk', '.efkmat', '.efkmodel'
        ]
        
        paths = []
        
        # 尋找所有檔案副檔名的位置
        for ext in file_extensions:
            start = 0
            while True:
                pos = combined_string.find(ext, start)
                if pos == -1:
                    break
                
                # 向前搜尋檔案名開始
                file_start = pos
                while file_start > 0:
                    char = combined_string[file_start - 1]
                    if char in '\\/':
                        break
                    if not char.isalnum() and char not in '._-':
                        break
                    file_start -= 1
                
                # 向後搜尋檔案名結束
                file_end = pos + len(ext)
                while file_end < len(combined_string):
                    char = combined_string[file_end]
                    if char in '\\/':
                        break
                    if not char.isalnum() and char not in '._-':
                        break
                    file_end += 1
                
                file_path = combined_string[file_start:file_end]
                if file_path not in paths:
                    paths.append(file_path)
                
                start = pos + 1
        
        return paths
    
    def _search_binary_patterns(self, content: bytes, efk_file_path: Path) -> List[str]:
        """
        在二進制內容中搜尋檔案路徑模式（保留以備將來擴展）
        
        Args:
            content: 檔案的二進制內容
            efk_file_path: EFK檔案路徑
            
        Returns:
            List[str]: 找到的檔案引用列表
        """
        # 目前使用UTF-16字串解析，此方法保留以備將來擴展
        return []
    
    def _extract_file_path(self, text_content: str, start_pos: int, efk_file_path: Path) -> Optional[str]:
        """
        從指定位置提取檔案路徑
        
        Args:
            text_content: 文字內容
            start_pos: 開始位置
            efk_file_path: EFK檔案路徑
            
        Returns:
            Optional[str]: 提取的檔案路徑，如果無效則返回None
        """
        # 向前搜尋檔案路徑的開始
        start = start_pos
        while start > 0 and text_content[start-1] not in ['\x00', '\n', '\r', '\t', ' ']:
            start -= 1
        
        # 向後搜尋檔案路徑的結束
        end = start_pos
        while end < len(text_content) and text_content[end] not in ['\x00', '\n', '\r', '\t', ' ']:
            end += 1
        
        file_path = text_content[start:end].strip()
        
        if self._is_valid_file_path(file_path, efk_file_path):
            return file_path
        
        return None
    
    def _is_valid_file_path(self, file_path: str, efk_file_path: Path) -> bool:
        """
        檢查檔案路徑是否有效
        
        Args:
            file_path: 檔案路徑
            efk_file_path: EFK檔案路徑
            
        Returns:
            bool: 是否為有效的檔案路徑
        """
        if not file_path or len(file_path) < 3:
            return False
        
        # 檢查是否包含有效的檔案副檔名
        valid_extensions = {
            '.efkmat', '.efkmodel', '.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp',
            '.tiff', '.tif', '.webp', '.ktx', '.pvr'
        }
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in valid_extensions:
            return False
        
        # 檢查路徑是否包含無效字元（但允許某些特殊字元）
        invalid_chars = ['<', '>', '|', '?', '*']
        if any(char in file_path for char in invalid_chars):
            return False
        
        # 檢查路徑長度
        if len(file_path) > 500:  # 路徑太長
            return False
        
        # 檢查是否為相對路徑或絕對路徑
        if file_path.startswith('http://') or file_path.startswith('https://'):
            return False  # 不支援網路路徑
        
        return True
    
    def get_statistics(self) -> Dict[str, int]:
        """
        取得掃描統計資訊
        
        Returns:
            Dict[str, int]: 統計資訊字典
        """
        total_efk_files = len(self.efk_files)
        analyzed_efk_files = len(self.results)
        total_referenced_files = sum(len(files) for files in self.results.values())
        
        return {
            "total_efk_files": total_efk_files,
            "analyzed_efk_files": analyzed_efk_files,
            "total_referenced_files": total_referenced_files
        } 