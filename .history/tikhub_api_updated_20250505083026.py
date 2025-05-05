import httpx
import asyncio
import os
import json
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tikhub-api")

# TikHub API配置
TIKHUB_API_BASE_URL = "https://api.tikhub.io"

# 尝试从环境变量获取API密钥
TIKHUB_API_KEY = os.environ.get("TIKHUB_API_KEY", "")

# 如果环境变量中没有API密钥，尝试从配置文件中读取
if not TIKHUB_API_KEY:
    try:
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                TIKHUB_API_KEY = config.get("tikhub_api_key", "")
    except Exception as e:
        logger.warning(f"读取配置文件时出错: {str(e)}")

# 初始化API
app = FastAPI(
    title="IVAS-IFM 视频平台集成 - TikHub API",
    description="使用TikHub提供的稳定API服务，支持抖音/TikTok/Xiaohongshu等多平台",
    version="0.2.0",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    success: bool
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
            "/api/xiaohongshu/post",
            "/api/hybrid/parse"
        ]
    }

@app.get("/api/video/info", response_model=VideoResponse)
async def get_video_info(url: str = Query(..., description="视频链接URL"), api_key: str = Depends(get_api_key)):
    """
    获取视频信息，支持抖音、TikTok、小红书等平台
    """
    try:
        logger.info(f"正在解析视频信息: {url}")
        
        # 使用混合解析API，自动识别平台 - V2版本使用新端点
        endpoint = f"{TIKHUB_API_BASE_URL}/api/v1/hybrid/video_data"
        
        # 调用TikHub API获取视频信息
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {api_key or TIKHUB_API_KEY}"}
            response = await client.get(endpoint, params={"url": url}, headers=headers)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"TikHub API返回错误: {response.status_code} - {response.text}",
                    "data": None
                }
            
            result = response.json()
            
            # 检查API响应
            if "error" in result and result["error"].get("code") != "ok":
                return {
                    "success": False,
                    "message": result["error"].get("message", "API返回错误"),
                    "data": None
                }
            
            # 从API响应中提取数据
            data = result.get("data", {})
            
            # 识别平台
            platform = "unknown"
            if "douyin.com" in url:
                platform = "douyin"
            elif "tiktok.com" in url:
                platform = "tiktok"
            elif "xiaohongshu.com" in url:
                platform = "xiaohongshu"
            
            # 标准化视频信息
            video_data = {
                "platform": platform,
                "video_id": data.get("id", ""),
                "url": url,
                "title": data.get("title", data.get("desc", "")),
                "description": data.get("desc", ""),
                "author": {
                    "id": data.get("author", {}).get("id", ""),
                    "nickname": data.get("author", {}).get("nickname", ""),
                    "signature": data.get("author", {}).get("signature", "")
                },
                "statistics": {
                    "play_count": data.get("statistics", {}).get("play_count", 0),
                    "like_count": data.get("statistics", {}).get("like_count", 0),
                    "comment_count": data.get("statistics", {}).get("comment_count", 0),
                    "share_count": data.get("statistics", {}).get("share_count", 0)
                },
                "video_url": data.get("video_url", data.get("url", "")),
                "cover_url": data.get("cover_url", data.get("cover", ""))
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
        
        # 使用混合解析API，自动识别平台 - V2版本使用新端点
        endpoint = f"{TIKHUB_API_BASE_URL}/api/v1/hybrid/video_data"
        
        # 调用TikHub API获取视频信息
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {api_key or TIKHUB_API_KEY}"}
            response = await client.get(endpoint, params={"url": url}, headers=headers)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"TikHub API返回错误: {response.status_code} - {response.text}",
                    "download_url": None
                }
            
            result = response.json()
            
            # 检查API响应
            if "error" in result and result["error"].get("code") != "ok":
                return {
                    "success": False,
                    "message": result["error"].get("message", "API返回错误"),
                    "download_url": None
                }
            
            # 从API响应中提取视频URL
            data = result.get("data", {})
            video_url = data.get("video_url", data.get("url", ""))
            
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
        
        # 调用TikHub API获取抖音视频信息 - 使用V2版本端点
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {api_key or TIKHUB_API_KEY}"}
            
            # 使用DouyinWeb API端点
            endpoint = f"{TIKHUB_API_BASE_URL}/api/v1/douyin/web/video_detail"
            response = await client.get(endpoint, params={"url": url}, headers=headers)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"TikHub API返回错误: {response.status_code} - {response.text}",
                    "data": None
                }
            
            result = response.json()
            
            return {
                "success": True,
                "message": "成功获取抖音视频信息",
                "data": result.get("data", {})
            }
    except Exception as e:
        logger.error(f"获取抖音视频信息时发生错误: {str(e)}")
        return {
            "success": False,
            "message": f"处理请求时发生错误: {str(e)}",
            "data": None
        }

