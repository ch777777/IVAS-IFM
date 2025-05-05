#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
代理管理器模块
提供代理IP管理和轮换功能
"""

import random
import time
from typing import Dict, List, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ProxyManager:
    """代理管理器"""
    
    def __init__(self):
        """初始化代理管理器"""
        self.proxies: List[Dict[str, str]] = []
        self.current_index = 0
        self.last_switch_time = 0
        self.switch_interval = 300  # 5分钟切换一次代理
        
    def add_proxy(self, proxy: Dict[str, str]) -> None:
        """
        添加代理
        
        Args:
            proxy: 代理配置，格式为 {'http': 'http://host:port', 'https': 'https://host:port'}
        """
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            logger.info(f"添加代理: {proxy}")
            
    def remove_proxy(self, proxy: Dict[str, str]) -> None:
        """
        移除代理
        
        Args:
            proxy: 要移除的代理配置
        """
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            logger.info(f"移除代理: {proxy}")
            
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        获取当前代理
        
        Returns:
            Optional[Dict[str, str]]: 代理配置，如果没有可用代理则返回None
        """
        if not self.proxies:
            return None
            
        current_time = time.time()
        if current_time - self.last_switch_time >= self.switch_interval:
            self._switch_proxy()
            self.last_switch_time = current_time
            
        return self.proxies[self.current_index]
        
    def _switch_proxy(self) -> None:
        """切换代理"""
        if not self.proxies:
            return
            
        # 随机选择一个不同的代理
        new_index = self.current_index
        while new_index == self.current_index and len(self.proxies) > 1:
            new_index = random.randint(0, len(self.proxies) - 1)
            
        self.current_index = new_index
        logger.info(f"切换代理: {self.proxies[self.current_index]}")
        
    def set_switch_interval(self, interval: int) -> None:
        """
        设置代理切换间隔
        
        Args:
            interval: 切换间隔（秒）
        """
        if interval > 0:
            self.switch_interval = interval
            logger.info(f"设置代理切换间隔: {interval}秒")
            
    def clear_proxies(self) -> None:
        """清空所有代理"""
        self.proxies.clear()
        self.current_index = 0
        logger.info("清空所有代理") 