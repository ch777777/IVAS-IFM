#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
请求管理模块
用于处理HTTP请求
"""

import time
import random
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from src.utils.logger import get_logger
from src.utils.proxy_manager import ProxyManager

logger = get_logger(__name__)

class RequestManager:
    """请求管理器"""
    
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        """
        初始化请求管理器
        
        Args:
            proxy_manager: 代理管理器实例
        """
        self.proxy_manager = proxy_manager
        self.session = None
        self.last_request_time = 0
        self.min_delay = 1  # 最小请求延迟（秒）
        self.max_delay = 3  # 最大请求延迟（秒）
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
            
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, 
                 params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        发送GET请求
        
        Args:
            url: 请求URL
            headers: 请求头
            params: 请求参数
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        await self._wait_for_rate_limit()
        
        try:
            proxy_config = self.proxy_manager.get_proxy_config() if self.proxy_manager else {}
            
            async with self.session.get(
                url,
                headers=headers,
                params=params,
                proxy=proxy_config.get('http'),
                ssl=False
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"请求失败: {url}, 错误: {str(e)}")
            raise
            
    async def post(self, url: str, data: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        发送POST请求
        
        Args:
            url: 请求URL
            data: 请求数据
            headers: 请求头
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        await self._wait_for_rate_limit()
        
        try:
            proxy_config = self.proxy_manager.get_proxy_config() if self.proxy_manager else {}
            
            async with self.session.post(
                url,
                json=data,
                headers=headers,
                proxy=proxy_config.get('http'),
                ssl=False
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"请求失败: {url}, 错误: {str(e)}")
            raise
            
    async def _wait_for_rate_limit(self):
        """等待请求速率限制"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_delay:
            delay = random.uniform(self.min_delay, self.max_delay)
            await asyncio.sleep(delay)
            
        self.last_request_time = time.time()
        
    def set_rate_limit(self, min_delay: float, max_delay: float):
        """
        设置请求速率限制
        
        Args:
            min_delay: 最小请求延迟（秒）
            max_delay: 最大请求延迟（秒）
        """
        self.min_delay = min_delay
        self.max_delay = max_delay 