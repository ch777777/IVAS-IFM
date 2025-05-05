#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
YouTube平台适配器模块
用于处理YouTube平台的视频搜索和信息获取
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.adapters.base_adapter import BaseAdapter
from src.utils.logger import get_logger

logger = get_logger(__name__)

class YouTubeAdapter(BaseAdapter):
    """YouTube平台适配器"""
    
    def __init__(self, proxy_manager=None):
        """初始化YouTube适配器"""
        super().__init__(proxy_manager)
        self.base_url = "https://www.youtube.com"
        self.search_url = f"{self.base_url}/results"
        self.video_url = f"{self.base_url}/watch"
        
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
                'search_query': query,
                'sp': 'CAI%253D'  # 按相关性排序
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
            url = f"{self.video_url}?v={video_id}"
            
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
        pattern = r'{"videoRenderer":{"videoId":"([^"]+)","thumbnail":{"thumbnails":\[{"url":"([^"]+)"[^}]+}],"title":{"runs":\[{"text":"([^"]+)"[^}]+}],"viewCountText":{"simpleText":"([^"]+)"[^}]+},"lengthText":{"simpleText":"([^"]+)"[^}]+},"publishedTimeText":{"simpleText":"([^"]+)"[^}]+}'
        
        matches = re.finditer(pattern, content)
        for match in matches:
            if len(videos) >= max_results:
                break
                
            video_id, thumbnail, title, view_count, duration, upload_date = match.groups()
            
            # 解析观看次数
            view_count = int(re.sub(r'[^\d]', '', view_count))
            
            # 解析时长
            duration = self._parse_duration(duration)
            
            # 解析上传日期
            upload_date = self._parse_upload_date(upload_date)
            
            videos.append({
                'id': video_id,
                'title': title,
                'thumbnail': thumbnail,
                'view_count': view_count,
                'duration': duration,
                'upload_date': upload_date,
                'url': f"{self.video_url}?v={video_id}"
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
            title_pattern = r'"title":"([^"]+)"'
            description_pattern = r'"description":{"simpleText":"([^"]+)"'
            view_count_pattern = r'"viewCount":{"simpleText":"([^"]+)"'
            like_count_pattern = r'"likeCount":{"simpleText":"([^"]+)"'
            upload_date_pattern = r'"uploadDate":"([^"]+)"'
            
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
                'tags': []  # YouTube API需要额外请求获取标签
            }
            
        except Exception as e:
            logger.error(f"解析视频信息失败: {str(e)}")
            return None
            
    def _parse_duration(self, duration: str) -> int:
        """
        解析视频时长
        
        Args:
            duration: 时长字符串，格式为 "HH:MM:SS" 或 "MM:SS"
            
        Returns:
            int: 时长（秒）
        """
        try:
            parts = duration.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            else:
                return 0
        except Exception:
            return 0
            
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