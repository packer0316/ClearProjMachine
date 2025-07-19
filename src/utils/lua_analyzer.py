#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lua檔案分析器 - 負責搜尋Lua程式碼中的圖片檔案引用
"""

import os
import re
from pathlib import Path
from typing import Set, List, Dict, Optional


class LuaAnalyzer:
    """Lua檔案分析器 - 搜尋Lua程式碼中的圖片檔案引用"""
    
    def __init__(self, code_project_path: str):
        """
        初始化Lua分析器
        
        Args:
            code_project_path: 程式碼專案根目錄路徑
        """
        self.code_project_path = Path(code_project_path)
        self.image_references = set()
        self.lua_files = []
        
        # 常見的圖片檔案擴展名
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tga', '.gif'}
        
        # 常見的Lua字串引用模式
        self.lua_string_patterns = [
            r'["\']([^"\']*\.(?:png|jpg|jpeg|bmp|tga|gif))["\']',  # "image.png" 或 'image.png'
            r'["\']([^"\']*)["\']',  # 一般字串，後續會檢查是否包含圖片
        ]
    
    def scan_lua_files(self) -> Set[str]:
        """
        掃描程式碼專案中的所有Lua檔案並提取圖片引用
        
        Returns:
            Set[str]: 在Lua檔案中發現的圖片檔案名稱集合
        """
        print(f"開始掃描Lua檔案: {self.code_project_path}")
        
        # 尋找所有Lua檔案
        self._find_all_lua_files()
        
        if not self.lua_files:
            print("未找到任何Lua檔案")
            return self.image_references
        
        print(f"找到 {len(self.lua_files)} 個Lua檔案")
        
        # 分析每個Lua檔案
        for lua_file in self.lua_files:
            try:
                self._analyze_lua_file(lua_file)
            except Exception as e:
                print(f"分析Lua檔案 {lua_file} 時發生錯誤: {str(e)}")
                continue
        
        print(f"Lua檔案分析完成，找到 {len(self.image_references)} 個圖片引用")
        return self.image_references
    
    def _find_all_lua_files(self):
        """尋找專案中的所有Lua檔案"""
        self.lua_files = []
        
        try:
            for root, dirs, files in os.walk(self.code_project_path):
                for file in files:
                    if file.lower().endswith('.lua'):
                        file_path = Path(root) / file
                        self.lua_files.append(file_path)
        except Exception as e:
            print(f"掃描Lua檔案時發生錯誤: {str(e)}")
    
    def _analyze_lua_file(self, lua_file_path: Path):
        """
        分析單個Lua檔案中的圖片引用
        
        Args:
            lua_file_path: Lua檔案路徑
        """
        try:
            # 讀取檔案內容
            with open(lua_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 使用正則表達式搜尋字串引用
            for pattern in self.lua_string_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    string_value = match.group(1)
                    
                    # 檢查是否是圖片檔案引用
                    if self._is_image_reference(string_value):
                        # 提取檔案名稱部分（去掉路徑）
                        image_name = self._extract_image_filename(string_value)
                        if image_name:
                            self.image_references.add(image_name)
                            print(f"  在 {lua_file_path.name} 中找到圖片引用: {string_value} -> {image_name}")
        
        except UnicodeDecodeError:
            # 嘗試其他編碼
            try:
                with open(lua_file_path, 'r', encoding='gb2312', errors='ignore') as f:
                    content = f.read()
                self._extract_from_content(content, lua_file_path.name)
            except Exception as e:
                print(f"無法讀取檔案 {lua_file_path}: {str(e)}")
        except Exception as e:
            print(f"分析檔案 {lua_file_path} 時發生錯誤: {str(e)}")
    
    def _extract_from_content(self, content: str, filename: str):
        """從內容中提取圖片引用"""
        for pattern in self.lua_string_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                string_value = match.group(1)
                
                if self._is_image_reference(string_value):
                    image_name = self._extract_image_filename(string_value)
                    if image_name:
                        self.image_references.add(image_name)
                        print(f"  在 {filename} 中找到圖片引用: {string_value} -> {image_name}")
    
    def _is_image_reference(self, string_value: str) -> bool:
        """
        檢查字串是否是圖片檔案引用
        
        Args:
            string_value: 要檢查的字串
            
        Returns:
            bool: 是否是圖片檔案引用
        """
        if not string_value or len(string_value) < 3:
            return False
        
        # 檢查是否有圖片副檔名
        for ext in self.image_extensions:
            if string_value.lower().endswith(ext):
                return True
        
        return False
    
    def _extract_image_filename(self, image_path: str) -> Optional[str]:
        """
        從圖片路徑中提取檔案名稱
        
        Args:
            image_path: 圖片路徑字串
            
        Returns:
            Optional[str]: 提取的檔案名稱，失敗則返回None
        """
        if not image_path:
            return None
        
        try:
            # 移除可能的引號
            clean_path = image_path.strip('\'"')
            
            # 提取檔案名（處理不同的路徑分隔符）
            filename = clean_path.replace('\\', '/').split('/')[-1]
            
            # 確保是有效的檔案名
            if filename and '.' in filename:
                return filename
            
        except Exception as e:
            print(f"提取檔案名時發生錯誤: {str(e)}")
        
        return None
    
    def check_if_file_referenced_in_lua(self, image_filename: str, unused_file_path: str) -> bool:
        """
        檢查指定的圖片檔案是否在Lua檔案中被引用
        使用相對路徑匹配邏輯
        
        Args:
            image_filename: 圖片檔案名稱
            unused_file_path: 未引用檔案的完整路徑
            
        Returns:
            bool: 是否在Lua中被引用
        """
        # 提取檔案名進行精確匹配
        filename_only = os.path.basename(image_filename)
        unused_filename = os.path.basename(unused_file_path)
        
        # 檢查檔案名是否在Lua引用列表中
        if filename_only.lower() in [ref.lower() for ref in self.image_references]:
            print(f"  🔍 Lua檔案引用檢查: {unused_filename} 在Lua檔案中被引用")
            return True
        
        # 檢查相對路徑匹配
        # 如果Lua中的引用包含路徑資訊，需要檢查路徑是否匹配
        for lua_ref in self.image_references:
            if self._path_matches(unused_file_path, lua_ref):
                print(f"  🔍 Lua檔案路徑匹配: {unused_filename} 通過路徑匹配被Lua檔案引用 ({lua_ref})")
                return True
        
        return False
    
    def _path_matches(self, full_path: str, lua_reference: str) -> bool:
        """
        檢查完整路徑是否與Lua引用的相對路徑匹配
        
        Args:
            full_path: 檔案的完整路徑
            lua_reference: Lua中的引用字串
            
        Returns:
            bool: 路徑是否匹配
        """
        try:
            # 正規化路徑分隔符
            full_path_normalized = full_path.replace('\\', '/')
            lua_ref_normalized = lua_reference.replace('\\', '/')
            
            # 如果Lua引用包含路徑分隔符，檢查路徑匹配
            if '/' in lua_ref_normalized:
                # 檢查完整路徑是否以Lua引用結尾
                if full_path_normalized.lower().endswith(lua_ref_normalized.lower()):
                    return True
                
                # 檢查前一層路徑是否匹配
                lua_parts = lua_ref_normalized.split('/')
                if len(lua_parts) >= 2:
                    # 取Lua引用的最後兩部分（目錄/檔案名）
                    lua_dir_file = '/'.join(lua_parts[-2:])
                    if lua_dir_file.lower() in full_path_normalized.lower():
                        return True
            else:
                # 只是檔案名，檢查檔案名是否匹配
                full_filename = os.path.basename(full_path_normalized)
                if full_filename.lower() == lua_ref_normalized.lower():
                    return True
        
        except Exception as e:
            print(f"路徑匹配檢查時發生錯誤: {str(e)}")
        
        return False
    
    def get_statistics(self) -> Dict[str, int]:
        """
        獲取分析統計信息
        
        Returns:
            Dict[str, int]: 統計信息
        """
        return {
            'total_lua_files': len(self.lua_files),
            'total_image_references': len(self.image_references)
        } 