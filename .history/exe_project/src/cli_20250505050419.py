#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import argparse
import asyncio
import json
from datetime import datetime, timedelta
from src.modules.vca.crawler_manager import CrawlerManager

def parse_args():
    parser = argparse.ArgumentParser(description='IVAS-IFM 视频搜索工具')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('-p', '--platforms', nargs='+', 
                      default=['youtube', 'bilibili', 'tiktok'],
                      help='要搜索的平台列表')
    parser.add_argument('-n', '--max-results', type=int, default=10,
                      help='每个平台的最大结果数')
    parser.add_argument('-d', '--duration', nargs=2, type=int,
                      help='视频时长范围（秒）')
    parser.add_argument('-u', '--upload-date', nargs=2,
                      help='上传日期范围（YYYY-MM-DD）')
    parser.add_argument('-v', '--min-views', type=int,
                      help='最小观看次数')
    parser.add_argument('-o', '--output',
                      help='输出JSON文件的路径')
    return parser.parse_args()

async def main():
    args = parse_args()
    
    # 初始化爬虫管理器
    manager = CrawlerManager()
    
    # 构建过滤条件
    filters = {}
    if args.duration:
        filters['duration_range'] = tuple(args.duration)
    if args.upload_date:
        filters['upload_date_range'] = tuple(args.upload_date)
    if args.min_views:
        filters['min_views'] = args.min_views
    
    try:
        # 执行搜索
        print(f"正在搜索: {args.query}")
        print(f"平台: {', '.join(args.platforms)}")
        if filters:
            print("过滤条件:")
            for key, value in filters.items():
                print(f"  - {key}: {value}")
        
        results = await manager.search_videos(
            query=args.query,
            platforms=args.platforms,
            max_results=args.max_results,
            filters=filters
        )
        
        # 打印结果
        print(f"\n找到 {len(results)} 个相关视频:")
        for i, video in enumerate(results, 1):
            print(f"\n{i}. {video['title']}")
            print(f"   平台: {video['platform']}")
            print(f"   相关度: {video['relevance_score']:.2f}")
            print(f"   时长: {video['duration']}秒")
            print(f"   观看数: {video['view_count']}")
            print(f"   链接: {video['url']}")
        
        # 保存结果
        output_file = args.output or f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"搜索过程中出错: {str(e)}")
    finally:
        manager.close()

if __name__ == "__main__":
    asyncio.run(main()) 