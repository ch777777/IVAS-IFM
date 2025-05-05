import os
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from tikhub_interface import TikHubInterface

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ivas-integration")

class IVASVideoProcessor:
    """IVAS-IFM视频处理集成模块"""
    
    def __init__(self, tikhub_api_key: str = None):
        """
        初始化IVAS视频处理模块
        
        参数:
            tikhub_api_key: TikHub API密钥
        """
        # 初始化TikHub接口
        self.tikhub = TikHubInterface(api_key=tikhub_api_key)
        logger.info("IVAS视频处理模块初始化完成")
        
        # 从配置加载API密钥
        config_path = Path(__file__).parent / "config.json"
        self.config = {}
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")
        
        # BibiGPT配置
        self.bibigpt_enabled = True
        self.bibigpt_api_key = self.config.get("bibigpt_api_key", os.environ.get("BIBIGPT_API_KEY", ""))
        self.bibigpt_api_url = self.config.get("bibigpt_api_url", "https://api.bibigpt.ai/v1/summarize")
        
        # KrillinAI翻译配置
        self.translation_enabled = True
        self.krillinai_api_key = self.config.get("krillinai_api_key", os.environ.get("KRILLINAI_API_KEY", ""))
        self.krillinai_api_url = self.config.get("krillinai_api_url", "https://api.krillinai.com/v1/translate")
        
        # 下载目录配置
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)
    
    def process_video_url(self, url: str) -> Dict:
        """
        处理视频URL，获取综合信息
        
        参数:
            url: 视频URL (支持TikTok, Douyin, Xiaohongshu等)
            
        返回:
            视频信息字典，包含解析结果、摘要、翻译等
        """
        logger.info(f"处理视频URL: {url}")
        
        # 解析视频URL
        parse_result = self.tikhub.parse_url(url)
        
        # 检查解析结果
        if "error" in parse_result:
            logger.error(f"视频解析失败: {parse_result}")
            return {"error": f"视频解析失败: {parse_result.get('error')}"}
        
        # 提取视频信息
        video_info = parse_result.get("video", {})
        
        # 生成视频摘要 (使用BibiGPT)
        summary = self._generate_summary(video_info) if self.bibigpt_enabled else None
        
        # 翻译视频信息 (使用KrillinAI)
        translations = self._translate_video_info(video_info) if self.translation_enabled else None
        
        # 组装结果
        result = {
            "parse_result": parse_result,
            "video_info": video_info,
            "summary": summary,
            "translations": translations,
            "download_url": video_info.get("download_url", ""),
            "platform": parse_result.get("platform", "unknown")
        }
        
        return result
    
    def download_video(self, url: str, filename: str = None) -> Dict:
        """
        下载视频并保存到本地
        
        参数:
            url: 视频URL
            filename: 保存的文件名，默认自动生成
            
        返回:
            下载结果信息
        """
        logger.info(f"下载视频: {url}")
        
        try:
            # 如果未指定文件名，生成随机文件名
            if not filename:
                import uuid
                filename = f"{uuid.uuid4().hex}.mp4"
            
            # 构建保存路径
            save_path = self.download_dir / filename
            
            # 下载视频
            file_path = self.tikhub.download_video_sync(url, save_path)
            
            if file_path:
                return {
                    "success": True,
                    "message": "视频下载成功",
                    "file_path": str(file_path),
                    "file_size": file_path.stat().st_size
                }
            else:
                return {
                    "success": False,
                    "message": "视频下载失败"
                }
        except Exception as e:
            logger.error(f"视频下载异常: {str(e)}")
            return {
                "success": False,
                "message": f"视频下载异常: {str(e)}"
            }
    
    def search_videos(self, keyword: str, platform: str = "douyin", count: int = 20) -> Dict:
        """
        搜索视频
        
        参数:
            keyword: 搜索关键词
            platform: 平台名称 (douyin, tiktok, xiaohongshu)
            count: 返回结果数量
            
        返回:
            搜索结果
        """
        logger.info(f"搜索视频 - 平台: {platform}, 关键词: {keyword}")
        
        try:
            # 调用TikHub搜索API
            videos = self.tikhub.search_videos(platform, keyword, count=count)
            
            # 为搜索结果添加摘要
            if self.bibigpt_enabled:
                for video in videos:
                    video["summary"] = self._generate_summary(video)
            
            return {
                "success": True,
                "videos": videos,
                "count": len(videos),
                "keyword": keyword,
                "platform": platform
            }
        except Exception as e:
            logger.error(f"搜索视频异常: {str(e)}")
            return {
                "success": False,
                "message": f"搜索视频异常: {str(e)}",
                "videos": []
            }
    
    def get_user_videos(self, user_id: str, platform: str = "douyin", count: int = 20) -> Dict:
        """
        获取用户视频列表
        
        参数:
            user_id: 用户ID
            platform: 平台名称
            count: 返回结果数量
            
        返回:
            用户视频信息
        """
        logger.info(f"获取用户视频 - 平台: {platform}, 用户ID: {user_id}")
        
        try:
            # 获取用户信息
            user_info = self.tikhub.get_user_info(platform, user_id)
            
            # 获取用户视频列表
            videos_result = self.tikhub.get_user_videos(platform, user_id, count=count)
            
            return {
                "success": True,
                "user_info": user_info,
                "videos": videos_result.get("videos", []),
                "cursor": videos_result.get("cursor", ""),
                "has_more": videos_result.get("has_more", False)
            }
        except Exception as e:
            logger.error(f"获取用户视频异常: {str(e)}")
            return {
                "success": False,
                "message": f"获取用户视频异常: {str(e)}"
            }
    
    def translate_text(self, text: str, source_lang: str = "zh", target_lang: str = "en") -> Dict:
        """
        翻译文本 (使用KrillinAI API)
        
        参数:
            text: 要翻译的文本
            source_lang: 源语言
            target_lang: 目标语言
            
        返回:
            翻译结果
        """
        logger.info(f"翻译文本 - 从 {source_lang} 到 {target_lang}")
        
        if not self.krillinai_api_key:
            logger.warning("KrillinAI API密钥未配置，使用模拟翻译")
            return self._mock_translate_text(text, source_lang, target_lang)
        
        try:
            # 调用KrillinAI API
            headers = {
                "Authorization": f"Bearer {self.krillinai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "source_language": source_lang,
                "target_language": target_lang
            }
            
            response = requests.post(
                self.krillinai_api_url,
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "original_text": text,
                    "translated_text": result.get("translation", ""),
                    "source_language": source_lang,
                    "target_language": target_lang
                }
            else:
                logger.error(f"翻译API请求失败: {response.status_code} {response.text}")
                # 失败时回退到模拟翻译
                return self._mock_translate_text(text, source_lang, target_lang)
                
        except Exception as e:
            logger.error(f"调用翻译API异常: {str(e)}")
            # 异常时回退到模拟翻译
            return self._mock_translate_text(text, source_lang, target_lang)
    
    def _mock_translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict:
        """模拟翻译文本 (当API调用失败时使用)"""
        # 简单的模拟翻译
        translations = {
            "zh-en": {
                "你好": "Hello",
                "这个视频很有趣": "This video is interesting",
                "我喜欢这个内容": "I like this content"
            },
            "en-zh": {
                "Hello": "你好",
                "This video is interesting": "这个视频很有趣",
                "I like this content": "我喜欢这个内容" 
            }
        }
        
        translation_key = f"{source_lang}-{target_lang}"
        mock_translation = translations.get(translation_key, {}).get(text, text)
        
        return {
            "success": True,
            "original_text": text,
            "translated_text": mock_translation,
            "source_language": source_lang,
            "target_language": target_lang,
            "is_mocked": True
        }
    
    def _generate_summary(self, video_info: Dict) -> Dict:
        """
        生成视频内容摘要 (使用BibiGPT API)
        
        参数:
            video_info: 视频信息
            
        返回:
            摘要信息
        """
        title = video_info.get("title", "")
        description = video_info.get("description", "")
        
        if not title and not description:
            return {
                "summary": "无法生成摘要，视频缺少文本信息。",
                "keywords": [],
                "sentiment": "neutral"
            }
        
        if not self.bibigpt_api_key:
            logger.warning("BibiGPT API密钥未配置，使用模拟摘要")
            return self._mock_generate_summary(video_info)
        
        try:
            # 准备视频内容数据
            video_content = {
                "title": title,
                "description": description,
                "platform": video_info.get("platform", ""),
                "author": video_info.get("author", {}).get("nickname", ""),
                "url": video_info.get("share_url", "")
            }
            
            # 调用BibiGPT API
            headers = {
                "Authorization": f"Bearer {self.bibigpt_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.bibigpt_api_url,
                headers=headers,
                json=video_content,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "summary": result.get("summary", ""),
                    "keywords": result.get("keywords", []),
                    "sentiment": result.get("sentiment", "neutral")
                }
            else:
                logger.error(f"摘要API请求失败: {response.status_code} {response.text}")
                # 失败时回退到模拟摘要
                return self._mock_generate_summary(video_info)
                
        except Exception as e:
            logger.error(f"调用摘要API异常: {str(e)}")
            # 异常时回退到模拟摘要
            return self._mock_generate_summary(video_info)
    
    def _mock_generate_summary(self, video_info: Dict) -> Dict:
        """模拟生成摘要 (当API调用失败时使用)"""
        title = video_info.get("title", "")
        description = video_info.get("description", "")
        
        # 模拟摘要生成
        combined_text = f"{title} {description}".strip()
        if len(combined_text) > 100:
            mock_summary = combined_text[:100] + "..."
        else:
            mock_summary = combined_text
        
        # 模拟关键词提取
        keywords = []
        for word in set(combined_text.split()):
            if len(word) > 1 and len(keywords) < 5:
                keywords.append(word)
        
        # 模拟情感分析
        sentiment = "positive" if "好" in combined_text or "喜欢" in combined_text else "neutral"
        
        return {
            "summary": mock_summary,
            "keywords": keywords,
            "sentiment": sentiment,
            "is_mocked": True
        }
    
    def _translate_video_info(self, video_info: Dict) -> Dict:
        """
        翻译视频信息 (使用KrillinAI API)
        
        参数:
            video_info: 视频信息
            
        返回:
            翻译后的视频信息
        """
        title = video_info.get("title", "")
        description = video_info.get("description", "")
        
        translated_info = {}
        
        # 翻译标题
        if title:
            title_result = self.translate_text(title, "zh", "en")
            translated_info["title"] = title_result.get("translated_text")
        
        # 翻译描述
        if description:
            desc_result = self.translate_text(description, "zh", "en")
            translated_info["description"] = desc_result.get("translated_text")
        
        return translated_info 