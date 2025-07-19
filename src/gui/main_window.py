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
        self.root.geometry("1000x800")  # 調整視窗大小：增加寬度和高度
        
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
        
        # 新增統計追蹤變數
        self.total_unused_count = 0
        self.total_unused_size = 0
        self.remaining_count = 0
        self.remaining_size = 0
        self.deleted_files = set()
        
        # 設定UI
        self._setup_ui()
        
        # 設定進度條樣式為綠色
        self._setup_progress_style()
        
        # 確保視窗被正確顯示
        self.root.update()
        self.root.deiconify()  # 確保視窗可見
    
    def _setup_progress_style(self):
        """設定進度條樣式為綠色"""
        try:
            self.style = ttk.Style()
            
            # 嘗試不同的主題來支援自訂顏色
            available_themes = self.style.theme_names()
            print(f"可用主題: {available_themes}")
            
            # 優先選擇支援自訂顏色的主題
            if 'alt' in available_themes:
                self.style.theme_use('alt')
            elif 'clam' in available_themes:
                self.style.theme_use('clam')
            elif 'default' in available_themes:
                self.style.theme_use('default')
            
            # 設定綠色進度條樣式
            self.style.configure("Green.Horizontal.TProgressbar",
                          background='#4CAF50',      # 進度條填充顏色（綠色）
                          troughcolor='#E8E8E8',     # 背景軌道顏色（淺灰）
                          borderwidth=1,
                          lightcolor='#66BB6A',      # 高亮顏色（淺綠）
                          darkcolor='#2E7D32',       # 陰影顏色（深綠）
                          focuscolor='#4CAF50')      # 焦點顏色
            
            # 設定進度條狀態樣式
            self.style.map("Green.Horizontal.TProgressbar",
                          background=[('active', '#66BB6A'),    # 活動狀態
                                    ('disabled', '#CCCCCC')])   # 禁用狀態
            
            print(f"已設定綠色進度條樣式")
            
        except Exception as e:
            print(f"設定進度條樣式時發生錯誤: {str(e)}")
    
    def _apply_progress_style(self):
        """應用綠色樣式到進度條"""
        try:
            if hasattr(self, 'progress_bar') and hasattr(self, 'style'):
                self.progress_bar.configure(style="Green.Horizontal.TProgressbar")
                print(f"已應用綠色樣式到進度條")
        except Exception as e:
            print(f"應用進度條樣式時發生錯誤: {str(e)}")
    
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
        
        # 自訂綠色進度條 - 使用 Canvas 確保顏色正確
        self.progress_frame = tk.Frame(unused_frame, height=25, bg='white')
        self.progress_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.progress_frame.grid_propagate(False)
        
        self.progress_canvas = tk.Canvas(
            self.progress_frame,
            height=20,
            bg='#E8E8E8',  # 淺灰色背景
            highlightthickness=1,
            highlightbackground='#CCCCCC'
        )
        self.progress_canvas.pack(fill='both', expand=True, padx=2, pady=2)
        
        # 初始化進度條變數
        self.progress_value = 0
        self.progress_max = 100
        
        # 綁定畫布大小改變事件
        self.progress_canvas.bind('<Configure>', self._on_progress_canvas_configure)
        
        # 狀態標籤
        self.status_label = ttk.Label(
            unused_frame,
            text="準備就緒",
            foreground="gray"
        )
        self.status_label.grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        # 重新設計的檔案列表 - 使用簡單的Listbox，調整高度以顯示至少4條內容
        self.unused_listbox = tk.Listbox(
            unused_frame,
            height=12,  # 增加高度，確保能顯示至少4條內容的預設高度
            selectmode=tk.EXTENDED,
            font=("Consolas", 9)
        )
        self.unused_listbox.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        # 綁定選擇事件來處理已刪除檔案的選擇限制
        self.unused_listbox.bind("<<ListboxSelect>>", self._on_listbox_select)
        
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
        
        # 統計資訊框架 - 在按鈕下方
        stats_frame = ttk.Frame(unused_frame)
        stats_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        # 統計標籤
        self.stats_label = ttk.Label(
            stats_frame,
            text="統計資訊：等待分析...",
            font=("Consolas", 9),
            foreground="gray"
        )
        self.stats_label.grid(row=0, column=0, sticky="w")
        
        # 選中檔案統計標籤
        self.selection_stats_label = ttk.Label(
            stats_frame,
            text="",
            font=("Consolas", 9),
            foreground="blue"
        )
        self.selection_stats_label.grid(row=1, column=0, sticky="w")
        
        # 輸出視窗區域
        output_frame = ttk.LabelFrame(main_frame, text="分析結果輸出", padding="10")
        output_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # 建立文字區域和捲軸
        self.output_text = tk.Text(output_frame, wrap=tk.WORD, height=18, font=("Consolas", 9))
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
            # 只清除未引用檔案列表，保留路徑選擇
            self._clear_unused_files_list()
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
        """添加文字到輸出視窗，根據訊息類型自動選擇顏色"""
        # 配置顏色標籤（如果尚未配置）
        self._configure_output_colors()
        
        # 根據訊息內容判斷顏色
        color_tag = self._get_message_color_tag(text)
        
        if color_tag:
            # 插入帶顏色的文字
            start_pos = self.output_text.index(tk.END + "-1c")  # 取得當前結束位置
            self.output_text.insert(tk.END, text + "\n", color_tag)  # 直接在插入時應用標籤
        else:
            # 插入普通文字
            self.output_text.insert(tk.END, text + "\n")
        
        self.output_text.see(tk.END)  # 自動捲動到底部
        self.root.update()  # 更新GUI
    
    def _configure_output_colors(self):
        """配置輸出視窗的顏色標籤"""
        if not hasattr(self, '_colors_configured'):
            # 成功訊息 - 綠色 (使用更明顯的顏色)
            self.output_text.tag_configure("success", 
                                         foreground="green",
                                         font=("Consolas", 9, "normal"))
            
            # 失敗訊息 - 紅色 (使用更明顯的顏色)
            self.output_text.tag_configure("error", 
                                         foreground="red",
                                         font=("Consolas", 9, "normal"))
            
            # 警告訊息 - 橙色 (使用更明顯的顏色)
            self.output_text.tag_configure("warning", 
                                         foreground="orange",
                                         font=("Consolas", 9, "normal"))
            
            # 資訊訊息 - 藍色 (使用更明顯的顏色)
            self.output_text.tag_configure("info", 
                                         foreground="blue",
                                         font=("Consolas", 9, "normal"))
            
            # 設定標籤優先級（確保我們的標籤在最上層）
            self.output_text.tag_raise("success")
            self.output_text.tag_raise("error") 
            self.output_text.tag_raise("warning")
            self.output_text.tag_raise("info")
            
            # 強制更新配置
            self.output_text.update()
            
            # 標記已配置
            self._colors_configured = True
    
    def _get_message_color_tag(self, text):
        """根據訊息內容判斷應該使用的顏色標籤"""
        # 警告訊息 - 橙色 (優先檢查，避免被錯誤訊息攔截)
        if any(indicator in text for indicator in ["⚠️", "警告", "無法解析", "UI更新失敗"]) or (text.startswith("⚠️") and "檔案不存在" in text):
            return "warning"
        
        # 成功訊息 - 綠色
        elif any(indicator in text for indicator in ["✅", "成功", "完成", "已刪除檔案", "已在檔案總管中開啟", "已複製檔案路徑", "沒有找到未引用的檔案"]):
            return "success"
        
        # 失敗訊息 - 紅色  
        elif any(indicator in text for indicator in ["❌", "失敗", "錯誤", "無法", "不存在", "未找到任何EFK", "刪除檔案失敗", "檢查結果時發生錯誤"]):
            return "error"
        
        # 資訊訊息 - 藍色
        elif any(indicator in text for indicator in ["🔍", "📊", "📁", "📄", "📋", "==="]):
            return "info"
        
        # 默認不使用顏色
        return None
    
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
            
            # 重置統計變數
            self.total_unused_count = 0
            self.total_unused_size = 0
            self.remaining_count = 0
            self.remaining_size = 0
            self.deleted_files = set()
            
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
            
            # 重置統計標籤
            if hasattr(self, 'stats_label') and self.stats_label.winfo_exists():
                self.stats_label.config(
                    text="統計資訊：等待分析...",
                    foreground="gray"
                )
            
            if hasattr(self, 'selection_stats_label') and self.selection_stats_label.winfo_exists():
                self.selection_stats_label.config(text="")
                
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
            
            # 初始化file_delete_buttons如果不存在
            if not hasattr(self, 'file_delete_buttons'):
                self.file_delete_buttons = {}
            
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
            
            # 更新統計資訊
            self._update_stats_display()
            
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
                
                # 將檔案標記為已刪除
                self.deleted_files.add(file_path)
                
                # 檢查GUI元件是否已經初始化
                if not hasattr(self, 'unused_listbox') or not self.unused_listbox.winfo_exists():
                    self._append_output(f"✅ 已刪除檔案: {file_path}")
                    self._update_stats_display()
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
                if hasattr(self, 'file_delete_buttons') and file_path in self.file_delete_buttons and self.file_delete_buttons[file_path].winfo_exists():
                    self.file_delete_buttons[file_path].config(state="disabled")
                
                self._append_output(f"✅ 已刪除檔案: {file_path}")
                
                # 更新統計資訊
                self._update_stats_display()
                self._update_selection_stats()
                
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
                # 檢查檔案是否存在
                if os.path.exists(file_path):
                    # 嘗試刪除檔案
                    os.remove(file_path)
                    deleted_count += 1
                    self._append_output(f"✅ 已刪除檔案: {file_path}")
                    
                    # 將檔案標記為已刪除
                    self.deleted_files.add(file_path)
                    
                    # 只有在GUI已初始化的情況下才更新UI
                    if hasattr(self, 'unused_listbox') and self.unused_listbox.winfo_exists():
                        try:
                            # 找到檔案在Listbox中的位置並更新顯示
                            self._update_deleted_file_display(file_path)
                        except Exception as ui_error:
                            # UI更新失敗不影響刪除統計
                            self._append_output(f"⚠️ UI更新失敗: {str(ui_error)}")
                else:
                    # 檔案不存在，不算失敗，因為可能已經被刪除了
                    self._append_output(f"⚠️ 檔案不存在: {file_path}")
            except Exception as e:
                failed_count += 1
                self._append_output(f"❌ 刪除檔案失敗: {file_path} - {str(e)}")
        
        self._append_output(f"✅ 批量刪除完成: 成功 {deleted_count} 個，失敗 {failed_count} 個")
        
        # 更新統計資訊
        self._update_stats_display()
        self._update_selection_stats()
    
    def _update_deleted_file_display(self, file_path: str):
        """更新已刪除檔案在Listbox中的顯示"""
        try:
            # 找到檔案在Listbox中的索引
            items = self.unused_listbox.get(0, tk.END)
            file_index = -1
            
            for i, item in enumerate(items):
                if item == file_path or item.endswith(file_path):
                    file_index = i
                    break
            
            if file_index >= 0:
                # 標記檔案為已刪除狀態
                if not hasattr(self, 'deleted_files'):
                    self.deleted_files = set()
                self.deleted_files.add(file_path)
                
                # 更新Listbox項目的顯示，添加已刪除標記和視覺效果
                self.unused_listbox.delete(file_index)
                deleted_display = f"🗑️ [已刪除] {os.path.basename(file_path)} - {os.path.dirname(file_path)}"
                self.unused_listbox.insert(file_index, deleted_display)
                
                # 清除該項目的選擇狀態
                self.unused_listbox.selection_clear(file_index)
                
                # 追蹤已刪除檔案的索引，防止重新選擇
                if not hasattr(self, 'disabled_items'):
                    self.disabled_items = set()
                self.disabled_items.add(file_index)
                
                # 嘗試設定該項目為灰色背景（如果支援的話）
                try:
                    self.unused_listbox.itemconfig(file_index, {'bg': '#E0E0E0', 'fg': '#808080'})
                except:
                    # 如果不支援itemconfig，則忽略
                    pass
                
                print(f"已更新檔案顯示: {file_path} (索引: {file_index})")
                
                # 更新統計資訊
                self._update_stats_display()
                self._update_selection_stats()
            
        except Exception as e:
            print(f"更新刪除檔案顯示時發生錯誤: {str(e)}")
    
    def _on_listbox_select(self, event):
        """處理Listbox選擇事件，防止選擇已刪除的檔案"""
        try:
            if hasattr(self, 'disabled_items'):
                # 取得當前選擇
                current_selection = list(self.unused_listbox.curselection())
                
                # 移除已刪除檔案的選擇
                valid_selection = []
                for index in current_selection:
                    if index not in self.disabled_items:
                        valid_selection.append(index)
                
                # 如果選擇有變化，更新選擇狀態
                if len(valid_selection) != len(current_selection):
                    self.unused_listbox.selection_clear(0, tk.END)
                    for index in valid_selection:
                        self.unused_listbox.selection_set(index)
            
            # 更新選擇統計資訊
            self._update_selection_stats()
            
        except Exception as e:
            print(f"處理Listbox選擇事件時發生錯誤: {str(e)}")
    
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
                # 檢查檔案是否存在
                if os.path.exists(file_path):
                    # 嘗試刪除檔案
                    os.remove(file_path)
                    deleted_count += 1
                    self._append_output(f"✅ 已刪除檔案: {file_path}")
                    
                    # 將檔案標記為已刪除
                    self.deleted_files.add(file_path)
                    
                    # 只有在GUI已初始化的情況下才更新UI
                    if gui_initialized:
                        try:
                            # 找到檔案在Listbox中的位置並更新顯示
                            self._update_deleted_file_display(file_path)
                        except Exception as ui_error:
                            # UI更新失敗不影響刪除統計
                            self._append_output(f"⚠️ UI更新失敗: {str(ui_error)}")
                else:
                    # 檔案不存在，不算失敗，因為可能已經被刪除了
                    self._append_output(f"⚠️ 檔案不存在: {file_path}")
            except Exception as e:
                failed_count += 1
                self._append_output(f"❌ 刪除檔案失敗: {file_path} - {str(e)}")
        
        self._append_output(f"✅ 批量刪除完成: 成功 {deleted_count} 個，失敗 {failed_count} 個")
        
        # 更新統計資訊
        self._update_stats_display()
        self._update_selection_stats()
        
        # 更新統計資訊
        self._update_stats_display()
        self._update_selection_stats()
    
    def _find_unused_files(self, referenced_files: Set[str], project_path: str) -> List[str]:
        """找出未被引用的檔案"""
        unused_files = []
        
        try:
            # 擴展檔案類型，包含圖片檔案和效果檔案
            target_extensions = {
                # 圖片檔案
                '.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.tiff', '.tif', '.webp', '.ktx', '.pvr',
                # 效果檔案
                '.efkmat', '.efkmodel'
            }
            
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    # 檢查是否為目標檔案類型
                    if file_ext in target_extensions:
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
            # 開始進度條 - 0%
            self._start_progress("正在準備分析...")
            
            # 清除輸出視窗和未引用檔案列表
            self._clear_output()
            self._clear_unused_files_list()
            self._append_output("=== EFK檔案分析開始 ===")
            self._append_output(f"掃描路徑: {self.selected_path.get()}")
            self._append_output("")
            
            # 進度 10% - 初始化掃描器
            self._update_progress(10, "正在初始化掃描器")
            
            # 使用預設的圖片類型集合
            default_image_types = {"png", "jpg", "jpeg", "tga", "dds", "bmp", "tiff", "tif", "webp", "ktx", "pvr"}
            scanner = EFKScanner(self.selected_path.get(), default_image_types)
            
            # 顯示進度訊息
            self._append_output("正在掃描EFK檔案...")
            self._append_output("請稍候，分析進行中...")
            self._append_output("")
            
            # 進度 30% - 開始掃描EFK檔案
            self._update_progress(30, "正在掃描EFK檔案")
            
            # 執行掃描
            results = scanner.scan_efk_files()
            
            # 進度 60% - 處理掃描結果
            self._update_progress(60, "正在處理掃描結果")
            
            # 顯示結果
            self._show_analysis_results_in_output(results, scanner)
            
            # 進度 80% - 查找未引用檔案
            self._update_progress(80, "正在查找未引用檔案")
            
            # 找出未引用的檔案
            self._find_and_display_unused_files(results, scanner)
            
            # 進度 100% - 分析完成
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
        """找出並顯示未引用的檔案 - 修正邏輯16: 考慮目錄範圍限制"""
        try:
            # 收集所有被引用的檔案路徑 - 新增目錄範圍檢查
            referenced_files = set()
            
            # 方法1: 從掃描結果中收集引用檔案，但要檢查目錄範圍
            for efk_file, ref_files in results.items():
                efk_dir = os.path.dirname(efk_file)  # EFK檔案所在的目錄
                
                for ref_file in ref_files:
                    # 嘗試找到檔案的完整路徑
                    full_path = self._find_file_path_in_directory(ref_file, efk_dir)
                    if full_path:
                        # 檢查引用檔案是否在同一個目錄下（或其子目錄）
                        if self._is_in_same_directory_scope(efk_file, full_path):
                            referenced_files.add(full_path)
                            self._append_output(f"🔍 找到同目錄引用檔案: {ref_file} -> {full_path}")
                        else:
                            self._append_output(f"⚠️  跨目錄引用（忽略）: {ref_file} -> {full_path}")
                    else:
                        # 如果在EFK檔案目錄找不到，嘗試在整個專案中找
                        full_path = self._find_file_path(ref_file, self.selected_path.get())
                        if full_path and self._is_in_same_directory_scope(efk_file, full_path):
                            referenced_files.add(full_path)
                            self._append_output(f"🔍 找到引用檔案: {ref_file} -> {full_path}")
                        else:
                            self._append_output(f"⚠️  無法解析引用檔案或跨目錄: {ref_file}")
            
            # 方法2: 直接從掃描器獲取所有檔案
            all_files_in_project = set()
            # 擴展檔案類型，包含圖片檔案和效果檔案
            target_extensions = {
                # 圖片檔案
                '.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.tiff', '.tif', '.webp', '.ktx', '.pvr',
                # 效果檔案
                '.efkmat', '.efkmodel'
            }
            
            for root, dirs, files in os.walk(self.selected_path.get()):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    # 檢查是否為目標檔案類型
                    if file_ext in target_extensions:
                        all_files_in_project.add(file_path)
            
            self._append_output(f"📊 專案中總共有 {len(all_files_in_project)} 個目標檔案（圖片 + 效果檔案）")
            self._append_output(f"📊 被引用的檔案（同目錄範圍）: {len(referenced_files)} 個")
            
            # 方法3: 改進的未引用檔案檢查 - 加入目錄範圍限制
            unused_files = []
            for file_path in all_files_in_project:
                is_referenced = False
                
                # 檢查是否在引用檔案列表中（已經過目錄範圍檢查）
                if file_path in referenced_files:
                    is_referenced = True
                else:
                    # 進一步檢查檔案名匹配，但仍要考慮目錄範圍
                    file_name = os.path.basename(file_path)
                    file_dir = os.path.dirname(file_path)
                    
                    for ref_path in referenced_files:
                        if os.path.basename(ref_path).lower() == file_name.lower():
                            # 檢查是否在相同的目錄範圍內
                            if self._is_in_same_directory_scope(file_path, ref_path):
                                is_referenced = True
                                break
                    
                    # 檢查相對路徑是否被引用（同樣考慮目錄範圍）
                    if not is_referenced:
                        relative_path = os.path.relpath(file_path, self.selected_path.get())
                        for efk_file, ref_files_list in results.items():
                            efk_dir = os.path.dirname(efk_file)
                            for ref_file in ref_files_list:
                                if ref_file.replace('\\', '/').lower() == relative_path.replace('\\', '/').lower():
                                    # 檢查是否在同一個目錄範圍
                                    if self._is_in_same_directory_scope(efk_file, file_path):
                                        is_referenced = True
                                        break
                            if is_referenced:
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
        """根據檔案名尋找完整路徑 - 修復跨目錄引用問題"""
        try:
            # 方法1: 直接檢查完整路徑
            if os.path.isabs(file_name) and os.path.exists(file_name):
                return file_name
            
            # 方法2: 相對於專案路徑檢查
            relative_path = os.path.join(project_path, file_name)
            if os.path.exists(relative_path):
                return relative_path
            
            # 方法3: 改進的檔案搜尋 - 優先考慮路徑結構匹配
            if '/' in file_name or '\\' in file_name:
                # 如果引用包含路徑，嘗試精確匹配路徑結構
                clean_name = file_name.replace('\\', '/').strip('/')
                
                # 在專案路徑下搜尋匹配的檔案結構
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_to_project = os.path.relpath(file_path, project_path)
                        relative_normalized = relative_to_project.replace('\\', '/')
                        
                        # 精確匹配相對路徑
                        if relative_normalized.lower() == clean_name.lower():
                            return file_path
                        
                        # 檢查末尾匹配（處理部分路徑的情況）
                        if relative_normalized.lower().endswith(clean_name.lower()):
                            # 確保是完整的檔案路徑匹配，而不是部分字串匹配
                            parts = clean_name.split('/')
                            rel_parts = relative_normalized.split('/')
                            if len(parts) <= len(rel_parts):
                                if rel_parts[-len(parts):] == [p.lower() for p in parts]:
                                    return file_path
            
            # 方法4: 檔案名精確匹配 - 改進版
            target_filename = os.path.basename(file_name).lower()
            target_ext = os.path.splitext(target_filename)[1]
            
            # 只搜尋相同副檔名的檔案
            valid_extensions = {'.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.tiff', '.tif', '.webp', '.ktx', '.pvr', '.efkmat', '.efkmodel'}
            
            if target_ext in valid_extensions:
                matches = []
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        if file.lower() == target_filename:
                            file_path = os.path.join(root, file)
                            matches.append(file_path)
                
                # 如果只有一個匹配，直接返回
                if len(matches) == 1:
                    return matches[0]
                
                # 如果有多個匹配，優先選擇路徑結構相似的
                if len(matches) > 1 and ('/' in file_name or '\\' in file_name):
                    file_dir_parts = file_name.replace('\\', '/').split('/')[:-1]  # 除了檔案名的目錄部分
                    
                    best_match = None
                    max_common_parts = 0
                    
                    for match in matches:
                        match_rel = os.path.relpath(match, project_path)
                        match_dir_parts = match_rel.replace('\\', '/').split('/')[:-1]
                        
                        # 計算共同的路徑部分
                        common_parts = 0
                        min_len = min(len(file_dir_parts), len(match_dir_parts))
                        for i in range(min_len):
                            if file_dir_parts[-(i+1)].lower() == match_dir_parts[-(i+1)].lower():
                                common_parts += 1
                            else:
                                break
                        
                        if common_parts > max_common_parts:
                            max_common_parts = common_parts
                            best_match = match
                    
                    if best_match:
                        return best_match
                
                # 如果沒有最佳匹配，返回第一個
                if matches:
                    return matches[0]
            
            # 方法5: 模糊檔案名匹配（處理檔案名可能有輕微差異的情況）
            base_name = os.path.splitext(os.path.basename(file_name))[0].lower()
            base_ext = os.path.splitext(os.path.basename(file_name))[1].lower()
            
            if base_ext in valid_extensions and len(base_name) > 2:
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        file_base = os.path.splitext(file)[0].lower()
                        file_ext = os.path.splitext(file)[1].lower()
                        
                        # 相同副檔名且檔案名相似
                        if file_ext == base_ext and file_base == base_name:
                            return os.path.join(root, file)
                                
        except Exception as e:
            print(f"路徑解析錯誤: {str(e)}")
        
        return None
    
    def _find_file_path_in_directory(self, file_name: str, directory_path: str) -> str:
        """在特定目錄下尋找檔案的完整路徑"""
        try:
            # 方法1: 直接檢查完整路徑
            if os.path.isabs(file_name) and os.path.exists(file_name):
                return file_name
            
            # 方法2: 相對於目錄檢查
            relative_path = os.path.join(directory_path, file_name)
            if os.path.exists(relative_path):
                return relative_path
            
            # 方法3: 改進的檔案搜尋 - 優先考慮路徑結構匹配
            if '/' in file_name or '\\' in file_name:
                # 如果引用包含路徑，嘗試精確匹配路徑結構
                clean_name = file_name.replace('\\', '/').strip('/')
                
                # 在目錄下搜尋匹配的檔案結構
                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_to_dir = os.path.relpath(file_path, directory_path)
                        relative_normalized = relative_to_dir.replace('\\', '/')
                        
                        # 精確匹配相對路徑
                        if relative_normalized.lower() == clean_name.lower():
                            return file_path
                        
                        # 檢查末尾匹配（處理部分路徑的情況）
                        if relative_normalized.lower().endswith(clean_name.lower()):
                            # 確保是完整的檔案路徑匹配，而不是部分字串匹配
                            parts = clean_name.split('/')
                            rel_parts = relative_normalized.split('/')
                            if len(parts) <= len(rel_parts):
                                if rel_parts[-len(parts):] == [p.lower() for p in parts]:
                                    return file_path
            
            # 方法4: 檔案名精確匹配 - 改進版
            target_filename = os.path.basename(file_name).lower()
            target_ext = os.path.splitext(target_filename)[1]
            
            # 只搜尋相同副檔名的檔案
            valid_extensions = {'.png', '.jpg', '.jpeg', '.tga', '.dds', '.bmp', '.tiff', '.tif', '.webp', '.ktx', '.pvr', '.efkmat', '.efkmodel'}
            
            if target_ext in valid_extensions:
                matches = []
                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        if file.lower() == target_filename:
                            file_path = os.path.join(root, file)
                            matches.append(file_path)
                
                # 如果只有一個匹配，直接返回
                if len(matches) == 1:
                    return matches[0]
                
                # 如果有多個匹配，優先選擇路徑結構相似的
                if len(matches) > 1 and ('/' in file_name or '\\' in file_name):
                    file_dir_parts = file_name.replace('\\', '/').split('/')[:-1]  # 除了檔案名的目錄部分
                    
                    best_match = None
                    max_common_parts = 0
                    
                    for match in matches:
                        match_rel = os.path.relpath(match, directory_path)
                        match_dir_parts = match_rel.replace('\\', '/').split('/')[:-1]
                        
                        # 計算共同的路徑部分
                        common_parts = 0
                        min_len = min(len(file_dir_parts), len(match_dir_parts))
                        for i in range(min_len):
                            if file_dir_parts[-(i+1)].lower() == match_dir_parts[-(i+1)].lower():
                                common_parts += 1
                            else:
                                break
                        
                        if common_parts > max_common_parts:
                            max_common_parts = common_parts
                            best_match = match
                    
                    if best_match:
                        return best_match
                
                # 如果沒有最佳匹配，返回第一個
                if matches:
                    return matches[0]
            
            # 方法5: 模糊檔案名匹配（處理檔案名可能有輕微差異的情況）
            base_name = os.path.splitext(os.path.basename(file_name))[0].lower()
            base_ext = os.path.splitext(os.path.basename(file_name))[1].lower()
            
            if base_ext in valid_extensions and len(base_name) > 2:
                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        file_base = os.path.splitext(file)[0].lower()
                        file_ext = os.path.splitext(file)[1].lower()
                        
                        # 相同副檔名且檔案名相似
                        if file_ext == base_ext and file_base == base_name:
                            return os.path.join(root, file)
                                
        except Exception as e:
            print(f"路徑解析錯誤: {str(e)}")
        
        return None
    
    def _is_in_same_directory_scope(self, efk_file_path: str, ref_file_path: str) -> bool:
        """檢查引用檔案是否在EFK檔案所在的目錄範圍內"""
        try:
            efk_dir = os.path.dirname(efk_file_path)
            ref_dir = os.path.dirname(ref_file_path)
            
            # 標準化路徑
            efk_dir = os.path.normpath(efk_dir)
            ref_dir = os.path.normpath(ref_dir)
            
            # 檢查兩種情況：
            # 1. 引用檔案在相同目錄
            # 2. 引用檔案在EFK檔案目錄的子目錄中
            if efk_dir == ref_dir:
                return True
            
            # 檢查引用檔案是否在EFK檔案目錄的子目錄中
            rel_path = os.path.relpath(ref_dir, efk_dir)
            # 如果相對路徑不以 '..' 開始，表示是子目錄或當前目錄
            return not rel_path.startswith('..')
            
        except Exception as e:
            print(f"檢查目錄範圍時發生錯誤: {str(e)}")
            return False
    
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
    
    def _get_file_size(self, file_path: str) -> int:
        """獲取檔案大小（位元組）"""
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
            else:
                return 0
        except Exception:
            return 0
    
    def _calculate_total_stats(self):
        """計算總統計資訊"""
        try:
            self.total_unused_count = len(self.unused_files)
            self.total_unused_size = 0
            self.remaining_count = 0
            self.remaining_size = 0
            
            for file_path in self.unused_files:
                file_size = self._get_file_size(file_path)
                self.total_unused_size += file_size
                
                # 如果檔案未被刪除，計入剩餘統計
                if file_path not in self.deleted_files:
                    self.remaining_count += 1
                    self.remaining_size += file_size
                    
        except Exception as e:
            print(f"計算統計資訊時發生錯誤: {str(e)}")
    
    def _update_stats_display(self):
        """更新統計資訊顯示"""
        try:
            if not hasattr(self, 'stats_label') or not self.stats_label.winfo_exists():
                return
                
            # 計算最新統計
            self._calculate_total_stats()
            
            # 格式化統計文字
            total_size_text = self._format_file_size(self.total_unused_size)
            remaining_size_text = self._format_file_size(self.remaining_size)
            deleted_count = self.total_unused_count - self.remaining_count
            
            stats_text = (
                f"統計：總數 {self.total_unused_count} 個 ({total_size_text}) | "
                f"剩餘 {self.remaining_count} 個 ({remaining_size_text}) | "
                f"已刪除 {deleted_count} 個"
            )
            
            self.stats_label.config(text=stats_text, foreground="black")
            
        except Exception as e:
            print(f"更新統計顯示時發生錯誤: {str(e)}")
    
    def _update_selection_stats(self):
        """更新選中檔案統計資訊"""
        try:
            if not hasattr(self, 'selection_stats_label') or not self.selection_stats_label.winfo_exists():
                return
                
            if not hasattr(self, 'unused_listbox') or not self.unused_listbox.winfo_exists():
                return
                
            selected_indices = self.unused_listbox.curselection()
            
            if not selected_indices:
                self.selection_stats_label.config(text="")
                return
            
            selected_count = 0
            selected_size = 0
            valid_selections = []
            
            for index in selected_indices:
                try:
                    file_path = self.unused_listbox.get(index)
                    
                    # 跳過已刪除的檔案（檢查檔案路徑是否包含已刪除標記）
                    if "🗑️ [已刪除]" in file_path:
                        continue
                        
                    # 檢查檔案是否在已刪除列表中
                    original_path = file_path
                    for unused_file in self.unused_files:
                        if unused_file.endswith(os.path.basename(file_path)) or unused_file == file_path:
                            original_path = unused_file
                            break
                    
                    if original_path not in self.deleted_files:
                        selected_count += 1
                        selected_size += self._get_file_size(original_path)
                        valid_selections.append(original_path)
                        
                except Exception as e:
                    print(f"處理選中項目時發生錯誤: {str(e)}")
                    continue
            
            if selected_count > 0:
                size_text = self._format_file_size(selected_size)
                selection_text = f"已選擇：{selected_count} 個檔案 ({size_text})"
                self.selection_stats_label.config(text=selection_text, foreground="blue")
            else:
                self.selection_stats_label.config(text="")
                
        except Exception as e:
            print(f"更新選擇統計時發生錯誤: {str(e)}")
    
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
        """在檔案總管中開啟並選中檔案 - 改進版"""
        try:
            import subprocess
            import platform
            
            # 修正路徑格式
            normalized_path = os.path.normpath(file_path)
            
            # 檢查檔案是否存在
            if not os.path.exists(normalized_path):
                # 嘗試其他路徑格式
                alt_path1 = file_path.replace('/', '\\')
                alt_path2 = file_path.replace('\\', '/')
                
                if os.path.exists(alt_path1):
                    normalized_path = alt_path1
                elif os.path.exists(alt_path2):
                    normalized_path = alt_path2
                else:
                    self._append_output(f"❌ 檔案不存在: {file_path}")
                    return
            
            # 取得檔案所在的資料夾路徑
            folder_path = os.path.dirname(normalized_path)
            
            if platform.system() == "Windows":
                # 嘗試多種方法來選中檔案
                select_methods = [
                    # 方法1: 標準 /select 方法（最常用）
                    ["explorer", "/select,", normalized_path],
                    # 方法2: 無逗號的 /select 方法
                    ["explorer", "/select", normalized_path],
                    # 方法3: 詳細的 /e,/select 方法
                    ["explorer", "/e,/select,", normalized_path]
                ]
                
                success = False
                for i, cmd in enumerate(select_methods, 1):
                    try:
                        # 不捕獲輸出，讓 explorer 正常執行
                        subprocess.run(cmd, timeout=3)
                        self._append_output(f"✅ 已在檔案總管中開啟並選中檔案: {normalized_path}")
                        success = True
                        break
                    except subprocess.TimeoutExpired:
                        # 超時也算成功，因為 explorer 可能還在運行
                        self._append_output(f"✅ 已在檔案總管中開啟並選中檔案: {normalized_path}")
                        success = True
                        break
                    except Exception as e:
                        # 繼續嘗試下一個方法
                        continue
                
                # 如果所有選中方法都失敗，回退到開啟資料夾
                if not success:
                    try:
                        subprocess.run(["explorer", folder_path], timeout=3)
                        self._append_output(f"⚠️ 無法選中檔案，已開啟資料夾: {folder_path}")
                    except Exception as e:
                        self._append_output(f"❌ 無法開啟檔案總管: {str(e)}")
                        
            elif platform.system() == "Darwin":  # macOS
                try:
                    subprocess.run(["open", "-R", normalized_path], timeout=3)
                    self._append_output(f"✅ 已在Finder中開啟並選中檔案: {normalized_path}")
                except Exception as e:
                    subprocess.run(["open", folder_path])
                    self._append_output(f"⚠️ 無法選中檔案，已開啟資料夾: {folder_path}")
                    
            else:  # Linux
                try:
                    # Linux上沒有標準的選中方法，直接開啟資料夾
                    subprocess.run(["xdg-open", folder_path], timeout=3)
                    self._append_output(f"✅ 已在檔案管理器中開啟資料夾: {folder_path}")
                except Exception as e:
                    self._append_output(f"❌ 無法開啟檔案管理器: {str(e)}")
                    
        except Exception as e:
            self._append_output(f"❌ 檔案總管操作失敗: {file_path} - {str(e)}")
    
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
        """開始進度條 - 重置為0%"""
        self.progress_value = 0
        self._draw_progress()
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=message, foreground="blue")
    
    def _update_progress(self, value: float, message: str = ""):
        """更新進度條值 (0-100)"""
        self.progress_value = min(max(value, 0), 100)  # 確保值在0-100範圍內
        self._draw_progress()
        if message and hasattr(self, 'status_label') and self.status_label.winfo_exists():
            percentage = min(max(value, 0), 100)
            display_message = f"{message} ({percentage:.1f}%)"
            self.status_label.config(text=display_message, foreground="blue")
    
    def _stop_progress(self, message: str = "完成"):
        """完成進度條 - 設為100%"""
        self.progress_value = 100
        self._draw_progress()
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=message, foreground="green")
    
    def _draw_progress(self):
        """繪製自訂的綠色進度條"""
        try:
            if hasattr(self, 'progress_canvas') and self.progress_canvas.winfo_exists():
                # 清除畫布
                self.progress_canvas.delete("all")
                
                # 獲取畫布尺寸
                canvas_width = self.progress_canvas.winfo_width()
                canvas_height = self.progress_canvas.winfo_height()
                
                # 如果畫布還沒有渲染，使用預設尺寸
                if canvas_width <= 1:
                    canvas_width = 300
                    canvas_height = 20
                
                # 計算進度條寬度
                progress_width = int((self.progress_value / self.progress_max) * canvas_width)
                
                # 繪製背景（灰色軌道）
                self.progress_canvas.create_rectangle(
                    0, 0, canvas_width, canvas_height,
                    fill='#E8E8E8', outline='#CCCCCC', width=1
                )
                
                # 繪製進度（綠色填充）
                if progress_width > 0:
                    self.progress_canvas.create_rectangle(
                        0, 0, progress_width, canvas_height,
                        fill='#4CAF50', outline='#4CAF50', width=0
                    )
                
                # 添加漸層效果（可選）
                if progress_width > 2:
                    # 頂部高亮
                    self.progress_canvas.create_rectangle(
                        0, 0, progress_width, 2,
                        fill='#66BB6A', outline='#66BB6A', width=0
                    )
                    # 底部陰影
                    self.progress_canvas.create_rectangle(
                        0, canvas_height-2, progress_width, canvas_height,
                        fill='#388E3C', outline='#388E3C', width=0
                    )
                
                # 強制更新畫布
                self.progress_canvas.update()
                
        except Exception as e:
            print(f"繪製進度條時發生錯誤: {str(e)}")
    
    def _on_progress_canvas_configure(self, event):
        """當進度條畫布大小改變時重新繪製"""
        self._draw_progress()
    
    def _update_status(self, message: str, color: str = "black"):
        """更新狀態標籤"""
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=message, foreground=color)
    
 