#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
遊戲圖片檢索工具 - 主程式
用於檢索遊戲專案中未被引用的圖片檔案
"""

import sys
import os

# 添加src目錄到Python路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import MainWindow


def main():
    """主程式入口點"""
    try:
        # 建立並執行主視窗
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"程式執行錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 