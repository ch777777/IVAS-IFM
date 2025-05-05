# TikHub API 集成使用指南

本文档提供有关IVAS-IFM系统中TikHub API集成的使用说明。

## 1. 简介

TikHub API是一个多社交媒体数据分析平台，提供包括抖音、TikTok、小红书等平台的数据接口服务。我们的集成使用FastAPI实现了一个简单易用的本地API服务，将TikHub的强大功能封装为更简单的接口。

## 2. 配置

### API密钥设置

在使用TikHub API集成服务前，您需要设置TikHub的API密钥。有两种方式可以设置：

1. **环境变量**：设置`TIKHUB_API_KEY`环境变量

   ```bash
   # Windows
   set TIKHUB_API_KEY=您的TikHub_API密钥
   
   # Linux/Mac
   export TIKHUB_API_KEY=您的TikHub_API密钥
   ```

2. **配置文件**：创建`config.json`文件（从`config.example.json`复制并修改）

   ```json
   {
       "tikhub_api_key": "您的TikHub_API密钥"
   }
   ```

## 3. 启动服务

### 使用启动脚本

1. **Windows**：直接运行`run_tikhub_api.bat`批处理文件
2. **其他系统**：运行`python run_tikhub_api.py`

### 使用集成启动菜单

运行`start_service.bat`并选择选项2启动TikHub API服务。

## 4. API端点

服务启动后，以下API端点可用：

### 基础端点

- **GET /** - 获取服务信息和可用端点列表
- **GET /health** - 服务健康检查

### 通用视频解析端点

- **GET /api/video/info** - 获取视频信息（支持多平台）
  - 参数：`url` - 视频URL

- **GET /api/video/download** - 获取视频下载链接（支持多平台）
  - 参数：`url` - 视频URL

### 平台特定端点

- **GET /api/douyin/video** - 抖音视频解析
  - 参数：`url` - 抖音视频URL

- **GET /api/tiktok/video** - TikTok视频解析
  - 参数：`url` - TikTok视频URL

- **GET /api/xiaohongshu/post** - 小红书笔记解析
  - 参数：`url` - 小红书笔记URL

### 混合解析端点

- **GET /api/hybrid/parse** - 自动识别并解析多平台内容
  - 参数：`url` - 任何支持平台的内容URL

## 5. 使用示例

### Python使用示例

```python
import requests

# 服务地址
API_BASE_URL = "http://localhost:8002"

# API密钥 (如果在服务器端已配置可省略)
API_KEY = "您的API密钥"

# 解析抖音视频
douyin_url = "https://www.douyin.com/video/7159502929156705567"
response = requests.get(
    f"{API_BASE_URL}/api/video/info",
    params={"url": douyin_url},
    headers={"X-API-KEY": API_KEY}
)

# 打印结果
if response.status_code == 200:
    data = response.json()
    if data["success"]:
        video_info = data["data"]
        print(f"视频标题: {video_info['title']}")
        print(f"作者: {video_info['author']['nickname']}")
        print(f"播放次数: {video_info['statistics']['play_count']}")
        print(f"视频下载链接: {video_info['video_url']}")
    else:
        print(f"解析失败: {data['message']}")
else:
    print(f"请求失败: {response.status_code}")
```

### cURL使用示例

```bash
# 获取视频信息
curl -X GET "http://localhost:8002/api/video/info?url=https://www.douyin.com/video/7159502929156705567" -H "X-API-KEY: 您的API密钥"

# 获取视频下载链接
curl -X GET "http://localhost:8002/api/video/download?url=https://www.douyin.com/video/7159502929156705567" -H "X-API-KEY: 您的API密钥"

# 使用混合解析端点
curl -X GET "http://localhost:8002/api/hybrid/parse?url=https://www.douyin.com/video/7159502929156705567" -H "X-API-KEY: 您的API密钥"
```

## 6. 测试工具

项目提供了两个测试工具：

1. **test_direct_api.py** - 直接测试TikHub原始API
   ```bash
   python test_direct_api.py
   ```

2. **test_all_endpoints.py** - 测试本地API服务的所有端点
   ```bash
   # 测试所有端点
   python test_all_endpoints.py --all
   
   # 测试基本端点
   python test_all_endpoints.py --basic
   
   # 测试抖音视频
   python test_all_endpoints.py --douyin
   
   # 测试TikTok视频
   python test_all_endpoints.py --tiktok
   
   # 测试小红书笔记
   python test_all_endpoints.py --xiaohongshu
   
   # 测试混合解析端点
   python test_all_endpoints.py --hybrid
   
   # 使用自定义URL
   python test_all_endpoints.py --douyin --douyin-url="您的抖音视频URL"
   ```

3. **test_tikhub_api.bat** - Windows批处理测试脚本
   ```bash
   test_tikhub_api.bat
   ```

## 7. 注意事项

- 请确保您有有效的TikHub API密钥
- 服务默认运行在`http://localhost:8002`
- API请求需要在头部包含`X-API-KEY`
- 出现问题时，请检查API密钥配置和网络连接 