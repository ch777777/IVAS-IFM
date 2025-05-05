# IVAS-IFM 视频平台API集成服务

这是一个为IVAS-IFM系统设计的视频平台API集成服务，整合了TikHub API与多种功能模块，提供统一的视频平台数据获取和处理能力。

## 功能特点

- **TikHub API集成**: 集成TikHub API，支持多平台视频解析和下载
- **多平台支持**: 支持TikTok、抖音、小红书等多个平台
- **视频内容分析**: 支持视频信息提取、摘要生成和情感分析（集成BibiGPT）
- **文本翻译**: 支持视频内容的多语言翻译（集成KrillinAI）
- **统一API接口**: 提供标准化的RESTful API，易于集成到其他系统

## 系统架构

![IVAS系统架构](docs/ivas_architecture.png)

IVAS-IFM系统由以下几个关键组件组成：

1. **TikHub API服务**: 提供基础的视频解析和下载功能
2. **IVAS API集成服务**: 集成各功能模块，提供统一接口
3. **Web界面**: 提供用户友好的Web操作界面
4. **摘要生成服务**: 集成BibiGPT功能
5. **翻译服务**: 集成KrillinAI功能

## 安装和配置

### 环境要求

- Python 3.7+
- 有效的TikHub API密钥
- BibiGPT API密钥（用于视频摘要功能）
- KrillinAI API密钥（用于文本翻译功能）

### 安装步骤

1. 安装依赖包：

```bash
pip install -r requirements.txt
```

2. 配置API密钥：

将您的API密钥添加到`config.json`文件中：

```json
{
  "tikhub_api_key": "您的TikHub API密钥",
  "bibigpt_api_key": "您的BibiGPT API密钥",
  "krillinai_api_key": "您的KrillinAI API密钥",
  "bibigpt_api_url": "https://api.bibigpt.ai/v1/summarize",
  "krillinai_api_url": "https://api.krillinai.com/v1/translate",
  "tikhub_api_url": "http://localhost:8002"
}
```

您也可以通过环境变量配置API密钥：

```bash
export TIKHUB_API_KEY="您的TikHub API密钥"
export BIBIGPT_API_KEY="您的BibiGPT API密钥"
export KRILLINAI_API_KEY="您的KrillinAI API密钥"
```

### 配置外部服务

#### BibiGPT摘要服务

BibiGPT是一个智能视频内容摘要服务，需要先注册账号并获取API密钥：

