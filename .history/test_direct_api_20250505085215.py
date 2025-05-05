import httpx
import asyncio
import json
from pathlib import Path

# 测试URL
TEST_DOUYIN_URL = "https://www.douyin.com/video/7159502929156705567"
TEST_TIKTOK_URL = "https://www.tiktok.com/@feelcomfy/video/7363865052876232991"
TEST_XIAOHONGSHU_URL = "https://www.xiaohongshu.com/explore/64e32b3b000000001e02e2c0"
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
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # 测试混合解析API
    print("\n=== 测试TikHub混合解析API ===")
    async with httpx.AsyncClient() as client:
        try:
            url = f"{TIKHUB_BASE_URL}/api/v1/hybrid/parsing?url={TEST_DOUYIN_URL}"
            print(f"请求URL: {url}")
            response = await client.get(url, headers=headers)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    if "error" in resp_json and resp_json["error"]["code"] == "ok":
                        print("混合解析API调用成功!")
                    else:
                        print(f"API返回错误: {resp_json.get('error', {}).get('message', '未知错误')}")
                except:
                    print("解析JSON响应失败")
            print(f"响应内容: {response.text[:200]}..." if len(response.text) > 200 else response.text)
        except Exception as e:
            print(f"请求混合解析API时出错: {str(e)}")
    
    # 测试抖音视频
    print("\n=== 测试TikHub抖音Web API ===")
    async with httpx.AsyncClient() as client:
        try:
            url = f"{TIKHUB_BASE_URL}/api/v1/douyin/web/fetch_video_data?url={TEST_DOUYIN_URL}"
            print(f"请求URL: {url}")
            response = await client.get(url, headers=headers)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    if "error" in resp_json and resp_json["error"]["code"] == "ok":
                        print("抖音Web API调用成功!")
                    else:
                        print(f"API返回错误: {resp_json.get('error', {}).get('message', '未知错误')}")
                except:
                    print("解析JSON响应失败")
            print(f"响应内容: {response.text[:200]}..." if len(response.text) > 200 else response.text)
        except Exception as e:
            print(f"请求抖音Web API时出错: {str(e)}")
    
    # 测试TikTok视频
    print("\n=== 测试TikHub TikTok Web API ===")
    async with httpx.AsyncClient() as client:
        try:
            url = f"{TIKHUB_BASE_URL}/api/v1/tiktok/web/fetch_video_data?url={TEST_TIKTOK_URL}"
            print(f"请求URL: {url}")
            response = await client.get(url, headers=headers)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    if "error" in resp_json and resp_json["error"]["code"] == "ok":
                        print("TikTok Web API调用成功!")
                    else:
                        print(f"API返回错误: {resp_json.get('error', {}).get('message', '未知错误')}")
                except:
                    print("解析JSON响应失败")
            print(f"响应内容: {response.text[:200]}..." if len(response.text) > 200 else response.text)
        except Exception as e:
            print(f"请求TikTok Web API时出错: {str(e)}")
    
    # 测试小红书笔记
    print("\n=== 测试TikHub小红书Web API ===")
    async with httpx.AsyncClient() as client:
        try:
            url = f"{TIKHUB_BASE_URL}/api/v1/xiaohongshu/web/fetch_note_info?url={TEST_XIAOHONGSHU_URL}"
            print(f"请求URL: {url}")
            response = await client.get(url, headers=headers)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    if "error" in resp_json and resp_json["error"]["code"] == "ok":
                        print("小红书Web API调用成功!")
                    else:
                        print(f"API返回错误: {resp_json.get('error', {}).get('message', '未知错误')}")
                except:
                    print("解析JSON响应失败")
            print(f"响应内容: {response.text[:200]}..." if len(response.text) > 200 else response.text)
        except Exception as e:
            print(f"请求小红书Web API时出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_tikhub_api()) 