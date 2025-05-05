#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
基础适配器模块
定义所有平台适配器的基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import aiohttp
from src.utils.logger import get_logger
from src.utils.proxy_manager import ProxyManager

logger = get_logger(__name__)

class BaseAdapter(ABC):
    """基础适配器类"""
    
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        """
        初始化适配器
        
        Args:
            proxy_manager: 代理管理器实例
        """
        self.proxy_manager = proxy_manager
        self.platform = self.__class__.__name__.replace('Adapter', '').lower()
        self.session = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
            self.session = None
            
    @abstractmethod
    async def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        搜索视频
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            
        Returns:
            List[Dict[str, Any]]: 视频列表
        """
        pass
        
    @abstractmethod
    async def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        获取视频信息
        
        Args:
            video_id: 视频ID
            
        Returns:
            Optional[Dict[str, Any]]: 视频信息
        """
        pass
        
    def _format_video_info(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化视频信息
        
        Args:
            video: 原始视频信息
            
        Returns:
            Dict[str, Any]: 格式化后的视频信息
        """
        return {
            'platform': self.platform,
            'id': video.get('id', ''),
            'title': video.get('title', ''),
            'url': video.get('url', ''),
            'thumbnail': video.get('thumbnail', ''),
            'duration': video.get('duration', 0),
            'upload_date': video.get('upload_date', ''),
            'view_count': video.get('view_count', 0),
            'like_count': video.get('like_count', 0),
            'comment_count': video.get('comment_count', 0),
            'description': video.get('description', ''),
            'tags': video.get('tags', [])
        }
        
    def _get_proxy_config(self) -> Dict[str, str]:
        """
        获取代理配置
        
        Returns:
            Dict[str, str]: 代理配置
        """
        if not self.proxy_manager:
            return {}
            
        proxy = self.proxy_manager.get_proxy()
        return proxy if proxy else {}
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        获取或创建HTTP会话
        
        Returns:
            aiohttp.ClientSession: HTTP会话
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session 