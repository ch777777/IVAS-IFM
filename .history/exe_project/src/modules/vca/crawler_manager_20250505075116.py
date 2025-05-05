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

from .download_manager import DownloadManager

logger = logging.getLogger(__name__)


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
                        from .platform_adapters.base import BasePlatformAdapter, AntiCrawlerMixin
                        
                        # Create a simple adapter on-the-fly
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
                task_id = self.download_manager.download(
                    url=video_url,
                    platform=platform,
                    output_dir=output_dir,
                    filename=filename,
                    video_info=video_info,
                    progress_callback=progress_callback
                )
                
                # Wait for download to complete (simplified approach)
                task = self.download_manager.get_task(task_id)
                while task.status in ["pending", "downloading"]:
                    time.sleep(0.5)
                    
                if task.status == "completed":
                    return task.output_path
                return None
            else:
                # Use platform adapter directly
                adapter = self.platform_adapters[platform]
                
                # Generate a dummy filename if not provided
                if not filename:
                    timestamp = int(time.time())
                    filename = f"video_{platform}_{timestamp}.mp4"
                    
                # Call adapter's download method
                return adapter.download_video(
                    video_url,
                    output_dir,
                    filename
                )
                
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None
    
    def _search_platform(
        self, 
        platform: str, 
        query: str, 
        max_results: int, 
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Search a specific platform for videos.
        
        Args:
            platform: Platform to search
            query: Search query
            max_results: Maximum number of results
            filters: Additional filters
            
        Returns:
            List of video results from the platform
        """
        adapter = self.platform_adapters.get(platform)
        if adapter and hasattr(adapter, 'search_videos'):
            try:
                platform_max_results = PLATFORM_CONFIGS.get(platform, {}).get('max_results', max_results)
                actual_max = min(max_results, platform_max_results)
                
                # Call the adapter's search method
                return adapter.search_videos(query, actual_max)
            except Exception as e:
                logger.error(f"Error calling {platform} adapter's search_videos: {e}")
                
        # Fallback to dummy results
        return self._create_dummy_results(platform, query, max_results)
    
    def _detect_platform_from_url(self, url: str) -> Optional[str]:
        """
        Detect which platform a URL belongs to.
        
        Args:
            url: URL to analyze
            
        Returns:
            Platform identifier or None if not recognized
        """
        url = url.lower()
        
        platform_domains = {
            "youtube": ["youtube.com", "youtu.be"],
            "bilibili": ["bilibili.com"],
            "tiktok": ["tiktok.com", "douyin.com"],
            "weibo": ["weibo.com"],
            "facebook": ["facebook.com", "fb.com"]
        }
        
        for platform, domains in platform_domains.items():
            if any(domain in url for domain in domains):
                return platform
                
        return None
    
    def _create_dummy_adapter(self, platform: str) -> Any:
        """
        Create a dummy adapter for a platform.
        
        Args:
            platform: Platform identifier
            
        Returns:
            Dummy adapter object with search_videos and download_video methods
        """
        # Create a simple object with required methods
        class DummyAdapter:
            def search_videos(self, query, max_results=10):
                return self._create_dummy_results(platform, query, max_results)
                
            def download_video(self, url, output_dir, filename=None, **kwargs):
                if not filename:
                    timestamp = int(time.time())
                    filename = f"video_{platform}_{timestamp}.mp4"
                    
                file_path = os.path.join(output_dir, filename)
                try:
                    with open(file_path, 'w') as f:
                        f.write(f"Simulated video download from {url}")
                    return file_path
                except Exception as e:
                    logger.error(f"Error in dummy adapter download: {e}")
                    return None
                    
            def _create_dummy_results(self, platform, query, max_results):
                results = []
                for i in range(1, min(max_results + 1, 11)):
                    results.append({
                        'title': f"{query} - Result {i} from {platform}",
                        'url': f"https://{platform}.com/video/{i}",
                        'author': f"Author {i}",
                        'views': i * 1000,
                        'duration': f"{i}:00",
                        'published': f"2025-05-0{i}",
                        'thumbnail': None,
                        'description': f"This is a sample description for {query} result {i} from {platform}."
                    })
                return results
        
        return DummyAdapter()
    
    def _create_dummy_results(self, platform: str, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Create dummy search results for testing.
        
        Args:
            platform: Platform identifier
            query: Search query
            max_results: Maximum number of results to generate
            
        Returns:
            List of dummy search results
        """
        results = []
        for i in range(1, min(max_results + 1, 11)):
            results.append({
                'title': f"{query} - Result {i} from {platform}",
                'url': f"https://{platform}.com/video/{i}",
                'author': f"Author {i}",
                'views': i * 1000,
                'duration': f"{i}:00",
                'published': f"2025-05-0{i}",
                'thumbnail': None,
                'description': f"This is a sample description for {query} result {i} from {platform}."
            })
        return results


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
 
 