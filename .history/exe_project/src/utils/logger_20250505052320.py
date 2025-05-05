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
    """系统日志记录器"""
    
    def __init__(self):
        """初始化日志记录器"""
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        self.log_file = os.path.join(self.log_dir, "system.log")
        self.login_log_file = os.path.join(self.log_dir, "login.log")
        self._setup_logging()
        
    def _setup_logging(self):
        """设置日志记录器"""
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 系统日志配置
        logging.basicConfig(
            level=getattr(logging, LOG_CONFIG["level"]),
            format=LOG_CONFIG["format"],
            datefmt=LOG_CONFIG["date_format"],
            handlers=[
                logging.FileHandler(self.log_file, encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
        
        # 登录日志配置
        self.login_logger = logging.getLogger("login")
        self.login_logger.setLevel(logging.INFO)
        login_handler = logging.FileHandler(self.login_log_file, encoding="utf-8")
        login_handler.setFormatter(logging.Formatter(LOG_CONFIG["format"]))
        self.login_logger.addHandler(login_handler)
        
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
        self.login_logger.info(message)
        
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
        logging.info(message)
        
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
        logging.error(message)
        
    def get_login_history(self, username: str = None, limit: int = 100) -> list:
        """
        获取登录历史记录
        
        Args:
            username: 用户名（可选）
            limit: 返回记录数量限制
            
        Returns:
            list: 登录历史记录列表
        """
        if not os.path.exists(self.login_log_file):
            return []
            
        history = []
        with open(self.login_log_file, "r", encoding="utf-8") as f:
            for line in f:
                if username and username not in line:
                    continue
                if "登录" in line:
                    history.append(line.strip())
                    
        return history[-limit:] 