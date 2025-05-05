#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
日志记录模块
实现系统日志的记录和管理功能
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from ..config.settings import LOG_CONFIG

class Logger:
    """日志记录器类"""
    
    def __init__(self):
        """初始化日志记录器"""
        # 创建logs目录
        os.makedirs("logs", exist_ok=True)
        
        # 设置日志文件名
        log_file = os.path.join("logs", f"app_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 配置日志记录器
        self.logger = logging.getLogger("UserAuthSystem")
        self.logger.setLevel(logging.DEBUG)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """记录一般信息"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告信息"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误信息"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """记录严重错误信息"""
        self.logger.critical(message)
        
    def log_login(self, username: str, success: bool, ip: str = "", user_agent: str = ""):
        """
        记录登录事件
        
        Args:
            username: 用户名
            success: 是否登录成功
            ip: IP地址
            user_agent: 用户代理
        """
        status = "成功" if success else "失败"
        message = f"用户 {username} 登录{status} - IP: {ip} - User-Agent: {user_agent}"
        self.logger.info(message)
        
    def log_action(self, username: str, action: str, details: Dict[str, Any] = None):
        """
        记录用户操作
        
        Args:
            username: 用户名
            action: 操作类型
            details: 操作详情
        """
        message = f"用户 {username} 执行操作: {action}"
        if details:
            message += f" - 详情: {json.dumps(details, ensure_ascii=False)}"
        self.logger.info(message)
        
    def log_error(self, error_type: str, error_message: str, username: str = None):
        """
        记录错误
        
        Args:
            error_type: 错误类型
            error_message: 错误信息
            username: 相关用户名（如果有）
        """
        message = f"错误类型: {error_type} - 信息: {error_message}"
        if username:
            message = f"用户 {username} - {message}"
        self.logger.error(message)
        
    def get_login_history(self, username: str = None, limit: int = 100) -> list:
        """
        获取登录历史记录
        
        Args:
            username: 用户名（可选）
            limit: 返回记录数量限制
            
        Returns:
            list: 登录历史记录列表
        """
        if not os.path.exists(os.path.join("logs", "app_latest.log")):
            return []
            
        history = []
        with open(os.path.join("logs", "app_latest.log"), "r", encoding="utf-8") as f:
            for line in f:
                if username and username not in line:
                    continue
                if "登录" in line:
                    history.append(line.strip())
                    
        return history[-limit:] 