#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C3B 模型檔案解析器
用於解析 Cocos2d-x 的 c3b 模型檔案並提取其中引用的圖片資源
"""

import struct
import os
import json
import argparse
from typing import List, Dict, Any, Optional
from pathlib import Path


class C3BParser:
    """C3B 檔案解析器"""
    
    def __init__(self):
        self.materials = []
        self.textures = []
        self.referenced_images = set()
        
    def read_string(self, data: bytes, offset: int) -> tuple[str, int]:
        """讀取字串，返回字串和新的偏移位置"""
        # 讀取字串長度 (4 bytes)
        length = struct.unpack('<I', data[offset:offset + 4])[0]
        offset += 4
        
        # 讀取字串內容
        string_data = data[offset:offset + length]
        # 移除 null terminator
        if length > 0 and string_data[-1] == 0:
            string_data = string_data[:-1]
        
        string = string_data.decode('utf-8', errors='ignore')
        offset += length
        
        return string, offset
    
    def read_uint32(self, data: bytes, offset: int) -> tuple[int, int]:
        """讀取 32 位無符號整數"""
        value = struct.unpack('<I', data[offset:offset + 4])[0]
        return value, offset + 4
    
    def read_float(self, data: bytes, offset: int) -> tuple[float, int]:
        """讀取 32 位浮點數"""
        value = struct.unpack('<f', data[offset:offset + 4])[0]
        return value, offset + 4
    
    def parse_header(self, data: bytes) -> int:
        """解析 C3B 檔案頭"""
        # 檢查檔案標識符 "C3B\0"
        if data[:4] != b'C3B\x00':
            raise ValueError("不是有效的 C3B 檔案")
        
        print("✓ 檔案格式: C3B")
        
        # 讀取版本資訊
        version = struct.unpack('<I', data[4:8])[0]
        print(f"✓ 檔案版本: {version}")
        
        return 8  # 返回頭部長度
    
    def extract_strings_from_data(self, data: bytes, start_offset: int = 0) -> List[str]:
        """從二進位資料中提取可能的字串（包括檔案名）"""
        strings = []
        i = start_offset
        
        while i < len(data) - 4:
            try:
                # 嘗試讀取長度
                length = struct.unpack('<I', data[i:i + 4])[0]
                
                # 檢查長度是否合理 (1-1024 字元)
                if 1 <= length <= 1024 and i + 4 + length <= len(data):
                    # 提取字串
                    string_data = data[i + 4:i + 4 + length]
                    
                    # 檢查是否包含 null terminator
                    if length > 0 and string_data[-1] == 0:
                        string_data = string_data[:-1]
                    
                    try:
                        string = string_data.decode('utf-8')
                        
                        # 檢查是否是有效的檔案名或材質名
                        if self.is_valid_resource_name(string):
                            strings.append(string)
                            print(f"✓ 發現字串: {string}")
                            
                            # 檢查是否是圖片檔案
                            if self.is_image_file(string):
                                self.referenced_images.add(string)
                                print(f"  → 圖片檔案: {string}")
                    
                    except UnicodeDecodeError:
                        pass
                
                i += 1
                
            except (struct.error, IndexError):
                i += 1
        
        return strings
    
    def is_valid_resource_name(self, string: str) -> bool:
        """檢查字串是否是有效的資源名稱"""
        if len(string) < 3 or len(string) > 256:
            return False
        
        # 檢查是否包含檔案副檔名
        if '.' in string:
            ext = string.split('.')[-1].lower()
            # 常見的圖片和模型檔案副檔名
            valid_extensions = {
                'png', 'jpg', 'jpeg', 'bmp', 'tga', 'pvr', 'ktx', 'astc',
                'c3b', 'c3t', 'fbx', 'obj', 'dae', 'blend',
                'fnt', 'ttf', 'json', 'plist', 'xml'
            }
            if ext in valid_extensions:
                return True
        
        # 檢查是否是材質名稱 (通常包含 material, mat, diffuse 等關鍵字)
        material_keywords = ['material', 'mat', 'diffuse', 'normal', 'specular', 'texture']
        for keyword in material_keywords:
            if keyword.lower() in string.lower():
                return True
        
        # 檢查是否包含常見的資源名稱字元 (字母、數字、下劃線、連字符)
        if all(c.isalnum() or c in '_-.' for c in string):
            return True
        
        return False
    
    def is_image_file(self, filename: str) -> bool:
        """檢查檔案是否是圖片檔案"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tga', '.pvr', '.ktx', '.astc'}
        return any(filename.lower().endswith(ext) for ext in image_extensions)
    
    def parse_c3b_file(self, filepath: str) -> Dict[str, Any]:
        """解析 C3B 檔案"""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            print(f"📁 正在解析檔案: {filepath}")
            print(f"📊 檔案大小: {len(data)} bytes")
            
            # 解析檔案頭
            offset = self.parse_header(data)
            
            # 提取所有可能的字串
            print("\n🔍 搜尋資源引用...")
            strings = self.extract_strings_from_data(data, offset)
            
            # 分析結果
            result = {
                'file_path': filepath,
                'file_size': len(data),
                'referenced_images': list(self.referenced_images),
                'all_strings': strings,
                'image_count': len(self.referenced_images)
            }
            
            return result
            
        except Exception as e:
            print(f"❌ 解析檔案時發生錯誤: {e}")
            return {'error': str(e)}
    
    def scan_directory(self, directory: str) -> List[Dict[str, Any]]:
        """掃描目錄中的所有 C3B 檔案"""
        results = []
        directory_path = Path(directory)
        
        print(f"📂 掃描目錄: {directory}")
        
        # 遞迴搜尋所有 .c3b 檔案
        c3b_files = list(directory_path.rglob("*.c3b"))
        
        if not c3b_files:
            print("❌ 未找到任何 .c3b 檔案")
            return results
        
        print(f"✓ 找到 {len(c3b_files)} 個 C3B 檔案")
        
        for c3b_file in c3b_files:
            print(f"\n{'='*60}")
            result = self.parse_c3b_file(str(c3b_file))
            results.append(result)
            
            # 清空上次的結果，為下個檔案準備
            self.referenced_images.clear()
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]], output_path: str = "c3b_analysis_report.json"):
        """生成分析報告"""
        print(f"\n📋 生成分析報告...")
        
        # 統計所有圖片引用
        all_images = set()
        file_count = 0
        total_size = 0
        
        for result in results:
            if 'error' not in result:
                file_count += 1
                total_size += result['file_size']
                all_images.update(result['referenced_images'])
        
        summary = {
            'scan_time': str(__import__('datetime').datetime.now()),
            'summary': {
                'total_c3b_files': file_count,
                'total_size_bytes': total_size,
                'unique_images_referenced': len(all_images),
                'all_referenced_images': sorted(list(all_images))
            },
            'file_details': results
        }
        
        # 保存到 JSON 檔案
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 報告已保存到: {output_path}")
        print(f"\n📊 分析摘要:")
        print(f"   - 已分析 {file_count} 個 C3B 檔案")
        print(f"   - 總檔案大小: {total_size / (1024*1024):.2f} MB")
        print(f"   - 發現 {len(all_images)} 個唯一的圖片引用:")
        
        for img in sorted(all_images):
            print(f"     • {img}")
        
        return summary


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="C3B 模型檔案解析器 - 提取圖片引用")
    parser.add_argument('input', help='C3B 檔案或包含 C3B 檔案的目錄路徑')
    parser.add_argument('-o', '--output', default='c3b_analysis_report.json', 
                       help='輸出報告檔案名 (預設: c3b_analysis_report.json)')
    parser.add_argument('-v', '--verbose', action='store_true', help='顯示詳細輸出')
    
    args = parser.parse_args()
    
    c3b_parser = C3BParser()
    
    # 檢查輸入是檔案還是目錄
    input_path = Path(args.input)
    
    if input_path.is_file() and input_path.suffix.lower() == '.c3b':
        # 單個檔案
        print("🎯 模式: 單檔案分析")
        result = c3b_parser.parse_c3b_file(str(input_path))
        results = [result] if result else []
    elif input_path.is_dir():
        # 目錄掃描
        print("🎯 模式: 目錄掃描")
        results = c3b_parser.scan_directory(str(input_path))
    else:
        print("❌ 錯誤: 輸入路徑不是有效的 C3B 檔案或目錄")
        return
    
    # 生成報告
    if results:
        c3b_parser.generate_report(results, args.output)
    else:
        print("❌ 沒有成功解析任何檔案")


if __name__ == "__main__":
    main() 