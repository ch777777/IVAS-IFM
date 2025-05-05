import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from ivas_integration import IVASVideoProcessor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ivas-api")

# 加载配置
config_path = Path(__file__).parent / "config.json"
try:
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            TIKHUB_API_KEY = config.get("tikhub_api_key", "")
            BIBIGPT_API_KEY = config.get("bibigpt_api_key", "")
            KRILLINAI_API_KEY = config.get("krillinai_api_key", "")
    else:
        TIKHUB_API_KEY = os.environ.get("TIKHUB_API_KEY", "0KMsWDohw2EtvSsxjmmtwUM33yUYhKD84a108Gz4mUZT0XUIIMJ/nDGNIg==")
        BIBIGPT_API_KEY = os.environ.get("BIBIGPT_API_KEY", "")
        KRILLINAI_API_KEY = os.environ.get("KRILLINAI_API_KEY", "")
except Exception as e:
    logger.warning(f"加载配置文件失败: {e}，将使用默认配置")
    TIKHUB_API_KEY = os.environ.get("TIKHUB_API_KEY", "0KMsWDohw2EtvSsxjmmtwUM33yUYhKD84a108Gz4mUZT0XUIIMJ/nDGNIg==")
    BIBIGPT_API_KEY = os.environ.get("BIBIGPT_API_KEY", "")
    KRILLINAI_API_KEY = os.environ.get("KRILLINAI_API_KEY", "")

# 创建下载目录
DOWNLOADS_DIR = Path(__file__).parent / "downloads"
DOWNLOADS_DIR.mkdir(exist_ok=True)

# 检查API密钥配置
if not BIBIGPT_API_KEY:
    logger.warning("BibiGPT API密钥未配置，将使用模拟摘要功能")
if not KRILLINAI_API_KEY:
    logger.warning("KrillinAI API密钥未配置，将使用模拟翻译功能")

# 创建FastAPI应用
app = FastAPI(
    title="IVAS-IFM 视频平台API集成服务",
    description="整合多个视频平台的API，提供统一的接口服务",
    version="1.0.0"
)

# 启用CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化IVAS视频处理器
ivas_processor = IVASVideoProcessor(tikhub_api_key=TIKHUB_API_KEY)

# 定义数据模型
class VideoSearchParams(BaseModel):
    """视频搜索参数"""
    keyword: str = Field(..., description="搜索关键词")
    platform: str = Field("douyin", description="平台名称: douyin/tiktok/xiaohongshu")
    count: int = Field(20, description="返回结果数量", ge=1, le=100)

class TranslationParams(BaseModel):
    """翻译参数"""
    text: str = Field(..., description="要翻译的文本")
    source_language: str = Field("zh", description="源语言代码")
    target_language: str = Field("en", description="目标语言代码")

class VideoUrlParams(BaseModel):
    """视频URL参数"""
    url: str = Field(..., description="视频URL")

class UserVideosParams(BaseModel):
    """用户视频参数"""
    user_id: str = Field(..., description="用户ID")
    platform: str = Field("douyin", description="平台名称: douyin/tiktok/xiaohongshu")
    count: int = Field(20, description="返回结果数量", ge=1, le=100)
    cursor: str = Field("", description="分页游标")

# 定义路由

@app.get("/")
async def read_root():
    """API首页"""
    # 检查API集成状态
    apis_status = {
        "tikhub": {"enabled": True, "status": "active"},
        "bibigpt": {"enabled": bool(BIBIGPT_API_KEY), "status": "active" if BIBIGPT_API_KEY else "mock"},
        "krillinai": {"enabled": bool(KRILLINAI_API_KEY), "status": "active" if KRILLINAI_API_KEY else "mock"}
    }
    
    return {
        "name": "IVAS-IFM 视频平台API集成服务",
        "version": "1.0.0",
        "documentation": "/docs",
        "supported_platforms": ["douyin", "tiktok", "xiaohongshu"],
        "apis_status": apis_status
    }

@app.get("/api/video/info")
async def get_video_info(url: str = Query(..., description="视频URL")):
    """获取视频信息，包含视频详情、摘要和翻译"""
    try:
        result = ivas_processor.process_video_url(url)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        logger.exception("获取视频信息失败")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/video/info")
async def post_video_info(params: VideoUrlParams):
    """获取视频信息 (POST版本)"""
    try:
        result = ivas_processor.process_video_url(params.url)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        logger.exception("获取视频信息失败")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/video/download")
