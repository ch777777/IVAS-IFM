import os
import argparse
from pathlib import Path
from pprint import pprint
from tikhub_interface import TikHubInterface

# API密钥
API_KEY = "0KMsWDohw2EtvSsxjmmtwUM33yUYhKD84a108Gz4mUZT0XUIIMJ/nDGNIg=="

def main():
    """TikHub API 示例应用"""
    parser = argparse.ArgumentParser(description="TikHub API 示例应用")
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 解析视频链接
    parse_parser = subparsers.add_parser("parse", help="解析视频链接")
    parse_parser.add_argument("url", help="视频URL")
    
    # 获取视频信息
    info_parser = subparsers.add_parser("info", help="获取视频信息")
    info_parser.add_argument("--platform", required=True, help="平台名称 (tiktok, douyin, xiaohongshu)")
    info_parser.add_argument("--video-id", required=True, help="视频ID")
    
    # 获取用户信息
    user_parser = subparsers.add_parser("user", help="获取用户信息")
    user_parser.add_argument("--platform", required=True, help="平台名称")
    user_parser.add_argument("--user-id", required=True, help="用户ID")
    
    # 获取用户视频列表
    user_videos_parser = subparsers.add_parser("user-videos", help="获取用户视频列表")
    user_videos_parser.add_argument("--platform", required=True, help="平台名称")
    user_videos_parser.add_argument("--user-id", required=True, help="用户ID")
    user_videos_parser.add_argument("--count", type=int, default=10, help="返回视频数量")
    
    # 搜索视频
    search_videos_parser = subparsers.add_parser("search-videos", help="搜索视频")
    search_videos_parser.add_argument("--platform", required=True, help="平台名称")
    search_videos_parser.add_argument("--keyword", required=True, help="搜索关键词")
    search_videos_parser.add_argument("--count", type=int, default=10, help="返回视频数量")
    
    # 下载视频
    download_parser = subparsers.add_parser("download", help="下载视频")
    download_parser.add_argument("--url", required=True, help="视频URL")
    download_parser.add_argument("--output", default="downloads", help="保存目录")
    
    # 获取视频评论
    comments_parser = subparsers.add_parser("comments", help="获取视频评论")
    comments_parser.add_argument("--platform", required=True, help="平台名称")
    comments_parser.add_argument("--video-id", required=True, help="视频ID")
    comments_parser.add_argument("--count", type=int, default=20, help="返回评论数量")
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 初始化TikHub接口
    tikhub = TikHubInterface(api_key=API_KEY)
    
    # 执行对应命令
    if args.command == "parse":
        print(f"正在解析视频: {args.url}")
        result = tikhub.parse_url(args.url)
        pprint(result)
        
    elif args.command == "info":
        print(f"正在获取{args.platform}平台视频信息, 视频ID: {args.video_id}")
        result = tikhub.get_video_info(args.platform, args.video_id)
        pprint(result)
        
    elif args.command == "user":
        print(f"正在获取{args.platform}平台用户信息, 用户ID: {args.user_id}")
        result = tikhub.get_user_info(args.platform, args.user_id)
        pprint(result)
        
    elif args.command == "user-videos":
        print(f"正在获取{args.platform}平台用户视频列表, 用户ID: {args.user_id}")
        result = tikhub.get_user_videos(args.platform, args.user_id, count=args.count)
        pprint(result)
        
    elif args.command == "search-videos":
        print(f"正在{args.platform}平台搜索视频, 关键词: {args.keyword}")
        result = tikhub.search_videos(args.platform, args.keyword, count=args.count)
        pprint(result)
        
    elif args.command == "download":
        print(f"正在下载视频: {args.url}")
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = tikhub.download_video_sync(args.url, output_dir)
        if file_path:
            print(f"视频下载成功: {file_path}")
        else:
            print("视频下载失败")
            
    elif args.command == "comments":
        print(f"正在获取{args.platform}平台视频评论, 视频ID: {args.video_id}")
        result = tikhub.get_video_comments(args.platform, args.video_id, count=args.count)
        pprint(result)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 