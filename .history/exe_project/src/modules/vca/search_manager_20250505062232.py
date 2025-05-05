#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
视频搜索和排序管理器模块
用于处理搜索结果的相关性排序
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from src.utils.logger import get_logger
from src.adapters.adapter_factory import AdapterFactory
from .content_analyzer import ContentAnalyzer
from .download_manager import DownloadManager

logger = get_logger(__name__)

class SearchManager:
    """视频搜索和排序管理器"""
    
    def __init__(self, proxy_manager=None):
        """
        初始化搜索管理器
        
        Args:
            proxy_manager: 代理管理器实例
        """
        self.proxy_manager = proxy_manager
        self.adapter_factory = AdapterFactory()
        self.content_analyzer = ContentAnalyzer()
        self.download_manager = DownloadManager(proxy_manager)
        
    async def search_videos(self, query: str, platforms: Optional[List[str]] = None, 
                          max_results: int = 10, analyze_content: bool = True) -> List[Dict[str, Any]]:
        """
        搜索视频并排序
        
        Args:
            query: 搜索关键词
            platforms: 要搜索的平台列表，如果为None则搜索所有支持的平台
            max_results: 每个平台的最大结果数
            analyze_content: 是否分析视频内容
            
        Returns:
            List[Dict[str, Any]]: 排序后的视频列表
        """
        try:
            # 确定要搜索的平台
            if not platforms:
                platforms = self.adapter_factory.get_supported_platforms()
                
            # 创建搜索任务
            search_tasks = []
            for platform in platforms:
                adapter = self.adapter_factory.create_adapter(platform, self.proxy_manager)
                if adapter:
                    task = adapter.search_videos(query, max_results)
                    search_tasks.append(task)
                    
            # 并发执行搜索
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # 合并搜索结果
            all_videos = []
            for result in search_results:
                if isinstance(result, Exception):
                    logger.error(f"搜索失败: {str(result)}")
                    continue
                all_videos.extend(result)
                
            # 如果不需要分析内容，直接返回结果
            if not analyze_content:
                return all_videos
                
            # 分析视频内容并计算相关性
            analyzed_videos = await self.content_analyzer.analyze_videos(all_videos, query)
            
            # 按相关性排序
            sorted_videos = sorted(analyzed_videos, key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            return sorted_videos
            
        except Exception as e:
            logger.error(f"搜索视频失败: {str(e)}")
            return []
            
    async def download_video(self, video: Dict[str, Any], output_dir: Optional[str] = None) -> Optional[str]:
        """
        下载视频
        
        Args:
            video: 视频信息
            output_dir: 输出目录
            
        Returns:
            Optional[str]: 下载后的视频文件路径
        """
        return await self.download_manager.download_video(video, output_dir)
        
    async def download_videos(self, videos: List[Dict[str, Any]], output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        批量下载视频
        
        Args:
            videos: 视频信息列表
            output_dir: 输出目录
            
        Returns:
            Dict[str, str]: 视频ID到文件路径的映射
        """
        return await self.download_manager.download_videos(videos, output_dir)
        
    def filter_videos(self, videos: List[Dict[str, Any]], 
                     min_duration: Optional[int] = None,
                     max_duration: Optional[int] = None,
                     min_views: Optional[int] = None,
                     max_views: Optional[int] = None,
                     min_date: Optional[datetime] = None,
                     max_date: Optional[datetime] = None,
                     platforms: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        过滤视频
        
        Args:
            videos: 视频列表
            min_duration: 最小时长（秒）
            max_duration: 最大时长（秒）
            min_views: 最小观看次数
            max_views: 最大观看次数
            min_date: 最小上传日期
            max_date: 最大上传日期
            platforms: 平台列表
            
        Returns:
            List[Dict[str, Any]]: 过滤后的视频列表
        """
        filtered_videos = []
        
        for video in videos:
            # 平台过滤
            if platforms and video.get('platform') not in platforms:
                continue
                
            # 时长过滤
            duration = video.get('duration', 0)
            if min_duration and duration < min_duration:
                continue
            if max_duration and duration > max_duration:
                continue
                
            # 观看次数过滤
            views = video.get('view_count', 0)
            if min_views and views < min_views:
                continue
            if max_views and views > max_views:
                continue
                
            # 日期过滤
            upload_date = video.get('upload_date')
            if upload_date:
                if min_date and upload_date < min_date:
                    continue
                if max_date and upload_date > max_date:
                    continue
                    
            filtered_videos.append(video)
            
        return filtered_videos 