import tikhub_sdk_v2
from tikhub_sdk_v2 import Configuration, ApiClient
from tikhub_sdk_v2 import HybridParsingApi, DouyinWebAPIApi, TikTokWebAPIApi
from pprint import pprint

# 测试URL
TEST_DOUYIN_URL = "https://www.douyin.com/video/7159502929156705567"
TEST_TIKTOK_URL = "https://www.tiktok.com/@feelcomfy/video/7363865052876232991"

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
            # 使用正确的方法名
            response = hybrid_api.hybrid_parsing_single_video_api_v1_hybrid_video_data_get(url=TEST_DOUYIN_URL)
            print("混合解析API调用成功!")
            pprint(response)
        except tikhub_sdk_v2.ApiException as e:
            print(f"混合解析API调用失败: {e}")
            print(f"错误状态码: {e.status}")
            print(f"错误原因: {e.reason}")
            print(f"错误响应体: {e.body}")
        
        # 仅显示抖音视频信息，其他接口暂不测试
        
    except Exception as e:
        print(f"发生未知错误: {str(e)}") 