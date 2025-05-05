#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多平台视频爬虫功能测试脚本
用于测试各个平台的搜索、获取视频信息和下载功能
支持的平台：YouTube, TikTok, Bilibili, 微博, Facebook
"""
import os
import sys
import logging
import argparse
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目根目录到系统路径
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

# 导入适配器
try:
    from src.modules.vca.platform_adapters.youtube import YoutubeAdapter
    from src.modules.vca.platform_adapters.tiktok import TiktokAdapter
    from src.modules.vca.platform_adapters.bilibili import BilibiliAdapter
    from src.modules.vca.platform_adapters.weibo import WeiboAdapter
    from src.modules.vca.platform_adapters.facebook import FacebookAdapter
except ImportError as e:
    print(f"导入适配器失败: {str(e)}")
    print("请确保项目路径正确，并且已安装必要的依赖")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('platform_test.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 定义支持的平台
SUPPORTED_PLATFORMS = {
    'youtube': YoutubeAdapter,
    'tiktok': TiktokAdapter,
    'bilibili': BilibiliAdapter,
    'weibo': WeiboAdapter,
    'facebook': FacebookAdapter
}

def get_adapter(platform: str, args: argparse.Namespace) -> Any:
    """创建指定平台的适配器实例"""
    if platform not in SUPPORTED_PLATFORMS:
        raise ValueError(f"不支持的平台: {platform}")
        
    if platform == 'youtube':
        return YoutubeAdapter(proxy=args.proxy if args.proxy else None)
    elif platform == 'tiktok':
        return TiktokAdapter(proxy=args.proxy if args.proxy else None)
    elif platform == 'bilibili':
        return BilibiliAdapter(
            cookie=args.cookie if args.cookie else None,
            proxy=args.proxy if args.proxy else None
        )
    elif platform == 'weibo':
        return WeiboAdapter(
            cookie=args.cookie if args.cookie else None,
            proxy=args.proxy if args.proxy else None
        )
    elif platform == 'facebook':
        return FacebookAdapter(
            proxy=args.proxy if args.proxy else None,
            use_selenium=args.selenium
        )
    
    return None

def test_search(platform: str, args: argparse.Namespace) -> List[Dict]:
    """测试平台搜索功能"""
    logger.info(f"测试 {platform} 平台搜索功能")
    
    try:
        adapter = get_adapter(platform, args)
        
        # 准备过滤条件
        filters = {}
        if args.duration:
            filters['duration'] = args.duration
        if args.date:
            filters['upload_date'] = args.date
            
        # 执行搜索
        logger.info(f"搜索关键词: {args.query}, 限制: {args.limit}")
        results = adapter.search_videos(
            search_query=args.query,
            limit=args.limit,
            filters=filters
        )
        
        # 输出结果
        logger.info(f"找到 {len(results)} 个视频")
        for idx, video in enumerate(results, 1):
            logger.info(f"视频 {idx}:")
            logger.info(f"  标题: {video.get('title', '未知')}")
            logger.info(f"  链接: {video.get('url', '未知')}")
            logger.info(f"  作者: {video.get('author', video.get('channel', video.get('channel_name', '未知')))}")
            
        # 释放资源
        if hasattr(adapter, 'close'):
            adapter.close()
            
        return results
        
    except Exception as e:
        logger.error(f"{platform} 搜索失败: {str(e)}")
        return []

def test_video_info(platform: str, video_url: str, args: argparse.Namespace) -> Optional[Dict]:
    """测试获取视频信息功能"""
    logger.info(f"测试 {platform} 平台获取视频信息功能")
    
    try:
        adapter = get_adapter(platform, args)
        
        # 获取视频信息
        logger.info(f"获取视频信息: {video_url}")
        video_info = adapter.get_video_info(video_url)
        
        if video_info:
            logger.info("视频信息获取成功:")
            logger.info(f"  ID: {video_info.get('id', video_info.get('video_id', '未知'))}")
            logger.info(f"  标题: {video_info.get('title', '未知')}")
            
            # 输出描述（如果存在）
            if 'text' in video_info or 'description' in video_info:
                description = video_info.get('text', video_info.get('description', ''))
                logger.info(f"  描述: {description[:50]}...")
                
            # 输出作者信息
            author = video_info.get('author', video_info.get('channel', video_info.get('channel_name', '未知')))
            logger.info(f"  作者: {author}")
            
            # 输出视频时长
            if 'duration' in video_info:
                logger.info(f"  时长: {video_info.get('duration')} 秒")
                
            # 输出上传日期
            if 'upload_date' in video_info:
                logger.info(f"  上传日期: {video_info.get('upload_date')}")
                
            # 输出视频链接（如果存在）
            if 'attachments' in video_info and 'video' in video_info['attachments']:
                logger.info(f"  视频链接: {video_info['attachments']['video'][0]}")
        else:
            logger.error("未能获取视频信息")
            
        # 释放资源
        if hasattr(adapter, 'close'):
            adapter.close()
            
        return video_info
        
    except Exception as e:
        logger.error(f"{platform} 获取视频信息失败: {str(e)}")
        return None

def test_download(platform: str, video_url: str, args: argparse.Namespace) -> Optional[str]:
    """测试视频下载功能"""
    logger.info(f"测试 {platform} 平台视频下载功能")
    
    try:
        adapter = get_adapter(platform, args)
        
        # 创建输出目录
        output_dir = os.path.join(args.output_dir, platform)
        os.makedirs(output_dir, exist_ok=True)
        
        # 构建文件名
        filename = args.filename or f"{platform}_test_video"
        
        # 下载视频
        logger.info(f"下载视频: {video_url}")
        
        if platform == 'bilibili':
            # B站需要指定清晰度
            file_path = adapter.download_video(
                video_url=video_url,
                output_path=output_dir,
                filename=filename,
                quality=32  # 480P清晰度
            )
        else:
            file_path = adapter.download_video(
                video_url=video_url,
                output_path=output_dir,
                filename=filename
            )
        
        if os.path.isfile(file_path):
            logger.info(f"视频下载成功: {file_path}")
        else:
            logger.error(f"视频下载失败: {file_path}")
            
        # 释放资源
        if hasattr(adapter, 'close'):
            adapter.close()
            
        return file_path
        
    except Exception as e:
        logger.error(f"{platform} 下载视频失败: {str(e)}")
        return None

def test_platform(platform: str, args: argparse.Namespace) -> Dict:
    """测试指定平台的所有功能"""
    results = {
        'platform': platform,
        'search': None,
        'video_info': None,
        'download': None
    }
    
    # 测试搜索功能
    search_results = test_search(platform, args)
    results['search'] = {
        'success': len(search_results) > 0,
        'count': len(search_results)
    }
    
    # 如果搜索成功且有结果，使用第一个结果测试其他功能
    if search_results:
        video_url = search_results[0].get('url')
        
        # 如果提供了特定URL，使用特定URL
        if args.url:
            video_url = args.url
            
        # 测试获取视频信息
        if hasattr(SUPPORTED_PLATFORMS[platform], 'get_video_info'):
            video_info = test_video_info(platform, video_url, args)
            results['video_info'] = {
                'success': video_info is not None,
                'video_url': video_url
            }
        
        # 测试下载功能
        if args.download and hasattr(SUPPORTED_PLATFORMS[platform], 'download_video'):
            file_path = test_download(platform, video_url, args)
            results['download'] = {
                'success': file_path is not None and os.path.isfile(file_path),
                'file_path': file_path
            }
    
    return results

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="多平台视频爬虫功能测试")
    
    # 基本参数
    parser.add_argument('--platform', '-p', type=str, required=True,
                      choices=SUPPORTED_PLATFORMS.keys(),
                      help='要测试的平台')
    parser.add_argument('--query', '-q', type=str,
                      help='搜索关键词')
    parser.add_argument('--url', '-u', type=str,
                      help='视频URL，用于测试获取视频信息和下载')
    parser.add_argument('--limit', '-l', type=int, default=5,
                      help='搜索结果数量限制')
    
    # 功能选择
    parser.add_argument('--download', '-d', action='store_true',
                      help='是否测试下载功能')
    parser.add_argument('--all', '-a', action='store_true',
                      help='测试所有功能')
    
    # 过滤条件
    parser.add_argument('--duration', type=str,
                      choices=['short', 'medium', 'long'],
                      help='视频时长过滤')
    parser.add_argument('--date', type=str,
                      choices=['today', 'week', 'month', 'year'],
                      help='上传日期过滤')
    
    # 其他配置
    parser.add_argument('--output-dir', '-o', type=str, default='./downloads',
                      help='视频下载目录')
    parser.add_argument('--filename', '-f', type=str,
                      help='下载的文件名（不含扩展名）')
    parser.add_argument('--cookie', '-c', type=str,
                      help='Cookie字符串，用于某些平台的认证')
    parser.add_argument('--proxy', type=str,
                      help='代理服务器地址')
    parser.add_argument('--selenium', '-s', action='store_true',
                      help='使用Selenium进行爬取')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='显示详细日志')
    parser.add_argument('--output-json', type=str,
                      help='将测试结果保存为JSON文件')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 验证参数
    if not args.query and not args.url:
        parser.error("必须提供搜索关键词(--query)或视频URL(--url)")
    
    # 执行测试
    platform = args.platform
    logger.info(f"开始测试平台: {platform}")
    
    results = test_platform(platform, args)
    
    # 输出测试结果摘要
    logger.info("\n=== 测试结果摘要 ===")
    logger.info(f"平台: {platform}")
    
    # 搜索结果
    if results['search']:
        status = "成功" if results['search']['success'] else "失败"
        logger.info(f"搜索: {status}, 找到 {results['search']['count']} 个结果")
    else:
        logger.info("搜索: 未测试")
    
    # 视频信息结果
    if results['video_info']:
        status = "成功" if results['video_info']['success'] else "失败"
        logger.info(f"获取视频信息: {status}, URL: {results['video_info']['video_url']}")
    else:
        logger.info("获取视频信息: 未测试")
    
    # 下载结果
    if results['download']:
        status = "成功" if results['download']['success'] else "失败"
        logger.info(f"下载视频: {status}, 文件: {results['download'].get('file_path', 'N/A')}")
    else:
        logger.info("下载视频: 未测试")
    
    # 输出JSON结果
    if args.output_json:
        try:
            with open(args.output_json, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"测试结果已保存到: {args.output_json}")
        except Exception as e:
            logger.error(f"保存结果到JSON失败: {str(e)}")
    
    logger.info("测试完成")

if __name__ == "__main__":
    main() 