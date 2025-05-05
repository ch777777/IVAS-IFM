import asyncio
import httpx
from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional
import logging
from douyin_tiktok_scraper.scraper import Scraper

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ivas-api-integration")

# 初始化API
app = FastAPI(
    title="IVAS-IFM 视频平台API集成",
    description="整合多个视频平台API，为IVAS-IFM系统提供统一接口",
    version="0.1.0",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建抖音/TikTok抓取器实例
scraper = Scraper()

# Pydantic 模型
class VideoInfo(BaseModel):
    platform: str
    video_id: str
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    video_url: Optional[str] = None
    cover_url: Optional[str] = None

class VideoResponse(BaseModel):
    success: bool
    message: str
    data: Optional[VideoInfo] = None

class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

class TranslationResponse(BaseModel):
    success: bool
    message: str
    translated_text: Optional[str] = None

# 路由

@app.get("/")
async def root():
    return {
        "message": "IVAS-IFM API 集成服务已启动",
        "available_endpoints": [
            "/api/video/info",
            "/api/video/download",
            "/api/video/translate",
            "/api/video/summary"
        ]
    }

@app.get("/api/video/info", response_model=VideoResponse)
async def get_video_info(url: str = Query(..., description="视频链接URL")):
    """
    获取视频信息，支持抖音、TikTok等平台
    """
    try:
        # 使用douyin-tiktok-scraper解析视频信息
        result = await scraper.hybrid_parsing(url)
        
        if not result or "status" in result and result["status"] == "failed":
            return {
                "success": False,
                "message": "无法解析视频信息",
                "data": None
            }
            
        # 处理结果
        platform = result.get("platform", "未知平台")
        video_data = {
            "platform": platform,
            "video_id": result.get("aweme_id", ""),
            "url": result.get("share_url", url),
            "title": result.get("desc", ""),
            "description": result.get("desc", ""),
            "author": {
                "id": result.get("author", {}).get("uid", ""),
                "nickname": result.get("author", {}).get("nickname", ""),
                "signature": result.get("author", {}).get("signature", "")
            },
            "statistics": {
                "play_count": result.get("statistics", {}).get("play_count", 0),
                "digg_count": result.get("statistics", {}).get("digg_count", 0),
                "comment_count": result.get("statistics", {}).get("comment_count", 0),
                "share_count": result.get("statistics", {}).get("share_count", 0)
            },
            "video_url": result.get("video", {}).get("play_addr", {}).get("url_list", [""])[0],
            "cover_url": result.get("video", {}).get("cover", {}).get("url_list", [""])[0]
        }
        
        return {
            "success": True,
            "message": "成功获取视频信息",
            "data": video_data
        }
    except Exception as e:
        logger.error(f"获取视频信息时发生错误: {str(e)}")
        return {
            "success": False,
            "message": f"处理请求时发生错误: {str(e)}",
            "data": None
        }

@app.get("/api/video/download")
async def download_video(url: str = Query(..., description="视频链接URL")):
    """
    获取无水印视频下载链接
    """
    try:
        # 使用douyin-tiktok-scraper解析视频信息
        result = await scraper.hybrid_parsing(url)
        
        if not result or "status" in result and result["status"] == "failed":
            raise HTTPException(status_code=404, detail="无法获取视频信息")
            
        # 获取无水印视频URL
        if "video" in result and "play_addr" in result["video"] and "url_list" in result["video"]["play_addr"]:
            video_url = result["video"]["play_addr"]["url_list"][0]
            return {
                "success": True,
                "message": "成功获取无水印视频链接",
                "download_url": video_url
            }
        else:
            return {
                "success": False,
                "message": "无法获取视频下载链接",
                "download_url": None
            }
    except Exception as e:
        logger.error(f"获取视频下载链接时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}")

@app.post("/api/video/translate", response_model=TranslationResponse)
async def translate_video_text(request: TranslationRequest):
    """
    翻译视频文本 (模拟KrillinAI功能)
    """
    try:
        # 这里仅作为演示，实际使用中应整合KrillinAI或其他翻译服务
        # 模拟翻译结果
        translated_text = f"[翻译] {request.text}"
        
        return {
            "success": True,
            "message": "文本翻译成功",
            "translated_text": translated_text
        }
    except Exception as e:
        logger.error(f"翻译视频文本时发生错误: {str(e)}")
        return {
            "success": False,
            "message": f"翻译过程中发生错误: {str(e)}",
            "translated_text": None
        }

@app.get("/api/video/summary")
async def get_video_summary(url: str = Query(..., description="视频链接URL")):
    """
    获取视频内容摘要 (模拟BibiGPT功能)
    """
    try:
        # 使用douyin-tiktok-scraper解析视频信息
        result = await scraper.hybrid_parsing(url)
        
        if not result or "status" in result and result["status"] == "failed":
            raise HTTPException(status_code=404, detail="无法获取视频信息")
            
        # 这里仅作为演示，实际使用中应整合BibiGPT或其他摘要服务
        # 从解析结果获取视频描述
        description = result.get("desc", "无描述")
        
        # 模拟生成摘要
        summary = f"视频摘要: {description[:50]}..." if len(description) > 50 else f"视频摘要: {description}"
        
        return {
            "success": True,
            "message": "成功生成视频摘要",
            "summary": summary,
            "full_text": description
        }
    except Exception as e:
        logger.error(f"生成视频摘要时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}")

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 