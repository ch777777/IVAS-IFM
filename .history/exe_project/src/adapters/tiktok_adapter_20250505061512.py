#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
TikTok平台适配器模块
用于处理TikTok平台的视频搜索和信息获取
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.adapters.base_adapter import BaseAdapter
from src.utils.logger import get_logger

logger = get_logger(__name__)

class TikTokAdapter(BaseAdapter):
    """TikTok平台适配器"""
    
    def __init__(self, proxy_manager=None):
        """初始化TikTok适配器"""
        super().__init__(proxy_manager)
        self.base_url = "https://www.tiktok.com"
        self.search_url = f"{self.base_url}/search"
        self.video_url = f"{self.base_url}/video"
        
    async def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        搜索视频
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            
        Returns:
            List[Dict[str, Any]]: 视频列表
        """
        try:
            # 构建搜索参数
            params = {
                'q': query,
                't': int(datetime.now().timestamp())
            }
            
            # 发送搜索请求
            async with self._get_session() as session:
                async with session.get(self.search_url, params=params, proxy=self._get_proxy_config()) as response:
                    if response.status != 200:
                        logger.error(f"搜索请求失败: {response.status}")
                        return []
                        
                    # 解析响应内容
                    content = await response.text()
                    videos = self._parse_search_results(content, max_results)
                    
                    # 格式化视频信息
                    return [self._format_video_info(video) for video in videos]
                    
        except Exception as e:
            logger.error(f"搜索视频失败: {str(e)}")
            return []
            
    async def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        获取视频信息
        
        Args:
            video_id: 视频ID
            
        Returns:
            Optional[Dict[str, Any]]: 视频信息
        """
        try:
            # 构建视频URL
            url = f"{self.video_url}/{video_id}"
            
            # 发送请求
            async with self._get_session() as session:
                async with session.get(url, proxy=self._get_proxy_config()) as response:
                    if response.status != 200:
                        logger.error(f"获取视频信息失败: {response.status}")
                        return None
                        
                    # 解析响应内容
                    content = await response.text()
                    video_info = self._parse_video_info(content)
                    
                    if not video_info:
                        return None
                        
                    # 添加视频ID
                    video_info['id'] = video_id
                    
                    # 格式化视频信息
                    return self._format_video_info(video_info)
                    
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
            return None
            
    def _parse_search_results(self, content: str, max_results: int) -> List[Dict[str, Any]]:
        """
        解析搜索结果
        
        Args:
            content: 响应内容
            max_results: 最大结果数
            
        Returns:
            List[Dict[str, Any]]: 视频列表
        """
        videos = []
        
        # 使用正则表达式提取视频信息
        pattern = r'<div class="tiktok-1qb12g8-DivItemContainer[^"]*".*?<a href="/video/([^"]+)".*?<img src="([^"]+)".*?<h3 class="[^"]*">([^<]+)</h3>.*?<strong[^>]*>([^<]+)</strong>.*?<span[^>]*>([^<]+)</span>'
        
        matches = re.finditer(pattern, content, re.DOTALL)
        for match in matches:
            if len(videos) >= max_results:
                break
                
            video_id, thumbnail, title, view_count, upload_date = match.groups()
            
            # 解析观看次数
            view_count = int(re.sub(r'[^\d]', '', view_count))
            
            # 解析上传日期
            upload_date = self._parse_upload_date(upload_date)
            
            videos.append({
                'id': video_id,
                'title': title,
                'thumbnail': thumbnail,
                'view_count': view_count,
                'duration': 0,  # TikTok API需要额外请求获取时长
                'upload_date': upload_date,
                'url': f"{self.video_url}/{video_id}"
            })
            
        return videos
        
    def _parse_video_info(self, content: str) -> Optional[Dict[str, Any]]:
        """
        解析视频信息
        
        Args:
            content: 响应内容
            
        Returns:
            Optional[Dict[str, Any]]: 视频信息
        """
        try:
            # 提取视频信息
            title_pattern = r'<h1[^>]*>([^<]+)</h1>'
            description_pattern = r'<div class="[^"]*desc[^"]*">([^<]+)</div>'
            view_count_pattern = r'<strong[^>]*>([^<]+)</strong>'
            like_count_pattern = r'<strong[^>]*>([^<]+)</strong>'
            upload_date_pattern = r'<span[^>]*>([^<]+)</span>'
            
            title = re.search(title_pattern, content)
            description = re.search(description_pattern, content)
            view_count = re.search(view_count_pattern, content)
            like_count = re.search(like_count_pattern, content)
            upload_date = re.search(upload_date_pattern, content)
            
            if not title:
                return None
                
            return {
                'title': title.group(1),
                'description': description.group(1) if description else '',
                'view_count': int(re.sub(r'[^\d]', '', view_count.group(1))) if view_count else 0,
                'like_count': int(re.sub(r'[^\d]', '', like_count.group(1))) if like_count else 0,
                'upload_date': upload_date.group(1) if upload_date else '',
                'tags': []  # TikTok API需要额外请求获取标签
            }
            
        except Exception as e:
            logger.error(f"解析视频信息失败: {str(e)}")
            return None
            
    def _parse_upload_date(self, date_str: str) -> str:
        """
        解析上传日期
        
        Args:
            date_str: 日期字符串，格式为 "X天前"、"X周前"、"X月前"、"X年前"
            
        Returns:
            str: 日期字符串，格式为 "YYYY-MM-DD"
        """
        try:
            now = datetime.now()
            
            if '天前' in date_str:
                days = int(re.sub(r'[^\d]', '', date_str))
                date = now.replace(day=now.day - days)
            elif '周前' in date_str:
                weeks = int(re.sub(r'[^\d]', '', date_str))
                date = now.replace(day=now.day - weeks * 7)
            elif '月前' in date_str:
                months = int(re.sub(r'[^\d]', '', date_str))
                date = now.replace(month=now.month - months)
            elif '年前' in date_str:
                years = int(re.sub(r'[^\d]', '', date_str))
                date = now.replace(year=now.year - years)
            else:
                return date_str
                
            return date.strftime('%Y-%m-%d')
            
        except Exception:
            return date_str 