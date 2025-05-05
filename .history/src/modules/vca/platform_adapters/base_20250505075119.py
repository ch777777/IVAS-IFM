#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
平台适配器基类

为所有平台适配器提供基本功能。
"""

import os
import time
import logging
import json
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BasePlatformAdapter(ABC):
    """所有平台适配器的基类"""
    
    def __init__(self, config=None):
        """初始化适配器"""
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def search_videos(self, query: str, max_results: int = 10, filters: Dict = None) -> List[Dict]:
        """
        搜索视频
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数量
            filters: 过滤条件
            
        Returns:
            搜索结果列表
        """
        pass
        
    @abstractmethod
    def download_video(self, video_url: str, output_dir: str, filename: str = None) -> Optional[str]:
        """
        下载视频
        
        Args:
            video_url: 视频URL
            output_dir: 输出目录
            filename: 文件名
            
        Returns:
            下载后的文件路径
        """
        pass
        
class DummyAdapter(BasePlatformAdapter):
    """模拟适配器，用于测试"""
    
    def __init__(self, platform: str, config: Dict = None):
        """初始化模拟适配器"""
        super().__init__(config)
        self.platform = platform
        
    def search_videos(self, query: str, max_results: int = 10, filters: Dict = None) -> List[Dict]:
        """搜索视频"""
        self.logger.info(f"模拟搜索: {self.platform}, 查询: {query}")
        results = []
        
        # 创建模拟结果
        for i in range(min(3, max_results)):
            results.append({
                "platform": self.platform,
                "video_id": f"dummy_{self.platform}_{i}",
                "title": f"【模拟】{self.platform.capitalize()} - {query} 视频 {i+1}",
                "url": f"https://www.{self.platform}.com/video/dummy_{i}",
                "thumbnail": f"https://via.placeholder.com/320x180.png?text={self.platform}+Demo",
                "channel": f"{self.platform.capitalize()} 演示频道",
                "publish_date": "2025-05-05",
                "duration": 60 * (i+1),
                "views": 1000 * (i+1),
                "description": f"这是一个模拟的 {self.platform} 视频，关键词: {query}"
            })
            
        return results
        
    def download_video(self, video_url: str, output_dir: str, filename: str = None) -> Optional[str]:
        """模拟下载视频"""
        self.logger.info(f"模拟下载: {self.platform}, URL: {video_url}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        if not filename:
            filename = f"demo_{self.platform}_{int(time.time())}.mp4"
            
        file_path = os.path.join(output_dir, filename)
        
        # 创建一个空白的模拟视频文件
        with open(file_path, "w") as f:
            f.write(f"这是一个模拟的 {self.platform} 视频文件，URL: {video_url}")
            
        self.logger.info(f"模拟下载完成: {file_path}")
        return file_path 