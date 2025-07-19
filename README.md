# 遊戲圖片檢索工具

這是一個用於檢索遊戲專案中未被引用的圖片檔案的Python工具。

## 功能特色

- 檢索遊戲專案中的圖片檔案
- 分析程式碼、c3b、spine、effekseer、csb檔案中的圖片引用
- 識別未被引用的圖片檔案
- 提供GUI介面讓使用者選擇要刪除的檔案

## 專案結構

```
清圖資料/
├── main.py              # 主程式入口
├── requirements.txt     # 專案依賴
├── README.md           # 專案說明
├── rule.md             # 專案規則
├── style.css           # 樣式檔案
├── src/                # 原始碼目錄
│   ├── __init__.py
│   ├── gui/            # GUI模組
│   │   ├── __init__.py
│   │   └── main_window.py
│   ├── scanner/        # 掃描器模組
│   │   ├── __init__.py
│   │   └── efk_scanner.py
│   └── utils/          # 工具模組
│       ├── __init__.py
│       └── logger.py
├── tools/              # 開發工具（僅供參考）
│   ├── README.md
│   └── *.py           # 各種分析工具
├── document/           # 文件目錄
├── logs/               # 日誌目錄
└── testEfk/           # 測試資料
```

## 安裝與執行

1. 確保已安裝Python 3.10
2. 安裝依賴套件：
   ```bash
   pip install -r requirements.txt
   ```
3. 執行程式：
   ```bash
   python main.py
   ```

## 使用方式

1. 啟動程式後會顯示GUI介面
2. 點擊「選擇專案資料夾」按鈕選擇遊戲專案路徑
3. 勾選要分析的圖片類型（PNG、JPG、JPEG）
4. 點擊「開始分析」按鈕開始檢索

## 開發進度

- [x] 步驟1：建立GUI介面（檔案路徑選擇、圖片類型選擇）
- [x] 步驟2：實作EFK檔案掃描功能
- [x] 步驟3：實作EFK檔案引用分析功能
- [x] 步驟4：整合精確EFK解析器到專案中
- [ ] 步驟5：實作其他檔案類型掃描（程式碼、c3b、spine、csb）
- [ ] 步驟6：實作結果顯示功能
- [ ] 步驟7：實作檔案刪除功能 