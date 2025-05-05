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
            # 打开Facebook搜索页面
            search_url = f"https://www.facebook.com/search/videos?q={search_query}"
            self.driver.get(search_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='article']"))
            )
            
            # 滚动加载更多结果
            scroll_count = min(limit // 10 + 1, 5)  # 最多滚动5次
            for _ in range(scroll_count):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # 等待内容加载
                
            # 查找视频元素
            video_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            
            # 提取视频信息
            for i, element in enumerate(video_elements[:limit]):
                try:
                    # 提取视频URL
                    link_elem = element.find_element(By.CSS_SELECTOR, "a[href*='/watch/']")
                    video_url = link_elem.get_attribute('href')
                    
                    # 提取视频标题
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, "span.d2edcug0")
                        title = title_elem.text
                    except:
                        title = "未知标题"
                    
                    # 提取作者信息
                    try:
                        author_elem = element.find_element(By.CSS_SELECTOR, "a.oajrlxb2")
                        author = author_elem.text
                        author_url = author_elem.get_attribute('href')
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
                        'thumbnail': None,  # 可以进一步提取
                        'duration': None,   # 可以进一步提取
                        'upload_date': None, # 可以进一步提取
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
        
        # 按上传日期过滤
        if 'upload_date' in filters:
            date_filter = filters['upload_date']
            now = datetime.now()
            
            if date_filter == 'today':
                cutoff = now - timedelta(days=1)
            elif date_filter == 'week':
                cutoff = now - timedelta(days=7)
            elif date_filter == 'month':
                cutoff = now - timedelta(days=30)
            elif date_filter == 'year':
                cutoff = now - timedelta(days=365)
            else:
                cutoff = None
                
            if cutoff:
                filtered_videos = [v for v in filtered_videos if v.get('upload_date') and 
                                  self._parse_date(v['upload_date']) >= cutoff]
        
        # 按视频时长过滤
        if 'duration' in filters:
            duration_filter = filters['duration']
            filtered_videos = [v for v in filtered_videos if self._check_duration(v, duration_filter)]
            
        return filtered_videos
        
    def _check_duration(self, video: Dict, duration_filter: str) -> bool:
        """检查视频时长是否符合过滤条件"""
        if not video.get('duration'):
            return True  # 无法获取时长，默认保留
            
        duration_seconds = video['duration']
        
        if duration_filter == 'short':  # 短视频 < 1分钟
            return duration_seconds < 60
        elif duration_filter == 'medium':  # 中等视频 1-5分钟
            return 60 <= duration_seconds <= 300
        elif duration_filter == 'long':  # 长视频 > 5分钟
            return duration_seconds > 300
            
        return True
        
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """解析日期字符串为datetime对象"""
        if not date_str:
            return None
            
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
            
    def download_video(self, 
                      video_url: str, 
                      output_path: str, 
                      filename: str = None) -> str:
        """
        下载Facebook视频
        
        Args:
            video_url: 视频URL
            output_path: 保存路径
            filename: 指定文件名（可选）
            
        Returns:
            保存的文件路径
        """
        logger.info(f"开始下载Facebook视频: {video_url}")
        
        try:
            # 确保输出目录存在
            os.makedirs(output_path, exist_ok=True)
            
            # 获取视频信息
            video_info = self.get_video_info(video_url)
            if not video_info:
                logger.error("无法获取视频信息")
                return ""
                
            # 确定文件名
            if not filename:
                # 从标题生成文件名
                title = video_info.get('title', 'facebook_video')
                # 移除文件名中的非法字符
                title = re.sub(r'[\\/*?:"<>|]', '', title)
                # 限制长度
                title = title[:50] if len(title) > 50 else title
                filename = f"{title}.mp4"
                
            filepath = os.path.join(output_path, filename)
            
            # 使用最佳质量的视频源
            video_src = None
            if 'sd_src' in video_info and video_info['sd_src']:
                video_src = video_info['sd_src']
            if 'hd_src' in video_info and video_info['hd_src']:
                video_src = video_info['hd_src']  # 优先使用高清源
                
            if not video_src:
                logger.error("未找到可用的视频源")
                return ""
                
            # 下载视频
            logger.info(f"下载视频到 {filepath}")
            response = self.session.get(video_src, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info(f"视频下载完成: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"下载视频失败: {str(e)}")
            return ""
            
    def get_video_info(self, video_url: str) -> Optional[Dict]:
        """
        获取Facebook视频信息
        
        Args:
            video_url: 视频URL
            
        Returns:
            视频详细信息
        """
        logger.info(f"获取视频信息: {video_url}")
        
        if self.use_selenium and self.driver:
            return self._get_video_info_with_selenium(video_url)
        else:
            return self._get_video_info_with_requests(video_url)
            
    def _get_video_info_with_requests(self, video_url: str) -> Optional[Dict]:
        """使用requests获取视频信息"""
        try:
            # 获取视频页面内容
            response = self.session.get(video_url)
            response.raise_for_status()
            
            # 解析页面内容
            html_content = response.text
            
            # 提取视频标题
            title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html_content)
            title = title_match.group(1) if title_match else "Facebook Video"
            
            # 提取视频源URL (标清和高清)
            sd_src_match = re.search(r'"sd_src":"([^"]+)"', html_content)
            sd_src = unquote(sd_src_match.group(1).replace('\\/', '/')) if sd_src_match else None
            
            hd_src_match = re.search(r'"hd_src":"([^"]+)"', html_content)
            hd_src = unquote(hd_src_match.group(1).replace('\\/', '/')) if hd_src_match else None
            
            # 提取作者信息
            author_match = re.search(r'<meta property="og:description" content="([^"]+)"', html_content)
            author_info = author_match.group(1) if author_match else ""
            
            # 提取缩略图
            thumbnail_match = re.search(r'<meta property="og:image" content="([^"]+)"', html_content)
            thumbnail = thumbnail_match.group(1) if thumbnail_match else None
            
            # 提取视频时长
            duration_match = re.search(r'"duration":"([^"]+)"', html_content)
            duration = float(duration_match.group(1)) if duration_match else None
            
            # 提取上传日期
            date_match = re.search(r'"publish_time":([0-9]+)', html_content)
            upload_date = None
            if date_match:
                timestamp = int(date_match.group(1))
                upload_date = datetime.fromtimestamp(timestamp).isoformat()
            
            # 整合视频信息
            video_info = {
                'title': title,
                'url': video_url,
                'platform': 'facebook',
                'sd_src': sd_src,
                'hd_src': hd_src,
                'author': author_info,
                'thumbnail': thumbnail,
                'duration': duration,
                'upload_date': upload_date
            }
            
            return video_info
            
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
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