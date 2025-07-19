# Tools 資料夾

這個資料夾包含了EFK檔案分析相關的工具和測試腳本。

## 檔案說明

### 分析工具
- `analyze_efk.py` - 基礎EFK檔案分析器
- `deep_efk_analyzer.py` - 深度EFK檔案分析器
- `correct_efk_parser.py` - 修正版EFK解析器
- `extract_efk_strings.py` - EFK字串提取工具
- `final_efk_analyzer.py` - 最終版EFK分析器
- `precise_efk_parser.py` - 精確EFK解析器（已整合到主專案）

## 使用說明

這些工具主要用於開發和測試階段，現在已經整合到主專案的 `src/scanner/efk_scanner.py` 中。

### 主要功能
- EFK檔案二進制結構解析
- UTF-16字串提取
- 檔案路徑引用分析
- 多種檔案格式支援

### 整合狀態
✅ **已整合到主專案**
- 精確的UTF-16字串解析
- 智能檔案路徑提取
- 改進的錯誤處理

## 注意事項

- 這些工具僅供參考和開發使用
- 實際功能已整合到主專案的掃描器中
- 如需修改EFK解析邏輯，請直接修改 `src/scanner/efk_scanner.py` 