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
        super().__init__('tiktok', proxy_manager)
        
    async def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        搜索TikTok视频
        
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
                'count': max_results,
                'type': 1  # 1表示视频
            }
            
            # 发送搜索请求
            response = await self.request_manager.get(
                self._get_search_url(),
                headers=self._get_headers(),
                params=params
            )
            
            # 解析响应
            videos = []
            if 'item_list' in response:
                for item in response['item_list']:
                    video_info = {
                        'id': item['id'],
                        'title': item.get('desc', ''),
                        'description': item.get('desc', ''),
                        'upload_date': datetime.fromtimestamp(item['create_time']).strftime('%Y-%m-%d'),
                        'url': f"https://www.tiktok.com/@{item['author']['unique_id']}/video/{item['id']}",
                        'thumbnail_url': item['video']['cover'],
                        'author': {
                            'id': item['author']['id'],
                            'name': item['author']['unique_id']
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
            logger.error(f"TikTok搜索失败: {str(e)}")
            return []
            
    async def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        获取TikTok视频详细信息
        
        Args:
            video_id: 视频ID
            
        Returns:
            Dict[str, Any]: 视频信息
        """
        try:
            # 构建请求参数
            params = {
                'video_id': video_id
            }
            
            # 发送请求
            response = await self.request_manager.get(
                f"{self._get_base_url()}/api/video/detail",
                headers=self._get_headers(),
                params=params
            )
            
            # 解析响应
            if 'item_info' in response:
                item = response['item_info']
                
                return {
                    'duration': item['video']['duration'],
                    'view_count': item['stats']['play_count'],
                    'tags': [tag['name'] for tag in item.get('challenges', [])]
                }
                
            return {}
            
        except Exception as e:
            logger.error(f"获取TikTok视频信息失败: {str(e)}")
            return {}
            
    def _parse_duration(self, duration: int) -> int:
        """
        解析TikTok视频时长
        
        Args:
            duration: TikTok视频时长（秒）
            
        Returns:
            int: 时长（秒）
        """
        try:
            return int(duration)
        except Exception as e:
            logger.error(f"解析时长失败: {str(e)}")
            return 0 