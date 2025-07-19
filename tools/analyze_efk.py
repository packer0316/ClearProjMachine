#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EFK檔案分析工具
專門用於分析EFFEKSEER檔案格式並提取引用的檔案
"""

import os
import struct
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import binascii


class EFKAnalyzer:
    """EFK檔案分析器"""
    
    def __init__(self, efk_file_path: str):
        self.efk_file_path = Path(efk_file_path)
        self.file_size = 0
        self.file_content = None
        self.analysis_result = {
            'file_info': {},
            'referenced_files': [],
            'binary_analysis': {},
            'text_analysis': {},
            'structure_info': {}
        }
    
    def analyze(self) -> Dict[str, Any]:
        """分析EFK檔案"""
        print(f"開始分析EFK檔案: {self.efk_file_path}")
        
        # 檢查檔案是否存在
        if not self.efk_file_path.exists():
            raise FileNotFoundError(f"檔案不存在: {self.efk_file_path}")
        
        # 獲取檔案資訊
        self._get_file_info()
        
        # 讀取檔案內容
        self._read_file_content()
        
        # 分析檔案結構
        self._analyze_file_structure()
        
        # 分析文字內容
        self._analyze_text_content()
        
        # 分析二進制內容
        self._analyze_binary_content()
        
        # 提取引用的檔案
        self._extract_referenced_files()
        
        return self.analysis_result
    
    def _get_file_info(self):
        """獲取檔案基本資訊"""
        stat = self.efk_file_path.stat()
        self.file_size = stat.st_size
        self.analysis_result['file_info'] = {
            'file_path': str(self.efk_file_path),
            'file_size': self.file_size,
            'file_size_human': f"{self.file_size / 1024:.2f} KB",
            'last_modified': stat.st_mtime
        }
        print(f"檔案大小: {self.file_size} bytes ({self.file_size / 1024:.2f} KB)")
    
    def _read_file_content(self):
        """讀取檔案內容"""
        try:
            with open(self.efk_file_path, 'rb') as f:
                self.file_content = f.read()
            print(f"成功讀取檔案內容，長度: {len(self.file_content)} bytes")
        except Exception as e:
            raise Exception(f"讀取檔案失敗: {e}")
    
    def _analyze_file_structure(self):
        """分析檔案結構"""
        print("分析檔案結構...")
        
        # 檢查檔案頭
        if len(self.file_content) >= 4:
            header = self.file_content[:4]
            header_hex = binascii.hexlify(header).decode('ascii')
            self.analysis_result['structure_info']['header'] = header_hex
            print(f"檔案頭: {header_hex}")
        
        # 檢查檔案尾
        if len(self.file_content) >= 4:
            footer = self.file_content[-4:]
            footer_hex = binascii.hexlify(footer).decode('ascii')
            self.analysis_result['structure_info']['footer'] = footer_hex
            print(f"檔案尾: {footer_hex}")
        
        # 分析檔案結構模式
        self._find_structure_patterns()
    
    def _find_structure_patterns(self):
        """尋找檔案結構模式"""
        patterns = {
            'null_bytes': b'\x00',
            'text_strings': b'[a-zA-Z0-9_./\\-]',
            'file_paths': b'[a-zA-Z]:[\\/]',
            'file_extensions': b'\.(efk|efkmat|efkmodel|png|jpg|jpeg|tga|dds|bmp|tiff?|webp|ktx|pvr)',
        }
        
        for pattern_name, pattern in patterns.items():
            if isinstance(pattern, bytes):
                count = self.file_content.count(pattern)
                self.analysis_result['structure_info'][f'{pattern_name}_count'] = count
                print(f"{pattern_name}: {count} 次")
    
    def _analyze_text_content(self):
        """分析文字內容"""
        print("分析文字內容...")
        
        # 嘗試不同的編碼方式
        encodings = ['utf-8', 'utf-16', 'utf-16le', 'utf-16be', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                text_content = self.file_content.decode(encoding, errors='ignore')
                self.analysis_result['text_analysis'][encoding] = {
                    'content': text_content,
                    'length': len(text_content),
                    'readable_chars': len([c for c in text_content if c.isprintable()])
                }
                print(f"使用 {encoding} 編碼成功，可讀字元: {len([c for c in text_content if c.isprintable()])}")
                break
            except Exception as e:
                print(f"使用 {encoding} 編碼失敗: {e}")
        
        # 提取可讀的文字內容
        if 'text_analysis' in self.analysis_result:
            for encoding, data in self.analysis_result['text_analysis'].items():
                text_content = data['content']
                
                # 尋找檔案路徑
                self._extract_paths_from_text(text_content, encoding)
                
                # 尋找JSON/XML結構
                self._extract_structured_data(text_content, encoding)
    
    def _extract_paths_from_text(self, text_content: str, encoding: str):
        """從文字內容中提取檔案路徑"""
        # 檔案路徑模式
        path_patterns = [
            r'["\']([^"\']*\.(?:efk|efkmat|efkmodel|png|jpg|jpeg|tga|dds|bmp|tiff?|webp|ktx|pvr))["\']',
            r'([a-zA-Z]:[\\/][^"\']*\.(?:efk|efkmat|efkmodel|png|jpg|jpeg|tga|dds|bmp|tiff?|webp|ktx|pvr))',
            r'([^"\']*[/\\][^"\']*\.(?:efk|efkmat|efkmodel|png|jpg|jpeg|tga|dds|bmp|tiff?|webp|ktx|pvr))',
        ]
        
        found_paths = []
        for pattern in path_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                path = match.group(1) if match.groups() else match.group(0)
                found_paths.append({
                    'path': path,
                    'pattern': pattern,
                    'position': match.start()
                })
        
        if found_paths:
            self.analysis_result['text_analysis'][encoding]['found_paths'] = found_paths
            print(f"在 {encoding} 編碼中找到 {len(found_paths)} 個檔案路徑")
    
    def _extract_structured_data(self, text_content: str, encoding: str):
        """提取結構化資料"""
        # 尋找JSON結構
        json_patterns = [
            r'\{[^{}]*\}',
            r'\[[^\[\]]*\]'
        ]
        
        json_structures = []
        for pattern in json_patterns:
            matches = re.finditer(pattern, text_content)
            for match in matches:
                try:
                    json_data = json.loads(match.group(0))
                    json_structures.append({
                        'data': json_data,
                        'position': match.start(),
                        'length': len(match.group(0))
                    })
                except:
                    pass
        
        if json_structures:
            self.analysis_result['text_analysis'][encoding]['json_structures'] = json_structures
            print(f"在 {encoding} 編碼中找到 {len(json_structures)} 個JSON結構")
    
    def _analyze_binary_content(self):
        """分析二進制內容"""
        print("分析二進制內容...")
        
        # 分析位元組分佈
        byte_counts = {}
        for byte in self.file_content:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1
        
        # 找出最常見的位元組
        most_common_bytes = sorted(byte_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        self.analysis_result['binary_analysis']['most_common_bytes'] = most_common_bytes
        
        # 尋找特定的二進制模式
        self._find_binary_patterns()
        
        # 分析檔案結構
        self._analyze_binary_structure()
    
    def _find_binary_patterns(self):
        """尋找二進制模式"""
        patterns = {
            'file_signatures': {
                b'PK': 'ZIP檔案',
                b'\x89PNG': 'PNG圖片',
                b'\xFF\xD8\xFF': 'JPEG圖片',
                b'DDS ': 'DDS圖片',
                b'BM': 'BMP圖片',
            },
            'text_strings': [
                b'.efk',
                b'.efkmat',
                b'.efkmodel',
                b'.png',
                b'.jpg',
                b'.jpeg',
                b'.tga',
                b'.dds',
                b'.bmp'
            ]
        }
        
        found_patterns = {}
        
        # 檢查檔案簽名
        for signature, description in patterns['file_signatures'].items():
            if self.file_content.startswith(signature):
                found_patterns[f'signature_{description}'] = True
        
        # 尋找文字字串
        for text_pattern in patterns['text_strings']:
            positions = []
            start = 0
            while True:
                pos = self.file_content.find(text_pattern, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            if positions:
                found_patterns[f'text_{text_pattern.decode("ascii", errors="ignore")}'] = positions
        
        self.analysis_result['binary_analysis']['found_patterns'] = found_patterns
        print(f"找到 {len(found_patterns)} 個二進制模式")
    
    def _analyze_binary_structure(self):
        """分析二進制結構"""
        # 分析檔案的不同區段
        sections = []
        
        # 尋找可能的區段邊界
        null_positions = []
        for i, byte in enumerate(self.file_content):
            if byte == 0:
                null_positions.append(i)
        
        # 分析連續的null位元組
        if null_positions:
            null_runs = []
            start = null_positions[0]
            count = 1
            
            for i in range(1, len(null_positions)):
                if null_positions[i] == null_positions[i-1] + 1:
                    count += 1
                else:
                    if count > 1:
                        null_runs.append((start, count))
                    start = null_positions[i]
                    count = 1
            
            if count > 1:
                null_runs.append((start, count))
            
            self.analysis_result['binary_analysis']['null_runs'] = null_runs
            print(f"找到 {len(null_runs)} 個null位元組區段")
    
    def _extract_referenced_files(self):
        """提取引用的檔案"""
        print("提取引用的檔案...")
        
        referenced_files = []
        
        # 從文字分析中提取
        for encoding, data in self.analysis_result.get('text_analysis', {}).items():
            if 'found_paths' in data:
                for path_info in data['found_paths']:
                    referenced_files.append({
                        'path': path_info['path'],
                        'source': f'text_analysis_{encoding}',
                        'position': path_info['position']
                    })
        
        # 從二進制分析中提取
        binary_data = self.analysis_result.get('binary_analysis', {})
        if 'found_patterns' in binary_data:
            for pattern_name, positions in binary_data['found_patterns'].items():
                if pattern_name.startswith('text_'):
                    for pos in positions:
                        # 嘗試提取完整的檔案路徑
                        extracted_path = self._extract_path_at_position(pos)
                        if extracted_path:
                            referenced_files.append({
                                'path': extracted_path,
                                'source': f'binary_analysis_{pattern_name}',
                                'position': pos
                            })
        
        # 去重並排序
        unique_files = {}
        for file_info in referenced_files:
            path = file_info['path']
            if path not in unique_files:
                unique_files[path] = file_info
            else:
                # 合併來源資訊
                unique_files[path]['source'] += f", {file_info['source']}"
        
        self.analysis_result['referenced_files'] = list(unique_files.values())
        print(f"找到 {len(self.analysis_result['referenced_files'])} 個引用的檔案")
    
    def _extract_path_at_position(self, position: int) -> Optional[str]:
        """在指定位置提取檔案路徑"""
        if position >= len(self.file_content):
            return None
        
        # 向前和向後搜尋路徑邊界
        start = max(0, position - 200)
        end = min(len(self.file_content), position + 200)
        
        # 嘗試解碼這個範圍
        try:
            text_segment = self.file_content[start:end].decode('utf-8', errors='ignore')
            
            # 尋找檔案路徑模式
            path_pattern = r'[^"\']*\.(?:efk|efkmat|efkmodel|png|jpg|jpeg|tga|dds|bmp|tiff?|webp|ktx|pvr)'
            matches = re.finditer(path_pattern, text_segment, re.IGNORECASE)
            
            for match in matches:
                return match.group(0)
        except:
            pass
        
        return None
    
    def print_summary(self):
        """列印分析摘要"""
        print("\n" + "="*50)
        print("EFK檔案分析摘要")
        print("="*50)
        
        # 檔案資訊
        file_info = self.analysis_result['file_info']
        print(f"檔案: {file_info['file_path']}")
        print(f"大小: {file_info['file_size_human']}")
        
        # 引用的檔案
        referenced_files = self.analysis_result['referenced_files']
        print(f"\n引用的檔案 ({len(referenced_files)} 個):")
        for i, file_info in enumerate(referenced_files, 1):
            print(f"  {i}. {file_info['path']} (來源: {file_info['source']})")
        
        # 結構資訊
        structure_info = self.analysis_result.get('structure_info', {})
        if structure_info:
            print(f"\n檔案結構:")
            for key, value in structure_info.items():
                print(f"  {key}: {value}")
        
        print("="*50)


def main():
    """主函數"""
    efk_file = r"C:\Users\User\Desktop\清圖資料\testEfk\Attack.efk"
    
    try:
        analyzer = EFKAnalyzer(efk_file)
        result = analyzer.analyze()
        analyzer.print_summary()
        
        # 儲存詳細結果
        output_file = "efk_analysis_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n詳細分析結果已儲存到: {output_file}")
        
    except Exception as e:
        print(f"分析失敗: {e}")


if __name__ == "__main__":
    main() 