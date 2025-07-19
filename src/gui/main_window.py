import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Set, Dict, Any
import os


class MainWindow:
    """主視窗類別 - 負責GUI介面的顯示和基本互動"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("遊戲圖片檢索工具")
        self.root.geometry("800x700")  # 增加視窗高度以容納輸出區域
        
        # 資料儲存
        self.selected_path = tk.StringVar()
        self.selected_image_types = set()
        self.selected_function = tk.StringVar()
        
        # 圖片類型選項
        self.image_types = {
            "PNG": "png",
            "JPG": "jpg", 
            "JPEG": "jpeg"
        }
        
        # 功能選項（後續會依需求擴充）
        self.functions = {
            "選擇功能": "none",
            "檢索EFK檔案": "efk_scan",
            "檢索程式碼檔案": "code_scan",
            "檢索C3B檔案": "c3b_scan",
            "檢索Spine檔案": "spine_scan",
            "檢索CSB檔案": "csb_scan"
        }
        
        self._setup_ui()
    
    def _setup_ui(self):
        """設定UI元件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 標題
        title_label = ttk.Label(main_frame, text="遊戲圖片檢索工具", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 功能選擇區域
        function_frame = ttk.LabelFrame(main_frame, text="功能選擇", padding="10")
        function_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 功能下拉選單
        self.function_combobox = ttk.Combobox(
            function_frame,
            textvariable=self.selected_function,
            values=list(self.functions.keys()),
            state="readonly",
            width=30
        )
        self.function_combobox.set("選擇功能")
        self.function_combobox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.function_combobox.bind("<<ComboboxSelected>>", self._on_function_change)
        
        # 檔案路徑選擇區域
        path_frame = ttk.LabelFrame(main_frame, text="專案路徑選擇", padding="10")
        path_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 路徑顯示
        self.path_label = ttk.Label(path_frame, text="尚未選擇路徑", foreground="gray")
        self.path_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 選擇按鈕
        select_button = ttk.Button(path_frame, text="選擇專案資料夾", command=self._select_path)
        select_button.grid(row=0, column=1)
        
        # 開始分析按鈕
        analyze_button = ttk.Button(
            main_frame, 
            text="開始分析", 
            command=self._start_analysis,
            style="Accent.TButton"
        )
        analyze_button.grid(row=3, column=0, columnspan=2, pady=(20, 10))
        
        # 輸出視窗區域
        output_frame = ttk.LabelFrame(main_frame, text="分析結果輸出", padding="10")
        output_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # 建立文字區域和捲軸
        self.output_text = tk.Text(output_frame, wrap=tk.WORD, height=15, font=("Consolas", 9))
        self.output_scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=self.output_scrollbar.set)
        
        # 放置文字區域和捲軸
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.output_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 清除輸出按鈕
        clear_button = ttk.Button(output_frame, text="清除輸出", command=self._clear_output)
        clear_button.grid(row=1, column=0, pady=(5, 0))
        
        # 設定網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)  # 讓輸出區域可以擴展
        path_frame.columnconfigure(0, weight=1)
        function_frame.columnconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
    
    def _select_path(self):
        """選擇專案資料夾"""
        path = filedialog.askdirectory(title="選擇遊戲專案資料夾")
        if path:
            self.selected_path.set(path)
            self.path_label.config(text=path, foreground="black")
    
    def _on_function_change(self, event=None):
        """功能選擇變更時的回調函數"""
        selected = self.selected_function.get()
        if selected != "選擇功能":
            # 重置所有選擇
            self._reset_selections()
            print(f"選擇的功能: {selected}")
    
    def _reset_selections(self):
        """重置所有選擇"""
        # 重置路徑選擇
        self.selected_path.set("")
        self.path_label.config(text="尚未選擇路徑", foreground="gray")
    
    def _clear_output(self):
        """清除輸出視窗"""
        self.output_text.delete(1.0, tk.END)
    
    def _append_output(self, text):
        """添加文字到輸出視窗"""
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)  # 自動捲動到底部
        self.root.update()  # 更新GUI
    

    
    def _start_analysis(self):
        """開始分析按鈕的回調函數"""
        if self.selected_function.get() == "選擇功能":
            messagebox.showwarning("警告", "請先選擇功能！")
            return
        
        if not self.selected_path.get():
            messagebox.showwarning("警告", "請先選擇專案路徑！")
            return
        
        # 根據選擇的功能執行對應的分析
        function_type = self.functions[self.selected_function.get()]
        print(f"選擇的功能: {self.selected_function.get()}")
        print(f"選擇的路徑: {self.selected_path.get()}")
        
        if function_type == "efk_scan":
            self._start_efk_analysis()
        else:
            messagebox.showinfo("資訊", f"{self.selected_function.get()}功能將在後續步驟中實作")
    
    def _start_efk_analysis(self):
        """開始EFK檔案分析"""
        from src.scanner.efk_scanner import EFKScanner
        
        try:
            # 清除輸出視窗
            self._clear_output()
            self._append_output("=== EFK檔案分析開始 ===")
            self._append_output(f"掃描路徑: {self.selected_path.get()}")
            self._append_output("")
            
            # 使用預設的圖片類型集合
            default_image_types = {"png", "jpg", "jpeg", "tga", "dds", "bmp", "tiff", "tif", "webp", "ktx", "pvr"}
            scanner = EFKScanner(self.selected_path.get(), default_image_types)
            
            # 顯示進度訊息
            self._append_output("正在掃描EFK檔案...")
            self._append_output("請稍候，分析進行中...")
            self._append_output("")
            
            # 執行掃描
            results = scanner.scan_efk_files()
            
            # 顯示結果
            self._show_analysis_results_in_output(results, scanner)
            
        except KeyboardInterrupt:
            self._append_output("❌ 分析已被使用者中斷")
        except Exception as e:
            # 使用更安全的錯誤處理
            try:
                error_msg = f"分析過程中發生錯誤：{str(e)}"
            except Exception:
                error_msg = "分析過程中發生未知錯誤"
            self._append_output(f"❌ 錯誤: {error_msg}")
    
    def _show_analysis_results_in_output(self, results, scanner):
        """在輸出視窗中顯示分析結果"""
        # 檢查是否有EFK檔案被掃描到
        try:
            if not scanner.efk_files:
                self._append_output("❌ 未找到任何EFK檔案")
                return
            
            if not results:
                self._append_output(f"⚠️ 找到 {len(scanner.efk_files)} 個EFK檔案，但未解析出引用的檔案")
                return
        except Exception as e:
            try:
                self._append_output(f"❌ 檢查結果時發生錯誤：{str(e)}")
            except Exception:
                self._append_output("❌ 檢查結果時發生未知錯誤")
            return
        
        # 顯示統計資訊
        stats = scanner.get_statistics()
        self._append_output("=== 分析結果 ===")
        self._append_output(f"總EFK檔案數: {stats['total_efk_files']}")
        self._append_output(f"已分析EFK檔案數: {stats['analyzed_efk_files']}")
        self._append_output(f"總引用檔案數: {stats['total_referenced_files']}")
        self._append_output("")
        
        # 顯示詳細結果
        if results:
            self._append_output("=== 詳細結果 ===")
            for efk_file, referenced_files in results.items():
                # 提取檔案名
                file_name = os.path.basename(efk_file)
                self._append_output(f"📁 EFK檔案: {file_name}")
                self._append_output(f"   完整路徑: {efk_file}")
                self._append_output(f"   引用的檔案 ({len(referenced_files)} 個):")
                
                for i, ref_file in enumerate(referenced_files, 1):
                    self._append_output(f"     {i}. {ref_file}")
                
                self._append_output("")
        
        self._append_output("=== 分析完成 ===")
    
    def _show_analysis_results(self, results):
        """顯示分析結果（保留舊方法以備將來使用）"""
        # 這個方法保留以備將來需要彈跳視窗時使用
        pass
    
    def run(self):
        """執行GUI應用程式"""
        self.root.mainloop()
    
    def get_selected_path(self) -> str:
        """取得選擇的路徑"""
        return self.selected_path.get()
    
 