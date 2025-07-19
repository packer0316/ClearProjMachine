#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精確的EFK檔案解析工具
正確分離連在一起的檔案路徑
"""

import struct
import binascii
import re
from pathlib import Path


def extract_file_paths_from_string(combined_string: str):
    """從連在一起的字串中提取個別檔案路徑"""
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


def parse_efk_file_precisely(file_path: str):
    """精確解析EFK檔案"""
    with open(file_path, 'rb') as f:
        content = f.read()
    
    print(f"檔案大小: {len(content)} bytes")
    print(f"檔案頭: {binascii.hexlify(content[:4]).decode('ascii')}")
    
    # 跳過檔案頭
    pos = 4
    
    strings = []
    
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
                            'string': string,
                            'hex': binascii.hexlify(string_data[:50]).decode('ascii')
                        })
                        print(f"[{pos}] 長度:{length} 字串: {string}")
                        
                        # 移動到下一個位置
                        pos += 4 + length * 2
                        continue
                    except:
                        pass
            except:
                pass
        
        pos += 1
    
    return strings


def analyze_efk_file_precisely(file_path: str):
    """精確分析EFK檔案"""
    print(f"精確分析EFK檔案: {file_path}")
    print("="*60)
    
    strings = parse_efk_file_precisely(file_path)
    
    print(f"\n找到 {len(strings)} 個UTF-16字串:")
    
    # 分類字串
    file_paths = []
    other_strings = []
    
    for string_info in strings:
        string = string_info['string']
        
        # 檢查是否包含檔案路徑
        if any(ext in string.lower() for ext in ['.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.efk', '.efkmat', '.efkmodel']):
            # 提取個別檔案路徑
            individual_paths = extract_file_paths_from_string(string)
            for path in individual_paths:
                file_paths.append({
                    'position': string_info['position'],
                    'original_string': string,
                    'extracted_path': path
                })
        else:
            other_strings.append(string_info)
    
    print(f"\n提取的檔案路徑 ({len(file_paths)} 個):")
    for i, path_info in enumerate(file_paths, 1):
        print(f"  {i}. {path_info['extracted_path']}")
        print(f"     來源字串: {path_info['original_string']}")
    
    print(f"\n其他字串 ({len(other_strings)} 個):")
    for i, string_info in enumerate(other_strings[:10], 1):
        print(f"  {i}. {string_info['string']}")
    
    return {
        'file_paths': file_paths,
        'other_strings': other_strings,
        'all_strings': strings
    }


def check_referenced_files_precisely(file_path: str):
    """精確檢查引用的檔案是否存在"""
    result = analyze_efk_file_precisely(file_path)
    
    efk_dir = Path(file_path).parent
    print(f"\n檢查同資料夾檔案:")
    print(f"目錄: {efk_dir}")
    
    # 列出目錄中的所有檔案
    all_files = list(efk_dir.glob('*'))
    print(f"目錄中的檔案:")
    for file in all_files:
        if file.is_file():
            print(f"  - {file.name} ({file.stat().st_size} bytes)")
    
    existing_files = []
    missing_files = []
    
    for file_path_info in result['file_paths']:
        file_name = file_path_info['extracted_path']
        full_path = efk_dir / file_name
        
        if full_path.exists():
            existing_files.append({
                'name': file_name,
                'full_path': str(full_path),
                'size': full_path.stat().st_size
            })
            print(f"  ✓ {file_name} (存在, {full_path.stat().st_size} bytes)")
        else:
            missing_files.append(file_name)
            print(f"  ✗ {file_name} (不存在)")
    
    print(f"\n總結:")
    print(f"EFK檔案引用的檔案: {len(result['file_paths'])} 個")
    print(f"實際存在的檔案: {len(existing_files)} 個")
    print(f"缺失的檔案: {len(missing_files)} 個")
    
    if existing_files:
        print(f"\n實際引用的檔案:")
        for i, file_info in enumerate(existing_files, 1):
            print(f"  {i}. {file_info['name']} ({file_info['size']} bytes)")
    
    if missing_files:
        print(f"\n缺失的檔案:")
        for i, file_name in enumerate(missing_files, 1):
            print(f"  {i}. {file_name}")
    
    return {
        'existing_files': existing_files,
        'missing_files': missing_files,
        'analysis_result': result
    }


def main():
    """主函數"""
    efk_file = r"C:\Users\User\Desktop\清圖資料\testEfk\Attack.efk"
    
    try:
        result = check_referenced_files_precisely(efk_file)
        
        # 儲存詳細結果
        import json
        output_file = "efk_analysis_precise_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n詳細分析結果已儲存到: {output_file}")
        
    except Exception as e:
        print(f"分析失敗: {e}")


if __name__ == "__main__":
    main() 