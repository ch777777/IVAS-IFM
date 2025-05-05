"""
向量匹配引擎
负责处理向量化后的查询与素材标签匹配
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class PrecisionMatcher:
    """精准匹配引擎，基于语义向量相似度"""
    
    def __init__(self, model_name='paraphrase-multilingual-mpnet-base-v2'):
        """
        初始化精准匹配引擎
        
        Args:
            model_name: 向量化模型名称，默认使用多语言模型
        """
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"成功加载向量化模型: {model_name}")
        except Exception as e:
            logger.error(f"向量化模型加载失败: {str(e)}")
            raise
        
    def match(self, user_query, video_tags, top_n=3):
        """
        匹配用户查询与视频标签
        
        Args:
            user_query: 用户搜索字符串
            video_tags: 视频标签列表
            top_n: 返回最匹配的结果数量
            
        Returns:
            匹配结果列表，每个元素为(标签, 相似度)元组
        """
        # 用户搜索词向量化
        query_embedding = self.model.encode(user_query)
        
        # 视频标签向量化
        tag_embeddings = self.model.encode(video_tags)
        
        # 计算余弦相似度
        similarities = cosine_similarity(
            query_embedding.reshape(1, -1), 
            tag_embeddings
        )[0]
        
        # 返回top_n个最匹配的结果
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        return [(video_tags[i], float(similarities[i])) for i in top_indices]
    
    def batch_match(self, user_query, video_tags_list, top_n=3):
        """
        批量匹配用户查询与多个视频的标签
        
        Args:
            user_query: 用户搜索字符串
            video_tags_list: 多个视频标签列表的列表，每个元素对应一个视频的标签
            top_n: 返回最匹配的结果数量
            
        Returns:
            匹配结果列表，按相似度降序排序
        """
        # 用户搜索词向量化
        query_embedding = self.model.encode(user_query)
        
        results = []
        
        # 处理每个视频的标签
        for video_id, tags in enumerate(video_tags_list):
            if not tags:
                continue
                
            # 视频标签向量化
            tag_embeddings = self.model.encode(tags)
            
            # 计算该视频中最相关标签的相似度
            max_similarity = np.max(cosine_similarity(
                query_embedding.reshape(1, -1), 
                tag_embeddings
            )[0])
            
            results.append((video_id, max_similarity))
        
        # 按相似度降序排序
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        
        # 返回top_n个结果
        return sorted_results[:top_n]


# 示例用法
if __name__ == "__main__":
    # 初始化匹配引擎
    matcher = PrecisionMatcher()
    
    # 模拟用户查询
    user_query = "户外运动背包防水测试"
    
    # 模拟视频标签
    video_tags = [
        "登山装备", 
        "产品测评", 
        "防水实验", 
        "用户实拍",
        "背包品牌",
        "户外活动"
    ]
    
    # 执行匹配
    matches = matcher.match(user_query, video_tags)
    
    # 打印结果
    print("查询:", user_query)
    print("匹配结果:")
    for tag, score in matches:
        print(f"  - {tag}: {score:.4f}") 
 