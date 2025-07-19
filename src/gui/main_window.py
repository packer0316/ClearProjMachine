import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Set, Dict, Any
import os


class MainWindow:
    """主視窗類別 - 負責GUI介面的顯示和基本互動"""
    
    def __init__(self):
        """初始化主視窗"""
        self.root = tk.Tk()
        self.root.title("遊戲圖片檢索工具")
        self.root.geometry("800x600")  # 設定初始大小
        
        # 初始化變數
        self.selected_path = tk.StringVar()
        self.selected_function = tk.StringVar()
        self.functions = {
            "EFK檔案掃描": "efk_scan"
        }
        
        # 初始化資料結構
        self.unused_files = []
        self.file_checkboxes = {}
        self.file_labels = {}
        
        # 設定UI
        self._setup_ui()
        
        # 確保視窗被正確顯示
        self.root.update()
        self.root.deiconify()  # 確保視窗可見
    
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
        
        # 未引用檔案區域 - 重新設計
        unused_frame = ttk.LabelFrame(main_frame, text="未引用檔案列表", padding="10")
        unused_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 10))
        
        # 進度條
        self.progress_bar = ttk.Progressbar(
            unused_frame,
            mode='indeterminate',
            length=200
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # 狀態標籤
        self.status_label = ttk.Label(
            unused_frame,
            text="準備就緒",
            foreground="gray"
        )
        self.status_label.grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        # 重新設計的檔案列表 - 使用簡單的Listbox
        self.unused_listbox = tk.Listbox(
            unused_frame,
            height=8,
            selectmode=tk.EXTENDED,
            font=("Consolas", 9)
        )
        self.unused_listbox.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        # 檔案列表的捲軸
        unused_scrollbar = ttk.Scrollbar(unused_frame, orient="vertical", command=self.unused_listbox.yview)
        unused_scrollbar.grid(row=2, column=1, sticky=(tk.N, tk.S))
        self.unused_listbox.configure(yscrollcommand=unused_scrollbar.set)
        
        # 檔案操作按鈕框架
        file_buttons_frame = ttk.Frame(unused_frame)
        file_buttons_frame.grid(row=3, column=0, columnspan=2, pady=(5, 0))
        
        # 刪除選中檔案按鈕
        self.delete_selected_button = ttk.Button(
            file_buttons_frame,
            text="🗑️ 刪除選中檔案",
            command=self._delete_selected_files,
            state="disabled"
        )
        self.delete_selected_button.grid(row=0, column=0, padx=(0, 10))
        
        # 全部清除按鈕
        self.clear_all_button = ttk.Button(
            file_buttons_frame, 
            text="🗑️ 全部清除", 
            command=self._clear_all_unused_files,
            state="disabled"
        )
        self.clear_all_button.grid(row=0, column=1, padx=(0, 10))
        
        # 在檔案總管中開啟按鈕
        self.open_in_explorer_button = ttk.Button(
            file_buttons_frame,
            text="📁 在檔案總管中開啟",
            command=self._open_selected_in_explorer,
            state="disabled"
        )
        self.open_in_explorer_button.grid(row=0, column=2)
        
        # 輸出視窗區域
        output_frame = ttk.LabelFrame(main_frame, text="分析結果輸出", padding="10")
        output_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
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
        main_frame.rowconfigure(4, weight=1)  # 讓未引用檔案區域可以擴展
        main_frame.rowconfigure(5, weight=1)  # 讓輸出區域可以擴展
        path_frame.columnconfigure(0, weight=1)
        function_frame.columnconfigure(0, weight=1)
        unused_frame.columnconfigure(0, weight=1)
        unused_frame.rowconfigure(2, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
    
    def _on_mousewheel(self, event):
        """處理滑鼠滾輪事件"""
        self.unused_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
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
        # 清除未引用檔案列表
        self._clear_unused_files_list()
    
    def _clear_output(self):
        """清除輸出視窗"""
        self.output_text.delete(1.0, tk.END)
    
    def _append_output(self, text):
        """添加文字到輸出視窗"""
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)  # 自動捲動到底部
        self.root.update()  # 更新GUI
    
    def _clear_unused_files_list(self):
        """清除未引用檔案列表"""
        try:
            # 檢查GUI元件是否已經初始化
            if not hasattr(self, 'unused_listbox'):
                print("警告: GUI元件尚未初始化")
                return
            
            # 檢查框架是否存在
            if not self.unused_listbox.winfo_exists():
                print("警告: GUI框架不存在")
                return
            
            # 清除所有項目
            self.unused_listbox.delete(0, tk.END)
            
            # 重置資料
            self.unused_files = []
            self.file_checkboxes = {}
            self.file_labels = {}
            if hasattr(self, 'file_delete_buttons'):
                self.file_delete_buttons = {}
            
            # 禁用全部清除按鈕
            if hasattr(self, 'clear_all_button') and self.clear_all_button.winfo_exists():
                self.clear_all_button.config(state="disabled")
            
            # 禁用刪除選中按鈕
            if hasattr(self, 'delete_selected_button') and self.delete_selected_button.winfo_exists():
                self.delete_selected_button.config(state="disabled")
            
            # 禁用開啟總管按鈕
            if hasattr(self, 'open_in_explorer_button') and self.open_in_explorer_button.winfo_exists():
                self.open_in_explorer_button.config(state="disabled")
            
            # 更新狀態標籤
            if hasattr(self, 'status_label'):
                self.status_label.config(
                    text="未引用檔案列表 (等待分析...)",
                    foreground="gray"
                )
                
        except Exception as e:
            print(f"清除未引用檔案列表時發生錯誤: {str(e)}")
    
    def _add_unused_file(self, file_path: str):
        """新增未引用檔案到列表"""
        if file_path in self.unused_files:
            return
        
        # 檢查GUI元件是否已經初始化
        if not hasattr(self, 'unused_listbox'):
            print("警告: GUI元件尚未初始化")
            return
        
        # 檢查框架是否存在
        if not self.unused_listbox.winfo_exists():
            print("警告: GUI框架不存在")
            return
        
        self.unused_files.append(file_path)
        
        try:
            # 添加項目到Listbox
            self.unused_listbox.insert(tk.END, file_path)
            
            # 建立checkbox變數
            checkbox_var = tk.BooleanVar()
            self.file_checkboxes[file_path] = checkbox_var
            
            # 啟用全部清除按鈕
            if hasattr(self, 'clear_all_button') and self.clear_all_button.winfo_exists():
                self.clear_all_button.config(state="normal")
            
            # 啟用刪除選中按鈕
            if hasattr(self, 'delete_selected_button') and self.delete_selected_button.winfo_exists():
                self.delete_selected_button.config(state="normal")
            
            # 啟用開啟總管按鈕
            if hasattr(self, 'open_in_explorer_button') and self.open_in_explorer_button.winfo_exists():
                self.open_in_explorer_button.config(state="normal")
            
            # 更新狀態標籤
            if hasattr(self, 'status_label'):
                self.status_label.config(
                    text=f"未引用檔案列表 (找到 {len(self.unused_files)} 個檔案)",
                    foreground="black"
                )
            
            # 添加調試信息
            print(f"=== 檔案項目調試信息 ===")
            print(f"檔案路徑: {file_path}")
            print(f"Listbox存在: {self.unused_listbox.winfo_exists()}")
            print(f"Listbox大小: {self.unused_listbox.winfo_width()}x{self.unused_listbox.winfo_height()}")
            print(f"Listbox項目數: {self.unused_listbox.size()}")
            
            # 檢查檔案項目是否可見
            try:
                items = self.unused_listbox.get(0, tk.END)
                print(f"Listbox所有項目: {items}")
            except Exception as e:
                print(f"檢查Listbox項目時發生錯誤: {str(e)}")
                
        except Exception as e:
            print(f"添加檔案到列表時發生錯誤: {str(e)}")
            # 如果添加失敗，從列表中移除
            if file_path in self.unused_files:
                self.unused_files.remove(file_path)
    
    def _delete_single_file(self, file_path: str):
        """刪除單個檔案"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                
                # 檢查GUI元件是否已經初始化
                if not hasattr(self, 'unused_listbox') or not self.unused_listbox.winfo_exists():
                    self._append_output(f"✅ 已刪除檔案: {file_path}")
                    return
                
                # 將檔案項目變為灰色並加上刪除線效果
                if file_path in self.file_labels:
                    labels = self.file_labels[file_path]
                    if labels['name'].winfo_exists():
                        labels['name'].config(
                            foreground="gray",
                            font=("TkDefaultFont", 9, "overstrike")
                        )
                    if labels['dir'].winfo_exists():
                        labels['dir'].config(
                            foreground="lightgray",
                            font=("TkDefaultFont", 8, "overstrike")
                        )
                    if labels['size'] and labels['size'].winfo_exists():
                        labels['size'].config(
                            foreground="lightgray",
                            font=("TkDefaultFont", 8, "overstrike")
                        )
                
                # 禁用checkbox
                if file_path in self.file_checkboxes:
                    # 找到對應的checkbox widget並禁用
                    for widget in self.unused_listbox.winfo_children():
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Checkbutton) and child.winfo_exists() and child.cget("variable") == str(self.file_checkboxes[file_path]):
                                child.config(state="disabled")
                                break
                
                # 禁用刪除按鈕
                if file_path in self.file_delete_buttons and self.file_delete_buttons[file_path].winfo_exists():
                    self.file_delete_buttons[file_path].config(state="disabled")
                
                self._append_output(f"✅ 已刪除檔案: {file_path}")
            else:
                self._append_output(f"❌ 檔案不存在: {file_path}")
        except Exception as e:
            self._append_output(f"❌ 刪除檔案失敗: {file_path} - {str(e)}")
    
    def _open_selected_in_explorer(self):
        """在檔案總管中開啟選中的檔案"""
        selected_indices = self.unused_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "請選擇要開啟的檔案！")
            return
        
        file_path = self.unused_listbox.get(selected_indices[0])
        self._open_in_explorer(file_path)
    
    def _delete_selected_files(self):
        """刪除選中的檔案"""
        selected_indices = self.unused_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "請選擇要刪除的檔案！")
            return
        
        file_paths_to_delete = [self.unused_listbox.get(i) for i in selected_indices]
        
        # 確認對話框
        result = messagebox.askyesno(
            "確認刪除", 
            f"確定要刪除選中的 {len(file_paths_to_delete)} 個檔案嗎？\n此操作無法復原！"
        )
        
        if not result:
            return
        
        deleted_count = 0
        failed_count = 0
        
        for file_path in file_paths_to_delete:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
                    
                    # 只有在GUI已初始化的情況下才更新UI
                    if hasattr(self, 'unused_listbox') and self.unused_listbox.winfo_exists():
                        # 將檔案標籤變為灰色並加上刪除線效果
                        if file_path in self.file_labels:
                            labels = self.file_labels[file_path]
                            if labels['name'].winfo_exists():
                                labels['name'].config(
                                    foreground="gray",
                                    font=("TkDefaultFont", 9, "overstrike")
                                )
                            if labels['dir'].winfo_exists():
                                labels['dir'].config(
                                    foreground="lightgray",
                                    font=("TkDefaultFont", 8, "overstrike")
                                )
                            if labels['size'] and labels['size'].winfo_exists():
                                labels['size'].config(
                                    foreground="lightgray",
                                    font=("TkDefaultFont", 8, "overstrike")
                                )
                        
                        # 禁用checkbox
                        if file_path in self.file_checkboxes:
                            # 找到對應的checkbox widget並禁用
                            for widget in self.unused_listbox.winfo_children():
                                for child in widget.winfo_children():
                                    if isinstance(child, ttk.Checkbutton) and child.winfo_exists() and child.cget("variable") == str(self.file_checkboxes[file_path]):
                                        child.config(state="disabled")
                                        break
                        
                        # 禁用刪除按鈕
                        if file_path in self.file_delete_buttons and self.file_delete_buttons[file_path].winfo_exists():
                            self.file_delete_buttons[file_path].config(state="disabled")
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                self._append_output(f"❌ 刪除檔案失敗: {file_path} - {str(e)}")
        
        self._append_output(f"✅ 批量刪除完成: 成功 {deleted_count} 個，失敗 {failed_count} 個")
    
    def _clear_all_unused_files(self):
        """清除所有未引用的檔案"""
        if not self.unused_files:
            return
        
        # 確認對話框
        result = messagebox.askyesno(
            "確認刪除", 
            f"確定要刪除所有 {len(self.unused_files)} 個未引用的檔案嗎？\n此操作無法復原！"
        )
        
        if not result:
            return
        
        deleted_count = 0
        failed_count = 0
        
        # 檢查GUI元件是否已經初始化
        gui_initialized = hasattr(self, 'unused_listbox') and self.unused_listbox.winfo_exists()
        
        for file_path in self.unused_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
                    
                    # 只有在GUI已初始化的情況下才更新UI
                    if gui_initialized:
                        # 將檔案標籤變為灰色並加上刪除線效果
                        if file_path in self.file_labels:
                            labels = self.file_labels[file_path]
                            if labels['name'].winfo_exists():
                                labels['name'].config(
                                    foreground="gray",
                                    font=("TkDefaultFont", 9, "overstrike")
                                )
                            if labels['dir'].winfo_exists():
                                labels['dir'].config(
                                    foreground="lightgray",
                                    font=("TkDefaultFont", 8, "overstrike")
                                )
                            if labels['size'] and labels['size'].winfo_exists():
                                labels['size'].config(
                                    foreground="lightgray",
                                    font=("TkDefaultFont", 8, "overstrike")
                                )
                        
                        # 禁用checkbox
                        if file_path in self.file_checkboxes:
                            # 找到對應的checkbox widget並禁用
                            for widget in self.unused_listbox.winfo_children():
                                for child in widget.winfo_children():
                                    if isinstance(child, ttk.Checkbutton) and child.winfo_exists() and child.cget("variable") == str(self.file_checkboxes[file_path]):
                                        child.config(state="disabled")
                                        break
                        
                        # 禁用刪除按鈕
                        if file_path in self.file_delete_buttons and self.file_delete_buttons[file_path].winfo_exists():
                            self.file_delete_buttons[file_path].config(state="disabled")
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                self._append_output(f"❌ 刪除檔案失敗: {file_path} - {str(e)}")
        
        self._append_output(f"✅ 批量刪除完成: 成功 {deleted_count} 個，失敗 {failed_count} 個")
    
    def _find_unused_files(self, referenced_files: Set[str], project_path: str) -> List[str]:
        """找出未被引用的檔案"""
        unused_files = []
        
        try:
            # 取得所有圖片檔案
            image_extensions = {'.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.tiff', '.tif', '.webp', '.ktx', '.pvr'}
            
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    # 檢查是否為圖片檔案
                    if file_ext in image_extensions:
                        # 檢查是否被引用
                        if file_path not in referenced_files:
                            unused_files.append(file_path)
            
        except Exception as e:
            self._append_output(f"❌ 搜尋未引用檔案時發生錯誤: {str(e)}")
        
        return unused_files
    
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
            # 開始進度條
            self._start_progress("正在準備分析...")
            
            # 清除輸出視窗和未引用檔案列表
            self._clear_output()
            self._clear_unused_files_list()
            self._append_output("=== EFK檔案分析開始 ===")
            self._append_output(f"掃描路徑: {self.selected_path.get()}")
            self._append_output("")
            
            # 更新狀態
            self._update_status("正在初始化掃描器...", "blue")
            
            # 使用預設的圖片類型集合
            default_image_types = {"png", "jpg", "jpeg", "tga", "dds", "bmp", "tiff", "tif", "webp", "ktx", "pvr"}
            scanner = EFKScanner(self.selected_path.get(), default_image_types)
            
            # 顯示進度訊息
            self._append_output("正在掃描EFK檔案...")
            self._append_output("請稍候，分析進行中...")
            self._append_output("")
            
            # 更新狀態
            self._update_status("正在掃描EFK檔案...", "blue")
            
            # 執行掃描
            results = scanner.scan_efk_files()
            
            # 更新狀態
            self._update_status("正在處理掃描結果...", "blue")
            
            # 顯示結果
            self._show_analysis_results_in_output(results, scanner)
            
            # 更新狀態
            self._update_status("正在查找未引用檔案...", "blue")
            
            # 找出未引用的檔案
            self._find_and_display_unused_files(results, scanner)
            
            # 停止進度條
            self._stop_progress("分析完成")
            
        except KeyboardInterrupt:
            self._stop_progress("分析被中斷")
            self._append_output("❌ 分析已被使用者中斷")
        except Exception as e:
            # 停止進度條
            self._stop_progress("分析失敗")
            # 使用更安全的錯誤處理
            try:
                error_msg = f"分析過程中發生錯誤：{str(e)}"
            except Exception:
                error_msg = "分析過程中發生未知錯誤"
            self._append_output(f"❌ 錯誤: {error_msg}")
    
    def _find_and_display_unused_files(self, results: Dict[str, List[str]], scanner):
        """找出並顯示未引用的檔案"""
        try:
            # 收集所有被引用的檔案路徑
            referenced_files = set()
            
            # 方法1: 從掃描結果中收集引用檔案
            for efk_file, ref_files in results.items():
                for ref_file in ref_files:
                    # 嘗試找到檔案的完整路徑
                    full_path = self._find_file_path(ref_file, self.selected_path.get())
                    if full_path:
                        referenced_files.add(full_path)
                        self._append_output(f"🔍 找到引用檔案: {ref_file} -> {full_path}")
                    else:
                        self._append_output(f"⚠️  無法解析引用檔案: {ref_file}")
            
            # 方法2: 直接從掃描器獲取所有檔案
            all_files_in_project = set()
            image_extensions = {'.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.tiff', '.tif', '.webp', '.ktx', '.pvr'}
            
            for root, dirs, files in os.walk(self.selected_path.get()):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    # 檢查是否為圖片檔案
                    if file_ext in image_extensions:
                        all_files_in_project.add(file_path)
            
            self._append_output(f"📊 專案中總共有 {len(all_files_in_project)} 個圖片檔案")
            self._append_output(f"📊 被引用的檔案: {len(referenced_files)} 個")
            
            # 方法3: 改進的未引用檔案檢查
            # 使用更精確的匹配邏輯
            unused_files = []
            for file_path in all_files_in_project:
                is_referenced = False
                
                # 檢查是否在引用檔案列表中
                if file_path in referenced_files:
                    is_referenced = True
                else:
                    # 檢查檔案名是否被引用（處理路徑不一致的情況）
                    file_name = os.path.basename(file_path)
                    for ref_path in referenced_files:
                        if os.path.basename(ref_path).lower() == file_name.lower():
                            is_referenced = True
                            break
                    
                    # 檢查相對路徑是否被引用
                    if not is_referenced:
                        relative_path = os.path.relpath(file_path, self.selected_path.get())
                        for ref_file in [ref for efk_file, ref_files in results.items() for ref in ref_files]:
                            if ref_file.replace('\\', '/').lower() == relative_path.replace('\\', '/').lower():
                                is_referenced = True
                                break
                
                if not is_referenced:
                    unused_files.append(file_path)
            
            if unused_files:
                self._append_output("")
                self._append_output("=== 未引用檔案列表 ===")
                self._append_output(f"找到 {len(unused_files)} 個未被引用的檔案:")
                
                # 檢查GUI元件是否已初始化
                if not hasattr(self, 'unused_listbox'):
                    self._append_output("⚠️  GUI元件尚未初始化，無法顯示檔案列表")
                    self._append_output("請重新啟動應用程式")
                    return
                
                if not self.unused_listbox.winfo_exists():
                    self._append_output("⚠️  GUI框架不存在，無法顯示檔案列表")
                    self._append_output("請重新啟動應用程式")
                    return
                
                # 更新狀態標籤
                if hasattr(self, 'status_label'):
                    self.status_label.config(
                        text=f"未引用檔案列表 (正在添加 {len(unused_files)} 個檔案...)",
                        foreground="blue"
                    )
                
                # 將未引用檔案加入GUI列表
                added_count = 0
                for file_path in unused_files:
                    try:
                        print(f"正在添加檔案到GUI: {file_path}")
                        self._add_unused_file(file_path)
                        self._append_output(f"  📄 {file_path}")
                        added_count += 1
                        
                        # 強制更新GUI
                        self.root.update()
                        self.root.after(50)  # 等待50毫秒
                        
                    except Exception as e:
                        self._append_output(f"  ❌ 添加檔案到列表失敗: {file_path} - {str(e)}")
                        print(f"添加檔案失敗: {str(e)}")
                
                self._append_output(f"✅ 成功添加 {added_count} 個檔案到列表")
                
                # 最終狀態更新
                if hasattr(self, 'status_label'):
                    self.status_label.config(
                        text=f"未引用檔案列表 (找到 {added_count} 個檔案)",
                        foreground="black"
                    )
                
                # 最終強制更新GUI
                self.root.update()
                self.root.after(200)  # 等待200毫秒確保完全更新
                
                # 檢查GUI列表中的實際項目
                if hasattr(self, 'unused_listbox') and self.unused_listbox.winfo_exists():
                    items = self.unused_listbox.get(0, tk.END)
                    self._append_output(f"🔍 GUI列表實際項目數: {len(items)}")
                    
                    for i, item in enumerate(items):
                        self._append_output(f"  📋 項目 {i+1}: {item}")
                
                self._append_output("")
                self._append_output("您可以使用上方的checkbox選擇檔案，或使用刪除按鈕進行操作")
            else:
                self._append_output("")
                self._append_output("✅ 沒有找到未引用的檔案")
                
                # 更新狀態標籤
                if hasattr(self, 'status_label'):
                    self.status_label.config(
                        text="未引用檔案列表 (沒有找到未引用檔案)",
                        foreground="green"
                    )
                
        except Exception as e:
            self._append_output(f"❌ 搜尋未引用檔案時發生錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _find_file_path(self, file_name: str, project_path: str) -> str:
        """根據檔案名尋找完整路徑"""
        try:
            # 方法1: 直接檢查完整路徑
            # 如果file_name已經是完整路徑，直接返回
            if os.path.isabs(file_name) and os.path.exists(file_name):
                return file_name
            
            # 方法2: 相對於專案路徑檢查
            relative_path = os.path.join(project_path, file_name)
            if os.path.exists(relative_path):
                return relative_path
            
            # 方法3: 在專案路徑下搜尋檔案（改進版本）
            # 首先嘗試精確匹配
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.lower() == os.path.basename(file_name).lower():
                        found_path = os.path.join(root, file)
                        # 檢查是否為圖片檔案
                        file_ext = os.path.splitext(file)[1].lower()
                        if file_ext in {'.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.tiff', '.tif', '.webp', '.ktx', '.pvr'}:
                            return found_path
            
            # 方法4: 處理相對路徑的情況
            # 如果file_name包含路徑分隔符，嘗試相對路徑匹配
            if '/' in file_name or '\\' in file_name:
                # 移除開頭的路徑分隔符
                clean_name = file_name.lstrip('/\\')
                relative_path = os.path.join(project_path, clean_name)
                if os.path.exists(relative_path):
                    return relative_path
                
                # 嘗試在子目錄中尋找
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        if file.lower() == os.path.basename(clean_name).lower():
                            found_path = os.path.join(root, file)
                            file_ext = os.path.splitext(file)[1].lower()
                            if file_ext in {'.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.tiff', '.tif', '.webp', '.ktx', '.pvr'}:
                                return found_path
            
            # 方法5: 處理子目錄中的檔案
            # 如果檔案在子目錄中，嘗試匹配子目錄路徑
            if '/' in file_name or '\\' in file_name:
                # 分割路徑
                path_parts = file_name.replace('\\', '/').split('/')
                if len(path_parts) > 1:
                    # 嘗試匹配子目錄結構
                    for root, dirs, files in os.walk(project_path):
                        for file in files:
                            if file.lower() == path_parts[-1].lower():
                                found_path = os.path.join(root, file)
                                file_ext = os.path.splitext(file)[1].lower()
                                if file_ext in {'.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.tiff', '.tif', '.webp', '.ktx', '.pvr'}:
                                    # 檢查路徑結構是否匹配
                                    relative_path = os.path.relpath(found_path, project_path)
                                    if relative_path.replace('\\', '/').lower() == file_name.replace('\\', '/').lower():
                                        return found_path
                                    
            # 方法6: 模糊匹配（最後手段）
            # 如果所有精確匹配都失敗，嘗試模糊匹配
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.lower() == os.path.basename(file_name).lower():
                        found_path = os.path.join(root, file)
                        file_ext = os.path.splitext(file)[1].lower()
                        if file_ext in {'.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.tiff', '.tif', '.webp', '.ktx', '.pvr'}:
                            return found_path
                                
        except Exception as e:
            print(f"路徑解析錯誤: {str(e)}")
        
        return None
    
    def _show_analysis_results_in_output(self, results, scanner):
        """在輸出視窗中顯示分析結果"""
        # 檢查是否有檔案被掃描到
        try:
            total_files = len(scanner.efk_files) + len(scanner.efkmat_files) + len(scanner.efkmodel_files)
            if total_files == 0:
                self._append_output("❌ 未找到任何EFK、EFKMAT或EFKMODEL檔案")
                return
            
            if not results:
                self._append_output(f"⚠️ 找到 {len(scanner.efk_files)} 個EFK檔案, {len(scanner.efkmat_files)} 個EFKMAT檔案, {len(scanner.efkmodel_files)} 個EFKMODEL檔案，但未解析出引用的檔案")
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
        self._append_output(f"總EFKMAT檔案數: {stats['total_efkmat_files']}")
        self._append_output(f"總EFKMODEL檔案數: {stats['total_efkmodel_files']}")
        self._append_output(f"已分析檔案數: {stats['analyzed_efk_files']}")
        self._append_output(f"總引用檔案數: {stats['total_referenced_files']}")
        self._append_output("")
        
        # 顯示詳細結果
        if results:
            self._append_output("=== 詳細結果 ===")
            for file_path, referenced_files in results.items():
                # 提取檔案名和類型
                file_name = os.path.basename(file_path)
                file_ext = os.path.splitext(file_name)[1].lower()
                
                if file_ext == '.efk':
                    file_type = "EFK檔案"
                elif file_ext == '.efkmat':
                    file_type = "EFKMAT檔案"
                elif file_ext == '.efkmodel':
                    file_type = "EFKMODEL檔案"
                else:
                    file_type = "檔案"
                
                self._append_output(f"📁 {file_type}: {file_name}")
                self._append_output(f"   完整路徑: {file_path}")
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
        """運行主視窗"""
        self.root.mainloop()
    
    def get_selected_path(self) -> str:
        """取得選擇的路徑"""
        return self.selected_path.get()
    
    def _format_file_size(self, size_bytes: int) -> str:
        """格式化檔案大小顯示"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def _create_context_menu(self, widget, file_path: str):
        """為檔案項目創建右鍵選單"""
        try:
            context_menu = tk.Menu(widget, tearoff=0)
            
            # 添加選單項目
            context_menu.add_command(
                label="🗑️ 刪除檔案",
                command=lambda: self._delete_single_file(file_path)
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="📁 在檔案總管中開啟",
                command=lambda: self._open_in_explorer(file_path)
            )
            context_menu.add_command(
                label="📋 複製檔案路徑",
                command=lambda: self._copy_file_path(file_path)
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="ℹ️ 檔案資訊",
                command=lambda: self._show_file_info(file_path)
            )
            
            # 綁定右鍵事件
            widget.bind("<Button-3>", lambda e: self._show_context_menu(e, context_menu))
            
            # 為子元件也綁定右鍵事件
            try:
                for child in widget.winfo_children():
                    if child.winfo_exists():
                        child.bind("<Button-3>", lambda e: self._show_context_menu(e, context_menu))
            except Exception as e:
                print(f"綁定子元件右鍵事件時發生錯誤: {str(e)}")
                
        except Exception as e:
            print(f"創建右鍵選單時發生錯誤: {str(e)}")
    
    def _show_context_menu(self, event, menu):
        """顯示右鍵選單"""
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _open_in_explorer(self, file_path: str):
        """在檔案總管中開啟檔案"""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.run(["explorer", "/select,", file_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "-R", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", os.path.dirname(file_path)])
            
            self._append_output(f"✅ 已在檔案總管中開啟: {file_path}")
        except Exception as e:
            self._append_output(f"❌ 無法在檔案總管中開啟: {file_path} - {str(e)}")
    
    def _copy_file_path(self, file_path: str):
        """複製檔案路徑到剪貼簿"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(file_path)
            self._append_output(f"✅ 已複製檔案路徑到剪貼簿: {file_path}")
        except Exception as e:
            self._append_output(f"❌ 無法複製檔案路徑: {str(e)}")
    
    def _show_file_info(self, file_path: str):
        """顯示檔案資訊"""
        try:
            import stat
            from datetime import datetime
            
            stat_info = os.stat(file_path)
            
            # 檔案大小
            size = stat_info.st_size
            size_text = self._format_file_size(size)
            
            # 修改時間
            mtime = datetime.fromtimestamp(stat_info.st_mtime)
            mtime_text = mtime.strftime("%Y-%m-%d %H:%M:%S")
            
            # 檔案權限
            permissions = stat.filemode(stat_info.st_mode)
            
            info_text = f"""檔案資訊:
路徑: {file_path}
大小: {size_text}
修改時間: {mtime_text}
權限: {permissions}"""
            
            messagebox.showinfo("檔案資訊", info_text)
            
        except Exception as e:
            messagebox.showerror("錯誤", f"無法取得檔案資訊: {str(e)}")
    
    def _start_progress(self, message: str = "處理中..."):
        """開始進度條動畫"""
        if hasattr(self, 'progress_bar') and self.progress_bar.winfo_exists():
            self.progress_bar.start(10)
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=message, foreground="blue")
    
    def _stop_progress(self, message: str = "完成"):
        """停止進度條動畫"""
        if hasattr(self, 'progress_bar') and self.progress_bar.winfo_exists():
            self.progress_bar.stop()
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=message, foreground="green")
    
    def _update_status(self, message: str, color: str = "black"):
        """更新狀態標籤"""
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=message, foreground=color)
    
 