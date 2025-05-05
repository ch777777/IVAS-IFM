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
        super().__init__('youtube', proxy_manager)
        
    async def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        搜索YouTube视频
        
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
                'max_results': max_results,
                'part': 'snippet',
                'type': 'video',
                'key': self.config.get('api_key', '')
            }
            
            # 发送搜索请求
            response = await self.request_manager.get(
                self._get_search_url(),
                headers=self._get_headers(),
                params=params
            )
            
            # 解析响应
            videos = []
            if 'items' in response:
                for item in response['items']:
                    video_info = {
                        'id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'upload_date': item['snippet']['publishedAt'].split('T')[0],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                        'thumbnail_url': item['snippet']['thumbnails']['high']['url'],
                        'author': {
                            'id': item['snippet']['channelId'],
                            'name': item['snippet']['channelTitle']
                        }
                    }
                    
                    # 获取视频详细信息
                    try:
                        details = await self.get_video_info(video_info['id'])
                        video_info.update({
                            'duration': details.get('duration', 0),
                            'view_count': details.get('view_count', 0),
                            'tags': details.get('tags', [])
                        })
                    except Exception as e:
                        logger.warning(f"获取视频详细信息失败: {str(e)}")
                        
                    videos.append(self._format_video_info(video_info))
                    
            return videos
            
        except Exception as e:
            logger.error(f"YouTube搜索失败: {str(e)}")
            return []
            
    async def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        获取YouTube视频详细信息
        
        Args:
            video_id: 视频ID
            
        Returns:
            Dict[str, Any]: 视频信息
        """
        try:
            # 构建请求参数
            params = {
                'id': video_id,
                'part': 'contentDetails,statistics',
                'key': self.config.get('api_key', '')
            }
            
            # 发送请求
            response = await self.request_manager.get(
                f"{self._get_base_url()}/videos",
                headers=self._get_headers(),
                params=params
            )
            
            # 解析响应
            if 'items' in response and response['items']:
                item = response['items'][0]
                
                # 解析时长
                duration = self._parse_duration(item['contentDetails']['duration'])
                
                return {
                    'duration': duration,
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'tags': item.get('snippet', {}).get('tags', [])
                }
                
            return {}
            
        except Exception as e:
            logger.error(f"获取YouTube视频信息失败: {str(e)}")
            return {}
            
    def _parse_duration(self, duration: str) -> int:
        """
        解析ISO 8601格式的时长
        
        Args:
            duration: ISO 8601格式的时长字符串
            
        Returns:
            int: 时长（秒）
        """
        try:
            # 匹配时长格式
            pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
            match = re.match(pattern, duration)
            
            if match:
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                seconds = int(match.group(3) or 0)
                
                return hours * 3600 + minutes * 60 + seconds
                
            return 0
            
        except Exception as e:
            logger.error(f"解析时长失败: {str(e)}")
            return 0 