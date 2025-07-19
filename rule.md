<!-- config
{
  "style": "style.css"
}
-->

# 這是 python 3.10 的專案
# to cursor: 
1. 你是一個python高手 不會犯低級的錯誤 
2. 你是專業的超級高級工程師 寫的程式碼 乾淨且高校
3. 你是一個遊戲特效高手 理解並持續學習 遊戲相關的知識 

模組拆分清楚
不要全部的功能都寫在同一個檔案
考慮清楚功能之間的擴充
不要有耦合與指標引用的函數共同引用造成後續衝突的問提
我要一個步驟一個步驟慢慢來做 因此 請遵守我給的步驟

1. 不要更動我的 rule.md 檔案 
2. 若要新增描述說明 一律修改在 document 裡面 
3. 自動生產出來的單元測試工具 測試結束後自動刪除 
4. 我不要有輸出的 json 檔案 
5. 除了 main.py 的 python 檔案 其他 python 檔案不要出現在專案的第一層 
6. 不要產生報告給 我不需要.md檔案
7. logs我也不要 不要產生 log檔案給我

## 最終目的

我想做一個可以檢索遊戲專案內 是否有多餘且沒有被 (程式碼、c3b、spine、effekseer、csb)引用到的圖 並列舉出來
讓使用者決定是否刪除
刪除時可以決定要刪除單張
還是全部刪除

---

### 規則說明 1

## 接下來我要一個一個步驟做 因為我要檢索各種不同類型的檔案內所引用的東西。

### 修改步驟 2

## 圖片選擇 那個窗框 先幫我拔掉

### 實作步驟 1

我要做一個 GUI 介面 1.有檔案路徑選擇按鈕
2..我要有下拉選單 可以選擇 { ... } 後續我會依造我的功能一個一個擴充 請各功能之間不要有參數引用的衝突 切換功能時 目前所引用的東西要重置

### 實作步驟 2

我想要先做一個可以檢索 .efk 檔案裡面所引用的檔案
ex: 我給一個路徑
去 parse 裡面所有的.efk 檔案
列出該.efk 檔案下所引用的檔案
ex: .efkmat .efkmodel .png .....

### 實作步驟 3

我想要先做一個可以檢索 .efk 檔案裡面所引用的檔案
ex: 我給一個路徑
去 parse 裡面所有(包含子路徑)的.efk 檔案
列出該.efk 檔案下所引用的檔案
ex: .efkmat .efkmodel .png .....

#### 修正步驟 3

我給的 "" 這個路徑下明明有 efk
我選擇檢索 efk 並且 按下開始分析 但結果跳出 未找到任何 EFK 檔案或引用的檔案

#### 修正步驟 3-2

按下開始分析後，顯示有找到 efk 檔案 但未解析出引用檔案
請以""為範例 試著解析出來

### 實作步驟 4

請將請將 python precise_efk_parser.py 裡面的功能 實做到這個專案中
python precise_efk_parser.py 這才是能真正反編譯 並檢所 efk 檔案的程式碼 目前的是錯誤的

#### 實作步驟 4-說明

很好 目前實作的功能是正常的 efk 可以正常掃描

### 實作步驟 5

請在原本的 GUI 介面上加一個輸出視窗 我不要彈跳出來的
當我按下開始分析後 輸出的資料都顯示在輸出視窗中 並且可以上下滑動
用滑鼠滾輪也可以上下滑動

### 實作步驟 6

再在原本的 GUI 介面上加上一個輸出視窗 在分析結果輸出的上方
我要列出這個資料下以下 完全沒有被任何一個 efk 檔案引用的檔案
並且條列出的檔案前方 加上 一個 checkbox 我要可以選擇 (可以複選) 在旁邊加上一個刪除檔案按鈕 可以單檔刪除
(單檔刪除後 列出來的條列文字不要清除 而是那條變成底)
並在輸出視窗下方加一個 全部清除的按鈕 可以一次刪除所有多出來的檔案

### 實作步驟 7

除了掃描 檔案是否有被.efk 檔案是否有引用外
也要掃描是否有被 .efkmat .efkmodel 引用
如果都沒有被引用再輸出印出來
ex:

1. .efkmat:C:\Users\User\Desktop\GIT_TIMD\ClearProjMachine\test\testEfk\Dissolve_04.efkmat
2. .efkmodel:C:\Users\User\Desktop\GIT_TIMD\ClearProjMachine\test\testEfk\Aurora_Path.efkmodel
   請確實單元測試 確認可以正確掃描這些範例裡面的檔案類型 有的是二進制 或 不知道甚麼進制 請自行判斷


