"""
爬虫管理器
负责协调多个爬虫实例，管理视频采集任务
"""
import logging
import concurrent.futures
import importlib
import os
from typing import Dict, List, Optional, Any, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from .platform_adapters import (
    YouTubeAdapter,
    TikTokAdapter,
    BilibiliAdapter,
    WeiboAdapter,
    FacebookAdapter
)

logger = logging.getLogger(__name__)

class CrawlerManager:
    """
    爬虫管理器，负责协调多个平台的视频搜索和结果处理
    """
    def __init__(self, max_workers: int = 5):
        """
        初始化爬虫管理器
        
        Args:
            max_workers: 最大并发工作线程数
        """
        self.logger = logging.getLogger('crawler_manager')
        self.max_workers = max_workers
        self.platform_adapters = {}
        self._init_platform_adapters()
    
    def _init_platform_adapters(self):
        """初始化各平台的适配器"""
        self.platform_adapters = {
            'youtube': YouTubeAdapter(),
            'tiktok': TikTokAdapter(),
            'bilibili': BilibiliAdapter(),
            'weibo': WeiboAdapter(),
            'facebook': FacebookAdapter()
        }
    
    async def _search_platform(self, platform: str, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        在单个平台上搜索视频
        
        Args:
            platform: 平台名称
            query: 搜索关键词
            max_results: 最大结果数量
            
        Returns:
            视频信息列表
        """
        try:
            adapter = self.platform_adapters.get(platform)
            if not adapter:
                self.logger.warning(f"未找到平台适配器: {platform}")
                return []
            
            results = await adapter.search_videos(query, max_results)
            return [{
                'platform': platform,
                'title': video.get('title', ''),
                'url': video.get('url', ''),
                'thumbnail': video.get('thumbnail', ''),
                'duration': video.get('duration', 0),
                'upload_date': video.get('upload_date', ''),
                'view_count': video.get('view_count', 0),
                'like_count': video.get('like_count', 0),
                'comment_count': video.get('comment_count', 0),
                'description': video.get('description', ''),
                'tags': video.get('tags', []),
                'relevance_score': self._calculate_relevance_score(video, query)
            } for video in results]
        except Exception as e:
            self.logger.error(f"搜索平台 {platform} 时出错: {str(e)}")
            return []
    
    def _calculate_relevance_score(self, video: Dict[str, Any], query: str) -> float:
        """
        计算视频与搜索关键词的相关度分数
        
        Args:
            video: 视频信息
            query: 搜索关键词
            
        Returns:
            相关度分数 (0-1)
        """
        score = 0.0
        
        # 标题相关度 (权重: 0.4)
        title = video.get('title', '').lower()
        if query.lower() in title:
            score += 0.4
        
        # 描述相关度 (权重: 0.2)
        description = video.get('description', '').lower()
        if query.lower() in description:
            score += 0.2
        
        # 标签相关度 (权重: 0.2)
        tags = [tag.lower() for tag in video.get('tags', [])]
        if query.lower() in tags:
            score += 0.2
        
        # 互动指标 (权重: 0.2)
        view_count = video.get('view_count', 0)
        like_count = video.get('like_count', 0)
        comment_count = video.get('comment_count', 0)
        
        # 归一化互动指标
        max_views = 1000000  # 假设的最大观看数
        max_likes = 100000   # 假设的最大点赞数
        max_comments = 10000 # 假设的最大评论数
        
        interaction_score = (
            min(view_count / max_views, 1) * 0.1 +
            min(like_count / max_likes, 1) * 0.05 +
            min(comment_count / max_comments, 1) * 0.05
        )
        
        score += interaction_score
        
        return min(score, 1.0)  # 确保分数不超过1
    
    async def search_videos(self, 
                          query: str, 
                          platforms: List[str] = None, 
                          max_results: int = 10,
                          filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        并发搜索多个平台的视频
        
        Args:
            query: 搜索关键词
            platforms: 要搜索的平台列表，如果为None则搜索所有平台
            max_results: 每个平台的最大结果数量
            filters: 过滤条件，如时长范围、上传日期等
            
        Returns:
            按相关度排序的视频信息列表
        """
        if platforms is None:
            platforms = list(self.platform_adapters.keys())
        
        # 创建搜索任务
        tasks = [
            self._search_platform(platform, query, max_results)
            for platform in platforms
        ]
        
        # 并发执行搜索
        results = await asyncio.gather(*tasks)
        
        # 合并所有平台的结果
        all_videos = []
        for platform_results in results:
            all_videos.extend(platform_results)
        
        # 应用过滤条件
        if filters:
            all_videos = self._apply_filters(all_videos, filters)
        
        # 按相关度分数排序
        all_videos.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return all_videos
    
    def _apply_filters(self, videos: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        应用过滤条件
        
        Args:
            videos: 视频列表
            filters: 过滤条件
            
        Returns:
            过滤后的视频列表
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
        
        # 观看数过滤
        if 'min_views' in filters:
            filtered_videos = [
                v for v in filtered_videos
                if v['view_count'] >= filters['min_views']
            ]
        
        # 平台过滤
        if 'platforms' in filters:
            filtered_videos = [
                v for v in filtered_videos
                if v['platform'] in filters['platforms']
            ]
        
        return filtered_videos
    
    def close(self):
        """关闭所有平台适配器"""
        for adapter in self.platform_adapters.values():
            if hasattr(adapter, 'close'):
                adapter.close()


# 示例用法
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建爬虫管理器
    manager = CrawlerManager(max_workers=3)
    
    # 加载平台适配器
    adapter_count = manager.load_platform_adapters()
    print(f"加载了 {adapter_count} 个平台适配器")
    
    # 输出支持的平台
    platforms = manager.get_supported_platforms()
    print(f"支持的平台: {platforms}")
    
    # 关闭管理器
    manager.shutdown() 
 
 