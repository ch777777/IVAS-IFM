#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import time
import random
import logging
import json
import pickle
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple
from urllib.parse import urlparse
from datetime import datetime, timedelta
from fake_useragent import UserAgent

class ProxyManager:
    """
    代理管理器，支持多种代理类型和自动轮换
    """
    def __init__(self, proxies: List[str] = None, proxy_file: str = None, rotation_interval: int = 10):
        self.proxies = []
        self.current_proxy_index = 0
        self.last_rotation_time = time.time()
        self.rotation_interval = rotation_interval
        
        if proxies:
            self.proxies = proxies
        elif proxy_file and os.path.exists(proxy_file):
            with open(proxy_file, 'r', encoding='utf-8') as f:
                self.proxies = [line.strip() for line in f.readlines() if line.strip()]
        
        self.logger = logging.getLogger('proxy_manager')
        self.logger.info(f"初始化代理管理器，加载了 {len(self.proxies)} 个代理")
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """获取当前代理"""
        if not self.proxies:
            return None
        
        # 检查是否需要轮换代理
        current_time = time.time()
        if current_time - self.last_rotation_time > self.rotation_interval:
            self.rotate_proxy()
        
        proxy_str = self.proxies[self.current_proxy_index]
        
        if '://' in proxy_str:
            protocol = proxy_str.split('://')[0]
            proxy_address = proxy_str
            return {protocol: proxy_address}
        else:
            # 假设为IP:PORT格式，默认使用http
            return {'http': f'http://{proxy_str}', 'https': f'http://{proxy_str}'}
    
    def rotate_proxy(self) -> None:
        """轮换到下一个代理"""
        if not self.proxies:
            return
            
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        self.last_rotation_time = time.time()
        self.logger.info(f"轮换代理为: {self.proxies[self.current_proxy_index]}")
    
    def mark_proxy_failed(self) -> None:
        """标记当前代理失败并轮换"""
        if not self.proxies:
            return
            
        failed_proxy = self.proxies[self.current_proxy_index]
        self.logger.warning(f"代理失败: {failed_proxy}")
        self.rotate_proxy()


