import requests
from pprint import pprint

# 服务地址
API_BASE_URL = "http://localhost:8002"

# API密钥
API_KEY = "0KMsWDohw2EtvSsxjmmtwUM33yUYhKD84a108Gz4mUZT0XUIIMJ/nDGNIg=="

def test_api(endpoint, params=None):
    """测试API端点"""
    if params is None:
        params = {}
    
    print(f"\n=== 测试端点: {endpoint} ===")
    
    try:
        url = f"{API_BASE_URL}{endpoint}"
        print(f"请求URL: {url}")
        
        # 发送请求
        response = requests.get(
            url,
            params=params,
            headers={"X-API-KEY": API_KEY}
        )
        
        # 打印响应
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("请求成功:")
            pprint(result)
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求出错: {str(e)}")

def main():
    """运行测试"""
    print("开始测试更新后的TikHub API服务...\n")
    
    # 测试根端点
    test_api("/")
    
    # 测试健康检查端点
    test_api("/health")
    
    # 测试混合解析端点
    test_url = "https://www.douyin.com/video/7159502929156705567"
    test_api("/api/hybrid/parse", {"url": test_url})
    
    print("\n所有测试完成!")

if __name__ == "__main__":
    main() 