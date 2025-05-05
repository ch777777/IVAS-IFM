#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
命令行界面模块
用于测试和演示视频搜索和分析功能
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime, timedelta
from typing import List, Optional
from src.utils.logger import get_logger
from src.utils.proxy_manager import ProxyManager
from src.modules.vca.search_manager import SearchManager

logger = get_logger(__name__)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='视频搜索和分析工具')
    
    # 搜索参数
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('-p', '--platforms', nargs='+', help='要搜索的平台列表')
    parser.add_argument('-n', '--max-results', type=int, default=10, help='每个平台的最大结果数')
    parser.add_argument('--no-analyze', action='store_true', help='不分析视频内容')
    
    # 过滤参数
    parser.add_argument('--min-duration', type=int, help='最小时长（秒）')
    parser.add_argument('--max-duration', type=int, help='最大时长（秒）')
    parser.add_argument('--min-views', type=int, help='最小观看次数')
    parser.add_argument('--max-views', type=int, help='最大观看次数')
    parser.add_argument('--days', type=int, help='最近N天内的视频')
    
    # 下载参数
    parser.add_argument('-d', '--download', action='store_true', help='下载视频')
    parser.add_argument('-o', '--output-dir', help='下载输出目录')
    
    return parser.parse_args()

async def main():
    """主函数"""
    args = parse_args()
    
    # 创建代理管理器
    proxy_manager = ProxyManager()
    
    # 创建搜索管理器
    search_manager = SearchManager(proxy_manager)
    
    try:
        # 搜索视频
        logger.info(f"开始搜索: {args.query}")
        videos = await search_manager.search_videos(
            query=args.query,
            platforms=args.platforms,
            max_results=args.max_results,
            analyze_content=not args.no_analyze
        )
        
        if not videos:
            logger.error("未找到视频")
            return
            
        # 应用过滤条件
        min_date = None
        if args.days:
            min_date = datetime.now() - timedelta(days=args.days)
            
        filtered_videos = search_manager.filter_videos(
            videos=videos,
            min_duration=args.min_duration,
            max_duration=args.max_duration,
            min_views=args.min_views,
            max_views=args.max_views,
            min_date=min_date,
            platforms=args.platforms
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
            if 'relevance_score' in video:
                print(f"   相关度: {video['relevance_score']:.2f}")
            print(f"   URL: {video['url']}")
            
        # 下载视频
        if args.download:
            print("\n开始下载视频...")
            output_dir = args.output_dir or os.path.join(os.path.dirname(__file__), 'downloads')
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