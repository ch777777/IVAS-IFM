#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import asyncio
import json
from datetime import datetime, timedelta
from src.modules.vca.crawler_manager import CrawlerManager

async def main():
    # 初始化爬虫管理器
    manager = CrawlerManager()
    
    # 搜索参数
    query = "Python教程"
    platforms = ["youtube", "bilibili", "tiktok"]
    max_results = 10
    
    # 过滤条件
    filters = {
        'duration_range': (60, 1800),  # 1分钟到30分钟
        'upload_date_range': (
            (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            datetime.now().strftime('%Y-%m-%d')
        ),
        'min_views': 1000
    }
    
    try:
        # 执行搜索
        print(f"正在搜索: {query}")
        results = await manager.search_videos(
            query=query,
            platforms=platforms,
            max_results=max_results,
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
        
        # 保存结果到JSON文件
        output_file = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"搜索过程中出错: {str(e)}")
    finally:
        # 关闭爬虫管理器
        manager.close()

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main()) 