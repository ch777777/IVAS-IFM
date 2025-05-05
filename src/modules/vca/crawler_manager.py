#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Crawler Manager for the VCA module.

This module manages the crawling process across multiple platforms.
"""

import os
import logging
import time
import importlib
from typing import Dict, List, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from src.config import settings
except ImportError:
    settings = None

try:
    from src.config.settings import PLATFORM_CONFIGS, DOWNLOAD_CONFIG
except ImportError:
    # Default configurations if settings module cannot be imported
    PLATFORM_CONFIGS = {
        "youtube": {"max_results": 50},
        "bilibili": {"max_results": 50},
        "tiktok": {"max_results": 30},
        "weibo": {"max_results": 30},
        "facebook": {"max_results": 30}
    }
    
    DOWNLOAD_CONFIG = {
        "default_output_dir": "downloads",
        "max_concurrent_downloads": 3,
    }

logger = logging.getLogger(__name__)


class DownloadManager:
    """简单的下载管理器"""
    
    def __init__(self, platform_adapters=None):
        self.platform_adapters = platform_adapters or {}
        
    def download(self, url, platform, output_dir, filename=None, video_info=None, progress_callback=None):
        """下载视频"""
        try:
            if platform in self.platform_adapters:
                adapter = self.platform_adapters[platform]
                return adapter.download_video(url, output_dir, filename)
            return None
        except Exception as e:
            logger.error(f"下载失败: {e}")
            return None


class CrawlerManager:
    """
    Manages the video crawling process across multiple platforms.
    
    This class coordinates the crawling process, distributing requests
    to platform-specific adapters and aggregating results.
    """
    
    def __init__(self):
        """Initialize the crawler manager."""
        self.platform_adapters = {}
        self.download_manager = None
        self.load_platform_adapters()
        self.initialize_download_manager()
        logger.info("CrawlerManager initialized")
    
    def load_platform_adapters(self):
        """Load available platform adapters."""
        try:
            # Try to dynamically load platform adapters
            for platform in PLATFORM_CONFIGS.keys():
                try:
                    # Attempt to import platform adapter
                    module_path = f".platform_adapters.{platform}"
                    module = importlib.import_module(module_path, package="src.modules.vca")
                    
                    # Check for adapter class
                    adapter_class_name = f"{platform.capitalize()}Adapter"
                    if hasattr(module, adapter_class_name):
                        adapter_class = getattr(module, adapter_class_name)
                        self.platform_adapters[platform] = adapter_class()
                        logger.info(f"Loaded {platform} adapter")
                    else:
                        # Fallback to base adapter
                        self.platform_adapters[platform] = self._create_dummy_adapter(platform)
                        logger.warning(f"Created dummy adapter for {platform}")
                        
                except ImportError:
                    logger.warning(f"Failed to import adapter for platform: {platform}")
                    self.platform_adapters[platform] = self._create_dummy_adapter(platform)
            
            logger.info(f"Loaded {len(self.platform_adapters)} platform adapters")
        except Exception as e:
            logger.error(f"Error loading platform adapters: {e}")
            # Fall back to dummy adapters
            for platform in PLATFORM_CONFIGS.keys():
                self.platform_adapters[platform] = self._create_dummy_adapter(platform)
    
    def initialize_download_manager(self):
        """Initialize the download manager."""
        try:
            self.download_manager = DownloadManager(platform_adapters=self.platform_adapters)
            logger.info("DownloadManager initialized")
        except Exception as e:
            logger.error(f"Error initializing download manager: {e}")
    
    def search_videos(
        self, 
        query: str, 
        platforms: Optional[List[str]] = None, 
        max_results: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for videos across multiple platforms.
        
        Args:
            query: The search query
            platforms: List of platforms to search (default: all available)
            max_results: Maximum number of results per platform
            filters: Additional filters to apply to the search
            
        Returns:
            Dictionary mapping platform names to lists of video results
        """
        if not query:
            logger.warning("Empty search query provided")
            return {}
            
        # Determine which platforms to search
        platforms_to_search = platforms or list(self.platform_adapters.keys())
        valid_platforms = [p for p in platforms_to_search if p in self.platform_adapters]
        
        if not valid_platforms:
            logger.warning(f"No valid platforms specified. Available: {list(self.platform_adapters.keys())}")
            return {}
            
        logger.info(f"Searching for '{query}' on platforms: {valid_platforms}")
        
        # Initialize results
        results = {}
        
        # Search each platform concurrently
        with ThreadPoolExecutor(max_workers=min(len(valid_platforms), 5)) as executor:
            future_to_platform = {
                executor.submit(
                    self._search_platform, platform, query, max_results, filters
                ): platform 
                for platform in valid_platforms
            }
            
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    platform_results = future.result()
                    results[platform] = platform_results
                    logger.info(f"Found {len(platform_results)} results on {platform}")
                except Exception as e:
                    logger.error(f"Error searching {platform}: {e}")
                    results[platform] = []
        
        return results
    
    def _search_platform(
        self, 
        platform: str, 
        query: str, 
        max_results: int, 
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        在指定平台上搜索视频
        
        Args:
            platform: 平台名称
            query: 搜索关键词
            max_results: 最大结果数
            filters: 搜索过滤条件
            
        Returns:
            搜索结果列表
        """
        # 检查是否使用模拟数据
        platform_config = PLATFORM_CONFIGS.get(platform, {})
        use_mock = platform_config.get("use_mock_data", False)
        
        if use_mock and hasattr(settings, "MOCK_DATA") and platform in settings.MOCK_DATA:
            # 使用模拟数据
            logger.info(f"使用 {platform} 平台模拟数据")
            results = settings.MOCK_DATA.get(platform, [])
            
            # 过滤结果 (简单匹配标题或描述中是否包含查询词)
            if query:
                query_lower = query.lower()
                results = [
                    r for r in results 
                    if query_lower in r.get("title", "").lower() or query_lower in r.get("description", "").lower()
                ]
            
            return results[:max_results]
        
        if platform not in self.platform_adapters:
            logger.warning(f"未找到 {platform} 平台适配器")
            return []
            
        adapter = self.platform_adapters[platform]
        try:
            # 使用适配器搜索视频
            results = adapter.search_videos(query, max_results, filters)
            return results
        except Exception as e:
            logger.error(f"在 {platform} 平台搜索时出错: {e}")
            return []
    
    def download_video(
        self, 
        video_url: str, 
        output_dir: Optional[str] = None, 
        filename: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> Optional[str]:
        """
        Download a video from any supported platform.
        
        Args:
            video_url: URL of the video to download
            output_dir: Directory to save the video
            filename: Filename to use (default: auto-generated)
            progress_callback: Callback for progress updates
            
        Returns:
            Path to the downloaded file, or None if download failed
        """
        if not video_url:
            logger.warning("No video URL provided")
            return None
            
        # Determine platform from URL
        platform = self._detect_platform_from_url(video_url)
        if not platform or platform not in self.platform_adapters:
            logger.warning(f"Unsupported platform for URL: {video_url}")
            return None
            
        # Set default output directory if not provided
        if not output_dir:
            output_dir = DOWNLOAD_CONFIG.get('default_output_dir', 'downloads')
            os.makedirs(output_dir, exist_ok=True)
            
        logger.info(f"Downloading video from {platform}: {video_url}")
        
        try:
            if self.download_manager:
                # Use download manager if available
                video_info = {"title": filename} if filename else {}
                return self.download_manager.download(
                    url=video_url,
                    platform=platform,
                    output_dir=output_dir,
                    filename=filename,
                    video_info=video_info,
                    progress_callback=progress_callback
                )
            else:
                # Direct adapter download
                adapter = self.platform_adapters[platform]
                return adapter.download_video(video_url, output_dir, filename)
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None
    
    def _detect_platform_from_url(self, url: str) -> Optional[str]:
        """
        从URL中检测平台
        
        Args:
            url: 视频URL
            
        Returns:
            平台名称，如果无法识别则返回None
        """
        url = url.lower()
        
        # 简单的URL匹配
        if "youtube.com" in url or "youtu.be" in url:
            return "youtube"
        elif "bilibili.com" in url:
            return "bilibili"
        elif "tiktok.com" in url:
            return "tiktok"
        elif "weibo.com" in url:
            return "weibo"
        elif "facebook.com" in url or "fb.com" in url:
            return "facebook"
        
        return None
    
    def _create_dummy_adapter(self, platform: str) -> Any:
        """
        创建一个模拟适配器
        
        Args:
            platform: 平台名称
            
        Returns:
            模拟适配器实例
        """
        logger.info(f"创建 {platform} 平台的模拟适配器")
        
        class DummyAdapter:
            def search_videos(self, query, max_results=10, filters=None, **kwargs):
                logger.info(f"模拟搜索: {platform}, 关键词: {query}")
                # 从设置中获取模拟数据，如果没有则生成空数据
                if hasattr(settings, "MOCK_DATA") and platform in settings.MOCK_DATA:
                    results = settings.MOCK_DATA.get(platform, [])
                    
                    # 过滤结果
                    if query:
                        query_lower = query.lower()
                        results = [
                            r for r in results 
                            if query_lower in r.get("title", "").lower() or query_lower in r.get("description", "").lower()
                        ]
                    
                    return results[:max_results]
                else:
                    # 生成默认的模拟数据
                    return self._create_dummy_results(platform, query, max_results)
            
            def download_video(self, url, output_dir, filename=None, **kwargs):
                logger.info(f"模拟下载: {platform}, URL: {url}")
                
                # 创建一个空文件作为下载结果
                if not filename:
                    filename = f"demo_{platform}_{int(time.time())}.mp4"
                
                file_path = os.path.join(output_dir, filename)
                with open(file_path, "w") as f:
                    f.write(f"这是一个模拟的 {platform} 视频文件，URL: {url}")
                
                return file_path
                
            def _create_dummy_results(self, platform, query, max_results):
                """创建模拟搜索结果"""
                results = []
                for i in range(min(3, max_results)):
                    results.append({
                        "platform": platform,
                        "video_id": f"dummy_{platform}_{i}",
                        "title": f"【模拟】{platform.capitalize()} - {query} 视频 {i+1}",
                        "url": f"https://www.{platform}.com/video/dummy_{i}",
                        "thumbnail": f"https://via.placeholder.com/320x180.png?text={platform}+Demo",
                        "channel": f"{platform.capitalize()} 演示频道",
                        "publish_date": "2025-05-05",
                        "duration": 60 * (i+1),
                        "views": 1000 * (i+1),
                        "description": f"这是一个模拟的 {platform} 视频，关键词: {query}"
                    })
                return results
                
        return DummyAdapter()
    
    def _create_dummy_results(self, platform: str, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        创建模拟搜索结果
        
        Args:
            platform: 平台名称
            query: 搜索关键词
            max_results: 最大结果数
            
        Returns:
            模拟搜索结果列表
        """
        results = []
        for i in range(min(3, max_results)):
            results.append({
                "platform": platform,
                "video_id": f"dummy_{platform}_{i}",
                "title": f"【模拟】{platform.capitalize()} - {query} 视频 {i+1}",
                "url": f"https://www.{platform}.com/video/dummy_{i}",
                "thumbnail": f"https://via.placeholder.com/320x180.png?text={platform}+Demo",
                "channel": f"{platform.capitalize()} 演示频道",
                "publish_date": "2025-05-05",
                "duration": 60 * (i+1),
                "views": 1000 * (i+1),
                "description": f"这是一个模拟的 {platform} 视频，关键词: {query}"
            })
        return results 