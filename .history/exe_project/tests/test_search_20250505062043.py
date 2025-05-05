#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
测试脚本
用于测试视频搜索和分析功能
"""

import os
import sys
import asyncio
import unittest
from datetime import datetime, timedelta
from src.utils.logger import get_logger
from src.utils.proxy_manager import ProxyManager
from src.modules.vca.search_manager import SearchManager

logger = get_logger(__name__)

class TestSearchManager(unittest.TestCase):
    """测试搜索管理器"""
    
    def setUp(self):
        """测试前准备"""
        self.proxy_manager = ProxyManager()
        self.search_manager = SearchManager(self.proxy_manager)
        
    async def async_test_search_videos(self):
        """测试视频搜索"""
        # 测试基本搜索
        videos = await self.search_manager.search_videos(
            query="python tutorial",
            platforms=["youtube", "bilibili"],
            max_results=5,
            analyze_content=True
        )
        
        self.assertIsNotNone(videos)
        self.assertGreater(len(videos), 0)
        
        # 验证视频信息
        video = videos[0]
        self.assertIn('title', video)
        self.assertIn('platform', video)
        self.assertIn('duration', video)
        self.assertIn('view_count', video)
        self.assertIn('upload_date', video)
        self.assertIn('url', video)
        self.assertIn('relevance_score', video)
        
        # 测试过滤功能
        filtered_videos = self.search_manager.filter_videos(
            videos=videos,
            min_duration=60,
            max_duration=600,
            min_views=1000,
            min_date=datetime.now() - timedelta(days=30)
        )
        
        self.assertLessEqual(len(filtered_videos), len(videos))
        
    async def async_test_download_video(self):
        """测试视频下载"""
        # 搜索视频
        videos = await self.search_manager.search_videos(
            query="python tutorial",
            platforms=["youtube"],
            max_results=1,
            analyze_content=False
        )
        
        if not videos:
            self.skipTest("未找到测试视频")
            
        # 测试下载
        output_dir = os.path.join(os.path.dirname(__file__), 'downloads')
        os.makedirs(output_dir, exist_ok=True)
        
        file_path = await self.search_manager.download_video(videos[0], output_dir)
        self.assertIsNotNone(file_path)
        self.assertTrue(os.path.exists(file_path))
        
        # 清理测试文件
        os.remove(file_path)
        
    def test_search_videos(self):
        """运行搜索测试"""
        asyncio.run(self.async_test_search_videos())
        
    def test_download_video(self):
        """运行下载测试"""
        asyncio.run(self.async_test_download_video())

if __name__ == '__main__':
    unittest.main() 