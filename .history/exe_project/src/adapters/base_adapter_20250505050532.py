#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
基础平台适配器模块
定义所有平台适配器的基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from src.utils.logger import get_logger
from src.utils.request_manager import RequestManager
from src.utils.proxy_manager import ProxyManager
from src.config.platform_config import get_platform_config

logger = get_logger(__name__)

class BaseAdapter(ABC):
    """基础平台适配器"""
    
    def __init__(self, platform: str, proxy_manager: Optional[ProxyManager] = None):
        """
        初始化平台适配器
        
        Args:
            platform: 平台名称
            proxy_manager: 代理管理器实例
        """
        self.platform = platform
        self.config = get_platform_config(platform)
        self.proxy_manager = proxy_manager
        self.request_manager = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.request_manager = RequestManager(self.proxy_manager)
        await self.request_manager.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.request_manager:
            await self.request_manager.__aexit__(exc_type, exc_val, exc_tb)
            
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
    async def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        获取视频信息
        
        Args:
            video_id: 视频ID
            
        Returns:
            Dict[str, Any]: 视频信息
        """
        pass
        
    def _format_video_info(self, raw_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化视频信息
        
        Args:
            raw_info: 原始视频信息
            
        Returns:
            Dict[str, Any]: 格式化后的视频信息
        """
        return {
            'platform': self.platform,
            'video_id': raw_info.get('id', ''),
            'title': raw_info.get('title', ''),
            'description': raw_info.get('description', ''),
            'duration': raw_info.get('duration', 0),
            'view_count': raw_info.get('view_count', 0),
            'upload_date': raw_info.get('upload_date', ''),
            'url': raw_info.get('url', ''),
            'thumbnail_url': raw_info.get('thumbnail_url', ''),
            'author': raw_info.get('author', {}),
            'tags': raw_info.get('tags', []),
            'raw_data': raw_info
        }
        
    def _get_headers(self) -> Dict[str, str]:
        """
        获取请求头
        
        Returns:
            Dict[str, str]: 请求头
        """
        return self.config.get('headers', {})
        
    def _get_rate_limit(self) -> Dict[str, int]:
        """
        获取速率限制
        
        Returns:
            Dict[str, int]: 速率限制
        """
        return self.config.get('rate_limit', {})
        
    def _get_base_url(self) -> str:
        """
        获取基础URL
        
        Returns:
            str: 基础URL
        """
        return self.config.get('base_url', '')
        
    def _get_search_url(self) -> str:
        """
        获取搜索URL
        
        Returns:
            str: 搜索URL
        """
        return self.config.get('search_url', '') 