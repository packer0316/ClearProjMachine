import logging
import os
from datetime import datetime
from pathlib import Path


class ScannerLogger:
    """掃描器日誌工具"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 設定日誌格式
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # 建立日誌檔案名稱
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"scanner_{timestamp}.log"
        
        # 設定日誌配置
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def info(self, message: str):
        """記錄資訊訊息"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """記錄警告訊息"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """記錄錯誤訊息"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """記錄除錯訊息"""
        self.logger.debug(message)
    
    def log_file_scan(self, file_path: str, success: bool, error_msg: str = None):
        """記錄檔案掃描結果"""
        if success:
            self.info(f"成功掃描檔案: {file_path}")
        else:
            self.error(f"掃描檔案失敗: {file_path} - {error_msg}")
    
    def log_scan_summary(self, total_files: int, successful_scans: int, failed_scans: int):
        """記錄掃描摘要"""
        self.info(f"掃描摘要 - 總檔案數: {total_files}, 成功: {successful_scans}, 失敗: {failed_scans}") 