#### 測試步驟7-1
先做一個單元測試 
掃描.efkmodel 裡面所引用的檔案
因為目前掃描出來 裡面都是沒有任何引用的 可能分析錯誤

#### 測試步驟7-2
用剛剛單元測試掃描
C:\Users\User\Desktop\OceanTale\effekseer\Efk
這底下所有的.ekfmodel 有沒有任何引用

#### 測試步驟7-3
我用這個專案掃描了
"C:\Users\User\Desktop\OceanTale\effekseer\Efk\CrazyPirateShip"
為甚麼列出的 .efk 只有 Attack.efk
而其他.efk都沒有引用任何東西嗎  請再次確認

#### 修正實作 7-4
當我選擇路徑 
"C:\Users\User\Desktop\OceanTale\effekseer\Efk\CrazyPirateShipEarth"
所有的檔案都有被引用
但是當我選擇
"C:\Users\User\Desktop\OceanTale\effekseer\Efk"
卻出現 "C:\Users\User\Desktop\OceanTale\effekseer\Efk\CrazyPirateShipEarth" 裡面有檔案未被引用
請修正這個問題

#### 修正實作 7-5
一樣的問題 當我選擇
"C:\Users\User\Desktop\OceanTale\effekseer\Efk\CrazyPirateShipEarth" 所有檔案都有被引用
但當我選擇路徑
"C:\Users\User\Desktop\OceanTale\effekseer\Efk"
卻出現
"C:\Users\User\Desktop\OceanTale\effekseer\Efk\CrazyPirateShipEarth\vfx_aurora.png"未被引用
請修正他

### 實作步驟 8
為引用檔案列表 
列出來的信息  請向上而下列出 不是先向下對齊
並且如果我點了刪除 
他的checkbox 跟 刪除按鈕應該要反灰並禁按

### 修正步驟 8-1
請幫我把  未引用檔案列表
這個UI的code刪除乾淨  重新做一個 
我要的功能是 如果有找到未被引用的資源 
就列在窗框內 要有checkBox可以選擇 並且 旁邊有刪除單檔的按鈕
下方有 刪除全部的按鈕 
當該檔被刪除 該列就會反"紅"(顏色) 並且該列的checkBox與刪除單檔的按鈕會反灰 不可按

### 實作步驟 9
請將這個專案中 
未引用檔按列表 以及 這個輸出框 從這個專案中移除 
我不要顯示這個功能 先把這個功能的code全部刪掉 
但是 分析結果輸出的所有功能要保留

### 實作步驟 10
很好 目前功能都正常


#### 優化步驟 11 
如果我先選擇檔案路徑 再功能選擇
不要清除我所選擇的檔案路徑

#### 優化步驟 12
1. 當我選擇一個 未引用檔案列表 裡面的檔案 按下"刪除除選中檔案"時
確實有刪除 但顯示"✅ 批量刪除完成: 成功 1 個，失敗 1 個"
應該是成功 1個 失敗0個才對 

2. 當我選擇檔案 再按下"再檔案總管中開啟"時 沒有正確開啟該檔案的位置
還是一樣 還是一樣 

#### 優化步驟 13:
當 "分析結果輸出" 這種成功的訊息時 :
"""您可以使用上方的checkbox選擇檔案，或使用刪除按鈕進行操作
✅ 已刪除檔案: C:/Users/User/Desktop/OceanTale/effekseer/Efk\CrazyPirateShipEarth\vfx_aurora - 複製.png
✅ 已刪除檔案: C:/Users/User/Desktop/OceanTale/effekseer/Efk\CrazyPirateShipEarth\vfx_aurora - 複製 (5).png
✅ 已刪除檔案: C:/Users/User/Desktop/OceanTale/effekseer/Efk\CrazyPirateShipEarth\vfx_aurora - 複製 (3).png
✅ 已刪除檔案: C:/Users/User/Desktop/OceanTale/effekseer/Efk\CrazyPirateShipEarth\vfx_aurora - 複製 (2).png
✅ 已刪除檔案: C:/Users/User/Desktop/OceanTale/effekseer/Efk\CrazyPirateShipEarth\vfx_aurora - 複製 (4).png
✅ 批量刪除完成: 成功 5 個，失敗 0 個"""
用綠色的字體  失敗的話則用紅色的字體




 