class CookieManager:
    """
    Cookie管理器，支持存储和加载Cookie
    """
    def __init__(self, cookie_dir: str = 'cookies'):
        self.cookie_dir = cookie_dir
        if not os.path.exists(cookie_dir):
            os.makedirs(cookie_dir)
        self.logger = logging.getLogger('cookie_manager')
    
    def save_cookies(self, domain: str, cookies: Dict[str, str]) -> None:
        """保存某域名的Cookie"""
        cookie_path = os.path.join(self.cookie_dir, f"{domain}.json")
        with open(cookie_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f)
        self.logger.info(f"已保存域名 {domain} 的Cookie")
    
    def save_session_cookies(self, domain: str, session: requests.Session) -> None:
        """保存会话的Cookie"""
        cookie_path = os.path.join(self.cookie_dir, f"{domain}.pkl")
        with open(cookie_path, 'wb') as f:
            pickle.dump(session.cookies, f)
        self.logger.info(f"已保存域名 {domain} 的会话Cookie")
    
    def load_cookies(self, domain: str) -> Optional[Dict[str, str]]:
        """加载某域名的Cookie"""
        cookie_path = os.path.join(self.cookie_dir, f"{domain}.json")
        if os.path.exists(cookie_path):
            with open(cookie_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def load_session_cookies(self, domain: str, session: requests.Session) -> bool:
        """加载会话的Cookie"""
        cookie_path = os.path.join(self.cookie_dir, f"{domain}.pkl")
        if os.path.exists(cookie_path):
            with open(cookie_path, 'rb') as f:
                session.cookies.update(pickle.load(f))
            self.logger.info(f"已加载域名 {domain} 的会话Cookie")
            return True
        return False


class BasePlatformAdapter(ABC):
    """
    平台适配器基类，提供基础功能和抽象方法
    """
    def __init__(self, 
                 use_proxy: bool = False, 
                 proxy_list: List[str] = None, 
                 proxy_file: str = None,
                 use_cookies: bool = True,
                 cookies_dir: str = 'cookies',
                 retry_times: int = 3,
                 retry_delay: int = 2,
                 timeout: int = 30):
        """
        初始化平台适配器基类
        
        Args:
            use_proxy: 是否使用代理
            proxy_list: 代理列表
            proxy_file: 代理文件路径
            use_cookies: 是否使用并保存Cookie
            cookies_dir: Cookie保存目录
            retry_times: 请求重试次数
            retry_delay: 重试延迟(秒)
            timeout: 请求超时时间(秒)
        """
        # 设置日志
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 代理设置
        self.use_proxy = use_proxy
        self.proxy_manager = None
        if use_proxy and (proxy_list or proxy_file):
            self.proxy_manager = ProxyManager(proxies=proxy_list, proxy_file=proxy_file)
        
        # Cookie设置
        self.use_cookies = use_cookies
        self.cookie_manager = CookieManager(cookie_dir=cookies_dir) if use_cookies else None
        
        # 请求设置
        self.retry_times = retry_times
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.session = self._create_session()
        
        # 用户代理生成器
        try:
            self.user_agent = UserAgent()
        except:
            self.logger.warning("无法加载UserAgent生成器，将使用固定的User-Agent")
            self.user_agent = None
    
    def _create_session(self) -> requests.Session:
        """创建并配置请求会话"""
        session = requests.Session()
        
        # 设置固定请求头
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 加载Cookie(如果启用)
        if self.use_cookies:
            domain = self._get_platform_domain()
            self.cookie_manager.load_session_cookies(domain, session)
        
        return session
    
    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        if self.user_agent:
            try:
                return self.user_agent.random
            except:
                pass
        
        # 备用User-Agent列表
        ua_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        ]
        return random.choice(ua_list)
    
    def _get_platform_domain(self) -> str:
        """获取平台域名，用于Cookie管理"""
        return self.platform_domain if hasattr(self, 'platform_domain') else self.__class__.__name__.lower()
    
    def _get_proxy(self) -> Optional[Dict[str, str]]:
        """获取当前代理"""
        if self.use_proxy and self.proxy_manager:
            return self.proxy_manager.get_proxy()
        return None
    
    def _rotate_proxy(self) -> None:
        """轮换到下一个代理"""
        if self.use_proxy and self.proxy_manager:
            self.proxy_manager.rotate_proxy()
    
    def _mark_proxy_failed(self) -> None:
        """标记当前代理失败"""
        if self.use_proxy and self.proxy_manager:
            self.proxy_manager.mark_proxy_failed()
    
    def _save_cookies(self) -> None:
        """保存当前会话的Cookie"""
        if self.use_cookies and self.cookie_manager:
            domain = self._get_platform_domain()
            self.cookie_manager.save_session_cookies(domain, self.session)
    
    def request(self, 
                method: str, 
                url: str, 
                params: Dict = None, 
                data: Dict = None, 
                json_data: Dict = None, 
                headers: Dict = None, 
                cookies: Dict = None, 
                allow_redirects: bool = True) -> Optional[requests.Response]:
        """
        发送HTTP请求，支持重试和代理切换
        
        Args:
            method: 请求方法，如GET、POST等
            url: 请求URL
            params: URL参数
            data: 表单数据
            json_data: JSON数据
            headers: 请求头
            cookies: Cookie
            allow_redirects: 是否允许重定向
        
        Returns:
            Response对象，请求失败返回None
        """
        # 复制默认会话的头信息
        request_headers = dict(self.session.headers)
        
        # 更新User-Agent
        request_headers['User-Agent'] = self._get_random_user_agent()
        
        # 合并自定义头
        if headers:
            request_headers.update(headers)
        
        # 获取当前代理
        proxies = self._get_proxy()
        
        for attempt in range(self.retry_times):
            try:
                self.logger.debug(f"发送 {method} 请求到 {url} (尝试 {attempt+1}/{self.retry_times})")
                
                # 使用会话发送请求
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json_data,
                    headers=request_headers,
                    cookies=cookies,
                    proxies=proxies,
                    timeout=self.timeout,
                    allow_redirects=allow_redirects
                )
                
                # 保存新的Cookie
                if self.use_cookies:
                    self._save_cookies()
                
                # 检查HTTP状态码
                if response.status_code >= 400:
                    self.logger.warning(f"请求失败: HTTP {response.status_code} {url}")
                    
                    # 对于代理相关的错误状态码，标记代理失败并切换
                    if response.status_code in [403, 407, 429, 500, 502, 503, 504]:
                        self._mark_proxy_failed()
                        proxies = self._get_proxy()
                
                # 假设某些平台有特殊的返回格式，需要检查内容
                if self._is_valid_response(response):
                    return response
                else:
                    self.logger.warning(f"响应格式无效: {url}")
            
            except requests.RequestException as e:
                self.logger.warning(f"请求异常: {str(e)} {url}")
                
                # 代理相关的错误，切换代理
                self._mark_proxy_failed()
                proxies = self._get_proxy()
            
            # 重试延迟，逐渐增加
            sleep_time = self.retry_delay * (1 + attempt)
            self.logger.debug(f"等待 {sleep_time} 秒后重试...")
            time.sleep(sleep_time)
        
        self.logger.error(f"所有重试均失败，无法请求: {url}")
        return None
    
    def _is_valid_response(self, response: requests.Response) -> bool:
        """
        验证响应是否有效（可由子类重写以实现平台特定的验证）
        """
        return response.status_code < 400
    
    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """发送GET请求"""
        return self.request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """发送POST请求"""
        return self.request('POST', url, **kwargs)
    
    @abstractmethod
    def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        搜索视频
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数量
        
        Returns:
            视频信息列表
        """
        pass
    
    @abstractmethod
    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        获取视频信息
        
        Args:
            video_id: 视频标识符
        
        Returns:
            视频详细信息
        """
        pass
    
    @abstractmethod
    def download_video(self, video_id: str, output_path: str, quality: str = 'best') -> Optional[str]:
        """
        下载视频
        
        Args:
            video_id: 视频标识符
            output_path: 输出路径
            quality: 视频质量
        
        Returns:
            下载的文件路径或None(失败时)
        """
        pass

