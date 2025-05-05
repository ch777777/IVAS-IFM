import asyncio
import httpx
import json
from pprint import pprint

# 测试URL
TEST_VIDEO_URL = "https://www.douyin.com/video/7159502929156705567"
API_BASE_URL = "http://localhost:8000"

async def test_video_info():
    """测试获取视频信息API"""
    print("\n=== 测试获取视频信息 ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/video/info", params={"url": TEST_VIDEO_URL})
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("成功获取视频信息:")
            pprint(result)
        else:
            print(f"请求失败: {response.text}")

async def test_video_download():
    """测试获取视频下载链接API"""
    print("\n=== 测试获取视频下载链接 ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/video/download", params={"url": TEST_VIDEO_URL})
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("成功获取视频下载链接:")
            pprint(result)
        else:
            print(f"请求失败: {response.text}")

async def test_video_summary():
    """测试获取视频摘要API"""
    print("\n=== 测试获取视频摘要 ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/video/summary", params={"url": TEST_VIDEO_URL})
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("成功获取视频摘要:")
            pprint(result)
        else:
            print(f"请求失败: {response.text}")

async def test_video_translate():
    """测试视频内容翻译API"""
    print("\n=== 测试视频内容翻译 ===")
    
    translation_request = {
        "text": "这是一个测试文本，需要翻译成英文",
        "source_language": "zh",
        "target_language": "en"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/api/video/translate", 
            json=translation_request
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("成功翻译文本:")
            pprint(result)
        else:
            print(f"请求失败: {response.text}")

async def run_all_tests():
    """运行所有测试"""
    print("开始测试 IVAS-IFM API 集成服务...\n")
    
    # 首先检查API是否在运行
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/")
            print(f"API 状态: {'在线' if response.status_code == 200 else '离线'}")
            if response.status_code == 200:
                print(f"API 响应: {response.json()}")
    except Exception as e:
        print(f"无法连接到API服务器: {str(e)}")
        print("请确保API服务器在运行，然后再尝试运行测试。")
        return
    
    # 运行测试
    await test_video_info()
    await test_video_download()
    await test_video_summary()
    await test_video_translate()
    
    print("\n所有测试完成!")

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 