#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正確的EFK檔案解析工具
"""

import struct
import binascii
from pathlib import Path


def parse_efk_strings(file_path: str):
    """正確解析EFK檔案中的UTF-16字串"""
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


def analyze_efk_structure(file_path: str):
    """分析EFK檔案結構"""
    with open(file_path, 'rb') as f:
        content = f.read()
    
    print(f"分析EFK檔案結構: {file_path}")
    print("="*60)
    
    # 跳過檔案頭
    pos = 4
    
    sections = []
    
    while pos < len(content):
        if pos + 4 <= len(content):
            try:
                length = struct.unpack('<I', content[pos:pos+4])[0]
                
                if 0 < length < 1000 and pos + 4 + length * 2 <= len(content):
                    string_data = content[pos+4:pos+4+length*2]
                    
                    try:
                        string = string_data.decode('utf-16le')
                        sections.append({
                            'position': pos,
                            'length': length,
                            'string': string,
                            'is_file_path': any(ext in string.lower() for ext in ['.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.efk', '.efkmat', '.efkmodel'])
                        })
                    except:
                        pass
                    
                    pos += 4 + length * 2
                    continue
            except:
                pass
        
        pos += 1
    
    # 分類結果
    file_paths = [s for s in sections if s['is_file_path']]
    other_strings = [s for s in sections if not s['is_file_path']]
    
    print(f"找到 {len(sections)} 個字串區段")
    print(f"檔案路徑: {len(file_paths)} 個")
    print(f"其他字串: {len(other_strings)} 個")
    
    print(f"\n檔案路徑:")
    for i, section in enumerate(file_paths, 1):
        print(f"  {i}. {section['string']}")
    
    print(f"\n其他字串 (前10個):")
    for i, section in enumerate(other_strings[:10], 1):
        print(f"  {i}. {section['string']}")
    
    return {
        'sections': sections,
        'file_paths': file_paths,
        'other_strings': other_strings
    }


def check_referenced_files(file_path: str):
    """檢查引用的檔案是否存在"""
    result = analyze_efk_structure(file_path)
    
    efk_dir = Path(file_path).parent
    print(f"\n檢查同資料夾檔案:")
    print(f"目錄: {efk_dir}")
    
    existing_files = []
    missing_files = []
    
    for file_path_info in result['file_paths']:
        file_name = file_path_info['string']
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
        result = check_referenced_files(efk_file)
        
        # 儲存詳細結果
        import json
        output_file = "efk_analysis_final.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n詳細分析結果已儲存到: {output_file}")
        
    except Exception as e:
        print(f"分析失敗: {e}")


if __name__ == "__main__":
    main() 