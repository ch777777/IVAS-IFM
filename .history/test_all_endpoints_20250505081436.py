import asyncio
import httpx
import os
import json
import argparse
from pathlib import Path
from pprint import pprint

# API配置
API_BASE_URL = "http://localhost:8002"  # TikHub API默认端口

# 测试URL
TEST_DOUYIN_URL = "https://www.douyin.com/video/7159502929156705567"
TEST_TIKTOK_URL = "https://www.tiktok.com/@feelcomfy/video/7363865052876232991"
TEST_XIAOHONGSHU_URL = "https://www.xiaohongshu.com/explore/64e32b3b000000001e02e2c0"

# 尝试从环境变量获取API密钥
TIKHUB_API_KEY = os.environ.get("TIKHUB_API_KEY", "")

# 如果环境变量中没有API密钥，尝试从配置文件中读取
if not TIKHUB_API_KEY:
    try:
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                TIKHUB_API_KEY = config.get("tikhub_api_key", "")
    except Exception as e:
        print(f"读取配置文件时出错: {str(e)}")

# 测试各个端点
async def test_root_endpoint():
    """测试根端点"""
    print("\n=== 测试根端点 ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            pprint(response.json())

async def test_health_endpoint():
    """测试健康检查端点"""
    print("\n=== 测试健康检查端点 ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            pprint(response.json())

async def test_video_info_endpoint(url):
    """测试视频信息端点"""
    print(f"\n=== 测试视频信息端点 [{url}] ===")
    
    headers = {"X-API-KEY": TIKHUB_API_KEY} if TIKHUB_API_KEY else {}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/video/info", 
            params={"url": url},
            headers=headers
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            pprint(response.json())
            
async def test_video_download_endpoint(url):
    """测试视频下载端点"""
    print(f"\n=== 测试视频下载端点 [{url}] ===")
    
    headers = {"X-API-KEY": TIKHUB_API_KEY} if TIKHUB_API_KEY else {}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/video/download", 
            params={"url": url},
            headers=headers
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            pprint(response.json())

async def test_douyin_video_endpoint(url):
    """测试抖音视频端点"""
    print(f"\n=== 测试抖音视频端点 [{url}] ===")
    
    headers = {"X-API-KEY": TIKHUB_API_KEY} if TIKHUB_API_KEY else {}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/douyin/video", 
            params={"url": url},
            headers=headers
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            pprint(response.json())

async def test_tiktok_video_endpoint(url):
    """测试TikTok视频端点"""
    print(f"\n=== 测试TikTok视频端点 [{url}] ===")
    
    headers = {"X-API-KEY": TIKHUB_API_KEY} if TIKHUB_API_KEY else {}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/tiktok/video", 
            params={"url": url},
            headers=headers
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            pprint(response.json())

async def test_xiaohongshu_post_endpoint(url):
    """测试小红书笔记端点"""
    print(f"\n=== 测试小红书笔记端点 [{url}] ===")
    
    headers = {"X-API-KEY": TIKHUB_API_KEY} if TIKHUB_API_KEY else {}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/xiaohongshu/post", 
            params={"url": url},
            headers=headers
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            pprint(response.json())

async def test_hybrid_parse_endpoint(url):
    """测试混合解析端点"""
    print(f"\n=== 测试混合解析端点 [{url}] ===")
    
    headers = {"X-API-KEY": TIKHUB_API_KEY} if TIKHUB_API_KEY else {}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/hybrid/parse", 
            params={"url": url},
            headers=headers
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            pprint(response.json())

async def run_selected_tests(args):
    """运行选择的测试"""
    print(f"开始测试 API 端点 ({API_BASE_URL})...\n")
    
    if not TIKHUB_API_KEY:
        print("警告: 未设置TIKHUB_API_KEY，API调用可能会失败。请在config.json或环境变量中设置API密钥。")
    
    # 测试基本端点
    if args.all or args.basic:
        await test_root_endpoint()
        await test_health_endpoint()
    
    # 测试视频信息和下载端点
    if args.all or args.common:
        if args.douyin_url:
            await test_video_info_endpoint(args.douyin_url)
            await test_video_download_endpoint(args.douyin_url)
        else:
            await test_video_info_endpoint(TEST_DOUYIN_URL)
            await test_video_download_endpoint(TEST_DOUYIN_URL)
    
    # 测试抖音视频端点
    if args.all or args.douyin:
        if args.douyin_url:
            await test_douyin_video_endpoint(args.douyin_url)
        else:
            await test_douyin_video_endpoint(TEST_DOUYIN_URL)
    
    # 测试TikTok视频端点
    if args.all or args.tiktok:
        if args.tiktok_url:
            await test_tiktok_video_endpoint(args.tiktok_url)
        else:
            await test_tiktok_video_endpoint(TEST_TIKTOK_URL)
    
    # 测试小红书笔记端点
    if args.all or args.xiaohongshu:
        if args.xiaohongshu_url:
            await test_xiaohongshu_post_endpoint(args.xiaohongshu_url)
        else:
            await test_xiaohongshu_post_endpoint(TEST_XIAOHONGSHU_URL)
    
    # 测试混合解析端点
    if args.all or args.hybrid:
        if args.douyin_url:
            await test_hybrid_parse_endpoint(args.douyin_url)
        elif args.tiktok_url:
            await test_hybrid_parse_endpoint(args.tiktok_url)
        elif args.xiaohongshu_url:
            await test_hybrid_parse_endpoint(args.xiaohongshu_url)
        else:
            await test_hybrid_parse_endpoint(TEST_DOUYIN_URL)
    
    print("\n所有测试完成!")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试TikHub API端点")
    
    # 选择要测试的端点
    parser.add_argument("--all", action="store_true", help="测试所有端点")
    parser.add_argument("--basic", action="store_true", help="测试基本端点")
    parser.add_argument("--common", action="store_true", help="测试通用视频信息和下载端点")
    parser.add_argument("--douyin", action="store_true", help="测试抖音端点")
    parser.add_argument("--tiktok", action="store_true", help="测试TikTok端点")
    parser.add_argument("--xiaohongshu", action="store_true", help="测试小红书端点")
    parser.add_argument("--hybrid", action="store_true", help="测试混合解析端点")
    
    # 自定义URL
    parser.add_argument("--douyin-url", help="自定义抖音视频URL")
    parser.add_argument("--tiktok-url", help="自定义TikTok视频URL")
    parser.add_argument("--xiaohongshu-url", help="自定义小红书笔记URL")
    
    # API URL
    parser.add_argument("--api-url", help="自定义API基础URL")
    
    args = parser.parse_args()
    
    # 如果没有选择任何测试，则默认测试所有端点
    if not (args.all or args.basic or args.common or args.douyin or args.tiktok or args.xiaohongshu or args.hybrid):
        args.all = True
    
    # 设置自定义API URL
    global API_BASE_URL
    if args.api_url:
        API_BASE_URL = args.api_url
    
    asyncio.run(run_selected_tests(args))

if __name__ == "__main__":
    main() 