1. 访问 [BibiGPT官网](https://bibigpt.ai) 注册账号
2. 在开发者设置中创建API密钥
3. 将API密钥添加到配置文件或环境变量

如果未配置BibiGPT API密钥，系统将使用内置的简单摘要功能。

#### KrillinAI翻译服务

KrillinAI是一个专业的翻译服务，需要先注册账号并获取API密钥：

1. 访问 [KrillinAI官网](https://krillinai.com) 注册账号
2. 在开发者控制台中创建API密钥
3. 将API密钥添加到配置文件或环境变量

如果未配置KrillinAI API密钥，系统将使用内置的简单翻译功能。

## 启动服务

IVAS-IFM系统提供了多种启动方式：

### 1. 交互式菜单启动

```bash
python start_ivas.py
```

这将显示一个交互式菜单，您可以选择启动各个服务：

```
==================================================
IVAS-IFM 视频平台API集成服务启动菜单
==================================================
1. 启动TikHub API服务 (基础解析服务)
2. 启动IVAS API服务 (集成服务)
3. 启动TikHub Web应用 (Web界面)
4. 启动所有服务
5. 退出
==================================================
请输入选项 [1-5]:
```

### 2. 命令行参数启动

```bash
# 启动所有服务
python start_ivas.py --all

# 仅启动TikHub API服务
python start_ivas.py --tikhub

# 仅启动IVAS API集成服务
python start_ivas.py --ivas

# 仅启动Web应用
python start_ivas.py --web

# 在前台运行（不在后台）
python start_ivas.py --all --foreground
```

### 3. 单独启动各个服务

```bash
# 启动TikHub API服务
python run_tikhub_api_updated.py

# 启动IVAS API服务
python ivas_api.py

# 启动Web应用
python web_app.py
```

## 使用API

### API文档

启动服务后，可以通过以下链接访问API文档：

- IVAS API: `http://localhost:8000/docs`
- TikHub API: `http://localhost:8002/docs`

### 常用API端点

#### 视频解析 (自动识别平台)

```
GET /api/hybrid/parse?url={视频链接}
```

获取指定视频的详细信息、摘要和翻译。

#### 视频下载

```
GET /api/video/download?url={视频链接}
```

获取指定视频的无水印下载链接。

#### 视频摘要

```
GET /api/video/summary?url={视频链接}
```

获取指定视频的内容摘要。

#### 搜索视频

```
POST /api/search/videos
Content-Type: application/json

{
  "keyword": "搜索关键词",
  "platform": "douyin",
  "count": 20
}
```

搜索指定平台的视频。

#### 翻译文本

```
POST /api/video/translate
Content-Type: application/json

{
  "text": "要翻译的文本",
  "source_language": "zh",
  "target_language": "en"
}
```

将文本从源语言翻译到目标语言。

## 开发接入指南

### 直接使用IVAS集成模块

您可以在自己的Python代码中直接使用IVAS集成模块：

```python
from ivas_integration import IVASVideoProcessor

# 初始化处理器
processor = IVASVideoProcessor(tikhub_api_key="您的API密钥")

# 解析视频
result = processor.process_video_url("https://www.douyin.com/video/7159502929156705567")
print(result)

# 下载视频
download_info = processor.download_video("https://www.douyin.com/video/7159502929156705567")
print(f"下载成功: {download_info['file_path']}")

# 翻译文本
translation = processor.translate_text("这个视频很有趣", "zh", "en")
print(f"翻译结果: {translation['translated_text']}")
```

### 通过API接入

从其他应用或服务中，您可以通过调用IVAS API来集成视频处理功能：

```javascript
// JavaScript示例
async function parseVideo(url) {
  const response = await fetch(`http://localhost:8000/api/hybrid/parse?url=${encodeURIComponent(url)}`);
  const data = await response.json();
  return data;
}

// 使用示例
parseVideo("https://www.douyin.com/video/7159502929156705567")
  .then(result => console.log(result))
  .catch(error => console.error(error));
```

## 集成自定义服务

### 集成不同的摘要服务

如果需要使用其他摘要服务替代BibiGPT，可以修改`ivas_integration.py`中的`_generate_summary`方法：

```python
def _generate_summary(self, video_info: Dict) -> Dict:
    # 这里替换为您自己的摘要API调用逻辑
    # 例如使用OpenAI GPT或其他摘要服务
    
    # 调用您的摘要API
    summary_result = your_summary_api.generate(
        title=video_info.get("title", ""),
        description=video_info.get("description", "")
    )
    
    return {
        "summary": summary_result.summary,
        "keywords": summary_result.keywords,
        "sentiment": summary_result.sentiment
    }
```

### 集成不同的翻译服务

如果需要使用其他翻译服务替代KrillinAI，可以修改`ivas_integration.py`中的`translate_text`方法：

```python
def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict:
    # 这里替换为您自己的翻译API调用逻辑
    # 例如使用Google Translate或DeepL等服务
    
    # 调用您的翻译API
    translation = your_translation_api.translate(
        text=text,
        source_language=source_lang,
        target_language=target_lang
    )
    
    return {
        "success": True,
        "original_text": text,
        "translated_text": translation.result,
        "source_language": source_lang,
        "target_language": target_lang
    }
```

## 注意事项

- 本项目仅供学习和研究使用
- 请确保使用的TikHub、BibiGPT和KrillinAI API密钥有效
- 使用时请遵守相关平台的使用条款和政策
- 如果未配置BibiGPT或KrillinAI密钥，系统将使用内置的简单功能模拟

## 贡献

欢迎提交Pull Request或Issue帮助改进IVAS-IFM系统。

## 许可

本项目采用MIT许可证。 