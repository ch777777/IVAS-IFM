"""
YouTube平台爬虫适配器
负责从YouTube获取视频数据
"""
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

try:
    from pytube import YouTube, Search
    import requests
except ImportError:
    raise ImportError("请安装pytube和requests库: pip install pytube requests")

logger = logging.getLogger(__name__)

# 平台名称常量，用于爬虫管理器注册
PLATFORM_NAME = "youtube"

class YoutubeAdapter:
    """YouTube平台适配器，提供视频搜索和下载功能"""
    
    def __init__(self, api_key: str = None, proxy: str = None):
        """
        初始化YouTube适配器
        
        Args:
            api_key: YouTube API密钥（可选）
            proxy: 代理服务器（可选）
        """
        self.api_key = api_key
        self.proxy = proxy
        self.session = self._create_session()
        logger.info("YouTube适配器已初始化")
        
    def _create_session(self) -> requests.Session:
        """创建请求会话"""
        session = requests.Session()
        if self.proxy:
            session.proxies = {
                'http': self.proxy,
                'https': self.proxy
            }
        return session
        
    def search_videos(self, 
                      search_query: str, 
                      limit: int = 10, 
                      filters: Dict = None) -> List[Dict]:
        """
        搜索YouTube视频
        
        Args:
            search_query: 搜索关键词
            limit: 限制结果数量
            filters: 过滤条件，支持以下字段:
                     - upload_date: 上传日期(today, week, month, year)
                     - duration: 视频时长(short, medium, long)
                     - quality: 视频质量(hd, sd)
                     
        Returns:
            视频信息列表
        """
        logger.info(f"搜索YouTube视频: {search_query}, 限制: {limit}")
        
        filters = filters or {}
        results = []
        
        try:
            # 使用pytube的Search类搜索视频
            search = Search(search_query)
            videos = search.results
            
            # 根据过滤条件过滤视频
            filtered_videos = self._apply_filters(videos, filters)
            
            # 获取指定数量的结果
            for video in filtered_videos[:limit]:
                try:
                    # 提取视频信息
                    video_info = self._extract_video_info(video)
                    results.append(video_info)
                except Exception as e:
                    logger.error(f"提取视频信息失败: {str(e)}")
                    continue
            
            logger.info(f"搜索完成，找到 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"YouTube搜索失败: {str(e)}")
            return []
            
    def _apply_filters(self, videos: List, filters: Dict) -> List:
        """应用过滤条件"""
        if not filters:
            return videos
            
        filtered_videos = videos
        
        # 根据上传日期过滤
        if 'upload_date' in filters:
            date_filter = filters['upload_date']
            now = datetime.now()
            
            if date_filter == 'today':
                date_threshold = now - timedelta(days=1)
            elif date_filter == 'week':
                date_threshold = now - timedelta(days=7)
            elif date_filter == 'month':
                date_threshold = now - timedelta(days=30)
            elif date_filter == 'year':
                date_threshold = now - timedelta(days=365)
            else:
                date_threshold = None
                
            if date_threshold:
                filtered_videos = [v for v in filtered_videos if self._get_video_date(v) >= date_threshold]
        
        # 根据时长过滤
        if 'duration' in filters:
            duration_filter = filters['duration']
            
            filtered_videos = [v for v in filtered_videos if self._check_duration(v, duration_filter)]
        
        return filtered_videos
        
    def _get_video_date(self, video) -> Optional[datetime]:
        """获取视频上传日期"""
        try:
            return video.publish_date or datetime.now()
        except Exception:
            return datetime.now()
            
    def _check_duration(self, video, duration_filter: str) -> bool:
        """检查视频时长是否符合过滤条件"""
        try:
            # 获取视频时长（秒）
            duration_seconds = video.length
            
            if duration_filter == 'short':
                return duration_seconds < 240  # 4分钟以下
            elif duration_filter == 'medium':
                return 240 <= duration_seconds < 1200  # 4-20分钟
            elif duration_filter == 'long':
                return duration_seconds >= 1200  # 20分钟以上
            else:
                return True
        except Exception:
            return True
        
    def _extract_video_info(self, video) -> Dict:
        """
        提取视频信息
        
        Returns:
            视频信息字典
        """
        info = {
            'platform': 'youtube',
            'video_id': video.video_id,
            'title': video.title,
            'url': video.watch_url,
            'thumbnail': video.thumbnail_url,
            'channel': video.author,
            'publish_date': video.publish_date.isoformat() if video.publish_date else None,
            'duration': video.length,  # 秒数
            'description': video.description,
            'views': video.views,
            'available_qualities': [s.resolution for s in video.streams.filter(progressive=True)],
            'keywords': video.keywords,
            'captions': list(video.captions.keys()) if video.captions else []
        }
        return info
        
    def download_video(self, 
                       video_url: str, 
                       output_path: str, 
                       quality: str = 'highest',
                       filename: str = None) -> str:
        """
        下载YouTube视频
        
        Args:
            video_url: 视频URL或ID
            output_path: 输出目录
            quality: 视频质量 ('highest', 'lowest', 或具体分辨率如'720p')
            filename: 自定义文件名（不包含扩展名）
            
        Returns:
            下载后的文件路径
        """
        try:
            # 创建输出目录
            os.makedirs(output_path, exist_ok=True)
            
            # 创建YouTube对象
            youtube = YouTube(video_url)
            
            # 选择视频质量
            if quality == 'highest':
                stream = youtube.streams.get_highest_resolution()
            elif quality == 'lowest':
                stream = youtube.streams.get_lowest_resolution()
            else:
                stream = youtube.streams.filter(res=quality, progressive=True).first()
                if not stream:
                    logger.warning(f"无法找到 {quality} 质量的视频，使用最高质量")
                    stream = youtube.streams.get_highest_resolution()
            
            # 下载视频
            filename = filename or youtube.title
            file_path = stream.download(output_path=output_path, filename=filename)
            
            logger.info(f"视频下载完成: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"视频下载失败: {str(e)}")
            raise
            
    def get_video_info(self, video_url: str) -> Dict:
        """
        获取单个视频的详细信息
        
        Args:
            video_url: 视频URL或ID
            
        Returns:
            视频详细信息
        """
        try:
            youtube = YouTube(video_url)
            return self._extract_video_info(youtube)
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
            raise


# 示例用法
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建适配器
    adapter = YoutubeAdapter()
    
    # 搜索视频
    results = adapter.search_videos(
        search_query="Python tutorial",
        limit=5,
        filters={
            'upload_date': 'month',
            'duration': 'medium'
        }
    )
    
    # 打印搜索结果
    for i, result in enumerate(results):
        print(f"\n--- 视频 {i+1} ---")
        print(f"标题: {result['title']}")
        print(f"频道: {result['channel']}")
        print(f"链接: {result['url']}")
        print(f"时长: {result['duration']} 秒")
        print(f"发布日期: {result['publish_date']}")
        print(f"关键词: {', '.join(result['keywords'][:5]) if result['keywords'] else '无'}")
        
    # 下载示例
    if results:
        print("\n下载第一个视频...")
        output_path = os.path.join(os.getcwd(), "downloads")
        adapter.download_video(
            video_url=results[0]['url'],
            output_path=output_path,
            quality='720p'
        ) 