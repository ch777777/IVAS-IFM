import tikhub_sdk_v2
from tikhub_sdk_v2 import HybridParsingApi
from tikhub_sdk_v2 import DouyinWebAPIApi
from tikhub_sdk_v2 import TikTokWebAPIApi
from tikhub_sdk_v2 import Configuration
from tikhub_sdk_v2 import ApiClient
from pprint import pprint

# 测试URL
TEST_DOUYIN_URL = "https://www.douyin.com/video/7159502929156705567"
TEST_TIKTOK_URL = "https://www.tiktok.com/@feelcomfy/video/7363865052876232991"
TEST_XIAOHONGSHU_URL = "https://www.xiaohongshu.com/explore/64e32b3b000000001e02e2c0"

# 设置API密钥
API_KEY = "0KMsWDohw2EtvSsxjmmtwUM33yUYhKD84a108Gz4mUZT0XUIIMJ/nDGNIg=="

# 配置SDK
configuration = Configuration()
configuration.access_token = API_KEY  # Bearer Token认证
configuration.host = "https://api.tikhub.io"  # API基础URL

# 创建API客户端
with ApiClient(configuration) as api_client:
    try:
        print("\n=== 测试TikHub SDK V2 ===")
        
        # 测试混合解析API
        print("\n=== 测试混合解析API ===")
        try:
            hybrid_api = HybridParsingApi(api_client)
            response = hybrid_api.hybrid_parsing_api_v1_hybrid_parsing_get(url=TEST_DOUYIN_URL)
            print("混合解析API调用成功!")
            pprint(response)
        except tikhub_sdk_v2.ApiException as e:
            print(f"混合解析API调用失败: {e}")
            print(f"错误状态码: {e.status}")
            print(f"错误原因: {e.reason}")
            print(f"错误响应体: {e.body}")
        
        # 测试抖音Web API
        print("\n=== 测试抖音Web API ===")
        try:
            douyin_api = DouyinWebAPIApi(api_client)
            response = douyin_api.fetch_video_data_api_v1_douyin_web_fetch_video_data_get(url=TEST_DOUYIN_URL)
            print("抖音Web API调用成功!")
            pprint(response)
        except tikhub_sdk_v2.ApiException as e:
            print(f"抖音Web API调用失败: {e}")
            print(f"错误状态码: {e.status}")
            print(f"错误原因: {e.reason}")
            print(f"错误响应体: {e.body}")
        
        # 测试TikTok Web API
        print("\n=== 测试TikTok Web API ===")
        try:
            tiktok_api = TikTokWebAPIApi(api_client)
            response = tiktok_api.fetch_video_data_api_v1_tiktok_web_fetch_video_data_get(url=TEST_TIKTOK_URL)
            print("TikTok Web API调用成功!")
            pprint(response)
        except tikhub_sdk_v2.ApiException as e:
            print(f"TikTok Web API调用失败: {e}")
            print(f"错误状态码: {e.status}")
            print(f"错误原因: {e.reason}")
            print(f"错误响应体: {e.body}")
        
    except Exception as e:
        print(f"发生未知错误: {str(e)}") 