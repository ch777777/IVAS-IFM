#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
相关性评分模块
用于计算搜索结果的相关性得分
"""

import re
from typing import Dict, Any, List
from src.utils.logger import get_logger

logger = get_logger(__name__)

class RelevanceScorer:
    """相关性评分器"""
    
    def __init__(self):
        """初始化相关性评分器"""
        self.weights = {
            'title_match': 0.4,      # 标题匹配权重
            'description_match': 0.2, # 描述匹配权重
            'view_count': 0.15,      # 观看次数权重
            'upload_date': 0.15,     # 上传日期权重
            'duration': 0.1          # 视频时长权重
        }
        
    def calculate_score(self, video: Dict[str, Any], query: str) -> float:
        """
        计算视频的相关性得分
        
        Args:
            video: 视频信息
            query: 搜索关键词
            
        Returns:
            float: 相关性得分（0-1之间）
        """
        try:
            # 计算各个维度的得分
            title_score = self._calculate_title_score(video.get('title', ''), query)
            desc_score = self._calculate_description_score(video.get('description', ''), query)
            view_score = self._calculate_view_score(video.get('view_count', 0))
            date_score = self._calculate_date_score(video.get('upload_date', ''))
            duration_score = self._calculate_duration_score(video.get('duration', 0))
            
            # 计算加权总分
            total_score = (
                title_score * self.weights['title_match'] +
                desc_score * self.weights['description_match'] +
                view_score * self.weights['view_count'] +
                date_score * self.weights['upload_date'] +
                duration_score * self.weights['duration']
            )
            
            return min(max(total_score, 0), 1)  # 确保得分在0-1之间
            
        except Exception as e:
            logger.error(f"计算相关性得分时出错: {str(e)}")
            return 0.0
            
    def _calculate_title_score(self, title: str, query: str) -> float:
        """
        计算标题匹配得分
        
        Args:
            title: 视频标题
            query: 搜索关键词
            
        Returns:
            float: 标题匹配得分（0-1之间）
        """
        if not title or not query:
            return 0.0
            
        # 将标题和查询转换为小写
        title_lower = title.lower()
        query_lower = query.lower()
        
        # 计算关键词匹配数
        query_words = set(query_lower.split())
        title_words = set(title_lower.split())
        matched_words = query_words.intersection(title_words)
        
        # 计算匹配率
        match_ratio = len(matched_words) / len(query_words) if query_words else 0
        
        # 考虑关键词顺序
        order_bonus = 0.0
        if query_lower in title_lower:
            order_bonus = 0.2
            
        return min(match_ratio + order_bonus, 1.0)
        
    def _calculate_description_score(self, description: str, query: str) -> float:
        """
        计算描述匹配得分
        
        Args:
            description: 视频描述
            query: 搜索关键词
            
        Returns:
            float: 描述匹配得分（0-1之间）
        """
        if not description or not query:
            return 0.0
            
        # 将描述和查询转换为小写
        desc_lower = description.lower()
        query_lower = query.lower()
        
        # 计算关键词匹配数
        query_words = set(query_lower.split())
        desc_words = set(desc_lower.split())
        matched_words = query_words.intersection(desc_words)
        
        # 计算匹配率
        match_ratio = len(matched_words) / len(query_words) if query_words else 0
        
        # 考虑关键词密度
        density = len(matched_words) / len(desc_words) if desc_words else 0
        
        return min(match_ratio * 0.7 + density * 0.3, 1.0)
        
    def _calculate_view_score(self, view_count: int) -> float:
        """
        计算观看次数得分
        
        Args:
            view_count: 观看次数
            
        Returns:
            float: 观看次数得分（0-1之间）
        """
        if not view_count:
            return 0.0
            
        # 使用对数函数计算得分
        return min(1.0, 0.5 + 0.5 * (1 / (1 + 1000000 / view_count)))
        
    def _calculate_date_score(self, upload_date: str) -> float:
        """
        计算上传日期得分
        
        Args:
            upload_date: 上传日期（YYYY-MM-DD格式）
            
        Returns:
            float: 上传日期得分（0-1之间）
        """
        if not upload_date:
            return 0.0
            
        try:
            # 解析日期
            from datetime import datetime
            upload_time = datetime.strptime(upload_date, '%Y-%m-%d')
            current_time = datetime.now()
            
            # 计算时间差（天）
            days_diff = (current_time - upload_time).days
            
            # 使用指数衰减函数计算得分
            return min(1.0, 1.0 * (0.95 ** days_diff))
            
        except Exception as e:
            logger.error(f"计算上传日期得分时出错: {str(e)}")
            return 0.0
            
    def _calculate_duration_score(self, duration: int) -> float:
        """
        计算视频时长得分
        
        Args:
            duration: 视频时长（秒）
            
        Returns:
            float: 视频时长得分（0-1之间）
        """
        if not duration:
            return 0.0
            
        # 理想时长范围（5-30分钟）
        min_duration = 300  # 5分钟
        max_duration = 1800  # 30分钟
        
        if duration < min_duration:
            return duration / min_duration
        elif duration > max_duration:
            return max(0.0, 1.0 - (duration - max_duration) / max_duration)
        else:
            return 1.0
            
    def set_weights(self, weights: Dict[str, float]):
        """
        设置评分权重
        
        Args:
            weights: 权重字典
        """
        # 验证权重
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError("权重之和必须为1")
            
        self.weights = weights 