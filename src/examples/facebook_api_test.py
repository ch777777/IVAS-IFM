#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Facebook视频爬虫API测试脚本
测试集成Evil0ctal/Douyin_TikTok_Download_API和bellingcat/facebook-downloader的功能
"""
import os
import sys
import logging
import argparse
from pathlib import Path

# 添加项目根目录到系统路径
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

try:
    from src.modules.vca.platform_adapters.facebook import FacebookAdapter
except ImportError:
    try:
        # 尝试相对导入
        sys.path.append(str(Path(__file__).resolve().parent.parent))
        from modules.vca.platform_adapters.facebook import FacebookAdapter
    except ImportError:
        print("无法导入FacebookAdapter，请确保项目路径正确")
        sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_search_videos(args):
    """测试搜索视频功能"""
    adapter = FacebookAdapter(use_selenium=True)
    
    try:
        # 搜索视频
        logger.info(f"开始搜索视频: {args.query}, 限制: {args.limit}")
        results = adapter.search_videos(search_query=args.query, limit=args.limit)
        
        logger.info(f"找到 {len(results)} 个视频")
        for idx, video in enumerate(results, 1):
            logger.info(f"视频 {idx}:")
            logger.info(f"  标题: {video.get('title', '未知')}")
            logger.info(f"  链接: {video.get('url', '未知')}")
            logger.info(f"  作者: {video.get('author', '未知')}")
    finally:
        adapter.close()

def test_get_video_info(args):
    """测试获取视频信息功能"""
    adapter = FacebookAdapter(use_selenium=True)
    
    try:
        # 获取视频信息
        logger.info(f"获取视频信息: {args.url}")
        video_info = adapter.get_video_info(args.url)
        
        if video_info:
            logger.info("视频信息获取成功:")
            logger.info(f"  ID: {video_info.get('id', '未知')}")
            logger.info(f"  标题: {video_info.get('title', '未知')}")
            logger.info(f"  描述: {video_info.get('text', '未知')[:50]}...")
            logger.info(f"  作者: {video_info.get('author', '未知')}")
            logger.info(f"  时长: {video_info.get('duration', '未知')} 秒")
            logger.info(f"  上传日期: {video_info.get('upload_date', '未知')}")
            
            # 输出附件信息
            attachments = video_info.get('attachments', {})
            if attachments.get('video'):
                logger.info(f"  视频链接: {attachments['video'][0]}")
            if attachments.get('thumbnail'):
                logger.info(f"  缩略图: {attachments['thumbnail'][0]}")
        else:
            logger.error("未能获取视频信息")
    finally:
        adapter.close()

def test_download_video(args):
    """测试下载视频功能"""
    adapter = FacebookAdapter(use_selenium=True)
    
    try:
        # 创建输出目录
        os.makedirs(args.output_dir, exist_ok=True)
        
        # 下载视频
        logger.info(f"下载视频: {args.url}")
        filename = args.filename or None
        result = adapter.download_video(
            video_url=args.url,
            output_path=args.output_dir,
            filename=filename
        )
        
        if os.path.isfile(result):
            logger.info(f"视频下载成功: {result}")
        else:
            logger.error(f"视频下载失败: {result}")
    finally:
        adapter.close()

def test_integrated_api(args):
    """测试集成API功能"""
    adapter = FacebookAdapter(use_selenium=True)
    
    # 配置使用Evil0ctal API
    adapter.use_evil0ctal_api = True
    adapter.evil0ctal_api_url = "https://api.douyin.wtf/api"
    
    try:
        # 测试API集成
        logger.info(f"测试集成API，Evil0ctal状态: {adapter.use_evil0ctal_api}")
        
        # 获取视频信息
        logger.info(f"获取视频信息: {args.url}")
        video_info = adapter.get_video_info(args.url)
        
        if video_info:
            logger.info("通过集成API获取视频信息成功")
            
            # 下载视频
            if args.download:
                os.makedirs(args.output_dir, exist_ok=True)
                logger.info(f"下载视频: {args.url}")
                filename = args.filename or f"api_test_{video_info.get('id', 'unknown')}"
                result = adapter.download_video(
                    video_url=args.url,
                    output_path=args.output_dir,
                    filename=filename
                )
                
                if os.path.isfile(result):
                    logger.info(f"通过集成API下载视频成功: {result}")
                else:
                    logger.error(f"通过集成API下载视频失败: {result}")
        else:
            logger.error("通过集成API未能获取视频信息")
    finally:
        adapter.close()

def main():
    parser = argparse.ArgumentParser(description="Facebook视频爬虫API测试脚本")
    subparsers = parser.add_subparsers(dest="command")
    
    # 搜索视频命令
    search_parser = subparsers.add_parser("search", help="搜索视频")
    search_parser.add_argument("--query", "-q", type=str, required=True, help="搜索关键词")
    search_parser.add_argument("--limit", "-l", type=int, default=5, help="结果数量限制")
    
    # 获取视频信息命令
    info_parser = subparsers.add_parser("info", help="获取视频信息")
    info_parser.add_argument("--url", "-u", type=str, required=True, help="视频URL")
    
    # 下载视频命令
    download_parser = subparsers.add_parser("download", help="下载视频")
    download_parser.add_argument("--url", "-u", type=str, required=True, help="视频URL")
    download_parser.add_argument("--output-dir", "-o", type=str, default="./downloads", help="输出目录")
    download_parser.add_argument("--filename", "-f", type=str, help="输出文件名（不含扩展名）")
    
    # 集成API测试命令
    api_parser = subparsers.add_parser("api", help="测试集成API功能")
    api_parser.add_argument("--url", "-u", type=str, required=True, help="视频URL")
    api_parser.add_argument("--download", "-d", action="store_true", help="是否下载视频")
    api_parser.add_argument("--output-dir", "-o", type=str, default="./downloads", help="输出目录")
    api_parser.add_argument("--filename", "-f", type=str, help="输出文件名（不含扩展名）")
    
    args = parser.parse_args()
    
    if args.command == "search":
        test_search_videos(args)
    elif args.command == "info":
        test_get_video_info(args)
    elif args.command == "download":
        test_download_video(args)
    elif args.command == "api":
        test_integrated_api(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 