import httpx
import asyncio
from fastapi import FastAPI, Query, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tikhub-api")

# 初始化API
app = FastAPI(
    title="IVAS-IFM 视频平台集成 - TikHub API",
    description="使用TikHub提供的稳定API服务，支持抖音/TikTok/Xiaohongshu等多平台",
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

# TikHub API配置
TIKHUB_API_BASE_URL = "https://api.tikhub.io"
TIKHUB_API_KEY = ""  # 在实际使用时需要替换为您的API密钥

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

# 依赖项 - API密钥验证
async def get_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=403, detail="API密钥缺失")
    return x_api_key

# 路由
@app.get("/")
async def root():
    return {
        "message": "IVAS-IFM API 集成服务已启动 - 使用TikHub API",
        "available_endpoints": [
            "/api/video/info",
            "/api/video/download",
            "/api/douyin/video",
            "/api/tiktok/video",
            "/api/xiaohongshu/video"
        ]
    }

@app.get("/api/video/info", response_model=VideoResponse)
async def get_video_info(url: str = Query(..., description="视频链接URL"), api_key: str = Depends(get_api_key)):
    """
    获取视频信息，支持抖音、TikTok、小红书等平台
    """
    try:
        logger.info(f"正在解析视频信息: {url}")
        
        # 根据URL确定平台
        platform = "unknown"
        if "douyin.com" in url:
            platform = "douyin"
            endpoint = f"{TIKHUB_API_BASE_URL}/douyin/video"
        elif "tiktok.com" in url:
            platform = "tiktok"
            endpoint = f"{TIKHUB_API_BASE_URL}/tiktok/video"
        elif "xiaohongshu.com" in url:
            platform = "xiaohongshu"
            endpoint = f"{TIKHUB_API_BASE_URL}/xiaohongshu/post"
        else:
            return {
                "success": False,
                "message": "不支持的平台或URL格式",
                "data": None
            }
        
        # 调用TikHub API获取视频信息
        async with httpx.AsyncClient() as client:
            headers = {"X-API-KEY": api_key or TIKHUB_API_KEY}
            response = await client.get(endpoint, params={"url": url}, headers=headers)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"TikHub API返回错误: {response.status_code} - {response.text}",
                    "data": None
                }
            
            result = response.json()
            
            # 检查API响应
            if not result or "statusCode" in result and result["statusCode"] != 0:
                return {
                    "success": False,
                    "message": result.get("message", "API返回错误"),
                    "data": None
                }
            
            # 从API响应中提取数据
            data = result.get("data", {})
            
            # 标准化视频信息
            video_data = {
                "platform": platform,
                "video_id": data.get("id", ""),
                "url": url,
                "title": data.get("desc", ""),
                "description": data.get("desc", ""),
                "author": {
                    "id": data.get("authorId", ""),
                    "nickname": data.get("authorName", ""),
                    "signature": data.get("authorSignature", "")
                },
                "statistics": {
                    "play_count": data.get("playCount", 0),
                    "like_count": data.get("likeCount", 0),
                    "comment_count": data.get("commentCount", 0),
                    "share_count": data.get("shareCount", 0)
                },
                "video_url": data.get("videoUrl", ""),
                "cover_url": data.get("coverUrl", "")
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
async def download_video(url: str = Query(..., description="视频链接URL"), api_key: str = Depends(get_api_key)):
    """
    获取无水印视频下载链接
    """
    try:
        logger.info(f"正在获取视频下载链接: {url}")
        
        # 根据URL确定平台和端点
        if "douyin.com" in url:
            endpoint = f"{TIKHUB_API_BASE_URL}/douyin/video"
        elif "tiktok.com" in url:
            endpoint = f"{TIKHUB_API_BASE_URL}/tiktok/video"
        elif "xiaohongshu.com" in url:
            endpoint = f"{TIKHUB_API_BASE_URL}/xiaohongshu/post"
        else:
            return {
                "success": False,
                "message": "不支持的平台或URL格式",
                "download_url": None
            }
        
        # 调用TikHub API获取视频信息
        async with httpx.AsyncClient() as client:
            headers = {"X-API-KEY": api_key or TIKHUB_API_KEY}
            response = await client.get(endpoint, params={"url": url}, headers=headers)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"TikHub API返回错误: {response.status_code} - {response.text}",
                    "download_url": None
                }
            
            result = response.json()
            
            # 检查API响应
            if not result or "statusCode" in result and result["statusCode"] != 0:
                return {
                    "success": False,
                    "message": result.get("message", "API返回错误"),
                    "download_url": None
                }
            
            # 从API响应中提取视频URL
            data = result.get("data", {})
            video_url = data.get("videoUrl", "")
            
            if not video_url:
                return {
                    "success": False,
                    "message": "无法获取视频下载链接",
                    "download_url": None
                }
            
            return {
                "success": True,
                "message": "成功获取无水印视频链接",
                "download_url": video_url
            }
    except Exception as e:
        logger.error(f"获取视频下载链接时发生错误: {str(e)}")
        return {
            "success": False,
            "message": f"处理请求时发生错误: {str(e)}",
            "download_url": None
        }

