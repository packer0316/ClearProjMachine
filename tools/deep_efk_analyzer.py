#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度EFK檔案分析工具
專門分析EFFEKSEER檔案格式的內部結構
"""

import struct
import binascii
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class DeepEFKAnalyzer:
    """深度EFK檔案分析器"""
    
    def __init__(self, efk_file_path: str):
        self.efk_file_path = Path(efk_file_path)
        self.file_content = None
        self.analysis_result = {
            'file_info': {},
            'header_analysis': {},
            'section_analysis': {},
            'string_table': {},
            'referenced_files': []
        }
    
    def analyze(self) -> Dict[str, Any]:
        """深度分析EFK檔案"""
        print(f"開始深度分析EFK檔案: {self.efk_file_path}")
        
        # 讀取檔案內容
        self._read_file_content()
        
        # 分析檔案頭
        self._analyze_header()
        
        # 分析檔案結構
        self._analyze_structure()
        
        # 提取字串表
        self._extract_string_table()
        
        # 分析引用
        self._analyze_references()
        
        return self.analysis_result
    
    def _read_file_content(self):
        """讀取檔案內容"""
        with open(self.efk_file_path, 'rb') as f:
            self.file_content = f.read()
        print(f"檔案大小: {len(self.file_content)} bytes")
    
    def _analyze_header(self):
        """分析檔案頭"""
        print("分析檔案頭...")
        
        if len(self.file_content) < 4:
            return
        
        # 檔案頭
        header = self.file_content[:4]
        header_hex = binascii.hexlify(header).decode('ascii')
        header_ascii = header.decode('ascii', errors='ignore')
        
        self.analysis_result['header_analysis'] = {
            'header_hex': header_hex,
            'header_ascii': header_ascii,
            'header_size': 4
        }
        
        print(f"檔案頭: {header_hex} ({header_ascii})")
        
        # 檢查是否為EFK檔案
        if header_ascii == 'EFKS':
            print("✓ 確認為EFFEKSEER檔案格式")
            self.analysis_result['header_analysis']['is_efk'] = True
        else:
            print("✗ 不是標準的EFFEKSEER檔案格式")
            self.analysis_result['header_analysis']['is_efk'] = False
    
    def _analyze_structure(self):
        """分析檔案結構"""
        print("分析檔案結構...")
        
        # 分析檔案的不同區段
        sections = []
        
        # 尋找可能的區段邊界
        pos = 4  # 跳過檔案頭
        
        while pos < len(self.file_content):
            section_info = self._analyze_section_at(pos)
            if section_info:
                sections.append(section_info)
                pos = section_info['end_pos']
            else:
                pos += 1
        
        self.analysis_result['section_analysis']['sections'] = sections
        print(f"找到 {len(sections)} 個可能的區段")
    
    def _analyze_section_at(self, start_pos: int) -> Optional[Dict[str, Any]]:
        """分析指定位置的區段"""
        if start_pos >= len(self.file_content):
            return None
        
        # 嘗試讀取區段長度
        if start_pos + 4 <= len(self.file_content):
            try:
                section_length = struct.unpack('<I', self.file_content[start_pos:start_pos+4])[0]
                
                # 檢查長度是否合理
                if 0 < section_length < 1000000 and start_pos + 4 + section_length <= len(self.file_content):
                    section_data = self.file_content[start_pos+4:start_pos+4+section_length]
                    
                    return {
                        'start_pos': start_pos,
                        'end_pos': start_pos + 4 + section_length,
                        'length': section_length,
                        'data': section_data,
                        'data_hex': binascii.hexlify(section_data[:50]).decode('ascii'),
                        'data_preview': section_data[:50].decode('utf-8', errors='ignore')
                    }
            except:
                pass
        
        # 尋找下一個可能的區段邊界
        for i in range(start_pos + 1, min(start_pos + 100, len(self.file_content))):
            if self.file_content[i] == 0:
                # 找到null位元組，可能是區段邊界
                section_data = self.file_content[start_pos:i]
                if len(section_data) > 0:
                    return {
                        'start_pos': start_pos,
                        'end_pos': i,
                        'length': len(section_data),
                        'data': section_data,
                        'data_hex': binascii.hexlify(section_data[:50]).decode('ascii'),
                        'data_preview': section_data.decode('utf-8', errors='ignore')
                    }
        
        return None
    
    def _extract_string_table(self):
        """提取字串表"""
        print("提取字串表...")
        
        strings = []
        
        # 尋找可讀的字串
        current_string = ""
        string_start = -1
        
        for i, byte in enumerate(self.file_content):
            if 32 <= byte <= 126:  # 可列印的ASCII字元
                if string_start == -1:
                    string_start = i
                current_string += chr(byte)
            else:
                if len(current_string) >= 3:  # 至少3個字元的字串
                    strings.append({
                        'position': string_start,
                        'content': current_string,
                        'length': len(current_string)
                    })
                current_string = ""
                string_start = -1
        
        # 處理最後一個字串
        if len(current_string) >= 3:
            strings.append({
                'position': string_start,
                'content': current_string,
                'length': len(current_string)
            })
        
        self.analysis_result['string_table']['strings'] = strings
        print(f"找到 {len(strings)} 個字串")
        
        # 顯示較長的字串
        long_strings = [s for s in strings if s['length'] > 10]
        print(f"較長的字串 ({len(long_strings)} 個):")
        for i, string_info in enumerate(long_strings[:10], 1):
            print(f"  {i}. [{string_info['position']}] {string_info['content']}")
    
    def _analyze_references(self):
        """分析檔案引用"""
        print("分析檔案引用...")
        
        referenced_files = []
        strings = self.analysis_result['string_table']['strings']
        
        # 檔案副檔名模式
        file_extensions = [
            '.efk', '.efkmat', '.efkmodel',
            '.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp',
            '.tiff', '.tif', '.webp', '.ktx', '.pvr'
        ]
        
        for string_info in strings:
            content = string_info['content'].lower()
            
            # 檢查是否包含檔案路徑
            for ext in file_extensions:
                if ext in content:
                    # 嘗試提取完整的檔案路徑
                    file_path = self._extract_file_path(content, ext)
                    if file_path:
                        referenced_files.append({
                            'path': file_path,
                            'source_string': string_info['content'],
                            'position': string_info['position'],
                            'extension': ext
                        })
                        break
        
        # 去重
        unique_files = {}
        for file_info in referenced_files:
            path = file_info['path']
            if path not in unique_files:
                unique_files[path] = file_info
        
        self.analysis_result['referenced_files'] = list(unique_files.values())
        print(f"找到 {len(self.analysis_result['referenced_files'])} 個引用的檔案")
    
    def _extract_file_path(self, content: str, extension: str) -> Optional[str]:
        """從內容中提取檔案路徑"""
        # 尋找包含副檔名的部分
        ext_pos = content.find(extension)
        if ext_pos == -1:
            return None
        
        # 向前搜尋路徑開始
        start_pos = ext_pos
        while start_pos > 0:
            char = content[start_pos - 1]
            if char in '\\/':
                break
            if not char.isalnum() and char not in '._-':
                break
            start_pos -= 1
        
        # 向後搜尋路徑結束
        end_pos = ext_pos + len(extension)
        while end_pos < len(content):
            char = content[end_pos]
            if char in '\\/':
                break
            if not char.isalnum() and char not in '._-':
                break
            end_pos += 1
        
        file_path = content[start_pos:end_pos]
        
        # 驗證路徑
        if len(file_path) >= len(extension) and file_path.endswith(extension):
            return file_path
        
        return None
    
    def print_summary(self):
        """列印分析摘要"""
        print("\n" + "="*60)
        print("深度EFK檔案分析摘要")
        print("="*60)
        
        # 檔案資訊
        file_info = self.analysis_result['file_info']
        print(f"檔案: {self.efk_file_path}")
        print(f"大小: {len(self.file_content)} bytes")
        
        # 檔案頭分析
        header_info = self.analysis_result['header_analysis']
        print(f"檔案頭: {header_info.get('header_ascii', 'Unknown')}")
        print(f"是否為EFK檔案: {header_info.get('is_efk', False)}")
        
        # 區段分析
        sections = self.analysis_result['section_analysis'].get('sections', [])
        print(f"\n檔案區段 ({len(sections)} 個):")
        for i, section in enumerate(sections[:5], 1):
            print(f"  區段 {i}: 位置 {section['start_pos']}-{section['end_pos']}, "
                  f"長度 {section['length']} bytes")
            if section['data_preview']:
                print(f"    預覽: {section['data_preview'][:50]}...")
        
        # 字串表
        strings = self.analysis_result['string_table'].get('strings', [])
        print(f"\n字串表 ({len(strings)} 個字串):")
        for i, string_info in enumerate(strings[:10], 1):
            if string_info['length'] > 5:
                print(f"  {i}. [{string_info['position']}] {string_info['content']}")
        
        # 引用的檔案
        referenced_files = self.analysis_result['referenced_files']
        print(f"\n引用的檔案 ({len(referenced_files)} 個):")
        for i, file_info in enumerate(referenced_files, 1):
            print(f"  {i}. {file_info['path']}")
            print(f"     來源: {file_info['source_string']}")
            print(f"     位置: {file_info['position']}")
        
        print("="*60)


def main():
    """主函數"""
    efk_file = r"C:\Users\User\Desktop\清圖資料\testEfk\Attack.efk"
    
    try:
        analyzer = DeepEFKAnalyzer(efk_file)
        result = analyzer.analyze()
        analyzer.print_summary()
        
        # 儲存詳細結果
        output_file = "deep_efk_analysis_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n詳細分析結果已儲存到: {output_file}")
        
    except Exception as e:
        print(f"分析失敗: {e}")


if __name__ == "__main__":
    main() 