#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
代理管理模块
用于管理和轮换代理
"""

import random
import time
from typing import List, Optional
from src.config.platform_config import PROXY_CONFIG
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ProxyManager:
    """代理管理器"""
    
    def __init__(self):
        """初始化代理管理器"""
        self.proxies = []
        self.current_proxy = None
        self.last_rotation = 0
        self.rotation_interval = PROXY_CONFIG['rotation_interval']
        self.proxy_type = PROXY_CONFIG['proxy_type']
        
    def load_proxies(self, proxy_list: List[str]) -> None:
        """
        加载代理列表
        
        Args:
            proxy_list: 代理列表
        """
        self.proxies = proxy_list
        logger.info(f"已加载 {len(self.proxies)} 个代理")
        
    def get_proxy(self) -> Optional[str]:
        """
        获取当前代理
        
        Returns:
            str: 代理地址，格式为 'http://host:port' 或 'https://host:port'
        """
        if not PROXY_CONFIG['enabled'] or not self.proxies:
            return None
            
        current_time = time.time()
        if (not self.current_proxy or 
            current_time - self.last_rotation >= self.rotation_interval):
            self._rotate_proxy()
            
        return self.current_proxy
        
    def _rotate_proxy(self) -> None:
        """轮换代理"""
        if not self.proxies:
            return
            
        self.current_proxy = random.choice(self.proxies)
        self.last_rotation = time.time()
        logger.debug(f"已切换到新代理: {self.current_proxy}")
        
    def format_proxy(self, proxy: str) -> dict:
        """
        格式化代理地址为请求格式
        
        Args:
            proxy: 代理地址
            
        Returns:
            dict: 格式化后的代理配置
        """
        if not proxy:
            return {}
            
        return {
            'http': f"{self.proxy_type}://{proxy}",
            'https': f"{self.proxy_type}://{proxy}"
        }
        
    def get_proxy_config(self) -> dict:
        """
        获取当前代理配置
        
        Returns:
            dict: 代理配置
        """
        proxy = self.get_proxy()
        return self.format_proxy(proxy) if proxy else {}
        
    def disable(self) -> None:
        """禁用代理"""
        self.current_proxy = None
        self.last_rotation = 0
        
    def enable(self) -> None:
        """启用代理"""
        if self.proxies:
            self._rotate_proxy() 