"""
多平台视频爬虫示例
展示如何使用爬虫管理器搜索和下载多个平台的视频
"""
import os
import sys
import logging
import argparse
import json
from typing import Dict, List

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.modules.vca.crawler_manager import CrawlerManager

def setup_logging(level: int = logging.INFO) -> None:
    """设置日志配置"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('crawler.log', encoding='utf-8')
        ]
    )

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='多平台视频爬虫')
    
    parser.add_argument('--query', '-q', type=str, required=True,
                        help='搜索关键词')
    
    parser.add_argument('--platforms', '-p', type=str, nargs='+',
                        default=['youtube', 'bilibili'],
                        help='要搜索的平台，可选: youtube, bilibili, tiktok, weibo, facebook')
    
    parser.add_argument('--limit', '-l', type=int, default=5,
                        help='每个平台返回的结果数量')
    
    parser.add_argument('--download', '-d', action='store_true',
                        help='是否下载视频')
    
    parser.add_argument('--output', '-o', type=str, default='./downloads',
                        help='视频下载目录')
    
    parser.add_argument('--duration', type=str, choices=['short', 'medium', 'long'],
                        help='视频时长过滤')
    
    parser.add_argument('--date', type=str, choices=['today', 'week', 'month', 'year'],
                        help='上传日期过滤')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='显示详细日志')
    
    parser.add_argument('--cookie', type=str, default='',
                        help='Cookie字符串，用于某些平台的认证')
    
    parser.add_argument('--proxy', type=str, default='',
                        help='代理服务器地址')
                        
    parser.add_argument('--output-json', type=str, default='',
                        help='将结果输出到JSON文件')
    
    return parser.parse_args()

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置日志级别
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    logger = logging.getLogger('multi_crawler')
    logger.info(f"开始搜索，关键词: {args.query}, 平台: {args.platforms}")
    
    # 创建爬虫管理器
    manager = CrawlerManager(max_workers=3)
    
    # 加载平台适配器
    adapter_count = manager.load_platform_adapters()
    logger.info(f"加载了 {adapter_count} 个平台适配器")
    
    # 准备过滤条件
    filters = {}
    if args.duration:
        filters['duration'] = args.duration
    if args.date:
        filters['upload_date'] = args.date
    
    # 获取支持的平台
    supported_platforms = manager.get_supported_platforms()
    logger.info(f"支持的平台: {supported_platforms}")
    
    # 验证请求的平台是否都受支持
    for platform in args.platforms:
        if platform not in supported_platforms:
            logger.warning(f"不支持的平台: {platform}，将被跳过")
    
    # 只使用受支持的平台
    platforms = [p for p in args.platforms if p in supported_platforms]
    
    # 如果使用TikTok，需要初始化Selenium
    if 'tiktok' in platforms:
        from src.modules.vca.platform_adapters.tiktok import TiktokAdapter
        # 注册TikTok适配器
        if args.proxy:
            manager.register_platform('tiktok', lambda: TiktokAdapter(proxy=args.proxy))
        else:
            manager.register_platform('tiktok', TiktokAdapter)
    
    # 如果使用微博，需要设置Cookie
    if 'weibo' in platforms and args.cookie:
        from src.modules.vca.platform_adapters.weibo import WeiboAdapter
        # 注册微博适配器
        if args.proxy:
            manager.register_platform('weibo', lambda: WeiboAdapter(cookie=args.cookie, proxy=args.proxy))
        else:
            manager.register_platform('weibo', lambda: WeiboAdapter(cookie=args.cookie))
    
    # 如果使用B站，可以设置Cookie获取更多内容
    if 'bilibili' in platforms and args.cookie:
        from src.modules.vca.platform_adapters.bilibili import BilibiliAdapter
        # 注册B站适配器
        if args.proxy:
            manager.register_platform('bilibili', lambda: BilibiliAdapter(cookie=args.cookie, proxy=args.proxy))
        else:
            manager.register_platform('bilibili', lambda: BilibiliAdapter(cookie=args.cookie))
    
    # 如果使用Facebook，需要初始化Selenium
    if 'facebook' in platforms:
        from src.modules.vca.platform_adapters.facebook import FacebookAdapter
        # 注册Facebook适配器
        if args.proxy:
            manager.register_platform('facebook', lambda: FacebookAdapter(proxy=args.proxy))
        else:
            manager.register_platform('facebook', FacebookAdapter)
    
    # 执行多平台搜索
    try:
        results = manager.crawl_multi_platform(
            search_query=args.query,
            platforms=platforms,
            limit_per_platform=args.limit,
            filters=filters
        )
        
        # 处理搜索结果
        all_videos = []
        for platform, videos in results.items():
            logger.info(f"平台 {platform} 找到 {len(videos)} 个结果")
            
            # 打印结果
            for i, video in enumerate(videos):
                logger.info(f"\n--- {platform} 视频 {i+1} ---")
                logger.info(f"标题: {video.get('title')}")
                logger.info(f"链接: {video.get('url')}")
                logger.info(f"发布者: {video.get('channel_name', video.get('channel', video.get('author', '')))}")
                logger.info(f"时长: {video.get('duration', '未知')} 秒")
                
                # 添加到总结果列表
                video['platform'] = platform
                all_videos.append(video)
                
                # 下载视频
                if args.download and video.get('url'):
                    try:
                        # 创建平台适配器
                        if platform == 'youtube':
                            from src.modules.vca.platform_adapters.youtube import YoutubeAdapter
                            adapter = YoutubeAdapter(proxy=args.proxy)
                        elif platform == 'bilibili':
                            from src.modules.vca.platform_adapters.bilibili import BilibiliAdapter
                            adapter = BilibiliAdapter(cookie=args.cookie, proxy=args.proxy)
                        elif platform == 'tiktok':
                            from src.modules.vca.platform_adapters.tiktok import TiktokAdapter
                            adapter = TiktokAdapter(proxy=args.proxy)
                        elif platform == 'weibo':
                            from src.modules.vca.platform_adapters.weibo import WeiboAdapter
                            adapter = WeiboAdapter(cookie=args.cookie, proxy=args.proxy)
                        elif platform == 'facebook':
                            from src.modules.vca.platform_adapters.facebook import FacebookAdapter
                            adapter = FacebookAdapter(proxy=args.proxy)
                        else:
                            logger.warning(f"不支持下载 {platform} 平台视频")
                            continue
                        
                        # 创建输出目录
                        output_dir = os.path.join(args.output, platform)
                        os.makedirs(output_dir, exist_ok=True)
                        
                        # 设置文件名
                        filename = f"{platform}_{video.get('video_id', '').replace('/', '_')}" if video.get('video_id') else None
                        
                        # 下载视频
                        if platform == 'youtube':
                            file_path = adapter.download_video(
                                video_url=video.get('url'),
                                output_path=output_dir,
                                filename=filename
                            )
                        elif platform == 'bilibili':
                            file_path = adapter.download_video(
                                video_url=video.get('url'),
                                output_path=output_dir,
                                filename=filename,
                                quality=32  # 480P清晰度
                            )
                        elif platform in ('tiktok', 'weibo', 'facebook'):
                            file_path = adapter.download_video(
                                video_url=video.get('url'),
                                output_path=output_dir,
                                filename=filename
                            )
                        
                        if file_path:
                            logger.info(f"视频已下载到: {file_path}")
                            video['local_path'] = file_path
                        else:
                            logger.warning(f"下载视频失败: {video.get('url')}")
                            
                    except Exception as e:
                        logger.error(f"下载视频时发生错误: {str(e)}")
            
        # 输出结果到JSON文件
        if args.output_json:
            try:
                with open(args.output_json, 'w', encoding='utf-8') as f:
                    json.dump(all_videos, f, ensure_ascii=False, indent=2)
                logger.info(f"搜索结果已保存到: {args.output_json}")
            except Exception as e:
                logger.error(f"保存结果到JSON失败: {str(e)}")
        
        logger.info("多平台搜索完成")
        
    except Exception as e:
        logger.error(f"执行搜索时发生错误: {str(e)}")
    finally:
        # 关闭爬虫管理器
        manager.shutdown()

if __name__ == "__main__":
    main() 
 