@app.get("/api/douyin/video", response_model=ApiResponse)
async def get_douyin_video(url: str = Query(..., description="抖音视频链接"), api_key: str = Depends(get_api_key)):
    """
    解析抖音视频信息
    """
    try:
        logger.info(f"正在解析抖音视频: {url}")
        
        # 调用TikHub API获取抖音视频信息
        async with httpx.AsyncClient() as client:
            headers = {"X-API-KEY": api_key or TIKHUB_API_KEY}
            response = await client.get(f"{TIKHUB_API_BASE_URL}/douyin/video", params={"url": url}, headers=headers)
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"TikHub API返回错误: {response.status_code} - {response.text}",
                    "data": None
                }
            
            result = response.json()
            
            # 检查API响应
            if not result or "statusCode" in result and result["statusCode"] != 0:
                return {
                    "status": "error",
                    "message": result.get("message", "API返回错误"),
                    "data": None
                }
            
            # 返回数据
            return {
                "status": "success",
                "message": "成功解析抖音视频",
                "data": result.get("data", {})
            }
    except Exception as e:
        logger.error(f"解析抖音视频时发生错误: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }

@app.get("/api/tiktok/video", response_model=ApiResponse)
async def get_tiktok_video(url: str = Query(..., description="TikTok视频链接"), api_key: str = Depends(get_api_key)):
    """
    解析TikTok视频信息
    """
    try:
        logger.info(f"正在解析TikTok视频: {url}")
        
        # 调用TikHub API获取TikTok视频信息
        async with httpx.AsyncClient() as client:
            headers = {"X-API-KEY": api_key or TIKHUB_API_KEY}
            response = await client.get(f"{TIKHUB_API_BASE_URL}/tiktok/video", params={"url": url}, headers=headers)
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"TikHub API返回错误: {response.status_code} - {response.text}",
                    "data": None
                }
            
            result = response.json()
            
            # 检查API响应
            if not result or "statusCode" in result and result["statusCode"] != 0:
                return {
                    "status": "error",
                    "message": result.get("message", "API返回错误"),
                    "data": None
                }
            
            # 返回数据
            return {
                "status": "success",
                "message": "成功解析TikTok视频",
                "data": result.get("data", {})
            }
    except Exception as e:
        logger.error(f"解析TikTok视频时发生错误: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }

@app.get("/api/xiaohongshu/post", response_model=ApiResponse)
async def get_xiaohongshu_post(url: str = Query(..., description="小红书笔记链接"), api_key: str = Depends(get_api_key)):
    """
    解析小红书笔记信息
    """
    try:
        logger.info(f"正在解析小红书笔记: {url}")
        
        # 调用TikHub API获取小红书笔记信息
        async with httpx.AsyncClient() as client:
            headers = {"X-API-KEY": api_key or TIKHUB_API_KEY}
            response = await client.get(f"{TIKHUB_API_BASE_URL}/xiaohongshu/post", params={"url": url}, headers=headers)
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"TikHub API返回错误: {response.status_code} - {response.text}",
                    "data": None
                }
            
            result = response.json()
            
            # 检查API响应
            if not result or "statusCode" in result and result["statusCode"] != 0:
                return {
                    "status": "error",
                    "message": result.get("message", "API返回错误"),
                    "data": None
                }
            
            # 返回数据
            return {
                "status": "success",
                "message": "成功解析小红书笔记",
                "data": result.get("data", {})
            }
    except Exception as e:
        logger.error(f"解析小红书笔记时发生错误: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "IVAS-IFM API Integration - TikHub"}

# 主入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tikhub_api:app", host="0.0.0.0", port=8002, reload=True) 