async def get_video_download(url: str = Query(..., description="视频URL")):
    """获取视频下载链接"""
    try:
        # 先解析获取下载链接
        result = ivas_processor.process_video_url(url)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "download_url": result.get("download_url", ""),
            "platform": result.get("platform")
        }
    except Exception as e:
        logger.exception("获取视频下载链接失败")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/video/download-file")
async def download_video_file(params: VideoUrlParams, background_tasks: BackgroundTasks):
    """下载视频到服务器并提供文件下载链接"""
    try:
        # 生成文件名
        import uuid
        filename = f"{uuid.uuid4().hex}.mp4"
        
        # 在后台任务中下载视频
        download_result = ivas_processor.download_video(params.url, filename)
        
        if not download_result.get("success"):
            raise HTTPException(status_code=400, detail=download_result.get("message"))
        
        file_path = download_result.get("file_path")
        
        return {
            "success": True,
            "message": "视频下载成功",
            "file_path": file_path,
            "file_size": download_result.get("file_size"),
            "download_url": f"/api/files/download/{os.path.basename(file_path)}"
        }
    except Exception as e:
        logger.exception("下载视频失败")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/download/{filename}")
async def download_file(filename: str):
    """下载已保存的文件"""
    file_path = DOWNLOADS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="video/mp4"
    )

@app.post("/api/search/videos")
async def search_videos(params: VideoSearchParams):
    """搜索视频"""
    try:
        result = ivas_processor.search_videos(
            keyword=params.keyword,
            platform=params.platform,
            count=params.count
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
    except Exception as e:
        logger.exception("搜索视频失败")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/user/videos")
async def get_user_videos(params: UserVideosParams):
    """获取用户视频列表"""
    try:
        result = ivas_processor.get_user_videos(
            user_id=params.user_id,
            platform=params.platform,
            count=params.count
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
    except Exception as e:
        logger.exception("获取用户视频失败")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/video/translate")
async def translate_text(params: TranslationParams):
    """翻译文本 (使用KrillinAI或内置模拟翻译)"""
    try:
        result = ivas_processor.translate_text(
            text=params.text,
            source_lang=params.source_language,
            target_lang=params.target_language
        )
        
        # 添加翻译服务信息
        if result.get("is_mocked", False):
            result["service"] = "mock"
        else:
            result["service"] = "krillinai"
        
        return result
    except Exception as e:
        logger.exception("翻译文本失败")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/video/summary")
async def get_video_summary(url: str = Query(..., description="视频URL")):
    """获取视频内容摘要 (使用BibiGPT或内置模拟摘要)"""
    try:
        # 先解析视频获取信息
        video_result = ivas_processor.process_video_url(url)
        if "error" in video_result:
            raise HTTPException(status_code=400, detail=video_result["error"])
        
        summary = video_result.get("summary", {})
        
        # 添加摘要服务信息
        if summary.get("is_mocked", False):
            service = "mock"
        else:
            service = "bibigpt"
        
        # 返回摘要部分
        return {
            "success": True,
            "video_info": {
                "title": video_result.get("video_info", {}).get("title", ""),
                "author": video_result.get("video_info", {}).get("author", {})
            },
            "summary": summary,
            "service": service
        }
    except Exception as e:
        logger.exception("获取视频摘要失败")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hybrid/parse")
async def hybrid_parse(url: str = Query(..., description="任何支持平台的链接")):
    """混合解析端点 (自动识别平台)"""
    try:
        result = ivas_processor.process_video_url(url)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        logger.exception("混合解析失败")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_api_status():
    """获取API服务状态"""
    return {
        "tikhub": {
            "enabled": True,
            "api_key_configured": bool(TIKHUB_API_KEY),
            "status": "active"
        },
        "bibigpt": {
            "enabled": True,
            "api_key_configured": bool(BIBIGPT_API_KEY),
            "status": "active" if BIBIGPT_API_KEY else "mock"
        },
        "krillinai": {
            "enabled": True,
            "api_key_configured": bool(KRILLINAI_API_KEY),
            "status": "active" if KRILLINAI_API_KEY else "mock"
        }
    }

# 平台特定端点
@app.get("/api/douyin/parse")
async def parse_douyin(url: str = Query(..., description="抖音视频链接")):
    """解析抖音视频"""
    return await hybrid_parse(url=url)

@app.get("/api/tiktok/parse")
async def parse_tiktok(url: str = Query(..., description="TikTok视频链接")):
    """解析TikTok视频"""
    return await hybrid_parse(url=url)

@app.get("/api/xiaohongshu/parse")
async def parse_xiaohongshu(url: str = Query(..., description="小红书笔记链接")):
    """解析小红书笔记"""
    return await hybrid_parse(url=url)

# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ivas_api:app", host="0.0.0.0", port=8000, reload=True) 