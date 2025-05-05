#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
B站平台适配器模块
用于处理B站平台的视频搜索和信息获取
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.adapters.base_adapter import BaseAdapter
from src.utils.logger import get_logger

logger = get_logger(__name__)

class BilibiliAdapter(BaseAdapter):
    """B站平台适配器"""
    
    def __init__(self, proxy_manager=None):
        """初始化B站适配器"""
        super().__init__('bilibili', proxy_manager)
        
    async def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        搜索B站视频
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            
        Returns:
            List[Dict[str, Any]]: 视频列表
        """
        try:
            # 构建搜索参数
            params = {
                'keyword': query,
                'page': 1,
                'page_size': max_results,
                'search_type': 'video'
            }
            
            # 发送搜索请求
            response = await self.request_manager.get(
                self._get_search_url(),
                headers=self._get_headers(),
                params=params
            )
            
            # 解析响应
            videos = []
            if 'result' in response:
                for item in response['result']:
                    video_info = {
                        'id': str(item['bvid']),
                        'title': item['title'],
                        'description': item.get('description', ''),
                        'upload_date': datetime.fromtimestamp(item['pubdate']).strftime('%Y-%m-%d'),
                        'url': f"https://www.bilibili.com/video/{item['bvid']}",
                        'thumbnail_url': item['pic'],
                        'author': {
                            'id': str(item['mid']),
                            'name': item['author']
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
            logger.error(f"B站搜索失败: {str(e)}")
            return []
            
    async def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        获取B站视频详细信息
        
        Args:
            video_id: 视频ID（BVID）
            
        Returns:
            Dict[str, Any]: 视频信息
        """
        try:
            # 构建请求参数
            params = {
                'bvid': video_id
            }
            
            # 发送请求
            response = await self.request_manager.get(
                f"{self._get_base_url()}/x/web-interface/view",
                headers=self._get_headers(),
                params=params
            )
            
            # 解析响应
            if 'data' in response:
                data = response['data']
                
                # 解析时长
                duration = self._parse_duration(data['duration'])
                
                return {
                    'duration': duration,
                    'view_count': data['stat']['view'],
                    'tags': [tag['tag_name'] for tag in data.get('tags', [])]
                }
                
            return {}
            
        except Exception as e:
            logger.error(f"获取B站视频信息失败: {str(e)}")
            return {}
            
    def _parse_duration(self, duration: int) -> int:
        """
        解析B站视频时长
        
        Args:
            duration: B站视频时长（秒）
            
        Returns:
            int: 时长（秒）
        """
        try:
            return int(duration)
        except Exception as e:
            logger.error(f"解析时长失败: {str(e)}")
            return 0 