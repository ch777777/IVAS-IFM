from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from douyin_tiktok_scraper.scraper import Scraper
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ivas-real-api")

# 初始化API
app = FastAPI(
    title="IVAS-IFM 视频平台集成 - 真实API",
    description="使用Douyin_TikTok_Download_API提供的真实API服务",
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

# Pydantic模型
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

class ApiResponse(BaseModel):
    status: str
    message: str
    data: Any = None

# 路由
@app.get("/")
async def root():
    return {
        "message": "IVAS-IFM API 集成服务已启动 - 使用真实API",
        "available_endpoints": [
            "/api/video/info",
            "/api/video/download",
            "/api/tiktok/video",
            "/api/douyin/video"
        ]
    }

@app.get("/api/video/info", response_model=VideoResponse)
async def get_video_info(url: str = Query(..., description="视频链接URL")):
    """
    获取视频信息，支持抖音、TikTok等平台
    """
    try:
        # 使用douyin-tiktok-scraper解析视频信息
        logger.info(f"正在解析视频信息: {url}")
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
        logger.info(f"正在获取视频下载链接: {url}")
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

@app.get("/api/tiktok/video", response_model=ApiResponse)
async def get_tiktok_video(url: str = Query(..., description="TikTok视频链接")):
    """
    解析TikTok视频信息
    """
    try:
        logger.info(f"正在解析TikTok视频: {url}")
        result = await scraper.get_tiktok_video_data(url)
        if result:
            return {
                "status": "success",
                "message": "成功解析TikTok视频",
                "data": result
            }
        return {
            "status": "error",
            "message": "无法解析TikTok视频",
            "data": None
        }
    except Exception as e:
        logger.error(f"解析TikTok视频时发生错误: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }

@app.get("/api/douyin/video", response_model=ApiResponse)
async def get_douyin_video(url: str = Query(..., description="抖音视频链接")):
    """
    解析抖音视频信息
    """
    try:
        logger.info(f"正在解析抖音视频: {url}")
        result = await scraper.get_douyin_video_data(url)
        if result:
            return {
                "status": "success",
                "message": "成功解析抖音视频",
                "data": result
            }
        return {
            "status": "error",
            "message": "无法解析抖音视频",
            "data": None
        }
    except Exception as e:
        logger.error(f"解析抖音视频时发生错误: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "IVAS-IFM API Integration"}

# 自定义错误处理
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return {
        "success": False,
        "message": f"处理请求时发生未知错误: {str(exc)}",
        "data": None
    } 