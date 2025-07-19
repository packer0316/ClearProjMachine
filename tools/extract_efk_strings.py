#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取EFK檔案中的UTF-16字串
"""

import struct
import binascii
from pathlib import Path


def extract_utf16_strings(file_path: str):
    """提取EFK檔案中的UTF-16字串"""
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
                    except:
                        try:
                            # 嘗試UTF-16BE解碼
                            string = string_data.decode('utf-16be')
                            strings.append({
                                'position': pos,
                                'length': length,
                                'string': string,
                                'hex': binascii.hexlify(string_data[:50]).decode('ascii')
                            })
                            print(f"[{pos}] 長度:{length} 字串: {string}")
                        except:
                            pass
                    
                    pos += 4 + length * 2
                    continue
            except:
                pass
        
        pos += 1
    
    return strings


def analyze_efk_file(file_path: str):
    """分析EFK檔案"""
    print(f"分析EFK檔案: {file_path}")
    print("="*50)
    
    strings = extract_utf16_strings(file_path)
    
    print(f"\n找到 {len(strings)} 個UTF-16字串:")
    
    # 分類字串
    file_paths = []
    other_strings = []
    
    for string_info in strings:
        string = string_info['string']
        if any(ext in string.lower() for ext in ['.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.efk', '.efkmat', '.efkmodel']):
            file_paths.append(string_info)
        else:
            other_strings.append(string_info)
    
    print(f"\n檔案路徑 ({len(file_paths)} 個):")
    for i, string_info in enumerate(file_paths, 1):
        print(f"  {i}. {string_info['string']}")
    
    print(f"\n其他字串 ({len(other_strings)} 個):")
    for i, string_info in enumerate(other_strings[:10], 1):
        print(f"  {i}. {string_info['string']}")
    
    return {
        'file_paths': file_paths,
        'other_strings': other_strings,
        'all_strings': strings
    }


def main():
    """主函數"""
    efk_file = r"C:\Users\User\Desktop\清圖資料\testEfk\Attack.efk"
    
    try:
        result = analyze_efk_file(efk_file)
        
        # 檢查同資料夾的檔案
        efk_dir = Path(efk_file).parent
        print(f"\n檢查同資料夾檔案:")
        print(f"目錄: {efk_dir}")
        
        existing_files = []
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
                print(f"  ✗ {file_name} (不存在)")
        
        print(f"\n總結:")
        print(f"EFK檔案引用的檔案: {len(result['file_paths'])} 個")
        print(f"實際存在的檔案: {len(existing_files)} 個")
        
        if existing_files:
            print(f"\n實際引用的檔案:")
            for i, file_info in enumerate(existing_files, 1):
                print(f"  {i}. {file_info['name']} ({file_info['size']} bytes)")
        
    except Exception as e:
        print(f"分析失敗: {e}")


if __name__ == "__main__":
    main() 