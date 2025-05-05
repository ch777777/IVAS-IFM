# TikHub API 集成实现文档

## 项目概述

本项目实现了对TikHub API的集成，提供了一个稳定的多平台视频解析服务，支持抖音、TikTok、小红书等平台的视频信息获取和无水印视频下载。

## 项目结构

```
/ (项目根目录)
  ├── tikhub_api.py          - TikHub API FastAPI服务
  ├── run_tikhub_api.py      - TikHub API服务启动脚本
  ├── run_tikhub_api.bat     - Windows环境下的TikHub API服务启动批处理脚本
  ├── tikhub_test.py         - TikHub API基本测试脚本
  ├── test_all_endpoints.py  - TikHub API全面测试脚本
  ├── test_tikhub_api.bat    - 测试批处理脚本
  ├── start_service.bat      - 服务启动菜单脚本
  ├── config.example.json    - 配置文件示例
  ├── app.py                 - 原始API服务
  └── README.md              - 项目文档
```

## 实现细节

### 1. TikHub API 服务 (`tikhub_api.py`)

- 使用FastAPI框架构建
- 提供多个API端点:
  - `/api/video/info` - 获取视频信息
  - `/api/video/download` - 获取无水印视频
  - `/api/douyin/video` - 解析抖音视频
  - `/api/tiktok/video` - 解析TikTok视频
  - `/api/xiaohongshu/post` - 解析小红书笔记
- 支持通过环境变量或配置文件设置API密钥
- 包含CORS中间件，允许跨域请求

### 2. API密钥配置

TikHub API密钥可以通过以下方式配置:

1. 环境变量 `TIKHUB_API_KEY`
2. 配置文件 `config.json` 中的 `tikhub_api_key` 字段

### 3. 服务启动

服务启动可以通过以下方式:

- 运行 `python run_tikhub_api.py`
- 运行 `run_tikhub_api.bat` (Windows环境)
- 通过 `start_service.bat` 菜单选择启动

默认情况下，服务运行在 `http://localhost:8002`，可以通过访问 `http://localhost:8002/docs` 查看API文档。

### 4. 测试

测试可以通过以下方式进行:

- 运行 `python tikhub_test.py` 进行基本测试
- 运行 `python test_all_endpoints.py` 进行全面测试
- 运行 `test_tikhub_api.bat` (Windows环境)

测试脚本支持多种参数，可以选择测试特定的端点或使用自定义的URL。

## 使用示例

### 示例1: 获取抖音视频信息

```python
import httpx

async def get_douyin_video_info(url):
    async with httpx.AsyncClient() as client:
        headers = {"X-API-KEY": "YOUR_API_KEY"}  # 替换为你的API密钥
        response = await client.get(
            "http://localhost:8002/api/douyin/video", 
            params={"url": url},
            headers=headers
        )
        return response.json()
```

### 示例2: 下载无水印TikTok视频

```python
import httpx

async def download_tiktok_video(url):
    async with httpx.AsyncClient() as client:
        headers = {"X-API-KEY": "YOUR_API_KEY"}  # 替换为你的API密钥
        response = await client.get(
            "http://localhost:8002/api/video/download", 
            params={"url": url},
            headers=headers
        )
        result = response.json()
        if result["success"]:
            # 下载视频
            video_url = result["download_url"]
            # 进一步处理...
        return result
```

## 注意事项

1. 使用TikHub API需要有效的API密钥
2. API调用可能受到TikHub API服务的速率限制
3. 使用时请遵守相关平台的使用条款和政策 