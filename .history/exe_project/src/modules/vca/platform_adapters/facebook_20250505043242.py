"""
Facebook平台爬虫适配器
负责从Facebook获取视频数据，集成了开源项目API能力
"""
import logging
import os
import json
import time
import re
import tempfile
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from urllib.parse import unquote, urlparse, parse_qs

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

# 尝试导入集成API模块
try:
    import facebook_downloader
    HAS_BELLINGCAT_API = True
except ImportError:
    HAS_BELLINGCAT_API = False
    logging.warning("未安装facebook-downloader库，将使用内置方法下载视频")

logger = logging.getLogger(__name__)

# 平台名称常量，用于爬虫管理器注册
PLATFORM_NAME = "facebook"

class FacebookAdapter:
    """Facebook平台适配器，提供视频搜索和下载功能"""
    
    def __init__(self, api_key: str = None, proxy: str = None, use_selenium: bool = True):
        """
        初始化Facebook适配器
        
        Args:
            api_key: Facebook API密钥（可选）
            proxy: 代理服务器（可选）
            use_selenium: 是否使用Selenium进行爬取
        """
        self.api_key = api_key
        self.proxy = proxy
        self.use_selenium = use_selenium
        self.session = self._create_session()
        self.driver = None
        
        # 是否使用Evil0ctal API
        self.use_evil0ctal_api = False
        self.evil0ctal_api_url = "https://api.douyin.wtf/api"
        
        if self.use_selenium:
            self._init_selenium()
            
        logger.info("Facebook适配器已初始化")
        
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
            'Referer': 'https://www.facebook.com/'
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
        搜索Facebook视频
        
        Args:
            search_query: 搜索关键词
            limit: 限制结果数量
            filters: 过滤条件，支持以下字段:
                     - upload_date: 上传日期(today, week, month, year)
                     - duration: 视频时长(short, medium, long)
                     
        Returns:
            视频信息列表
        """
        logger.info(f"搜索Facebook视频: {search_query}, 限制: {limit}")
        
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
            logger.error(f"Facebook搜索失败: {str(e)}")
            return []
            
    def _search_with_api(self, search_query: str, limit: int, filters: Dict) -> List[Dict]:
        """使用API搜索视频"""
        results = []
        
        try:
            # Facebook搜索URL
            search_url = f"https://www.facebook.com/search/videos?q={search_query}"
            
            response = self.session.get(search_url)
            
            # 解析HTML内容
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取视频信息
            video_containers = soup.select('div[data-pagelet="SearchResults"] > div')
            
            for i, container in enumerate(video_containers[:limit]):
                try:
                    # 提取视频链接
                    link_elem = container.select_one('a[href*="/watch/"]')
                    if not link_elem:
                        logger.error(f"提取视频元素 {i} 信息失败: 未找到视频链接")
                        continue
                        
                    video_url = "https://www.facebook.com" + link_elem.get('href')
                    
                    # 提取视频标题
                    title_elem = container.select_one('span.d2edcug0')
                    title = title_elem.text if title_elem else "未知标题"
                    
                    # 提取创作者信息
                    author_elem = container.select_one('a.oajrlxb2')
                    author = author_elem.text if author_elem else "未知作者"
                    author_url = "https://www.facebook.com" + author_elem.get('href') if author_elem else None
                    
                    # 创建视频信息
                    video_info = {
                        'title': title,
                        'url': video_url,
                        'platform': 'facebook',
                        'author': author,
                        'author_url': author_url,
                        'thumbnail': None,  # Facebook页面动态加载，难以直接获取缩略图
                        'duration': None,   # 需要单独请求获取
                        'upload_date': None, # 需要单独请求获取
                    }
                    
                    results.append(video_info)
                except Exception as e:
                    logger.error(f"解析视频容器失败: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"API搜索失败: {str(e)}")
            return []
            
    def _search_with_selenium(self, search_query: str, limit: int, filters: Dict) -> List[Dict]:
        """使用Selenium搜索视频"""
        results = []
        
        try:
            # 打开Facebook视频搜索页面
            search_url = f"https://www.facebook.com/search/videos?q={search_query}"
            self.driver.get(search_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
            )
            
            # 向下滚动页面，加载更多结果
            results_loaded = 0
            max_scroll_attempts = 10
            scroll_attempts = 0
            
            while results_loaded < limit and scroll_attempts < max_scroll_attempts:
                # 获取当前视频容器元素
                video_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                results_loaded = len(video_elements)
                
                if results_loaded >= limit:
                    break
                    
                # 向下滚动
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # 等待内容加载
                scroll_attempts += 1
            
            # 提取视频信息
            video_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            
            for i, element in enumerate(video_elements[:limit]):
                try:
                    # 提取视频链接
                    link_elem = element.find_element(By.CSS_SELECTOR, "a[href*='/watch/']")
                    video_url = link_elem.get_attribute("href")
                    
                    # 提取视频标题
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, "span.d2edcug0")
                        title = title_elem.text
                    except:
                        title = "未知标题"
                    
                    # 提取创作者信息
                    try:
                        author_elem = element.find_element(By.CSS_SELECTOR, "a.oajrlxb2 > span")
                        author = author_elem.text
                        author_url = element.find_element(By.CSS_SELECTOR, "a.oajrlxb2").get_attribute("href")
                    except:
                        author = "未知作者"
                        author_url = None
                    
                    # 创建视频信息
                    video_info = {
                        'title': title,
                        'url': video_url,
                        'platform': 'facebook',
                        'author': author,
                        'author_url': author_url,
                        'thumbnail': None,
                        'duration': None,
                        'upload_date': None,
                    }
                    
                    results.append(video_info)
                    
                except Exception as e:
                    logger.error(f"提取视频元素 {i} 信息失败: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Selenium搜索失败: {str(e)}")
            return []
            
    def _apply_filters(self, videos: List[Dict], filters: Dict) -> List[Dict]:
        """应用过滤条件"""
        if not filters:
            return videos
            
        filtered_videos = videos.copy()
        
        # 应用上传日期过滤
        if 'upload_date' in filters and filters['upload_date']:
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
                filtered_videos = [
                    video for video in filtered_videos
                    if video.get('upload_date') and self._parse_date(video['upload_date']) >= date_threshold
                ]
        
        # 应用视频时长过滤
        if 'duration' in filters and filters['duration']:
            duration_filter = filters['duration']
            filtered_videos = [
                video for video in filtered_videos
                if self._check_duration(video, duration_filter)
            ]
            
        return filtered_videos
        
    def _check_duration(self, video: Dict, duration_filter: str) -> bool:
        """检查视频时长是否满足过滤条件"""
        if not video.get('duration'):
            return True
            
        duration_seconds = video['duration']
        
        if duration_filter == 'short':  # 短视频（小于4分钟）
            return duration_seconds < 240
        elif duration_filter == 'medium':  # 中等视频（4-20分钟）
            return 240 <= duration_seconds < 1200
        elif duration_filter == 'long':  # 长视频（大于20分钟）
            return duration_seconds >= 1200
            
        return True
            
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """解析日期字符串为日期对象"""
        if not date_str:
            return None
            
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None
            
    def download_video(self, 
                      video_url: str, 
                      output_path: str = "./downloads", 
                      filename: str = None,
                      with_audio: bool = True) -> str:
        """
        下载Facebook视频
        
        Args:
            video_url: 视频URL
            output_path: 输出路径
            filename: 文件名，不含扩展名
            with_audio: 是否包含音频
            
        Returns:
            保存的文件路径或错误信息
        """
        logger.info(f"开始下载Facebook视频: {video_url}")
        
        # 创建输出目录
        os.makedirs(output_path, exist_ok=True)
        
        # 获取视频信息
        video_info = self.get_video_info(video_url)
        if not video_info:
            error_msg = "无法获取视频信息"
            logger.error(error_msg)
            return error_msg
            
        # 如果未指定文件名，使用视频标题
        if not filename:
            if video_info.get('title'):
                # 清理文件名，去除不合法字符
                filename = re.sub(r'[^\w\s-]', '', video_info['title'])
                filename = re.sub(r'[-\s]+', '_', filename).strip('-_')
            else:
                # 使用视频ID作为文件名
                video_id = self._extract_video_id(video_url)
                filename = f"facebook_video_{video_id}"
        
        # 尝试使用不同的方法下载
        file_path = None
        
        # 方法1: 使用bellingcat/facebook-downloader（如果已安装）
        if HAS_BELLINGCAT_API:
            try:
                # 创建临时目录存储下载文件
                temp_dir = tempfile.mkdtemp()
                # 构建命令行调用
                cmd = ["facebook_downloader"]
                if not with_audio:
                    cmd.append("--audio")
                cmd.extend(["-o", os.path.join(temp_dir, filename), video_url])
                
                # 执行命令
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    # 查找下载的文件
                    downloaded_files = os.listdir(temp_dir)
                    if downloaded_files:
                        temp_file = os.path.join(temp_dir, downloaded_files[0])
                        final_path = os.path.join(output_path, f"{filename}.mp4")
                        # 移动到目标目录
                        import shutil
                        shutil.move(temp_file, final_path)
                        file_path = final_path
                        logger.info(f"使用facebook-downloader下载成功: {file_path}")
                
                # 清理临时目录
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
                if file_path:
                    return file_path
                    
            except Exception as e:
                logger.error(f"使用facebook-downloader下载失败: {str(e)}")
        
        # 方法2: 使用Evil0ctal/Douyin_TikTok_Download_API
        if self.use_evil0ctal_api:
            try:
                # 通过API获取无水印链接
                api_url = f"{self.evil0ctal_api_url}/download?url={video_url}&prefix=false&watermark=false"
                response = requests.get(api_url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success" and data.get("data"):
                        video_url_no_watermark = data["data"].get("video_url")
                        if video_url_no_watermark:
                            # 下载无水印视频
                            video_response = requests.get(video_url_no_watermark, stream=True, timeout=60)
                            if video_response.status_code == 200:
                                file_path = os.path.join(output_path, f"{filename}.mp4")
                                with open(file_path, 'wb') as f:
                                    for chunk in video_response.iter_content(chunk_size=8192):
                                        f.write(chunk)
                                logger.info(f"使用Evil0ctal API下载成功: {file_path}")
                                return file_path
            except Exception as e:
                logger.error(f"使用Evil0ctal API下载失败: {str(e)}")
        
        # 方法3: 直接从视频信息中提取下载链接
        try:
            if video_info and video_info.get('attachments', {}).get('video'):
                video_urls = video_info['attachments']['video']
                if video_urls:
                    video_url_no_watermark = video_urls[0]  # 使用最高质量的视频链接
                    video_response = requests.get(video_url_no_watermark, stream=True, timeout=60)
                    if video_response.status_code == 200:
                        file_path = os.path.join(output_path, f"{filename}.mp4")
                        with open(file_path, 'wb') as f:
                            for chunk in video_response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        logger.info(f"使用直接下载方法成功: {file_path}")
                        return file_path
        except Exception as e:
            logger.error(f"直接下载方法失败: {str(e)}")
        
        # 所有方法均失败
        if not file_path:
            error_msg = "视频下载失败"
            logger.error(error_msg)
            return error_msg
            
        return file_path
            
    def get_video_info(self, video_url: str) -> Optional[Dict]:
        """
        获取视频信息
        
        Args:
            video_url: 视频URL
            
        Returns:
            视频信息字典或None
        """
        logger.info(f"获取视频信息: {video_url}")
        
        try:
            if self.use_selenium and self.driver:
                # 使用Selenium获取视频信息
                return self._get_video_info_with_selenium(video_url)
            else:
                # 使用请求获取视频信息
                return self._get_video_info_with_requests(video_url)
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
            return None
    
    def _extract_video_id(self, video_url: str) -> str:
        """从URL中提取视频ID"""
        try:
            # 处理不同形式的Facebook视频URL
            if 'facebook.com/watch' in video_url:
                # 形如 https://www.facebook.com/watch?v=123456789
                parsed_url = urlparse(video_url)
                query_params = parse_qs(parsed_url.query)
                if 'v' in query_params:
                    return query_params['v'][0]
            elif 'facebook.com/video' in video_url:
                # 形如 https://www.facebook.com/username/videos/123456789
                match = re.search(r'/videos/(\d+)', video_url)
                if match:
                    return match.group(1)
            elif 'facebook.com' in video_url and '/videos/' in video_url:
                # 形如 https://www.facebook.com/username/videos/123456789
                match = re.search(r'/videos/(\d+)', video_url)
                if match:
                    return match.group(1)
            
            # 默认返回URL的最后部分
            return video_url.split('/')[-1].split('?')[0]
        except Exception:
            # 失败时返回随机数
            import random
            return f"unknown_{random.randint(10000, 99999)}"
            
    def _get_video_info_with_requests(self, video_url: str) -> Optional[Dict]:
        """使用HTTP请求获取视频信息"""
        try:
            # 尝试方法1: 使用Evil0ctal API获取视频信息
            if self.use_evil0ctal_api:
                try:
                    api_url = f"{self.evil0ctal_api_url}/hybrid/video_data?url={video_url}&minimal=false"
                    response = requests.get(api_url, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "success":
                            video_data = data.get("data", {})
                            # 转换为标准格式
                            return {
                                'id': video_data.get('id', self._extract_video_id(video_url)),
                                'title': video_data.get('title', '未知标题'),
                                'text': video_data.get('text', ''),
                                'author': video_data.get('author', {}).get('name', '未知作者'),
                                'author_url': video_data.get('author', {}).get('url', ''),
                                'url': video_url,
                                'platform': 'facebook',
                                'upload_date': video_data.get('create_time', ''),
                                'duration': video_data.get('duration', 0),
                                'attachments': {
                                    'video': [video_data.get('video_url', '')],
                                    'thumbnail': [video_data.get('cover_url', '')]
                                },
                                'payload': video_data
                            }
                except Exception as e:
                    logger.error(f"使用Evil0ctal API获取视频信息失败: {str(e)}")
            
            # 尝试方法2: 直接解析网页
            response = self.session.get(video_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title = soup.select_one('meta[property="og:title"]')
            title_text = title.get('content', '') if title else '未知标题'
            
            # 提取描述
            description = soup.select_one('meta[property="og:description"]')
            description_text = description.get('content', '') if description else ''
            
            # 提取视频URL
            video_url_elem = soup.select_one('meta[property="og:video:url"]')
            video_url_hd = video_url_elem.get('content', '') if video_url_elem else ''
            
            # 提取缩略图
            thumbnail = soup.select_one('meta[property="og:image"]')
            thumbnail_url = thumbnail.get('content', '') if thumbnail else ''
            
            # 提取作者信息
            author_elem = soup.select_one('meta[property="og:video:actor"]') or soup.select_one('meta[property="og:video:director"]')
            author = author_elem.get('content', '') if author_elem else '未知作者'
            
            # 构建结果
            result = {
                'id': self._extract_video_id(video_url),
                'title': title_text,
                'text': description_text,
                'author': author,
                'author_url': '',
                'url': video_url,
                'platform': 'facebook',
                'upload_date': '',
                'duration': 0,
                'attachments': {
                    'video': [video_url_hd] if video_url_hd else [],
                    'thumbnail': [thumbnail_url] if thumbnail_url else []
                },
                'payload': {}
            }
            
            return result
            
        except Exception as e:
            logger.error(f"使用requests获取视频信息失败: {str(e)}")
            return None
            
    def _get_video_info_with_selenium(self, video_url: str) -> Optional[Dict]:
        """使用Selenium获取视频信息"""
        try:
            # 打开视频页面
            self.driver.get(video_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            
            # 执行JavaScript提取视频信息
            video_info_script = """
            var videoInfo = {};
            
            // 提取标题
            var titleElem = document.querySelector('meta[property="og:title"]');
            videoInfo.title = titleElem ? titleElem.getAttribute('content') : 'Facebook Video';
            
            // 提取视频源
            var videoElem = document.querySelector('video');
            videoInfo.sd_src = videoElem ? videoElem.src : null;
            
            // 提取缩略图
            var thumbnailElem = document.querySelector('meta[property="og:image"]');
            videoInfo.thumbnail = thumbnailElem ? thumbnailElem.getAttribute('content') : null;
            
            // 提取作者信息
            var authorElem = document.querySelector('meta[property="og:description"]');
            videoInfo.author = authorElem ? authorElem.getAttribute('content') : '';
            
            // 提取时长
            videoInfo.duration = videoElem ? videoElem.duration : null;
            
            return videoInfo;
            """
            
            video_info = self.driver.execute_script(video_info_script)
            
            # 补充额外信息
            video_info['url'] = video_url
            video_info['platform'] = 'facebook'
            video_info['hd_src'] = video_info.get('sd_src')  # 在Selenium中难以提取HD源
            
            # 尝试提取上传日期
            try:
                date_element = self.driver.find_element(By.CSS_SELECTOR, "span[data-testid='story-time']")
                date_text = date_element.get_attribute('title')
                if date_text:
                    upload_date = datetime.strptime(date_text, '%Y年%m月%d日 %H:%M').isoformat()
                    video_info['upload_date'] = upload_date
            except:
                video_info['upload_date'] = None
                
            return video_info
            
        except Exception as e:
            logger.error(f"使用Selenium获取视频信息失败: {str(e)}")
            return None
            
    def close(self):
        """关闭资源"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            
        self.session.close()
        logger.info("Facebook适配器资源已关闭") 