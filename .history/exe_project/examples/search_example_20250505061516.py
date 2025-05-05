#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
示例脚本
展示如何使用视频搜索和分析功能
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from src.utils.logger import get_logger
from src.utils.proxy_manager import ProxyManager
from src.modules.vca.search_manager import SearchManager

logger = get_logger(__name__)

async def main():
    """主函数"""
    # 创建代理管理器
    proxy_manager = ProxyManager()
    
    # 创建搜索管理器
    search_manager = SearchManager(proxy_manager)
    
    try:
        # 搜索视频
        query = "python tutorial"
        logger.info(f"开始搜索: {query}")
        
        videos = await search_manager.search_videos(
            query=query,
            platforms=["youtube", "bilibili", "tiktok"],
            max_results=5,
            analyze_content=True
        )
        
        if not videos:
            logger.error("未找到视频")
            return
            
        # 过滤视频
        filtered_videos = search_manager.filter_videos(
            videos=videos,
            min_duration=60,  # 至少1分钟
            max_duration=600,  # 最多10分钟
            min_views=1000,  # 至少1000次观看
            min_date=datetime.now() - timedelta(days=30)  # 最近30天
        )
        
        if not filtered_videos:
            logger.error("过滤后没有符合条件的视频")
            return
            
        # 显示结果
        print(f"\n找到 {len(filtered_videos)} 个视频:")
        for i, video in enumerate(filtered_videos, 1):
            print(f"\n{i}. {video['title']}")
            print(f"   平台: {video['platform']}")
            print(f"   时长: {video['duration']}秒")
            print(f"   观看次数: {video['view_count']}")
            print(f"   上传时间: {video['upload_date']}")
            print(f"   相关度: {video['relevance_score']:.2f}")
            print(f"   URL: {video['url']}")
            
        # 下载视频
        print("\n开始下载视频...")
        output_dir = os.path.join(os.path.dirname(__file__), 'downloads')
        os.makedirs(output_dir, exist_ok=True)
        
        results = await search_manager.download_videos(filtered_videos, output_dir)
        
        print(f"\n下载完成，共 {len(results)} 个视频:")
        for video_id, file_path in results.items():
            print(f"- {file_path}")
            
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
        return 1
        
    return 0

if __name__ == '__main__':
    sys.exit(asyncio.run(main())) 