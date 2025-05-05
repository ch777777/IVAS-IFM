import asyncio
import httpx
from pprint import pprint

# 测试URL
TEST_DOUYIN_URL = "https://www.douyin.com/video/7159502929156705567"
TEST_TIKTOK_URL = "https://www.tiktok.com/@feelcomfy/video/7363865052876232991"
API_BASE_URL = "http://localhost:8001"

async def test_video_info(url):
    """测试获取视频信息API"""
    print(f"\n=== 测试获取视频信息 [{url}] ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/video/info", params={"url": url})
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("成功获取视频信息:")
            pprint(result)
        else:
            print(f"请求失败: {response.text}")

async def test_video_download(url):
    """测试获取视频下载链接API"""
    print(f"\n=== 测试获取视频下载链接 [{url}] ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/video/download", params={"url": url})
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("成功获取视频下载链接:")
            pprint(result)
        else:
            print(f"请求失败: {response.text}")

async def test_douyin_video(url):
    """测试抖音视频API"""
    print(f"\n=== 测试抖音视频专用API [{url}] ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/douyin/video", params={"url": url})
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("成功获取抖音视频信息:")
            if result["status"] == "success":
                # 只打印部分关键信息
                video_data = result["data"]
                important_info = {
                    "平台": video_data.get("platform", ""),
                    "描述": video_data.get("desc", ""),
                    "作者": video_data.get("author", {}).get("nickname", ""),
                    "视频ID": video_data.get("aweme_id", ""),
                    "无水印视频": video_data.get("video", {}).get("play_addr", {}).get("url_list", ["无"])[0],
                }
                pprint(important_info)
            else:
                pprint(result)
        else:
            print(f"请求失败: {response.text}")

async def test_tiktok_video(url):
    """测试TikTok视频API"""
    print(f"\n=== 测试TikTok视频专用API [{url}] ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/tiktok/video", params={"url": url})
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("成功获取TikTok视频信息:")
            if result["status"] == "success":
                # 只打印部分关键信息
                video_data = result["data"]
                important_info = {
                    "平台": video_data.get("platform", ""),
                    "描述": video_data.get("desc", ""),
                    "作者": video_data.get("author", {}).get("nickname", ""),
                    "视频ID": video_data.get("aweme_id", ""),
                    "无水印视频": video_data.get("video", {}).get("play_addr", {}).get("url_list", ["无"])[0],
                }
                pprint(important_info)
            else:
                pprint(result)
        else:
            print(f"请求失败: {response.text}")

async def run_all_tests():
    """运行所有测试"""
    print("开始测试 IVAS-IFM 真实API 集成服务...\n")
    
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
    
    # 运行单个API测试，以便查看详细错误信息
    try:
        print("\n测试抖音URL解析...")
        await test_douyin_video(TEST_DOUYIN_URL)
    except Exception as e:
        print(f"测试抖音URL时发生错误: {str(e)}")
    
    try:
        print("\n测试TikTok URL解析...")
        await test_tiktok_video(TEST_TIKTOK_URL)
    except Exception as e:
        print(f"测试TikTok URL时发生错误: {str(e)}")
    
    print("\n所有测试完成!")

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 