# 留待子类实现的其他基础方法
class AntiCrawlerMixin:
    """
    反爬虫混入类，提供各种反爬策略
    """
    def __init__(self):
        # 添加延迟范围
        self.delay_range = (1, 3)  # 默认1-3秒延迟
        
        # 访问时间窗口计数
        self.request_times = []
        self.max_requests_per_minute = 20
    
    def _random_delay(self) -> None:
        """添加随机延迟"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def _rate_limit(self) -> None:
        """实现速率限制"""
        current_time = time.time()
        
        # 清理超过1分钟的请求记录
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        # 检查是否超过速率限制
        if len(self.request_times) >= self.max_requests_per_minute:
            wait_time = 60 - (current_time - self.request_times[0])
            if wait_time > 0:
                self.logger.info(f"达到速率限制，等待 {wait_time:.2f} 秒")
                time.sleep(wait_time)
        
        # 记录当前请求时间
        self.request_times.append(current_time)
    
    def _add_referer(self, url: str, headers: Dict[str, str]) -> Dict[str, str]:
        """添加合理的Referer头"""
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        referer_options = [
            base_url,
            f"{base_url}/",
            f"{base_url}/search",
            f"{base_url}/feed",
            "https://www.google.com/",
            "https://www.bing.com/",
            "https://www.baidu.com/",
        ]
        
        headers['Referer'] = random.choice(referer_options)
        return headers
    
    def _randomize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """随机化头顺序和增加常见头"""
        # 常见的额外头
        extra_headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 随机挑选一些额外头
        for key, value in extra_headers.items():
            if random.random() > 0.3:  # 70%的概率添加一个额外头
                headers[key] = value
        
        # 转换为列表然后随机打乱顺序再转回字典
        header_items = list(headers.items())
        random.shuffle(header_items)
        return dict(header_items) 