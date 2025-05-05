#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
平台适配器工厂模块
用于创建和管理平台适配器实例
"""

from typing import Dict, Type, Optional
from src.adapters.base_adapter import BaseAdapter
from src.adapters.youtube_adapter import YouTubeAdapter
from src.adapters.bilibili_adapter import BilibiliAdapter
from src.adapters.tiktok_adapter import TikTokAdapter
from src.adapters.weibo_adapter import WeiboAdapter
from src.utils.proxy_manager import ProxyManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AdapterFactory:
    """平台适配器工厂"""
    
    # 平台适配器映射
    _adapters: Dict[str, Type[BaseAdapter]] = {
        'youtube': YouTubeAdapter,
        'bilibili': BilibiliAdapter,
        'tiktok': TikTokAdapter,
        'weibo': WeiboAdapter
    }
    
    @classmethod
    def create_adapter(cls, platform: str, proxy_manager: Optional[ProxyManager] = None) -> Optional[BaseAdapter]:
        """
        创建平台适配器实例
        
        Args:
            platform: 平台名称
            proxy_manager: 代理管理器实例
            
        Returns:
            Optional[BaseAdapter]: 平台适配器实例
        """
        try:
            platform = platform.lower()
            if platform not in cls._adapters:
                logger.error(f"不支持的平台: {platform}")
                return None
                
            adapter_class = cls._adapters[platform]
            return adapter_class(proxy_manager)
            
        except Exception as e:
            logger.error(f"创建适配器失败: {str(e)}")
            return None
            
    @classmethod
    def get_supported_platforms(cls) -> list:
        """
        获取支持的平台列表
        
        Returns:
            list: 支持的平台列表
        """
        return list(cls._adapters.keys())
        
    @classmethod
    def register_adapter(cls, platform: str, adapter_class: Type[BaseAdapter]) -> bool:
        """
        注册新的平台适配器
        
        Args:
            platform: 平台名称
            adapter_class: 适配器类
            
        Returns:
            bool: 是否注册成功
        """
        try:
            if not issubclass(adapter_class, BaseAdapter):
                logger.error(f"适配器类必须继承自BaseAdapter: {adapter_class}")
                return False
                
            platform = platform.lower()
            cls._adapters[platform] = adapter_class
            logger.info(f"注册新平台适配器: {platform}")
            return True
            
        except Exception as e:
            logger.error(f"注册适配器失败: {str(e)}")
            return False
            
    @classmethod
    def unregister_adapter(cls, platform: str) -> bool:
        """
        注销平台适配器
        
        Args:
            platform: 平台名称
            
        Returns:
            bool: 是否注销成功
        """
        try:
            platform = platform.lower()
            if platform in cls._adapters:
                del cls._adapters[platform]
                logger.info(f"注销平台适配器: {platform}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"注销适配器失败: {str(e)}")
            return False 