#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
平台配置文件
包含各个视频平台的特定配置信息
"""

# 平台配置
PLATFORM_CONFIG = {
    'youtube': {
        'name': 'YouTube',
        'base_url': 'https://www.youtube.com',
        'search_url': 'https://www.youtube.com/results',
        'api_key': '',  # 需要用户配置
        'rate_limit': {
            'requests_per_minute': 60,
            'concurrent_requests': 5
        },
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    },
    'bilibili': {
        'name': '哔哩哔哩',
        'base_url': 'https://www.bilibili.com',
        'search_url': 'https://search.bilibili.com/video',
        'rate_limit': {
            'requests_per_minute': 30,
            'concurrent_requests': 3
        },
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com'
        }
    },
    'tiktok': {
        'name': 'TikTok',
        'base_url': 'https://www.tiktok.com',
        'search_url': 'https://www.tiktok.com/search',
        'rate_limit': {
            'requests_per_minute': 20,
            'concurrent_requests': 2
        },
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    },
    'weibo': {
        'name': '微博视频',
        'base_url': 'https://weibo.com',
        'search_url': 'https://s.weibo.com/video',
        'rate_limit': {
            'requests_per_minute': 30,
            'concurrent_requests': 3
        },
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }
}

# 代理配置
PROXY_CONFIG = {
    'enabled': False,
    'proxy_list': [],
    'proxy_type': 'http',  # http, https, socks5
    'rotation_interval': 300  # 代理轮换间隔（秒）
}

# 搜索配置
SEARCH_CONFIG = {
    'default_max_results': 10,
    'relevance_threshold': 0.5,
    'sort_by': 'relevance',  # relevance, views, date
    'default_filters': {
        'duration_range': (60, 1800),  # 1分钟到30分钟
        'min_views': 1000
    }
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'crawler.log'
}

def get_platform_config(platform):
    """获取指定平台的配置"""
    return PLATFORM_CONFIG.get(platform, {})

def get_all_platforms():
    """获取所有支持的平台列表"""
    return list(PLATFORM_CONFIG.keys())

def update_platform_config(platform, config):
    """更新平台配置"""
    if platform in PLATFORM_CONFIG:
        PLATFORM_CONFIG[platform].update(config)
        return True
    return False

def enable_proxy(proxy_list, proxy_type='http'):
    """启用代理"""
    PROXY_CONFIG['enabled'] = True
    PROXY_CONFIG['proxy_list'] = proxy_list
    PROXY_CONFIG['proxy_type'] = proxy_type

def disable_proxy():
    """禁用代理"""
    PROXY_CONFIG['enabled'] = False
    PROXY_CONFIG['proxy_list'] = [] 