@app.get("/api/tiktok/video", response_model=ApiResponse)
async def get_tiktok_video(url: str = Query(..., description="TikTok视频链接"), api_key: str = Depends(get_api_key)):
    """
    解析TikTok视频信息
    """
    try:
        logger.info(f"正在解析TikTok视频: {url}")
        
        # 调用TikHub API获取TikTok视频信息 - 使用V2版本端点
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {api_key or TIKHUB_API_KEY}"}
            
            # 使用TikTokWeb API端点
            endpoint = f"{TIKHUB_API_BASE_URL}/api/v1/tiktok/web/video_detail"
            response = await client.get(endpoint, params={"url": url}, headers=headers)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"TikHub API返回错误: {response.status_code} - {response.text}",
                    "data": None
                }
            
            result = response.json()
            
            return {
                "success": True,
                "message": "成功获取TikTok视频信息",
                "data": result.get("data", {})
            }
    except Exception as e:
        logger.error(f"获取TikTok视频信息时发生错误: {str(e)}")
        return {
            "success": False,
            "message": f"处理请求时发生错误: {str(e)}",
            "data": None
        }

@app.get("/api/xiaohongshu/post", response_model=ApiResponse)
async def get_xiaohongshu_post(url: str = Query(..., description="小红书笔记链接"), api_key: str = Depends(get_api_key)):
    """
    解析小红书笔记信息
    """
    try:
        logger.info(f"正在解析小红书笔记: {url}")
        
        # 调用TikHub API获取小红书笔记信息 - 使用V2版本端点
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {api_key or TIKHUB_API_KEY}"}
            
            # 使用XiaohongshuWeb API端点
            endpoint = f"{TIKHUB_API_BASE_URL}/api/v1/xiaohongshu/web/note_detail"
            response = await client.get(endpoint, params={"url": url}, headers=headers)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"TikHub API返回错误: {response.status_code} - {response.text}",
                    "data": None
                }
            
            result = response.json()
            
            return {
                "success": True,
                "message": "成功获取小红书笔记信息",
                "data": result.get("data", {})
            }
    except Exception as e:
        logger.error(f"获取小红书笔记信息时发生错误: {str(e)}")
        return {
            "success": False,
            "message": f"处理请求时发生错误: {str(e)}",
            "data": None
        }

@app.get("/api/hybrid/parse", response_model=ApiResponse)
async def hybrid_parse(url: str = Query(..., description="视频/笔记链接，支持多平台自动识别"), api_key: str = Depends(get_api_key)):
    """
    混合解析接口，自动识别链接类型并解析
    """
    try:
        logger.info(f"正在混合解析链接: {url}")
        
        # 使用混合解析API，自动识别平台 - 使用V2版本端点
        endpoint = f"{TIKHUB_API_BASE_URL}/api/v1/hybrid/video_data"
        
        # 调用TikHub API获取内容信息
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {api_key or TIKHUB_API_KEY}"}
            response = await client.get(endpoint, params={"url": url}, headers=headers)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"TikHub API返回错误: {response.status_code} - {response.text}",
                    "data": None
                }
            
            result = response.json()
            
            # 检查API响应
            if "error" in result and result["error"].get("code") != "ok":
                return {
                    "success": False,
                    "message": result["error"].get("message", "API返回错误"),
                    "data": None
                }
            
            # 返回数据
            return {
                "success": True,
                "message": "成功解析内容",
                "data": result.get("data", {})
            }
    except Exception as e:
        logger.error(f"混合解析链接时发生错误: {str(e)}")
        return {
            "success": False,
            "message": f"处理请求时发生错误: {str(e)}",
            "data": None
        }

@app.get("/health")
async def health_check():
    """
    健康检查端点
    """
    return {
        "status": "ok",
        "message": "Service is running",
        "version": "0.2.0"
    } 