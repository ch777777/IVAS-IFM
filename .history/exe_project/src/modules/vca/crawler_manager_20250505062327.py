#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
爬虫管理器模块
用于协调和管理多个平台的视频搜索
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.adapters.adapter_factory import AdapterFactory
from src.utils.proxy_manager import ProxyManager
from src.utils.relevance_scorer import RelevanceScorer
from src.utils.logger import get_logger

logger = get_logger(__name__)

class CrawlerManager:
    """爬虫管理器"""
    
    def __init__(self):
        """初始化爬虫管理器"""
        self.proxy_manager = ProxyManager()
        self.relevance_scorer = RelevanceScorer()
        self.adapters = {}
        
    def initialize_adapters(self, platforms: List[str]) -> None:
        """
        初始化平台适配器
        
        Args:
            platforms: 平台列表
        """
        for platform in platforms:
            adapter = AdapterFactory.create_adapter(platform, self.proxy_manager)
            if adapter:
                self.adapters[platform] = adapter
                logger.info(f"初始化平台适配器: {platform}")
                
    async def search_videos(self, query: str, platforms: List[str] = None,
                          max_results: int = 10, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        搜索视频
        
        Args:
            query: 搜索关键词
            platforms: 平台列表，如果为None则使用所有已初始化的平台
            max_results: 每个平台的最大结果数
            filters: 过滤条件
            
        Returns:
            List[Dict[str, Any]]: 视频列表
        """
        try:
            # 初始化适配器
            if not platforms:
                platforms = list(self.adapters.keys())
            self.initialize_adapters(platforms)
            
            # 并发搜索所有平台
            tasks = []
            for platform in platforms:
                if platform in self.adapters:
                    adapter = self.adapters[platform]
                    tasks.append(self._search_platform(adapter, query, max_results))
                    
            # 等待所有搜索完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 合并结果
            all_videos = []
            for platform_results in results:
                if isinstance(platform_results, Exception):
                    logger.error(f"平台搜索失败: {str(platform_results)}")
                    continue
                all_videos.extend(platform_results)
                
            # 计算相关性得分
            for video in all_videos:
                video['relevance_score'] = self.relevance_scorer.calculate_score(video, query)
                
            # 应用过滤条件
            if filters:
                all_videos = self._apply_filters(all_videos, filters)
                
            # 按相关性得分排序
            all_videos.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return all_videos
            
        except Exception as e:
            logger.error(f"视频搜索失败: {str(e)}")
            return []
            
    async def _search_platform(self, adapter: Any, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        搜索单个平台
        
        Args:
            adapter: 平台适配器
            query: 搜索关键词
            max_results: 最大结果数
            
        Returns:
            List[Dict[str, Any]]: 视频列表
        """
        try:
            async with adapter as a:
                return await a.search_videos(query, max_results)
        except Exception as e:
            logger.error(f"平台搜索失败: {str(e)}")
            return []
            
    def _apply_filters(self, videos: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        应用过滤条件
        
        Args:
            videos: 视频列表
            filters: 过滤条件
            
        Returns:
            List[Dict[str, Any]]: 过滤后的视频列表
        """
        filtered_videos = videos
        
        # 时长过滤
        if 'duration_range' in filters:
            min_duration, max_duration = filters['duration_range']
            filtered_videos = [
                v for v in filtered_videos
                if min_duration <= v['duration'] <= max_duration
            ]
            
        # 上传日期过滤
        if 'upload_date_range' in filters:
            start_date, end_date = filters['upload_date_range']
            filtered_videos = [
                v for v in filtered_videos
                if start_date <= v['upload_date'] <= end_date
            ]
            
        # 观看次数过滤
        if 'min_views' in filters:
            min_views = filters['min_views']
            filtered_videos = [
                v for v in filtered_videos
                if v['view_count'] >= min_views
            ]
            
        # 平台过滤
        if 'platforms' in filters:
            platforms = filters['platforms']
            filtered_videos = [
                v for v in filtered_videos
                if v['platform'] in platforms
            ]
            
        return filtered_videos
        
    def close(self) -> None:
        """关闭爬虫管理器"""
        self.adapters.clear()
        logger.info("爬虫管理器已关闭")


# 示例用法
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建爬虫管理器
    manager = CrawlerManager()
    
    # 加载平台适配器
    adapter_count = manager.load_platform_adapters()
    print(f"加载了 {adapter_count} 个平台适配器")
    
    # 输出支持的平台
    platforms = manager.get_supported_platforms()
    print(f"支持的平台: {platforms}")
    
    # 关闭管理器
    manager.shutdown() 
 
 