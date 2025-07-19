import os
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
import struct
from src.utils.logger import ScannerLogger


class EFKScanner:
    """EFK檔案掃描器 - 負責解析.efk、.efkmat、.efkmodel檔案中的引用檔案"""
    
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
        self.efkmat_files = []
        self.efkmodel_files = []
        self.results = {}
        self.logger = ScannerLogger()
        self.successful_scans = 0
        self.failed_scans = 0
    
    def scan_efk_files(self) -> Dict[str, List[str]]:
        """
        掃描專案中的所有.efk、.efkmat、.efkmodel檔案並分析其引用的檔案
        
        Returns:
            Dict[str, List[str]]: 以檔案路徑為key，引用檔案列表為value的字典
        """
        try:
            self.logger.info(f"開始掃描專案: {self.project_path}")
            
            # 尋找所有相關檔案
            self._find_all_efk_files()
            total_files = len(self.efk_files) + len(self.efkmat_files) + len(self.efkmodel_files)
            self.logger.info(f"找到 {len(self.efk_files)} 個EFK檔案, {len(self.efkmat_files)} 個EFKMAT檔案, {len(self.efkmodel_files)} 個EFKMODEL檔案")
            
            # 分析每個EFK檔案
            for i, efk_file in enumerate(self.efk_files, 1):
                try:
                    self.logger.info(f"分析EFK檔案 {i}/{len(self.efk_files)}: {efk_file.name}")
                    referenced_files = self._analyze_efk_file(efk_file)
                    if referenced_files:
                        self.results[str(efk_file)] = referenced_files
                        self.successful_scans += 1
                        self.logger.info(f"成功解析EFK檔案，找到 {len(referenced_files)} 個引用")
                    else:
                        self.successful_scans += 1
                        self.logger.warning(f"EFK檔案解析完成，但未找到引用")
                except Exception as e:
                    self.failed_scans += 1
                    error_msg = str(e)
                    self.logger.error(f"分析EFK檔案 {efk_file} 時發生錯誤: {error_msg}")
                    self.logger.log_file_scan(str(efk_file), False, error_msg)
                    continue
            
            # 分析每個EFKMAT檔案
            for i, efkmat_file in enumerate(self.efkmat_files, 1):
                try:
                    self.logger.info(f"分析EFKMAT檔案 {i}/{len(self.efkmat_files)}: {efkmat_file.name}")
                    referenced_files = self._analyze_efkmat_file(efkmat_file)
                    if referenced_files:
                        self.results[str(efkmat_file)] = referenced_files
                        self.successful_scans += 1
                        self.logger.info(f"成功解析EFKMAT檔案，找到 {len(referenced_files)} 個引用")
                    else:
                        self.successful_scans += 1
                        self.logger.warning(f"EFKMAT檔案解析完成，但未找到引用")
                except Exception as e:
                    self.failed_scans += 1
                    error_msg = str(e)
                    self.logger.error(f"分析EFKMAT檔案 {efkmat_file} 時發生錯誤: {error_msg}")
                    self.logger.log_file_scan(str(efkmat_file), False, error_msg)
                    continue
            
            # 分析每個EFKMODEL檔案
            for i, efkmodel_file in enumerate(self.efkmodel_files, 1):
                try:
                    self.logger.info(f"分析EFKMODEL檔案 {i}/{len(self.efkmodel_files)}: {efkmodel_file.name}")
                    referenced_files = self._analyze_efkmodel_file(efkmodel_file)
                    if referenced_files:
                        self.results[str(efkmodel_file)] = referenced_files
                        self.successful_scans += 1
                        self.logger.info(f"成功解析EFKMODEL檔案，找到 {len(referenced_files)} 個引用")
                    else:
                        self.successful_scans += 1
                        self.logger.warning(f"EFKMODEL檔案解析完成，但未找到引用")
                except Exception as e:
                    self.failed_scans += 1
                    error_msg = str(e)
                    self.logger.error(f"分析EFKMODEL檔案 {efkmodel_file} 時發生錯誤: {error_msg}")
                    self.logger.log_file_scan(str(efkmodel_file), False, error_msg)
                    continue
            
            # 記錄掃描摘要
            self.logger.log_scan_summary(total_files, self.successful_scans, self.failed_scans)
            self.logger.info(f"掃描完成，總共解析出 {len(self.results)} 個有效結果")
            
            return self.results
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"掃描過程中發生錯誤: {error_msg}")
            return self.results
    
    def _find_all_efk_files(self):
        """尋找專案中的所有.efk、.efkmat、.efkmodel檔案"""
        self.efk_files = []
        self.efkmat_files = []
        self.efkmodel_files = []
        
        try:
            for root, dirs, files in os.walk(self.project_path):
                for file in files:
                    file_lower = file.lower()
                    file_path = Path(root) / file
                    
                    if file_lower.endswith('.efk'):
                        self.efk_files.append(file_path)
                    elif file_lower.endswith('.efkmat'):
                        self.efkmat_files.append(file_path)
                    elif file_lower.endswith('.efkmodel'):
                        self.efkmodel_files.append(file_path)
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
    
    def _analyze_efkmat_file(self, efkmat_file_path: Path) -> List[str]:
        """
        分析單個EFKMAT檔案中的引用檔案
        
        Args:
            efkmat_file_path: EFKMAT檔案路徑
            
        Returns:
            List[str]: 引用檔案的路徑列表
        """
        referenced_files = []
        
        try:
            # 檢查檔案是否存在且可讀
            if not efkmat_file_path.exists():
                print(f"檔案不存在: {efkmat_file_path}")
                return referenced_files
            
            if not efkmat_file_path.is_file():
                print(f"不是檔案: {efkmat_file_path}")
                return referenced_files
            
            # 檢查檔案大小
            file_size = efkmat_file_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB限制
                print(f"檔案太大，跳過: {efkmat_file_path} ({file_size} bytes)")
                return referenced_files
            
            # 讀取EFKMAT檔案內容
            with open(efkmat_file_path, 'rb') as f:
                content = f.read()
            
            # 嘗試解析EFKMAT檔案結構
            referenced_files = self._parse_efkmat_content(content, efkmat_file_path)
            
        except PermissionError:
            print(f"沒有權限讀取檔案: {efkmat_file_path}")
        except Exception as e:
            # 使用更安全的錯誤處理
            try:
                print(f"解析EFKMAT檔案 {efkmat_file_path} 時發生錯誤: {str(e)}")
            except Exception:
                print(f"解析EFKMAT檔案時發生未知錯誤")
        
        return referenced_files
    
    def _analyze_efkmodel_file(self, efkmodel_file_path: Path) -> List[str]:
        """
        分析單個EFKMODEL檔案中的引用檔案
        
        Args:
            efkmodel_file_path: EFKMODEL檔案路徑
            
        Returns:
            List[str]: 引用檔案的路徑列表
        """
        referenced_files = []
        
        try:
            # 檢查檔案是否存在且可讀
            if not efkmodel_file_path.exists():
                print(f"檔案不存在: {efkmodel_file_path}")
                return referenced_files
            
            if not efkmodel_file_path.is_file():
                print(f"不是檔案: {efkmodel_file_path}")
                return referenced_files
            
            # 檢查檔案大小
            file_size = efkmodel_file_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB限制
                print(f"檔案太大，跳過: {efkmodel_file_path} ({file_size} bytes)")
                return referenced_files
            
            # 讀取EFKMODEL檔案內容
            with open(efkmodel_file_path, 'rb') as f:
                content = f.read()
            
            # 嘗試解析EFKMODEL檔案結構
            referenced_files = self._parse_efkmodel_content(content, efkmodel_file_path)
            
        except PermissionError:
            print(f"沒有權限讀取檔案: {efkmodel_file_path}")
        except Exception as e:
            # 使用更安全的錯誤處理
            try:
                print(f"解析EFKMODEL檔案 {efkmodel_file_path} 時發生錯誤: {str(e)}")
            except Exception:
                print(f"解析EFKMODEL檔案時發生未知錯誤")
        
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
    
    def _parse_efkmat_content(self, content: bytes, efkmat_file_path: Path) -> List[str]:
        """
        解析EFKMAT檔案內容，尋找引用的檔案
        
        Args:
            content: EFKMAT檔案的二進制內容
            efkmat_file_path: EFKMAT檔案路徑
            
        Returns:
            List[str]: 引用檔案的路徑列表
        """
        referenced_files = []
        
        try:
            # 嘗試多種解析方法
            # 方法1: 解析UTF-16字串
            strings = self._parse_utf16_strings(content)
            
            # 從字串中提取檔案路徑
            for string_info in strings:
                string = string_info['string']
                
                # 檢查是否包含檔案路徑
                if any(ext in string.lower() for ext in ['.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.efk', '.efkmat', '.efkmodel']):
                    # 提取個別檔案路徑
                    individual_paths = self._extract_file_paths_from_string(string)
                    referenced_files.extend(individual_paths)
            
            # 方法2: 搜尋二進制模式
            binary_patterns = self._search_binary_patterns(content, efkmat_file_path)
            referenced_files.extend(binary_patterns)
            
            # 移除重複
            referenced_files = list(set(referenced_files))
            
        except Exception as e:
            self.logger.error(f"解析EFKMAT檔案內容時發生錯誤: {str(e)}")
        
        return referenced_files
    
    def _parse_efkmodel_content(self, content: bytes, efkmodel_file_path: Path) -> List[str]:
        """
        解析EFKMODEL檔案內容，尋找引用的檔案
        
        Args:
            content: EFKMODEL檔案的二進制內容
            efkmodel_file_path: EFKMODEL檔案路徑
            
        Returns:
            List[str]: 引用檔案的路徑列表
        """
        referenced_files = []
        
        try:
            # 方法1: 改進的UTF-16字串解析
            strings = self._parse_utf16_strings(content)
            
            # 從字串中提取檔案路徑
            for string_info in strings:
                string = string_info['string']
                
                # 檢查是否包含檔案路徑
                if any(ext in string.lower() for ext in ['.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.efk', '.efkmat', '.efkmodel', '.obj', '.fbx', '.3ds', '.dae']):
                    # 提取個別檔案路徑
                    individual_paths = self._extract_file_paths_from_string(string)
                    referenced_files.extend(individual_paths)
            
            # 方法2: 改進的二進制模式搜尋
            binary_patterns = self._search_binary_patterns_improved(content, efkmodel_file_path)
            referenced_files.extend(binary_patterns)
            
            # 方法3: 搜尋可能的檔案引用
            additional_refs = self._search_efkmodel_references(content)
            referenced_files.extend(additional_refs)
            
            # 移除重複
            referenced_files = list(set(referenced_files))
            
        except Exception as e:
            self.logger.error(f"解析EFKMODEL檔案內容時發生錯誤: {str(e)}")
        
        return referenced_files
    
    def _parse_utf16_strings(self, content: bytes) -> List[Dict[str, any]]:
        """
        解析檔案中的UTF-16字串
        
        Args:
            content: 檔案的二進制內容
            
        Returns:
            List[Dict[str, any]]: 字串資訊列表
        """
        strings = []
        
        # 方法1: 標準UTF-16字串解析
        pos = 4  # 跳過檔案頭（4 bytes）
        
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
        
        # 方法2: 改進的UTF-16字串搜尋
        # 搜尋可能的UTF-16字串模式
        for i in range(0, len(content) - 4, 2):  # 每2字節檢查一次
            try:
                # 嘗試讀取長度
                if i + 4 <= len(content):
                    length = struct.unpack('<I', content[i:i+4])[0]
                    
                    if 0 < length < 500 and i + 4 + length * 2 <= len(content):
                        # 讀取字串數據
                        string_data = content[i+4:i+4+length*2]
                        
                        # 嘗試不同的UTF-16編碼
                        for encoding in ['utf-16le', 'utf-16be']:
                            try:
                                string = string_data.decode(encoding)
                                if any(char.isprintable() for char in string):
                                    strings.append({
                                        'position': i,
                                        'length': length,
                                        'string': string
                                    })
                                    break
                            except:
                                continue
            except:
                continue
        
        # 方法3: 直接搜尋可讀字符串
        # 搜尋連續的可打印字符
        current_string = ""
        string_start = 0
        
        for i in range(len(content)):
            try:
                char = content[i:i+1].decode('ascii')
                if char.isprintable():
                    if not current_string:
                        string_start = i
                    current_string += char
                else:
                    if len(current_string) > 3:  # 至少3個字符
                        strings.append({
                            'position': string_start,
                            'length': len(current_string),
                            'string': current_string
                        })
                    current_string = ""
            except:
                if current_string:
                    if len(current_string) > 3:
                        strings.append({
                            'position': string_start,
                            'length': len(current_string),
                            'string': current_string
                        })
                    current_string = ""
        
        # 處理最後一個字符串
        if len(current_string) > 3:
            strings.append({
                'position': string_start,
                'length': len(current_string),
                'string': current_string
            })
        
        # 移除重複的字符串
        unique_strings = []
        seen_strings = set()
        
        for string_info in strings:
            string = string_info['string']
            if string not in seen_strings and len(string) > 2:
                unique_strings.append(string_info)
                seen_strings.add(string)
        
        return unique_strings
    
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
            '.efk', '.efkmat', '.efkmodel', '.obj', '.fbx', '.3ds', '.dae', '.blend',
            '.mtl', '.mat', '.material', '.mesh', '.model'
        ]
        
        paths = []
        
        # 方法1: 使用正則表達式搜尋檔案路徑
        for ext in file_extensions:
            # 改進的正則表達式，支援更多字符
            pattern = r'[a-zA-Z0-9_\-\.\\\/\s]+' + re.escape(ext)
            matches = re.findall(pattern, combined_string, re.IGNORECASE)
            for match in matches:
                # 清理匹配的字符串
                cleaned_path = match.strip()
                if cleaned_path and self._is_valid_file_path(cleaned_path, None):
                    paths.append(cleaned_path)
        
        # 方法2: 直接搜尋檔案副檔名
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
                    # 擴展允許的字符
                    if char in '\\/':
                        break
                    if not (char.isalnum() or char in '._- '):
                        break
                    file_start -= 1
                
                # 提取檔案路徑
                file_path = combined_string[file_start:pos + len(ext)]
                # 清理路徑
                file_path = file_path.strip()
                if file_path and self._is_valid_file_path(file_path, None):
                    paths.append(file_path)
                
                start = pos + len(ext)
        
        # 方法3: 搜尋特定的檔案名模式
        # 處理UTF-16編碼的特殊情況
        for ext in file_extensions:
            # 搜尋可能的UTF-16編碼檔案名
            # 在UTF-16中，ASCII字符後面會跟一個null字節
            utf16_pattern = ext.replace('.', '.\x00')
            pos = 0
            while True:
                pos = combined_string.find(utf16_pattern, pos)
                if pos == -1:
                    break
                
                # 向前搜尋檔案名開始
                file_start = pos
                while file_start > 0:
                    char = combined_string[file_start - 1]
                    if char in '\\/\x00':
                        break
                    if not (char.isalnum() or char in '._- ' or char == '\x00'):
                        break
                    file_start -= 1
                
                # 提取檔案路徑並清理null字節
                file_path = combined_string[file_start:pos + len(ext)]
                file_path = file_path.replace('\x00', '').strip()
                if file_path and self._is_valid_file_path(file_path, None):
                    paths.append(file_path)
                
                pos += len(ext)
        
        # 移除重複並過濾
        unique_paths = []
        for path in paths:
            if path not in unique_paths and len(path) > 3:  # 過濾太短的路徑
                unique_paths.append(path)
        
        return unique_paths
    
    def _search_binary_patterns(self, content: bytes, file_path: Path) -> List[str]:
        """
        搜尋二進制內容中的檔案路徑模式
        
        Args:
            content: 檔案內容
            file_path: 檔案路徑
            
        Returns:
            List[str]: 找到的檔案路徑列表
        """
        paths = []
        
        try:
            # 嘗試不同的編碼方式
            encodings = ['utf-8', 'utf-16le', 'utf-16be', 'ascii']
            
            for encoding in encodings:
                try:
                    text_content = content.decode(encoding, errors='ignore')
                    
                    # 搜尋檔案路徑模式
                    for match in re.finditer(r'[a-zA-Z0-9_\-\.\\\/]+\.(png|jpg|jpeg|tga|dds|bmp|efk|efkmat|efkmodel)', text_content, re.IGNORECASE):
                        file_path_str = match.group(0)
                        if self._is_valid_file_path(file_path_str, file_path):
                            paths.append(file_path_str)
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"搜尋二進制模式時發生錯誤: {str(e)}")
        
        return paths
    
    def _search_binary_patterns_improved(self, content: bytes, file_path: Path) -> List[str]:
        """
        改進的二進制模式搜尋
        
        Args:
            content: 檔案內容
            file_path: 檔案路徑
            
        Returns:
            List[str]: 找到的檔案路徑列表
        """
        paths = []
        
        try:
            # 擴展的檔案副檔名
            file_extensions = [
                '.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp',
                '.efk', '.efkmat', '.efkmodel', '.obj', '.fbx', '.3ds', '.dae', '.blend',
                '.mtl', '.mat', '.material', '.mesh', '.model'
            ]
            
            # 嘗試不同的編碼
            encodings = ['utf-8', 'utf-16le', 'utf-16be', 'ascii', 'latin-1']
            
            for encoding in encodings:
                try:
                    text_content = content.decode(encoding, errors='ignore')
                    
                    # 搜尋檔案路徑模式
                    for ext in file_extensions:
                        pattern = r'[a-zA-Z0-9_\-\.\\\/]+' + re.escape(ext)
                        matches = re.findall(pattern, text_content, re.IGNORECASE)
                        for match in matches:
                            if self._is_valid_file_path(match, file_path):
                                paths.append(match)
                except Exception:
                    continue
            
            # 二進制搜尋
            for ext in file_extensions:
                pattern = ext.encode()
                pos = 0
                while True:
                    pos = content.find(pattern, pos)
                    if pos == -1:
                        break
                    
                    # 向前搜尋檔案名開始
                    start = pos
                    while start > 0:
                        char = content[start - 1]
                        if char in b'\\/':
                            break
                        if not (32 <= char <= 126):  # 可打印字符
                            break
                        start -= 1
                    
                    # 提取檔案名
                    if start < pos:
                        try:
                            filename = content[start:pos + len(pattern)].decode('ascii', errors='ignore')
                            if self._is_valid_file_path(filename, file_path):
                                paths.append(filename)
                        except Exception:
                            pass
                    
                    pos += 1
                    
        except Exception as e:
            self.logger.error(f"改進的二進制模式搜尋時發生錯誤: {str(e)}")
        
        return paths
    
    def _search_efkmodel_references(self, content: bytes) -> List[str]:
        """
        專門搜尋EFKMODEL檔案中的引用
        
        Args:
            content: 檔案內容
            
        Returns:
            List[str]: 找到的引用檔案列表
        """
        references = []
        
        try:
            # 搜尋可能的字符串塊
            pos = 0
            while pos < len(content):
                # 尋找可能的字符串開始
                if pos + 4 <= len(content):
                    try:
                        length = struct.unpack('<I', content[pos:pos+4])[0]
                        if 0 < length < 1000 and pos + 4 + length <= len(content):
                            # 嘗試解析為字符串
                            string_data = content[pos+4:pos+4+length]
                            try:
                                # 嘗試不同的編碼
                                for encoding in ['utf-8', 'utf-16le', 'ascii']:
                                    try:
                                        string = string_data.decode(encoding)
                                        if any(char.isprintable() for char in string):
                                            # 檢查是否包含檔案路徑
                                            if any(ext in string.lower() for ext in ['.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.efk', '.efkmat', '.efkmodel', '.obj', '.fbx', '.3ds', '.dae']):
                                                # 提取檔案路徑
                                                individual_paths = self._extract_file_paths_from_string(string)
                                                references.extend(individual_paths)
                                            break
                                    except Exception:
                                        continue
                            except Exception:
                                pass
                    except Exception:
                        pass
                pos += 1
                
        except Exception as e:
            self.logger.error(f"搜尋EFKMODEL引用時發生錯誤: {str(e)}")
        
        return references
    
    def _extract_file_path(self, text_content: str, start_pos: int, file_path: Path) -> Optional[str]:
        """
        從文字內容中提取檔案路徑
        
        Args:
            text_content: 文字內容
            start_pos: 開始位置
            file_path: 檔案路徑
            
        Returns:
            Optional[str]: 提取的檔案路徑，如果沒有找到則返回None
        """
        try:
            # 搜尋檔案路徑模式
            pattern = r'[a-zA-Z0-9_\-\.\\\/]+\.(png|jpg|jpeg|tga|dds|bmp|efk|efkmat|efkmodel)'
            match = re.search(pattern, text_content[start_pos:], re.IGNORECASE)
            
            if match:
                file_path_str = match.group(0)
                if self._is_valid_file_path(file_path_str, file_path):
                    return file_path_str
            
        except Exception as e:
            self.logger.error(f"提取檔案路徑時發生錯誤: {str(e)}")
        
        return None
    
    def _is_valid_file_path(self, file_path: str, base_file_path: Path) -> bool:
        """
        檢查檔案路徑是否有效
        
        Args:
            file_path: 檔案路徑
            base_file_path: 基礎檔案路徑
            
        Returns:
            bool: 是否為有效的檔案路徑
        """
        try:
            # 檢查是否包含有效的檔案副檔名
            valid_extensions = {
                '.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', 
                '.efk', '.efkmat', '.efkmodel', '.obj', '.fbx', '.3ds', '.dae', '.blend',
                '.mtl', '.mat', '.material', '.mesh', '.model'
            }
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext not in valid_extensions:
                return False
            
            # 檢查路徑是否包含無效字元
            invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
            if any(char in file_path for char in invalid_chars):
                return False
            
            # 檢查路徑長度
            if len(file_path) > 260:  # Windows路徑長度限制
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_statistics(self) -> Dict[str, int]:
        """
        取得掃描統計資訊
        
        Returns:
            Dict[str, int]: 統計資訊字典
        """
        total_referenced_files = sum(len(files) for files in self.results.values())
        
        return {
            'total_efk_files': len(self.efk_files),
            'total_efkmat_files': len(self.efkmat_files),
            'total_efkmodel_files': len(self.efkmodel_files),
            'analyzed_efk_files': self.successful_scans,
            'total_referenced_files': total_referenced_files,
            'failed_scans': self.failed_scans
        } 