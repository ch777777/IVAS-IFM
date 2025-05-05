import httpx
import asyncio

async def test_api():
    print("开始测试 IVAS-IFM API 集成服务...")
    async with httpx.AsyncClient() as client:
        try:
            # 测试根路径API
            resp = await client.get('http://localhost:8000/')
            print(f'API状态: {resp.status_code}')
            print(resp.json())
            
            # 测试视频信息API
            resp = await client.get('http://localhost:8000/api/video/info', params={"url": "https://example.com/video"})
            print("\n=== 视频信息API测试 ===")
            print(f'状态码: {resp.status_code}')
            print(resp.json())
            
            # 测试视频下载API
            resp = await client.get('http://localhost:8000/api/video/download', params={"url": "https://example.com/video"})
            print("\n=== 视频下载API测试 ===")
            print(f'状态码: {resp.status_code}')
            print(resp.json())
            
            # 测试翻译API
            resp = await client.post('http://localhost:8000/api/video/translate', 
                                    json={"text": "这是测试文本", "source_language": "zh", "target_language": "en"})
            print("\n=== 翻译API测试 ===")
            print(f'状态码: {resp.status_code}')
            print(resp.json())
            
            print("\n所有测试完成!")
        except Exception as e:
            print(f"测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_api()) 