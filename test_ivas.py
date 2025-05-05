import os
import json
import logging
import argparse
from pathlib import Path
from pprint import pprint
from ivas_integration import IVASVideoProcessor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ivas-test")

# API密钥
TIKHUB_API_KEY = "0KMsWDohw2EtvSsxjmmtwUM33yUYhKD84a108Gz4mUZT0XUIIMJ/nDGNIg=="

def parse_video(processor, url, verbose=False):
    """测试视频解析"""
    logger.info(f"测试视频解析 URL: {url}")
    result = processor.process_video_url(url)
    
    if "error" in result:
        logger.error(f"解析失败: {result['error']}")
        return False
    
    logger.info("解析成功!")
    
    if verbose:
        logger.info("视频信息：")
        if "video_info" in result:
            video_info = result["video_info"]
            print(f"标题: {video_info.get('title', '无标题')}")
            print(f"作者: {video_info.get('author', {}).get('nickname', '未知')}")
            print(f"平台: {result.get('platform', '未知')}")
            print(f"下载链接: {result.get('download_url', '无')}")
        
        if "summary" in result and result["summary"]:
            print("\n摘要信息：")
            pprint(result["summary"])
        
        if "translations" in result and result["translations"]:
            print("\n翻译信息：")
            pprint(result["translations"])
    
    return True

def search_videos(processor, keyword, platform="douyin", count=5, verbose=False):
    """测试视频搜索"""
    logger.info(f"测试视频搜索 - 平台: {platform}, 关键词: {keyword}")
    result = processor.search_videos(keyword, platform, count)
    
    if not result.get("success", False):
        logger.error(f"搜索失败: {result.get('message', '未知错误')}")
        return False
    
    videos = result.get("videos", [])
    logger.info(f"搜索成功! 共找到 {len(videos)} 个结果")
    
    if verbose and videos:
        print("\n搜索结果:")
        for i, video in enumerate(videos[:3], 1):  # 只显示前3个结果
            print(f"视频 {i}:")
            print(f"  标题: {video.get('title', '无标题')}")
            print(f"  作者: {video.get('author', {}).get('nickname', '未知')}")
            if "summary" in video:
                print(f"  摘要: {video['summary'].get('summary', '无摘要')}")
            print()
    
    return True

def download_video(processor, url, output_dir="downloads", verbose=False):
    """测试视频下载"""
    logger.info(f"测试视频下载 URL: {url}")
    
    # 确保下载目录存在
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 下载视频
    result = processor.download_video(url)
    
    if not result.get("success", False):
        logger.error(f"下载失败: {result.get('message', '未知错误')}")
        return False
    
    file_path = result.get("file_path", "")
    logger.info(f"下载成功! 文件保存在: {file_path}")
    
    if verbose:
        print(f"文件大小: {result.get('file_size', 0) / 1024 / 1024:.2f} MB")
    
    return True

def translate_text(processor, text, source="zh", target="en", verbose=False):
    """测试文本翻译"""
    logger.info(f"测试文本翻译: {text}")
    result = processor.translate_text(text, source, target)
    
    if not result.get("success", False):
        logger.error(f"翻译失败: {result.get('message', '未知错误')}")
        return False
    
    translated_text = result.get("translated_text", "")
    logger.info(f"翻译成功! 原文: {text}, 译文: {translated_text}")
    
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="IVAS-IFM 集成测试工具")
    parser.add_argument("--parse", help="测试视频解析 (输入视频URL)")
    parser.add_argument("--search", help="测试视频搜索 (输入搜索关键词)")
    parser.add_argument("--platform", default="douyin", help="指定平台 (douyin/tiktok/xiaohongshu)")
    parser.add_argument("--download", help="测试视频下载 (输入视频URL)")
    parser.add_argument("--translate", help="测试文本翻译 (输入要翻译的文本)")
    parser.add_argument("--source", default="zh", help="源语言 (默认: zh)")
    parser.add_argument("--target", default="en", help="目标语言 (默认: en)")
    parser.add_argument("--count", type=int, default=5, help="搜索结果数量 (默认: 5)")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")
    
    args = parser.parse_args()
    
    # 初始化IVAS处理器
    processor = IVASVideoProcessor(tikhub_api_key=TIKHUB_API_KEY)
    
    # 运行测试
    if args.all:
        # 运行所有测试
        test_url = "https://www.douyin.com/video/7159502929156705567"
        test_keyword = "搞笑"
        test_text = "这个视频很有趣，我很喜欢"
        
        logger.info("=== 运行所有测试 ===")
        parse_video(processor, test_url, args.verbose)
        search_videos(processor, test_keyword, args.platform, args.count, args.verbose)
        download_video(processor, test_url, "downloads", args.verbose)
        translate_text(processor, test_text, args.source, args.target, args.verbose)
    else:
        # 运行指定测试
        if args.parse:
            parse_video(processor, args.parse, args.verbose)
        
        if args.search:
            search_videos(processor, args.search, args.platform, args.count, args.verbose)
        
        if args.download:
            download_video(processor, args.download, "downloads", args.verbose)
        
        if args.translate:
            translate_text(processor, args.translate, args.source, args.target, args.verbose)
        
        # 如果没有指定任何测试，显示帮助
        if not any([args.parse, args.search, args.download, args.translate, args.all]):
            parser.print_help()

if __name__ == "__main__":
    main() 