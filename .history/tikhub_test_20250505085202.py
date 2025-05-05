import asyncio
import httpx
import os
import json
from pathlib import Path
from pprint import pprint

# 测试URL
TEST_DOUYIN_URL = "https://www.douyin.com/video/7159502929156705567"
TEST_TIKTOK_URL = "https://www.tiktok.com/@feelcomfy/video/7363865052876232991"
TEST_XIAOHONGSHU_URL = "https://www.xiaohongshu.com/explore/64e32b3b000000001e02e2c0"
API_BASE_URL = "http://localhost:8002"

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

async def test_api_connection():
    """测试API连接"""
    print("\n=== 测试API连接 ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/")
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("API响应:")
            pprint(result)
        else:
            print(f"请求失败: {response.text}")

async def test_douyin_video(url):
    """测试抖音视频API"""
    print(f"\n=== 测试抖音视频API [{url}] ===")
    
    headers = {"X-API-KEY": TIKHUB_API_KEY} if TIKHUB_API_KEY else {}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/douyin/video", 
            params={"url": url},
            headers=headers
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("抖音视频信息:")
            if result["status"] == "success":
                data = result["data"]
                important_info = {
                    "描述": data.get("desc", "")[:100] + "..." if len(data.get("desc", "")) > 100 else data.get("desc", ""),
                    "作者": data.get("authorName", ""),
                    "视频ID": data.get("id", ""),
                    "无水印视频URL": data.get("videoUrl", "")[:50] + "..." if data.get("videoUrl", "") else "无"
                }
                pprint(important_info)
            else:
                pprint(result)
        else:
            print(f"请求失败: {response.text}")

async def test_tiktok_video(url):
    """测试TikTok视频API"""
    print(f"\n=== 测试TikTok视频API [{url}] ===")
    
    headers = {"X-API-KEY": TIKHUB_API_KEY} if TIKHUB_API_KEY else {}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/tiktok/video", 
            params={"url": url},
            headers=headers
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("TikTok视频信息:")
            if result["status"] == "success":
                data = result["data"]
                important_info = {
                    "描述": data.get("desc", "")[:100] + "..." if len(data.get("desc", "")) > 100 else data.get("desc", ""),
                    "作者": data.get("authorName", ""),
                    "视频ID": data.get("id", ""),
                    "无水印视频URL": data.get("videoUrl", "")[:50] + "..." if data.get("videoUrl", "") else "无"
                }
                pprint(important_info)
            else:
                pprint(result)
        else:
            print(f"请求失败: {response.text}")

async def test_xiaohongshu_post(url):
    """测试小红书笔记API"""
    print(f"\n=== 测试小红书笔记API [{url}] ===")
    
    headers = {"X-API-KEY": TIKHUB_API_KEY} if TIKHUB_API_KEY else {}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/xiaohongshu/post", 
            params={"url": url},
            headers=headers
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("小红书笔记信息:")
            if result["status"] == "success":
                data = result["data"]
                important_info = {
                    "标题": data.get("title", ""),
                    "描述": data.get("desc", "")[:100] + "..." if len(data.get("desc", "")) > 100 else data.get("desc", ""),
                    "作者": data.get("authorName", ""),
                    "笔记ID": data.get("id", "")
                }
                
                # 打印图片和视频链接(如果有)
                if "images" in data and data["images"]:
                    important_info["图片数量"] = len(data["images"])
                    important_info["第一张图片URL"] = data["images"][0][:50] + "..." if data["images"][0] else "无"
                
                if "videoUrl" in data and data["videoUrl"]:
                    important_info["视频URL"] = data["videoUrl"][:50] + "..." if data["videoUrl"] else "无"
                
                pprint(important_info)
            else:
                pprint(result)
        else:
            print(f"请求失败: {response.text}")

async def test_video_download(url):
    """测试视频下载API"""
    print(f"\n=== 测试视频下载API [{url}] ===")
    
    headers = {"X-API-KEY": TIKHUB_API_KEY} if TIKHUB_API_KEY else {}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/video/download", 
            params={"url": url},
            headers=headers
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("视频下载信息:")
            pprint(result)
        else:
            print(f"请求失败: {response.text}")

async def run_all_tests():
    """运行所有测试"""
    print("开始测试 TikHub API 集成服务...\n")
    
    if not TIKHUB_API_KEY:
        print("警告: 未设置TIKHUB_API_KEY，API调用可能会失败。请在脚本中设置你的API密钥。")
    
    # 首先检查API是否在运行
    try:
        await test_api_connection()
    except Exception as e:
        print(f"无法连接到API服务器: {str(e)}")
        print("请确保API服务器在运行，然后再尝试运行测试。")
        return
    
    # 测试抖音视频
    try:
        await test_douyin_video(TEST_DOUYIN_URL)
        await test_video_download(TEST_DOUYIN_URL)
    except Exception as e:
        print(f"测试抖音视频时发生错误: {str(e)}")
    
    # 测试TikTok视频
    try:
        await test_tiktok_video(TEST_TIKTOK_URL)
        await test_video_download(TEST_TIKTOK_URL)
    except Exception as e:
        print(f"测试TikTok视频时发生错误: {str(e)}")
    
    # 测试小红书笔记
    try:
        await test_xiaohongshu_post(TEST_XIAOHONGSHU_URL)
    except Exception as e:
        print(f"测试小红书笔记时发生错误: {str(e)}")
    
    print("\n所有测试完成!")

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 