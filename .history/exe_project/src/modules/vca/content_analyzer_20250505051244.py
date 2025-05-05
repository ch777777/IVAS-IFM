#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
视频内容分析器模块
用于分析视频内容和关键词匹配
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
import torch
from transformers import CLIPProcessor, CLIPModel
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ContentAnalyzer:
    """视频内容分析器"""
    
    def __init__(self):
        """初始化内容分析器"""
        # 初始化CLIP模型用于图像-文本匹配
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
    async def analyze_video(self, video_path: str, query: str, sample_interval: int = 30) -> Dict[str, Any]:
        """
        分析视频内容
        
        Args:
            video_path: 视频文件路径
            query: 搜索关键词
            sample_interval: 采样间隔（秒）
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            # 打开视频文件
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"无法打开视频文件: {video_path}")
                return None
                
            # 获取视频信息
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            
            # 计算采样帧
            sample_frames = []
            frame_interval = int(fps * sample_interval)
            
            for frame_idx in range(0, total_frames, frame_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    sample_frames.append(frame)
                    
            cap.release()
            
            # 分析采样帧
            relevance_scores = []
            for frame in sample_frames:
                score = self._analyze_frame(frame, query)
                relevance_scores.append(score)
                
            # 计算平均相关度
            avg_relevance = np.mean(relevance_scores)
            
            # 生成分析报告
            analysis_result = {
                'video_path': video_path,
                'duration': duration,
                'sample_count': len(sample_frames),
                'relevance_score': float(avg_relevance),
                'frame_scores': [float(score) for score in relevance_scores],
                'query': query
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"视频分析失败: {str(e)}")
            return None
            
    def _analyze_frame(self, frame: np.ndarray, query: str) -> float:
        """
        分析单个视频帧
        
        Args:
            frame: 视频帧
            query: 搜索关键词
            
        Returns:
            float: 相关度得分 (0-1)
        """
        try:
            # 预处理图像
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            inputs = self.processor(
                images=image,
                text=query,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            # 获取图像和文本特征
            image_features = self.model.get_image_features(inputs["pixel_values"])
            text_features = self.model.get_text_features(inputs["input_ids"])
            
            # 计算相似度
            similarity = torch.nn.functional.cosine_similarity(
                image_features, text_features
            )
            
            return float(similarity.item())
            
        except Exception as e:
            logger.error(f"帧分析失败: {str(e)}")
            return 0.0
            
    async def analyze_videos(self, videos: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        批量分析视频
        
        Args:
            videos: 视频信息列表
            query: 搜索关键词
            
        Returns:
            List[Dict[str, Any]]: 分析结果列表
        """
        results = []
        for video in videos:
            if 'video_path' in video:
                analysis = await self.analyze_video(video['video_path'], query)
                if analysis:
                    # 合并原始视频信息和分析结果
                    video.update(analysis)
                    results.append(video)
                    
        # 按相关度排序
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results 