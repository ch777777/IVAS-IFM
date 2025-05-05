#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
相关性评分器模块
用于计算视频与搜索关键词的相关性得分
"""

from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)

class RelevanceScorer:
    """相关性评分器"""
    
    def __init__(self):
        """初始化相关性评分器"""
        # 定义评分权重
        self.weights = {
            'title': 0.4,      # 标题相关度权重
            'description': 0.2, # 描述相关度权重
            'tags': 0.2,       # 标签相关度权重
            'interaction': 0.2  # 互动指标权重
        }
        
        # 定义互动指标的最大值
        self.max_values = {
            'views': 1000000,   # 最大观看数
            'likes': 100000,    # 最大点赞数
            'comments': 10000   # 最大评论数
        }
        
    def calculate_score(self, video: Dict[str, Any], query: str) -> float:
        """
        计算视频与搜索关键词的相关性得分
        
        Args:
            video: 视频信息
            query: 搜索关键词
            
        Returns:
            float: 相关性得分 (0-1)
        """
        try:
            score = 0.0
            query = query.lower()
            
            # 计算标题相关度
            title = video.get('title', '').lower()
            if query in title:
                score += self.weights['title']
                
            # 计算描述相关度
            description = video.get('description', '').lower()
            if query in description:
                score += self.weights['description']
                
            # 计算标签相关度
            tags = [tag.lower() for tag in video.get('tags', [])]
            if query in tags:
                score += self.weights['tags']
                
            # 计算互动指标得分
            interaction_score = self._calculate_interaction_score(video)
            score += interaction_score * self.weights['interaction']
            
            return min(score, 1.0)  # 确保分数不超过1
            
        except Exception as e:
            logger.error(f"计算相关性得分失败: {str(e)}")
            return 0.0
            
    def _calculate_interaction_score(self, video: Dict[str, Any]) -> float:
        """
        计算互动指标得分
        
        Args:
            video: 视频信息
            
        Returns:
            float: 互动指标得分 (0-1)
        """
        try:
            # 获取互动数据
            view_count = video.get('view_count', 0)
            like_count = video.get('like_count', 0)
            comment_count = video.get('comment_count', 0)
            
            # 归一化互动指标
            view_score = min(view_count / self.max_values['views'], 1)
            like_score = min(like_count / self.max_values['likes'], 1)
            comment_score = min(comment_count / self.max_values['comments'], 1)
            
            # 计算加权平均分
            interaction_score = (
                view_score * 0.5 +    # 观看数权重
                like_score * 0.3 +    # 点赞数权重
                comment_score * 0.2    # 评论数权重
            )
            
            return interaction_score
            
        except Exception as e:
            logger.error(f"计算互动指标得分失败: {str(e)}")
            return 0.0 