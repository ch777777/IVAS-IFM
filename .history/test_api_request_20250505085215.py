import requests

# 服务地址
API_BASE_URL = "http://localhost:8002"

# API密钥
API_KEY = "0KMsWDohw2EtvSsxjmmtwUM33yUYhKD84a108Gz4mUZT0XUIIMJ/nDGNIg=="

# 测试根端点
print("=== 测试根端点 ===")
response = requests.get(f"{API_BASE_URL}/")
print(f"状态码: {response.status_code}")
print(response.json())

# 测试混合解析端点
print("\n=== 测试混合解析端点 ===")
douyin_url = "https://www.douyin.com/video/7159502929156705567"
response = requests.get(
    f"{API_BASE_URL}/api/hybrid/parse",
    params={"url": douyin_url},
    headers={"X-API-KEY": API_KEY}
)
print(f"状态码: {response.status_code}")
print(response.json()) 