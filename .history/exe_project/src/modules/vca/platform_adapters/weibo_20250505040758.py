"""
微博平台爬虫适配器
负责从微博获取视频数据
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
except ImportError:
    raise ImportError("请安装必要的依赖: pip install requests beautifulsoup4")

logger = logging.getLogger(__name__)

# 平台名称常量，用于爬虫管理器注册
PLATFORM_NAME = "weibo"

class WeiboAdapter:
    """微博平台适配器，提供视频搜索和下载功能"""
    
    def __init__(self, api_key: str = None, proxy: str = None, cookie: str = None):
        """
        初始化微博适配器
        
        Args:
            api_key: API密钥（可选）
            proxy: 代理服务器（可选）
            cookie: 登录Cookie（必要，用于获取内容）
        """
        self.api_key = api_key
        self.proxy = proxy
        self.cookie = cookie
        self.session = self._create_session()
        logger.info("微博适配器已初始化")
        
    def _create_session(self) -> requests.Session:
        """创建请求会话"""
        session = requests.Session()
        
        # 添加请求头，模拟浏览器
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept': 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://weibo.com/'
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
        搜索微博视频
        
        Args:
            search_query: 搜索关键词
            limit: 限制结果数量
            filters: 过滤条件，支持以下字段:
                     - upload_date: 上传日期(today, week, month, year)
                     - sort_type: 排序方式(hot, time)
                     
        Returns:
            视频信息列表
        """
        logger.info(f"搜索微博视频: {search_query}, 限制: {limit}")
        
        filters = filters or {}
        results = []
        
        try:
            # 确保有Cookie，否则无法搜索
            if not self.cookie:
                logger.error("微博搜索需要设置Cookie")
                return []
                
            # 处理排序方式
            sort_type = filters.get('sort_type', 'hot')
            if sort_type not in ['hot', 'time']:
                sort_type = 'hot'
                
            # 处理时间范围
            upload_date = filters.get('upload_date', '')
            time_scope = ''
            if upload_date == 'today':
                time_scope = '1'  # 1天内
            elif upload_date == 'week':
                time_scope = '7'  # 7天内
            elif upload_date == 'month':
                time_scope = '30'  # 30天内
            elif upload_date == 'year':
                time_scope = '365'  # 365天内
                
            # 计算需要请求的页数
            page_size = 10  # 微博每页约10个结果
            pages = (limit + page_size - 1) // page_size
            
            # 发起多页请求
            collected = 0
            for page in range(1, pages + 1):
                page_results = self._search_page(search_query, page, sort_type, time_scope)
                
                results.extend(page_results)
                collected += len(page_results)
                
                if collected >= limit or len(page_results) < page_size:
                    break
                    
                # 防止请求过快
                time.sleep(1)
                
            # 截取所需数量
            results = results[:limit]
            
            logger.info(f"搜索完成，找到 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"微博搜索失败: {str(e)}")
            return []
            
    def _search_page(self, 
                    query: str, 
                    page: int, 
                    sort_type: str, 
                    time_scope: str) -> List[Dict]:
        """搜索单页视频"""
        results = []
        
        try:
            # 微博搜索API
            timestamp = int(time.time() * 1000)
            base_url = "https://m.weibo.cn/api/container/getIndex"
            params = {
                'containerid': f'100103type=61&q={query}&t=0',
                'page_type': 'searchall',
                'page': page
            }
            
            # 添加排序方式
            if sort_type == 'time':
                params['containerid'] = f'100103type=61&q={query}&t=0&f=1'
                
            # 添加时间范围
            if time_scope:
                params['containerid'] += f'&xsort=hot&suball=1&timescope=custom:{time_scope}:'
                
            response = self.session.get(base_url, params=params)
            data = response.json()
            
            if data.get('ok') == 1 and 'data' in data:
                cards = data['data'].get('cards', [])
                
                for card in cards:
                    # 只处理微博内容卡片
                    if card.get('card_type') == 9:
                        mblog = card.get('mblog', {})
                        
                        # 检查是否包含视频
                        if 'page_info' in mblog and mblog['page_info'].get('type') == 'video':
                            try:
                                video_info = self._extract_video_info(mblog)
                                if video_info:
                                    results.append(video_info)
                            except Exception as e:
                                logger.error(f"提取视频信息失败: {str(e)}")
                                continue
            else:
                logger.error(f"微博API返回错误: {data}")
                
            return results
            
        except Exception as e:
            logger.error(f"搜索页面失败: {str(e)}")
            return []
            
    def _extract_video_info(self, mblog: Dict) -> Dict:
        """从微博API结果中提取视频信息"""
        # 获取视频相关信息
        page_info = mblog.get('page_info', {})
        video_info = page_info.get('media_info', {})
        
        # 提取视频ID
        video_id = page_info.get('object_id', '')
        if not video_id:
            video_id = f"weibo_{mblog.get('id', '')}"
            
        # 提取发布时间
        created_at = mblog.get('created_at', '')
        publish_date = None
        
        try:
            # 尝试解析时间格式
            if re.match(r'\d{4}-\d{2}-\d{2}', created_at):
                publish_date = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            elif re.match(r'\w{3} \w{3} \d{2} \d{2}:\d{2}:\d{2} \+\d{4} \d{4}', created_at):
                publish_date = datetime.strptime(created_at, '%a %b %d %H:%M:%S +0800 %Y')
            else:
                # 处理相对时间，如"2分钟前"
                now = datetime.now()
                if '分钟前' in created_at:
                    minutes = int(re.search(r'(\d+)分钟前', created_at).group(1))
                    publish_date = now - timedelta(minutes=minutes)
                elif '小时前' in created_at:
                    hours = int(re.search(r'(\d+)小时前', created_at).group(1))
                    publish_date = now - timedelta(hours=hours)
                elif '昨天' in created_at:
                    publish_date = now - timedelta(days=1)
                else:
                    # 当年的日期格式，如"07-12"
                    if re.match(r'\d{2}-\d{2}', created_at):
                        month, day = created_at.split('-')
                        publish_date = datetime(now.year, int(month), int(day))
        except Exception:
            publish_date = None
            
        # 转换为ISO格式
        if publish_date:
            publish_date = publish_date.isoformat()
            
        # 提取视频时长
        duration = video_info.get('duration', 0)
        
        # 构建视频信息
        info = {
            'platform': 'weibo',
            'video_id': video_id,
            'title': page_info.get('title', mblog.get('text', '')).replace('<span class="surl-text">', '').replace('</span>', ''),
            'url': page_info.get('page_url', f"https://m.weibo.cn/detail/{mblog.get('id', '')}"),
            'thumbnail': page_info.get('page_pic', {}).get('url', ''),
            'channel': mblog.get('user', {}).get('id', 0),
            'channel_name': mblog.get('user', {}).get('screen_name', ''),
            'publish_date': publish_date,
            'duration': duration,
            'description': mblog.get('text', ''),
            'views': mblog.get('attitudes_count', 0),  # 点赞数
            'comments': mblog.get('comments_count', 0),  # 评论数
            'reposts': mblog.get('reposts_count', 0),  # 转发数
            'download_url': video_info.get('stream_url_hd', video_info.get('stream_url', ''))
        }
        
        return info
        
    def get_video_info(self, video_url: str) -> Optional[Dict]:
        """
        获取单个视频的详细信息
        
        Args:
            video_url: 视频URL或微博ID
            
        Returns:
            视频详细信息
        """
        try:
            # 提取微博ID
            weibo_id = video_url
            
            if 'weibo.com/detail/' in video_url or 'm.weibo.cn/detail/' in video_url:
                weibo_id = video_url.split('/detail/')[1].split('?')[0].split('/')[0]
                
            # 使用微博状态API获取详细信息
            api_url = f"https://m.weibo.cn/statuses/show?id={weibo_id}"
            
            response = self.session.get(api_url)
            data = response.json()
            
            if data.get('ok') == 1 and 'data' in data:
                mblog = data['data']
                
                # 检查是否包含视频
                if 'page_info' in mblog and mblog['page_info'].get('type') == 'video':
                    return self._extract_video_info(mblog)
                else:
                    logger.warning(f"该微博不包含视频: {weibo_id}")
                    return None
            else:
                logger.error(f"获取微博信息失败: {data}")
                return None
                
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
            return None
            
    def download_video(self, 
                      video_url: str, 
                      output_path: str, 
                      filename: str = None) -> str:
        """
        下载微博视频
        
        Args:
            video_url: 视频URL或微博ID
            output_path: 输出目录
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
                
            # 获取下载链接
            download_url = video_info.get('download_url', '')
            if not download_url:
                raise ValueError(f"无法获取视频下载链接: {video_url}")
                
            # 不提供文件名则使用视频ID
            if not filename:
                filename = f"weibo_{video_info['video_id']}"
                
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
            
    def get_user_videos(self, 
                       user_id: str, 
                       limit: int = 10) -> List[Dict]:
        """
        获取用户的视频列表
        
        Args:
            user_id: 用户ID
            limit: 返回视频数量
            
        Returns:
            视频列表
        """
        try:
            results = []
            page = 1
            collected = 0
            
            while collected < limit:
                # 用户微博列表API
                api_url = f"https://m.weibo.cn/api/container/getIndex"
                params = {
                    'type': 'uid',
                    'value': user_id,
                    'containerid': f'107603{user_id}',
                    'page': page
                }
                
                response = self.session.get(api_url, params=params)
                data = response.json()
                
                if data.get('ok') != 1 or 'data' not in data:
                    break
                    
                cards = data['data'].get('cards', [])
                if not cards:
                    break
                    
                # 处理每条微博
                found_in_page = 0
                for card in cards:
                    if card.get('card_type') == 9:  # 微博卡片
                        mblog = card.get('mblog', {})
                        
                        # 检查是否包含视频
                        if 'page_info' in mblog and mblog['page_info'].get('type') == 'video':
                            try:
                                video_info = self._extract_video_info(mblog)
                                if video_info:
                                    results.append(video_info)
                                    collected += 1
                                    found_in_page += 1
                                    
                                    if collected >= limit:
                                        break
                            except Exception as e:
                                logger.error(f"提取视频信息失败: {str(e)}")
                                continue
                                
                # 如果当前页没有找到视频或已达到限制，退出循环
                if found_in_page == 0 or collected >= limit:
                    break
                    
                page += 1
                # 防止请求过快
                time.sleep(1)
                
            return results
            
        except Exception as e:
            logger.error(f"获取用户视频列表失败: {str(e)}")
            return []


# 示例用法
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建适配器 (需要提供Cookie)
    cookie = "SUB=xxx; SUBP=xxx"  # 替换为实际的Cookie
    adapter = WeiboAdapter(cookie=cookie)
    
    # 搜索视频
    results = adapter.search_videos(
        search_query="Python教程",
        limit=5,
        filters={
            'upload_date': 'month',
            'sort_type': 'hot'  # 按热度排序
        }
    )
    
    # 打印搜索结果
    for i, result in enumerate(results):
        print(f"\n--- 视频 {i+1} ---")
        print(f"标题: {result['title']}")
        print(f"作者: {result['channel_name']}")
        print(f"链接: {result['url']}")
        print(f"时长: {result['duration']} 秒")
        print(f"点赞: {result['views']}")
        
    # 下载示例
    if results:
        print("\n下载第一个视频...")
        output_path = os.path.join(os.getcwd(), "downloads")
        adapter.download_video(
            video_url=results[0]['url'],
            output_path=output_path
        ) 