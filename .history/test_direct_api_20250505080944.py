import httpx
import asyncio
import json
from pathlib import Path

# 测试URL
TEST_DOUYIN_URL = "https://www.douyin.com/video/7159502929156705567"
TEST_TIKTOK_URL = "https://www.tiktok.com/@feelcomfy/video/7363865052876232991"
TIKHUB_BASE_URL = "https://api.tikhub.io"

# 从配置文件读取API密钥
config_path = Path(__file__).parent / "config.json"
api_key = ""

if config_path.exists():
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            api_key = config.get("tikhub_api_key", "")
    except Exception as e:
        print(f"读取配置文件时出错: {str(e)}")

if not api_key:
    print("错误: 未找到API密钥，请确保config.json文件存在且包含有效的tikhub_api_key")
    exit(1)

async def test_tikhub_api():
    print(f"使用API密钥: {api_key[:10]}..." if len(api_key) > 10 else api_key)
    
    headers = {"X-API-KEY": api_key}
    
    # 测试抖音视频
    print("\n=== 直接测试TikHub API (抖音) ===")
    async with httpx.AsyncClient() as client:
        try:
            url = f"{TIKHUB_BASE_URL}/douyin/video?url={TEST_DOUYIN_URL}"
            print(f"请求URL: {url}")
            response = await client.get(url, headers=headers)
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}..." if len(response.text) > 200 else response.text)
        except Exception as e:
            print(f"请求抖音视频时出错: {str(e)}")
    
    # 测试TikTok视频
    print("\n=== 直接测试TikHub API (TikTok) ===")
    async with httpx.AsyncClient() as client:
        try:
            url = f"{TIKHUB_BASE_URL}/tiktok/video?url={TEST_TIKTOK_URL}"
            print(f"请求URL: {url}")
            response = await client.get(url, headers=headers)
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}..." if len(response.text) > 200 else response.text)
        except Exception as e:
            print(f"请求TikTok视频时出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_tikhub_api()) 