import httpx
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tikhub-interface")

class TikHubInterface:
    """TikHub API接口封装"""
    
    def __init__(self, api_key: str = None, base_url: str = "http://localhost:8002"):
        """
        初始化TikHub接口
        
        参数:
            api_key: TikHub API密钥
            base_url: API基础URL，默认为本地服务
        """
        # 尝试从配置文件或环境变量获取API密钥
        if api_key is None:
            api_key = os.environ.get("TIKHUB_API_KEY", "")
            
            if not api_key:
                config_path = Path(__file__).parent / "config.json"
                if config_path.exists():
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                        api_key = config.get("tikhub_api_key", "")
        
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"X-API-KEY": self.api_key}
        
        logger.info(f"TikHub接口初始化完成，基础URL: {self.base_url}")
    
    async def _request(self, endpoint: str, params: Dict = None, method: str = "GET") -> Dict:
        """
        发送API请求
        
        参数:
            endpoint: API端点
            params: 请求参数
            method: 请求方法 (GET/POST)
            
        返回:
            响应数据字典
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"请求: {method} {url} 参数: {params}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == "GET":
                    response = await client.get(url, params=params, headers=self.headers)
                else:
                    response = await client.post(url, json=params, headers=self.headers)
                
                response.raise_for_status()
                result = response.json()
                logger.debug(f"响应: {result}")
                return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP错误: {e.response.status_code} {e.response.text}")
            return {"error": str(e), "status_code": e.response.status_code}
        except Exception as e:
            logger.error(f"请求错误: {str(e)}")
            return {"error": str(e)}
    
    def request(self, endpoint: str, params: Dict = None, method: str = "GET") -> Dict:
        """同步请求API接口"""
        return asyncio.run(self._request(endpoint, params, method))
    
    # ===== 视频解析模块 =====
    
    def parse_url(self, url: str) -> Dict:
        """
        通用视频解析接口 (自动识别平台)
        
        参数:
            url: 视频URL (支持TikTok, Douyin, Xiaohongshu等)
            
        返回:
            解析结果
        """
        return self.request("/api/hybrid/parse", {"url": url})
    
    def parse_tiktok(self, url: str) -> Dict:
        """解析TikTok视频"""
        return self.request("/api/tiktok/parse", {"url": url})
    
    def parse_douyin(self, url: str) -> Dict:
        """解析抖音视频"""
        return self.request("/api/douyin/parse", {"url": url})
    
    def parse_xiaohongshu(self, url: str) -> Dict:
        """解析小红书视频/图文"""
        return self.request("/api/xiaohongshu/parse", {"url": url})
    
    # ===== 视频信息模块 =====
    
    def get_video_info(self, platform: str, video_id: str) -> Dict:
        """
        获取视频详细信息
        
        参数:
            platform: 平台名称 (tiktok, douyin, xiaohongshu)
            video_id: 视频ID
            
        返回:
            视频信息
        """
        return self.request("/api/video/info", {"platform": platform, "video_id": video_id})
    
    def get_user_info(self, platform: str, user_id: str) -> Dict:
        """
        获取用户信息
        
        参数:
            platform: 平台名称
            user_id: 用户ID
            
        返回:
            用户信息
        """
        return self.request("/api/user/info", {"platform": platform, "user_id": user_id})
    
    # ===== 视频下载模块 =====
    
    def get_download_url(self, platform: str, video_id: str) -> str:
        """
        获取视频下载URL
        
        参数:
            platform: 平台名称
            video_id: 视频ID
            
        返回:
            下载链接
        """
        result = self.request("/api/video/download", {"platform": platform, "video_id": video_id})
        return result.get("download_url", "")
    
    async def download_video(self, url: str, save_path: Union[str, Path]) -> Path:
        """
        下载视频到本地
        
        参数:
            url: 视频URL或平台视频链接
            save_path: 保存路径
            
        返回:
            保存的文件路径
        """
        # 如果url看起来像平台视频链接而不是直接下载链接
        if any(domain in url for domain in ["tiktok.com", "douyin.com", "xiaohongshu.com"]):
            # 先解析获取下载链接
            parse_result = self.parse_url(url)
            if "error" in parse_result:
                logger.error(f"解析URL失败: {parse_result}")
                return None
                
            # 从解析结果中获取下载链接
            if "video" in parse_result and "download_url" in parse_result["video"]:
                download_url = parse_result["video"]["download_url"]
            else:
                logger.error("无法从解析结果中获取下载链接")
                return None
        else:
            # 直接使用提供的URL作为下载链接
            download_url = url
        
        # 确保保存路径是Path对象
        save_path = Path(save_path)
        if save_path.is_dir():
            # 从URL中提取文件名
            filename = os.path.basename(download_url.split("?")[0]) or "video.mp4"
            save_path = save_path / filename
        
        # 下载文件
        logger.info(f"开始下载视频: {download_url} 到 {save_path}")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("GET", download_url) as response:
                    response.raise_for_status()
                    
                    # 确保目录存在
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 写入文件
                    with open(save_path, "wb") as f:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
            
            logger.info(f"视频下载完成: {save_path}")
            return save_path
        except Exception as e:
            logger.error(f"下载视频失败: {str(e)}")
            return None
    
    def download_video_sync(self, url: str, save_path: Union[str, Path]) -> Path:
        """同步下载视频"""
        return asyncio.run(self.download_video(url, save_path))
    
    # ===== 搜索模块 =====
    
    def search_videos(self, platform: str, keyword: str, count: int = 20) -> List[Dict]:
        """
        搜索视频
        
        参数:
            platform: 平台名称
            keyword: 搜索关键词
            count: 返回结果数量
            
        返回:
            视频列表
        """
        result = self.request("/api/search/videos", 
                             {"platform": platform, "keyword": keyword, "count": count})
        return result.get("videos", [])
    
    def search_users(self, platform: str, keyword: str, count: int = 20) -> List[Dict]:
        """
        搜索用户
        
        参数:
            platform: 平台名称
            keyword: 搜索关键词
            count: 返回结果数量
            
        返回:
            用户列表
        """
        result = self.request("/api/search/users", 
                             {"platform": platform, "keyword": keyword, "count": count})
        return result.get("users", [])
    
    # ===== 用户模块 =====
    
    def get_user_videos(self, platform: str, user_id: str, cursor: str = "", count: int = 20) -> Dict:
        """
        获取用户视频列表
        
        参数:
            platform: 平台名称
            user_id: 用户ID
            cursor: 分页游标
            count: 返回数量
            
        返回:
            视频列表和下一页游标
        """
        return self.request("/api/user/videos", 
                           {"platform": platform, "user_id": user_id, 
                            "cursor": cursor, "count": count})
    
    def get_user_following(self, platform: str, user_id: str, cursor: str = "", count: int = 20) -> Dict:
        """获取用户关注列表"""
        return self.request("/api/user/following", 
                           {"platform": platform, "user_id": user_id, 
                            "cursor": cursor, "count": count})
    
    def get_user_followers(self, platform: str, user_id: str, cursor: str = "", count: int = 20) -> Dict:
        """获取用户粉丝列表"""
        return self.request("/api/user/followers", 
                           {"platform": platform, "user_id": user_id, 
                            "cursor": cursor, "count": count})
    
    # ===== 评论模块 =====
    
    def get_video_comments(self, platform: str, video_id: str, cursor: str = "", count: int = 20) -> Dict:
        """
        获取视频评论
        
        参数:
            platform: 平台名称
            video_id: 视频ID
            cursor: 分页游标
            count: 返回数量
            
        返回:
            评论列表和下一页游标
        """
        return self.request("/api/video/comments", 
                           {"platform": platform, "video_id": video_id, 
                            "cursor": cursor, "count": count}) 