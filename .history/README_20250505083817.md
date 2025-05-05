# IVAS-IFM 视频平台API集成服务

这是一个为IVAS-IFM系统设计的视频平台API集成服务，整合了多个开源项目的功能，包括：

- **Douyin_TikTok_Download_API**: 提供抖音、TikTok等平台的视频解析和下载功能
- **TikHub API**: 提供稳定的抖音、TikTok、小红书等多平台视频解析服务
- **BibiGPT**: 提供视频内容摘要功能（当前为模拟实现）
- **KrillinAI**: 提供视频文本翻译功能（当前为模拟实现）
- **Butterfly**: 提供统一的API接口（已集成到本项目中）

## 功能特点

- 支持多平台视频信息获取 (抖音、TikTok、小红书等)
- 获取无水印视频下载链接
- 视频内容摘要生成
- 视频文本翻译功能
- RESTful API接口设计

## 环境要求

- Python 3.9+
- pip

## 安装与启动

1. 克隆项目并进入项目目录
```bash
mkdir ivas_api_integration
cd ivas_api_integration
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. 安装依赖
```bash
pip install requests aiohttp fastapi uvicorn httpx
```

4. 配置TikHub API (如果使用TikHub API)
   - 将`config.example.json`复制为`config.json`
   - 在`config.json`中填入你的TikHub API密钥
   - 或者设置环境变量`TIKHUB_API_KEY`

5. 启动原始服务器 (不使用TikHub API)
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

6. 或启动TikHub API服务
```bash
# Windows
run_tikhub_api.bat
# 或使用集成启动菜单
start_service.bat  # 然后选择选项2

# Linux/Mac
python run_tikhub_api.py
```

7. 访问API文档
```
# 原始API
http://localhost:8000/docs

# TikHub API服务
http://localhost:8002/docs
```

## TikHub API接口说明

### API认证

所有TikHub API请求都需要包含API密钥。在请求头中添加以下字段：

```
X-API-KEY: 您的TikHub_API密钥
```

### 1. 视频信息获取

```
GET /api/video/info?url={视频链接}
```

获取指定视频的详细信息，包括标题、描述、作者、统计数据等。

### 2. 无水印视频下载

```
GET /api/video/download?url={视频链接}
```

获取指定视频的无水印下载链接。

### 3. 抖音视频解析

```
GET /api/douyin/video?url={抖音视频链接}
```

解析抖音视频信息。

### 4. TikTok视频解析

```
GET /api/tiktok/video?url={TikTok视频链接}
```

解析TikTok视频信息。

### 5. 小红书笔记解析

```
GET /api/xiaohongshu/post?url={小红书笔记链接}
```

解析小红书笔记信息。

### 6. 混合解析（自动识别平台）

```
GET /api/hybrid/parse?url={任何支持平台的链接}
```

自动识别链接类型并解析相应平台的内容信息，支持抖音、TikTok、小红书等多个平台。

## 测试TikHub API

使用提供的测试脚本来测试TikHub API功能：

### 测试所有端点

```bash
python test_all_endpoints.py --all
```

### 测试特定端点

```bash
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
```

### 直接测试TikHub API

```bash
python test_direct_api.py
```

## API接口说明

### 1. 视频信息获取

```
GET /api/video/info?url={视频链接}
```

获取指定视频的详细信息，包括标题、描述、作者、统计数据等。

### 2. 无水印视频下载

```
GET /api/video/download?url={视频链接}
```

获取指定视频的无水印下载链接。

### 3. 视频内容摘要

```
GET /api/video/summary?url={视频链接}
```

获取指定视频的内容摘要。

### 4. 视频文本翻译

```
POST /api/video/translate
```

请求体示例:
```json
{
  "text": "要翻译的文本",
  "source_language": "zh",
  "target_language": "en"
}
```

将视频相关文本从源语言翻译到目标语言。

## 测试

使用提供的测试脚本来测试API功能：

```bash
# 测试原始API
python test_api.py

# 测试TikHub API
python test_all_endpoints.py
```

## 进阶配置

### 整合更多功能

要整合更多功能，可以参考以下开源项目:

1. **KrillinAI** (翻译和配音功能): <https://github.com/krillinai/KrillinAI>
2. **BibiGPT** (内容理解和摘要): <https://github.com/JimmyLv/BibiGPT-v1>

### 自定义配置

可以在`app.py`中修改相关配置，例如:

- 调整API端点
- 更改日志级别
- 添加自定义中间件

## 详细文档

更多详细使用说明请参阅：

- [TikHub API 集成使用指南](TIKHUB_API_USAGE.md)
- [TikHub API 集成实现文档](TIKHUB_INTEGRATION.md)

## 注意事项

- 本项目仅供学习和研究使用
- 请确保您使用的TikHub API密钥有效
- 使用时请遵守相关平台的使用条款和政策

# TikHub API 集成项目

这个项目提供了与TikHub API的集成，让您可以轻松地访问和使用TikTok、抖音、小红书等平台的数据。

## 功能特点

- 多平台支持：支持TikTok、抖音、小红书等多个平台
- 视频解析：解析视频链接，获取视频信息、下载链接等
- 视频下载：直接下载视频到本地
- 搜索功能：搜索视频和用户信息
- 用户数据：获取用户信息、视频列表、粉丝列表等
- 评论数据：获取视频评论

## 安装和配置

### 环境要求

- Python 3.7+
- 有效的TikHub API密钥

### 安装步骤

1. 安装依赖包：

```bash
pip install -r requirements.txt
```

2. 配置API密钥：

将您的TikHub API密钥添加到`config.json`文件中：

```json
{
  "tikhub_api_key": "您的API密钥"
}
```

## 使用方法

### 启动本地API服务

```bash
python run_tikhub_api_updated.py
```

这将启动本地API服务在端口8002上。

### 使用命令行工具

示例应用提供了命令行接口，可以轻松使用主要功能：

```bash
# 解析视频链接
python example_app.py parse https://www.tiktok.com/@example/video/1234567890

# 获取视频信息
python example_app.py info --platform tiktok --video-id 1234567890

# 搜索视频
python example_app.py search-videos --platform tiktok --keyword "dance" --count 10

# 下载视频
python example_app.py download --url https://www.tiktok.com/@example/video/1234567890 --output downloads
```

### 启动Web应用

项目还提供了一个Web界面，方便使用各种功能：

```bash
python web_app.py
```

然后在浏览器中访问 http://localhost:8000 即可使用Web界面。

### 编程接口

您也可以在自己的代码中直接使用TikHub接口：

```python
from tikhub_interface import TikHubInterface

# 初始化接口
tikhub = TikHubInterface(api_key="您的API密钥")

# 解析视频链接
result = tikhub.parse_url("https://www.tiktok.com/@example/video/1234567890")
print(result)

# 下载视频
tikhub.download_video_sync("https://www.tiktok.com/@example/video/1234567890", "downloads")
```

## 接口文档

详细的API使用说明请参考TikHub官方文档：https://github.com/TikHub/TikHub-API-Python-SDK-V2

## 注意事项

- 确保您有有效的TikHub API密钥
- 使用API时注意遵守平台的使用条款和限制
- 如遇到API请求失败，可能是远程API有所变化，请检查最新的TikHub文档 