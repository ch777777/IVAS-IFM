#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
配置文件模块
用于存储全局设置
"""

import os
from typing import Dict, Any

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 环境配置
ENV = os.getenv('ENV', 'development')
DEBUG = ENV == 'development'

# 目录配置
DOWNLOAD_DIR = os.path.join(ROOT_DIR, 'downloads')
LOG_DIR = os.path.join(ROOT_DIR, 'logs')
CACHE_DIR = os.path.join(ROOT_DIR, 'cache')

# 创建必要的目录
for directory in [DOWNLOAD_DIR, LOG_DIR, CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)

# 日志配置
LOG_CONFIG = {
    'level': 'DEBUG' if DEBUG else 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# 代理配置
PROXY_CONFIG = {
    'enabled': False,
    'rotation_interval': 300,  # 5分钟
    'proxies': []
}

# 内容分析配置
CONTENT_ANALYSIS_CONFIG = {
    'enabled': True,
    'sample_interval': 1,  # 1秒
    'max_samples': 30,
    'min_confidence': 0.5
}

# 下载配置
DOWNLOAD_CONFIG = {
    'chunk_size': 8192,
    'max_retries': 3,
    'timeout': 30,
    'concurrent_downloads': 3
}

# 平台配置
PLATFORM_CONFIGS: Dict[str, Dict[str, Any]] = {
    'youtube': {
        'name': 'YouTube',
        'base_url': 'https://www.youtube.com',
        'search_url': 'https://www.youtube.com/results',
        'video_url': 'https://www.youtube.com/watch',
        'api_key': os.getenv('YOUTUBE_API_KEY', ''),
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    },
    'bilibili': {
        'name': '哔哩哔哩',
        'base_url': 'https://www.bilibili.com',
        'search_url': 'https://search.bilibili.com/video',
        'video_url': 'https://www.bilibili.com/video',
        'cookie': os.getenv('BILIBILI_COOKIE', ''),
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com'
        }
    },
    'tiktok': {
        'name': 'TikTok',
        'base_url': 'https://www.tiktok.com',
        'search_url': 'https://www.tiktok.com/search',
        'video_url': 'https://www.tiktok.com/@',
        'cookie': os.getenv('TIKTOK_COOKIE', ''),
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    },
    'weibo': {
        'name': '微博',
        'base_url': 'https://weibo.com',
        'search_url': 'https://s.weibo.com/video',
        'video_url': 'https://weibo.com/tv/show',
        'cookie': os.getenv('WEIBO_COOKIE', ''),
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://weibo.com'
        }
    }
}

# 安全配置
SECURITY_CONFIG = {
    'secret_key': os.getenv('SECRET_KEY', 'dev-secret-key'),
    'allowed_hosts': os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(','),
    'cors_origins': os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
} 
 
 