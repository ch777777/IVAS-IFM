#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
微博平台适配器模块
用于处理微博平台的视频搜索和信息获取
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.adapters.base_adapter import BaseAdapter
from src.utils.logger import get_logger

logger = get_logger(__name__)

class WeiboAdapter(BaseAdapter):
    """微博平台适配器"""
    
    def __init__(self, proxy_manager=None):
        """初始化微博适配器"""
        super().__init__('weibo', proxy_manager)
        
    async def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        搜索微博视频
        
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
                'xsort': 'hot',  # 按热度排序
                'page': 1,
                'count': max_results
            }
            
            # 发送搜索请求
            response = await self.request_manager.get(
                self._get_search_url(),
                headers=self._get_headers(),
                params=params
            )
            
            # 解析响应
            videos = []
            if 'data' in response and 'cards' in response['data']:
                for card in response['data']['cards']:
                    if 'mblog' in card:
                        mblog = card['mblog']
                        if 'page_info' in mblog and mblog['page_info'].get('type') == 'video':
                            video_info = {
                                'id': mblog['id'],
                                'title': mblog.get('text', ''),
                                'description': mblog.get('text', ''),
                                'upload_date': datetime.strptime(
                                    mblog['created_at'],
                                    '%a %b %d %H:%M:%S %z %Y'
                                ).strftime('%Y-%m-%d'),
                                'url': f"https://weibo.com/{mblog['user']['id']}/{mblog['bid']}",
                                'thumbnail_url': mblog['page_info']['page_pic']['url'],
                                'author': {
                                    'id': mblog['user']['id'],
                                    'name': mblog['user']['screen_name']
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
            logger.error(f"微博搜索失败: {str(e)}")
            return []
            
    async def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        获取微博视频详细信息
        
        Args:
            video_id: 视频ID
            
        Returns:
            Dict[str, Any]: 视频信息
        """
        try:
            # 构建请求参数
            params = {
                'id': video_id
            }
            
            # 发送请求
            response = await self.request_manager.get(
                f"{self._get_base_url()}/api/statuses/show",
                headers=self._get_headers(),
                params=params
            )
            
            # 解析响应
            if 'page_info' in response:
                page_info = response['page_info']
                
                return {
                    'duration': self._parse_duration(page_info.get('duration', 0)),
                    'view_count': response.get('reposts_count', 0) + response.get('comments_count', 0),
                    'tags': [tag['name'] for tag in response.get('tags', [])]
                }
                
            return {}
            
        except Exception as e:
            logger.error(f"获取微博视频信息失败: {str(e)}")
            return {}
            
    def _parse_duration(self, duration: int) -> int:
        """
        解析微博视频时长
        
        Args:
            duration: 微博视频时长（秒）
            
        Returns:
            int: 时长（秒）
        """
        try:
            return int(duration)
        except Exception as e:
            logger.error(f"解析时长失败: {str(e)}")
            return 0 