#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
配置文件模块
用于存储全局设置
"""

import os
from typing import Dict, Any

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 下载目录
DOWNLOAD_DIR = os.path.join(ROOT_DIR, 'downloads')

# 日志目录
LOG_DIR = os.path.join(ROOT_DIR, 'logs')

# 缓存目录
CACHE_DIR = os.path.join(ROOT_DIR, 'cache')

# 创建必要的目录
for directory in [DOWNLOAD_DIR, LOG_DIR, CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)

# 平台配置
PLATFORM_CONFIGS: Dict[str, Dict[str, Any]] = {
    'youtube': {
        'name': 'YouTube',
        'base_url': 'https://www.youtube.com',
        'search_url': 'https://www.youtube.com/results',
        'video_url': 'https://www.youtube.com/watch',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    },
    'bilibili': {
        'name': '哔哩哔哩',
        'base_url': 'https://www.bilibili.com',
        'search_url': 'https://search.bilibili.com/video',
        'video_url': 'https://www.bilibili.com/video',
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
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    },
    'weibo': {
        'name': '微博',
        'base_url': 'https://weibo.com',
        'search_url': 'https://s.weibo.com/video',
        'video_url': 'https://weibo.com/tv/show',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://weibo.com'
        }
    }
}

# 代理配置
PROXY_CONFIG = {
    'enabled': False,  # 是否启用代理
    'rotation_interval': 300,  # 代理轮换间隔（秒）
    'proxies': []  # 代理列表
}

# 内容分析配置
CONTENT_ANALYSIS_CONFIG = {
    'enabled': True,  # 是否启用内容分析
    'sample_interval': 1,  # 采样间隔（秒）
    'max_samples': 30,  # 最大采样数
    'min_confidence': 0.5  # 最小置信度
}

# 下载配置
DOWNLOAD_CONFIG = {
    'chunk_size': 8192,  # 下载块大小
    'max_retries': 3,  # 最大重试次数
    'timeout': 30,  # 超时时间（秒）
    'concurrent_downloads': 3  # 并发下载数
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',  # 日志级别
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
    'date_format': '%Y-%m-%d %H:%M:%S',  # 日期格式
    'max_size': 10 * 1024 * 1024,  # 最大文件大小（字节）
    'backup_count': 5  # 备份文件数
} 