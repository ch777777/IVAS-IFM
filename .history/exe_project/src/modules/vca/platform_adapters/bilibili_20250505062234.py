"""
Bilibili平台爬虫适配器
负责从Bilibili获取视频数据
"""
import logging
import os
import json
import re
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

try:
    import requests
    from bs4 import BeautifulSoup
    import execjs
except ImportError:
    raise ImportError("请安装必要的依赖: pip install requests beautifulsoup4 pyexecjs")

logger = logging.getLogger(__name__)

# 平台名称常量，用于爬虫管理器注册
PLATFORM_NAME = "bilibili"

class BilibiliAdapter:
    """Bilibili平台适配器，提供视频搜索和下载功能"""
    
    def __init__(self, api_key: str = None, proxy: str = None, cookie: str = None):
        """
        初始化Bilibili适配器
        
        Args:
            api_key: API密钥（可选）
            proxy: 代理服务器（可选）
            cookie: 登录Cookie（可选，用于获取更多内容）
        """
        self.api_key = api_key
        self.proxy = proxy
        self.cookie = cookie
        self.session = self._create_session()
        logger.info("Bilibili适配器已初始化")
        
    def _create_session(self) -> requests.Session:
        """创建请求会话"""
        session = requests.Session()
        
        # 添加请求头，模拟浏览器
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.bilibili.com/'
        })
        
        # 添加Cookie
        if self.cookie:
            session.headers.update({
                'Cookie': self.cookie
            })
        
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
        搜索Bilibili视频
        
        Args:
            search_query: 搜索关键词
            limit: 限制结果数量
            filters: 过滤条件，支持以下字段:
                     - upload_date: 上传日期(today, week, month, year)
                     - duration: 视频时长(short, medium, long)
                     - order: 排序方式(default, click, pubdate, dm, stow, scores)
                     - tids: 分区ID
                     
        Returns:
            视频信息列表
        """
        logger.info(f"搜索Bilibili视频: {search_query}, 限制: {limit}")
        
        filters = filters or {}
        results = []
        
        try:
            # 计算需要请求的页数
            page_size = min(20, limit)  # Bilibili每页最多20个结果
            pages = (limit + page_size - 1) // page_size
            
            # 构建API参数
            params = {
                'keyword': search_query,
                'page': 1,
                'pagesize': page_size,
                'search_type': 'video',
                'highlight': 0,
                'single_column': 0,
                'platform': 'pc'
            }
            
            # 添加排序方式
            if 'order' in filters:
                order_map = {
                    'default': '',      # 默认排序
                    'click': 'click',   # 最多播放
                    'pubdate': 'pubdate',  # 最新发布
                    'dm': 'dm',         # 弹幕数
                    'stow': 'stow',     # 收藏数
                    'scores': 'scores'  # 评论数
                }
                if filters['order'] in order_map:
                    params['order'] = order_map[filters['order']]
            
            # 添加分区筛选
            if 'tids' in filters:
                params['tids'] = filters['tids']
                
            # 添加时长筛选
            if 'duration' in filters:
                duration_map = {
                    'short': 1,   # 10分钟以下
                    'medium': 2,  # 10-30分钟
                    'long': 3     # 30分钟以上
                }
                if filters['duration'] in duration_map:
                    params['duration'] = duration_map[filters['duration']]
            
            # 添加日期筛选
            if 'upload_date' in filters:
                date_map = {
                    'today': 1,   # 1天内
                    'week': 7,    # 7天内
                    'month': 30,  # 30天内
                    'year': 365   # 365天内
                }
                if filters['upload_date'] in date_map:
                    params['order'] = 'pubdate'  # 设置为按发布日期排序
                    params['duration'] = date_map[filters['upload_date']]
                    
            # 发起多页请求
            collected = 0
            for page in range(1, pages + 1):
                params['page'] = page
                page_results = self._search_page(params)
                
                results.extend(page_results)
                collected += len(page_results)
                
                if collected >= limit or len(page_results) < page_size:
                    break
                    
                # 防止请求过快
                time.sleep(0.5)
                
            # 截取所需数量
            results = results[:limit]
            
            logger.info(f"搜索完成，找到 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"Bilibili搜索失败: {str(e)}")
            return []
            
    def _search_page(self, params: Dict) -> List[Dict]:
        """搜索单页视频"""
        results = []
        
        try:
            # Bilibili搜索API
            search_url = "https://api.bilibili.com/x/web-interface/search/type"
            
            response = self.session.get(search_url, params=params)
            data = response.json()
            
            if data.get('code') == 0 and 'data' in data:
                result_data = data['data']
                videos = result_data.get('result', [])
                
                for video in videos:
                    try:
                        video_info = self._extract_video_info(video)
                        if video_info:
                            results.append(video_info)
                    except Exception as e:
                        logger.error(f"提取视频信息失败: {str(e)}")
                        continue
            else:
                error_msg = data.get('message', 'Unknown error')
                logger.error(f"Bilibili API返回错误: {error_msg}")
                
            return results
            
        except Exception as e:
            logger.error(f"搜索页面失败: {str(e)}")
            return []
            
    def _extract_video_info(self, video: Dict) -> Dict:
        """从API结果中提取视频信息"""
        # 提取视频时长（格式如 "12:34"）
        duration = video.get('duration', '0:0')
        duration_parts = duration.split(':')
        duration_seconds = 0
        
        if len(duration_parts) == 2:
            duration_seconds = int(duration_parts[0]) * 60 + int(duration_parts[1])
        elif len(duration_parts) == 3:
            duration_seconds = int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60 + int(duration_parts[2])
            
        # 提取发布时间
        pubdate = video.get('pubdate', 0)
        if not pubdate:
            pubdate_str = video.get('created', '')
            # 尝试从字符串中提取发布时间
            if pubdate_str:
                try:
                    if re.match(r'\d{4}-\d{2}-\d{2}', pubdate_str):
                        pubdate = int(datetime.strptime(pubdate_str, '%Y-%m-%d').timestamp())
                    else:
                        # 处理相对时间，如"2天前"
                        now = datetime.now()
                        if '天前' in pubdate_str:
                            days = int(re.search(r'(\d+)天前', pubdate_str).group(1))
                            pubdate = int((now - timedelta(days=days)).timestamp())
                        elif '小时前' in pubdate_str:
                            hours = int(re.search(r'(\d+)小时前', pubdate_str).group(1))
                            pubdate = int((now - timedelta(hours=hours)).timestamp())
                        elif '分钟前' in pubdate_str:
                            minutes = int(re.search(r'(\d+)分钟前', pubdate_str).group(1))
                            pubdate = int((now - timedelta(minutes=minutes)).timestamp())
                except Exception:
                    pubdate = 0
                    
        # 提取视频ID
        bvid = video.get('bvid', '')
        aid = video.get('aid', 0)
            
        video_info = {
            'platform': 'bilibili',
            'video_id': bvid,
            'aid': aid,
            'title': video.get('title', '').replace('<em class="keyword">', '').replace('</em>', ''),
            'url': f"https://www.bilibili.com/video/{bvid}",
            'thumbnail': video.get('pic', ''),
            'channel': video.get('mid', 0),
            'channel_name': video.get('author', ''),
            'publish_date': datetime.fromtimestamp(pubdate).isoformat() if pubdate else None,
            'duration': duration_seconds,
            'description': video.get('description', ''),
            'views': video.get('play', 0),
            'danmaku': video.get('danmaku', 0),  # 弹幕数
            'likes': video.get('favorites', 0),  # 收藏数
            'comments': video.get('review', 0),  # 评论数
            'tags': video.get('tag', '').split(',') if video.get('tag') else []
        }
        
        return video_info
        
    def get_video_info(self, video_url: str) -> Optional[Dict]:
        """
        获取单个视频的详细信息
        
        Args:
            video_url: 视频URL或视频ID(BV号)
            
        Returns:
            视频详细信息
        """
        try:
            # 提取BV号
            bvid = video_url
            if 'bilibili.com/video/' in video_url:
                bvid = video_url.split('bilibili.com/video/')[1].split('?')[0].split('/')[0]
                
            # 使用视频信息API获取详细信息
            api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            
            response = self.session.get(api_url)
            data = response.json()
            
            if data.get('code') == 0 and 'data' in data:
                video_data = data['data']
                
                # 提取分P信息
                pages = []
                for page in video_data.get('pages', []):
                    pages.append({
                        'cid': page.get('cid'),
                        'page': page.get('page'),
                        'part': page.get('part'),
                        'duration': page.get('duration')
                    })
                    
                # 构建视频信息
                video_info = {
                    'platform': 'bilibili',
                    'video_id': video_data.get('bvid'),
                    'aid': video_data.get('aid'),
                    'title': video_data.get('title'),
                    'url': f"https://www.bilibili.com/video/{bvid}",
                    'thumbnail': video_data.get('pic'),
                    'channel': video_data.get('owner', {}).get('mid'),
                    'channel_name': video_data.get('owner', {}).get('name'),
                    'publish_date': datetime.fromtimestamp(video_data.get('pubdate', 0)).isoformat(),
                    'duration': video_data.get('duration'),
                    'description': video_data.get('desc'),
                    'views': video_data.get('stat', {}).get('view'),
                    'danmaku': video_data.get('stat', {}).get('danmaku'),  # 弹幕数
                    'likes': video_data.get('stat', {}).get('favorite'),  # 收藏数
                    'coins': video_data.get('stat', {}).get('coin'),  # 投币数
                    'shares': video_data.get('stat', {}).get('share'),  # 分享数
                    'comments': video_data.get('stat', {}).get('reply'),  # 评论数
                    'tags': [tag.get('tag_name') for tag in video_data.get('tags', [])],
                    'cid': video_data.get('cid'),  # 首P的CID
                    'pages': pages  # 分P信息
                }
                
                return video_info
            else:
                error_msg = data.get('message', 'Unknown error')
                logger.error(f"获取视频信息失败: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
            return None
            
    def download_video(self, 
                      video_url: str, 
                      output_path: str, 
                      quality: int = 80,
                      filename: str = None) -> str:
        """
        下载Bilibili视频
        
        Args:
            video_url: 视频URL或BV号
            output_path: 输出目录
            quality: 视频质量 (80: 高清 1080P, 64: 高清 720P, 32: 清晰 480P, 16: 流畅 360P)
            filename: 自定义文件名（不包含扩展名）
            
        Returns:
            下载后的文件路径
        """
        try:
            # 创建输出目录
            os.makedirs(output_path, exist_ok=True)
            
            # 获取视频信息
            video_info = self.get_video_info(video_url)
            if not video_info:
                raise ValueError(f"无法获取视频信息: {video_url}")
                
            # 提取视频ID和CID
            bvid = video_info['video_id']
            aid = video_info['aid']
            cid = video_info['cid']
            
            # 不提供文件名则使用视频标题
            if not filename:
                filename = re.sub(r'[\\/:*?"<>|]', '_', video_info['title'])  # 移除非法字符
                
            # 获取视频下载链接
            download_url = self._get_video_download_url(bvid, aid, cid, quality)
            if not download_url:
                raise ValueError(f"无法获取视频下载链接: {bvid}")
                
            # 下载视频
            file_path = os.path.join(output_path, f"{filename}.mp4")
            
            with self.session.get(download_url, stream=True) as response:
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            
            logger.info(f"视频下载完成: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"视频下载失败: {str(e)}")
            raise
            
    def _get_video_download_url(self, bvid: str, aid: int, cid: int, quality: int = 80) -> Optional[str]:
        """获取视频下载链接"""
        try:
            # 使用获取视频流API
            api_url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn={quality}&otype=json&fnver=0&fnval=16"
            
            response = self.session.get(api_url)
            data = response.json()
            
            if data.get('code') == 0 and 'data' in data:
                # 获取最高质量的视频流
                dash = data['data'].get('dash')
                if dash:
                    videos = dash.get('video', [])
                    if videos:
                        # 根据清晰度排序
                        videos.sort(key=lambda x: x.get('bandwidth', 0), reverse=True)
                        return videos[0].get('baseUrl')
                        
                # 如果没有DASH格式，尝试获取普通格式
                durl = data['data'].get('durl')
                if durl and len(durl) > 0:
                    return durl[0].get('url')
                    
            logger.error(f"获取视频流失败: {data.get('message', 'Unknown error')}")
            return None
            
        except Exception as e:
            logger.error(f"获取视频下载链接失败: {str(e)}")
            return None
            
    def get_user_videos(self, 
                       user_id: str, 
                       limit: int = 10, 
                       page: int = 1) -> List[Dict]:
        """
        获取UP主的视频列表
        
        Args:
            user_id: UP主ID
            limit: 返回视频数量
            page: 页码
            
        Returns:
            视频列表
        """
        try:
            # 空间视频列表API
            api_url = f"https://api.bilibili.com/x/space/arc/search"
            params = {
                'mid': user_id,
                'ps': limit,
                'pn': page,
                'order': 'pubdate',  # 按发布日期排序
                'jsonp': 'jsonp'
            }
            
            response = self.session.get(api_url, params=params)
            data = response.json()
            
            results = []
            
            if data.get('code') == 0 and 'data' in data:
                video_list = data['data'].get('list', {}).get('vlist', [])
                
                for video in video_list:
                    try:
                        video_info = {
                            'platform': 'bilibili',
                            'video_id': video.get('bvid'),
                            'aid': video.get('aid'),
                            'title': video.get('title'),
                            'url': f"https://www.bilibili.com/video/{video.get('bvid')}",
                            'thumbnail': video.get('pic'),
                            'channel': video.get('mid'),
                            'channel_name': video.get('author'),
                            'publish_date': datetime.fromtimestamp(video.get('created')).isoformat(),
                            'duration': video.get('length'),
                            'description': video.get('description'),
                            'views': video.get('play'),
                            'comments': video.get('comment')
                        }
                        results.append(video_info)
                    except Exception as e:
                        logger.error(f"提取UP主视频信息失败: {str(e)}")
                        continue
                        
            return results
            
        except Exception as e:
            logger.error(f"获取UP主视频列表失败: {str(e)}")
            return []
            
    def get_popular_videos(self, 
                          limit: int = 10, 
                          region_id: int = 0) -> List[Dict]:
        """
        获取热门视频
        
        Args:
            limit: 返回视频数量
            region_id: 分区ID (0: 全站, 1: 动画, 3: 音乐, 4: 游戏, 5: 娱乐, ...)
            
        Returns:
            热门视频列表
        """
        try:
            # 热门视频API
            api_url = "https://api.bilibili.com/x/web-interface/popular"
            params = {
                'ps': limit,
                'pn': 1
            }
            
            # 如果指定了分区，使用分区热门API
            if region_id > 0:
                api_url = "https://api.bilibili.com/x/web-interface/ranking/region"
                params['rid'] = region_id
                
            response = self.session.get(api_url, params=params)
            data = response.json()
            
            results = []
            
            if data.get('code') == 0 and 'data' in data:
                video_list = data['data'].get('list', [])
                
                for video in video_list[:limit]:
                    try:
                        video_info = {
                            'platform': 'bilibili',
                            'video_id': video.get('bvid'),
                            'aid': video.get('aid'),
                            'title': video.get('title'),
                            'url': f"https://www.bilibili.com/video/{video.get('bvid')}",
                            'thumbnail': video.get('pic'),
                            'channel': video.get('owner', {}).get('mid'),
                            'channel_name': video.get('owner', {}).get('name'),
                            'publish_date': datetime.fromtimestamp(video.get('pubdate')).isoformat(),
                            'description': video.get('desc'),
                            'duration': self._parse_duration(video.get('duration')),
                            'views': video.get('stat', {}).get('view'),
                            'danmaku': video.get('stat', {}).get('danmaku'),
                            'likes': video.get('stat', {}).get('like'),
                            'coins': video.get('stat', {}).get('coin'),
                            'favorites': video.get('stat', {}).get('favorite')
                        }
                        results.append(video_info)
                    except Exception as e:
                        logger.error(f"提取热门视频信息失败: {str(e)}")
                        continue
                        
            return results
            
        except Exception as e:
            logger.error(f"获取热门视频失败: {str(e)}")
            return []
            
    def _parse_duration(self, duration_str: str) -> int:
        """解析时长字符串为秒数"""
        if not duration_str:
            return 0
            
        try:
            # 处理"12:34"格式
            if ':' in duration_str:
                parts = duration_str.split(':')
                if len(parts) == 2:
                    return int(parts[0]) * 60 + int(parts[1])
                elif len(parts) == 3:
                    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                    
            # 处理整数格式（秒数）
            return int(duration_str)
            
        except Exception:
            return 0


# 示例用法
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建适配器
    adapter = BilibiliAdapter()
    
    # 搜索视频
    results = adapter.search_videos(
        search_query="Python教程",
        limit=5,
        filters={
            'upload_date': 'month',
            'duration': 'medium',
            'order': 'click'  # 按播放量排序
        }
    )
    
    # 打印搜索结果
    for i, result in enumerate(results):
        print(f"\n--- 视频 {i+1} ---")
        print(f"标题: {result['title']}")
        print(f"UP主: {result['channel_name']}")
        print(f"链接: {result['url']}")
        print(f"时长: {result['duration']} 秒")
        print(f"播放量: {result['views']}")
        print(f"发布日期: {result['publish_date']}")
        
    # 获取热门视频
    print("\n获取热门视频...")
    popular_videos = adapter.get_popular_videos(limit=3)
    
    for i, video in enumerate(popular_videos):
        print(f"\n--- 热门视频 {i+1} ---")
        print(f"标题: {video['title']}")
        print(f"UP主: {video['channel_name']}")
        print(f"播放量: {video['views']}")
        
    # 下载示例
    if results:
        print("\n下载第一个视频...")
        output_path = os.path.join(os.getcwd(), "downloads")
        adapter.download_video(
            video_url=results[0]['url'],
            output_path=output_path,
            quality=32  # 480P清晰度
        ) 
 
 