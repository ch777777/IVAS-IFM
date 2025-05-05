"""
TikTok平台爬虫适配器
负责从TikTok获取视频数据
"""
import logging
import os
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

try:
    import requests
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    raise ImportError("请安装必要的依赖: pip install requests beautifulsoup4 selenium webdriver-manager")

logger = logging.getLogger(__name__)

# 平台名称常量，用于爬虫管理器注册
PLATFORM_NAME = "tiktok"

class TiktokAdapter:
    """TikTok平台适配器，提供视频搜索和下载功能"""
    
    def __init__(self, api_key: str = None, proxy: str = None, use_selenium: bool = True):
        """
        初始化TikTok适配器
        
        Args:
            api_key: TikTok API密钥（可选）
            proxy: 代理服务器（可选）
            use_selenium: 是否使用Selenium进行爬取
        """
        self.api_key = api_key
        self.proxy = proxy
        self.use_selenium = use_selenium
        self.session = self._create_session()
        self.driver = None
        
        if self.use_selenium:
            self._init_selenium()
            
        logger.info("TikTok适配器已初始化")
        
    def _create_session(self) -> requests.Session:
        """创建请求会话"""
        session = requests.Session()
        
        # 添加请求头，模拟浏览器
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.tiktok.com/'
        })
        
        if self.proxy:
            session.proxies = {
                'http': self.proxy,
                'https': self.proxy
            }
            
        return session
        
    def _init_selenium(self):
        """初始化Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")
            
            # 添加代理
            if self.proxy:
                chrome_options.add_argument(f'--proxy-server={self.proxy}')
                
            # 添加User-Agent
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # 初始化WebDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Selenium WebDriver初始化成功")
            
        except Exception as e:
            logger.error(f"初始化Selenium WebDriver失败: {str(e)}")
            self.driver = None
            self.use_selenium = False
            
    def search_videos(self, 
                     search_query: str, 
                     limit: int = 10, 
                     filters: Dict = None) -> List[Dict]:
        """
        搜索TikTok视频
        
        Args:
            search_query: 搜索关键词
            limit: 限制结果数量
            filters: 过滤条件，支持以下字段:
                     - upload_date: 上传日期(today, week, month, year)
                     - duration: 视频时长(short, medium, long)
                     
        Returns:
            视频信息列表
        """
        logger.info(f"搜索TikTok视频: {search_query}, 限制: {limit}")
        
        filters = filters or {}
        results = []
        
        try:
            if self.use_selenium and self.driver:
                # 使用Selenium爬取
                results = self._search_with_selenium(search_query, limit, filters)
            else:
                # 使用API爬取
                results = self._search_with_api(search_query, limit, filters)
                
            # 应用过滤条件
            filtered_results = self._apply_filters(results, filters)
            
            logger.info(f"搜索完成，找到 {len(filtered_results)} 个结果")
            return filtered_results[:limit]
            
        except Exception as e:
            logger.error(f"TikTok搜索失败: {str(e)}")
            return []
            
    def _search_with_api(self, search_query: str, limit: int, filters: Dict) -> List[Dict]:
        """使用API搜索视频"""
        results = []
        
        try:
            # TikTok网页搜索API
            # 注意：TikTok的API可能会经常变化，需要随时调整
            search_url = f"https://www.tiktok.com/api/search/general/full/?aid=1988&keyword={search_query}&count={limit}"
            
            response = self.session.get(search_url)
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                for item in data['data']:
                    if item.get('type') == 'video':
                        video_info = self._extract_video_info_from_api(item)
                        if video_info:
                            results.append(video_info)
            
            return results
            
        except Exception as e:
            logger.error(f"API搜索失败: {str(e)}")
            return []
            
    def _search_with_selenium(self, search_query: str, limit: int, filters: Dict) -> List[Dict]:
        """使用Selenium搜索视频"""
        results = []
        
        try:
            # 打开TikTok搜索页面
            search_url = f"https://www.tiktok.com/search?q={search_query}"
            self.driver.get(search_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-e2e='search-common-video']"))
            )
            
            # 滚动加载更多结果
            scroll_count = min(limit // 10 + 1, 5)  # 最多滚动5次
            for _ in range(scroll_count):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # 等待内容加载
                
            # 查找视频元素
            video_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='search-common-video']")
            
            # 提取视频信息
            for i, element in enumerate(video_elements[:limit]):
                try:
                    # 提取视频信息
                    video_info = self._extract_video_info_from_element(element)
                    if video_info:
                        results.append(video_info)
                except Exception as e:
                    logger.error(f"提取视频元素 {i} 信息失败: {str(e)}")
                    continue
                    
            return results
            
        except Exception as e:
            logger.error(f"Selenium搜索失败: {str(e)}")
            return []
            
    def _extract_video_info_from_api(self, item: Dict) -> Optional[Dict]:
        """从API结果中提取视频信息"""
        try:
            video_data = item.get('item', {})
            author_data = video_data.get('author', {})
            
            video_info = {
                'platform': 'tiktok',
                'video_id': video_data.get('id'),
                'title': video_data.get('desc', ''),
                'url': f"https://www.tiktok.com/@{author_data.get('uniqueId')}/video/{video_data.get('id')}",
                'thumbnail': video_data.get('video', {}).get('cover'),
                'channel': author_data.get('uniqueId'),
                'publish_date': self._format_timestamp(video_data.get('createTime')),
                'duration': video_data.get('video', {}).get('duration'),
                'description': video_data.get('desc', ''),
                'views': video_data.get('stats', {}).get('playCount'),
                'likes': video_data.get('stats', {}).get('diggCount'),
                'shares': video_data.get('stats', {}).get('shareCount'),
                'comments': video_data.get('stats', {}).get('commentCount'),
                'music': video_data.get('music', {}).get('title')
            }
            
            return video_info
            
        except Exception as e:
            logger.error(f"从API提取视频信息失败: {str(e)}")
            return None
            
    def _extract_video_info_from_element(self, element) -> Optional[Dict]:
        """从Selenium元素中提取视频信息"""
        try:
            # 提取视频链接和ID
            video_link = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            video_id = video_link.split("/")[-1] if "/video/" in video_link else None
            
            # 提取视频标题
            title_element = element.find_element(By.CSS_SELECTOR, "div[class*='video-card-big-title']")
            title = title_element.text if title_element else ""
            
            # 提取缩略图
            thumbnail = element.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
            
            # 提取频道名
            channel_element = element.find_element(By.CSS_SELECTOR, "a[data-e2e='video-author-avatar']")
            channel = channel_element.get_attribute("href").split("@")[-1] if channel_element else ""
            
            # 提取视图数
            views_element = element.find_element(By.CSS_SELECTOR, "strong[data-e2e='search-card-like-count']")
            views = views_element.text if views_element else "0"
            
            # 构建视频信息
            video_info = {
                'platform': 'tiktok',
                'video_id': video_id,
                'title': title,
                'url': video_link,
                'thumbnail': thumbnail,
                'channel': channel,
                'views': self._parse_count(views),
                'publish_date': None,  # 需要进入视频页面才能获取
                'duration': None  # 需要进入视频页面才能获取
            }
            
            return video_info
            
        except Exception as e:
            logger.error(f"从元素提取视频信息失败: {str(e)}")
            return None
            
    def _apply_filters(self, videos: List[Dict], filters: Dict) -> List[Dict]:
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
                filtered_videos = [v for v in filtered_videos if self._parse_date(v.get('publish_date')) >= date_threshold]
        
        # 根据时长过滤
        if 'duration' in filters:
            duration_filter = filters['duration']
            
            filtered_videos = [v for v in filtered_videos if self._check_duration(v, duration_filter)]
        
        return filtered_videos
        
    def _check_duration(self, video: Dict, duration_filter: str) -> bool:
        """检查视频时长是否符合过滤条件"""
        try:
            # 获取视频时长（秒）
            duration_seconds = video.get('duration')
            
            if not duration_seconds:
                return True
                
            if duration_filter == 'short':
                return duration_seconds < 60  # 1分钟以下
            elif duration_filter == 'medium':
                return 60 <= duration_seconds < 180  # 1-3分钟
            elif duration_filter == 'long':
                return duration_seconds >= 180  # 3分钟以上
            else:
                return True
        except Exception:
            return True
            
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str:
            return datetime.now()
            
        try:
            return datetime.fromisoformat(date_str)
        except Exception:
            return datetime.now()
            
    def _format_timestamp(self, timestamp) -> Optional[str]:
        """将时间戳格式化为ISO格式日期字符串"""
        if not timestamp:
            return None
            
        try:
            dt = datetime.fromtimestamp(int(timestamp))
            return dt.isoformat()
        except Exception:
            return None
            
    def _parse_count(self, count_str: str) -> int:
        """解析数字字符串（例如：'1.2K'）"""
        if not count_str:
            return 0
            
        try:
            count_str = count_str.strip().lower()
            
            if 'k' in count_str:
                return int(float(count_str.replace('k', '')) * 1000)
            elif 'm' in count_str:
                return int(float(count_str.replace('m', '')) * 1000000)
            elif 'b' in count_str:
                return int(float(count_str.replace('b', '')) * 1000000000)
            else:
                return int(count_str)
        except Exception:
            return 0
            
    def download_video(self, 
                      video_url: str, 
                      output_path: str, 
                      filename: str = None) -> str:
        """
        下载TikTok视频
        
        Args:
            video_url: 视频URL或ID
            output_path: 输出目录
            filename: 自定义文件名（不包含扩展名）
            
        Returns:
            下载后的文件路径
        """
        try:
            # 创建输出目录
            os.makedirs(output_path, exist_ok=True)
            
            # 获取视频ID
            video_id = video_url.split("/")[-1] if "/video/" in video_url else video_url
            
            # 访问视频页面
            response = self.session.get(video_url if "http" in video_url else f"https://www.tiktok.com/video/{video_id}")
            
            # 查找视频下载链接
            soup = BeautifulSoup(response.text, 'html.parser')
            video_element = soup.find('video')
            
            if not video_element or not video_element.get('src'):
                # 如果无法直接找到，尝试使用Selenium
                if self.use_selenium and self.driver:
                    return self._download_with_selenium(video_url, output_path, filename)
                else:
                    raise ValueError("无法找到视频下载链接")
            
            video_url = video_element['src']
            
            # 下载视频
            video_response = self.session.get(video_url, stream=True)
            
            if not filename:
                filename = f"tiktok_{video_id}"
                
            file_path = os.path.join(output_path, f"{filename}.mp4")
            
            with open(file_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            logger.info(f"视频下载完成: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"视频下载失败: {str(e)}")
            raise
            
    def _download_with_selenium(self, video_url: str, output_path: str, filename: str = None) -> str:
        """使用Selenium下载视频"""
        try:
            # 获取视频ID
            video_id = video_url.split("/")[-1] if "/video/" in video_url else video_url
            
            # 访问视频页面
            self.driver.get(video_url if "http" in video_url else f"https://www.tiktok.com/video/{video_id}")
            
            # 等待视频加载
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            
            # 获取视频元素
            video_element = self.driver.find_element(By.TAG_NAME, "video")
            video_src = video_element.get_attribute("src")
            
            if not video_src:
                raise ValueError("无法找到视频下载链接")
                
            # 下载视频
            video_response = self.session.get(video_src, stream=True)
            
            if not filename:
                filename = f"tiktok_{video_id}"
                
            file_path = os.path.join(output_path, f"{filename}.mp4")
            
            with open(file_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            logger.info(f"视频下载完成: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Selenium下载失败: {str(e)}")
            raise
            
    def get_video_info(self, video_url: str) -> Optional[Dict]:
        """
        获取单个视频的详细信息
        
        Args:
            video_url: 视频URL或ID
            
        Returns:
            视频详细信息
        """
        try:
            # 获取视频ID
            video_id = video_url.split("/")[-1] if "/video/" in video_url else video_url
            
            # 构建API URL
            api_url = f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={video_id}"
            
            response = self.session.get(api_url)
            data = response.json()
            
            if 'aweme_list' in data and len(data['aweme_list']) > 0:
                aweme = data['aweme_list'][0]
                
                video_info = {
                    'platform': 'tiktok',
                    'video_id': aweme.get('aweme_id'),
                    'title': aweme.get('desc', ''),
                    'url': f"https://www.tiktok.com/@{aweme.get('author', {}).get('unique_id')}/video/{aweme.get('aweme_id')}",
                    'thumbnail': aweme.get('video', {}).get('cover', {}).get('url_list', [None])[0],
                    'channel': aweme.get('author', {}).get('unique_id'),
                    'channel_name': aweme.get('author', {}).get('nickname'),
                    'publish_date': self._format_timestamp(aweme.get('create_time')),
                    'duration': aweme.get('video', {}).get('duration') / 1000,  # 转为秒
                    'description': aweme.get('desc', ''),
                    'views': aweme.get('statistics', {}).get('play_count'),
                    'likes': aweme.get('statistics', {}).get('digg_count'),
                    'shares': aweme.get('statistics', {}).get('share_count'),
                    'comments': aweme.get('statistics', {}).get('comment_count'),
                    'music': aweme.get('music', {}).get('title')
                }
                
                return video_info
            else:
                # 如果API获取失败，尝试使用Selenium
                if self.use_selenium and self.driver:
                    return self._get_video_info_with_selenium(video_url)
                else:
                    logger.warning(f"无法通过API获取视频信息: {video_id}")
                    return None
                
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
            
            # 如果API获取失败，尝试使用Selenium
            if self.use_selenium and self.driver:
                return self._get_video_info_with_selenium(video_url)
            else:
                return None
                
    def _get_video_info_with_selenium(self, video_url: str) -> Optional[Dict]:
        """使用Selenium获取视频信息"""
        try:
            # 访问视频页面
            self.driver.get(video_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            
            # 获取视频ID
            video_id = video_url.split("/")[-1] if "/video/" in video_url else self.driver.current_url.split("/")[-1]
            
            # 获取视频标题
            title_element = self.driver.find_element(By.CSS_SELECTOR, "div[data-e2e='video-desc']")
            title = title_element.text if title_element else ""
            
            # 获取频道信息
            channel_element = self.driver.find_element(By.CSS_SELECTOR, "a[data-e2e='video-author-avatar']")
            channel = channel_element.get_attribute("href").split("@")[-1] if channel_element else ""
            
            # 获取统计信息
            likes_element = self.driver.find_element(By.CSS_SELECTOR, "strong[data-e2e='like-count']")
            likes = likes_element.text if likes_element else "0"
            
            comments_element = self.driver.find_element(By.CSS_SELECTOR, "strong[data-e2e='comment-count']")
            comments = comments_element.text if comments_element else "0"
            
            # 构建视频信息
            video_info = {
                'platform': 'tiktok',
                'video_id': video_id,
                'title': title,
                'url': self.driver.current_url,
                'channel': channel,
                'likes': self._parse_count(likes),
                'comments': self._parse_count(comments)
            }
            
            return video_info
            
        except Exception as e:
            logger.error(f"Selenium获取视频信息失败: {str(e)}")
            return None
            
    def close(self):
        """关闭资源"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"关闭WebDriver失败: {str(e)}")


# 示例用法
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建适配器
    adapter = TiktokAdapter(use_selenium=True)
    
    try:
        # 搜索视频
        results = adapter.search_videos(
            search_query="python tutorial",
            limit=5,
            filters={
                'upload_date': 'month',
                'duration': 'short'
            }
        )
        
        # 打印搜索结果
        for i, result in enumerate(results):
            print(f"\n--- 视频 {i+1} ---")
            print(f"标题: {result['title']}")
            print(f"链接: {result['url']}")
            print(f"频道: {result['channel']}")
            
        # 下载示例
        if results:
            print("\n下载第一个视频...")
            output_path = os.path.join(os.getcwd(), "downloads")
            adapter.download_video(
                video_url=results[0]['url'],
                output_path=output_path
            )
    finally:
        # 关闭资源
        adapter.close() 
 
 