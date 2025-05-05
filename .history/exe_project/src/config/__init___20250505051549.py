#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
配置包初始化模块
用于初始化和导出配置
"""

from .env import load_env, get_env, set_env, get_bool_env
from .settings import (
    ROOT_DIR,
    ENV,
    DEBUG,
    DOWNLOAD_DIR,
    LOG_DIR,
    CACHE_DIR,
    LOG_CONFIG,
    PROXY_CONFIG,
    CONTENT_ANALYSIS_CONFIG,
    DOWNLOAD_CONFIG,
    PLATFORM_CONFIGS,
    SECURITY_CONFIG
)

# 加载环境变量
load_env()

__all__ = [
    'load_env',
    'get_env',
    'set_env',
    'get_bool_env',
    'ROOT_DIR',
    'ENV',
    'DEBUG',
    'DOWNLOAD_DIR',
    'LOG_DIR',
    'CACHE_DIR',
    'LOG_CONFIG',
    'PROXY_CONFIG',
    'CONTENT_ANALYSIS_CONFIG',
    'DOWNLOAD_CONFIG',
    'PLATFORM_CONFIGS',
    'SECURITY_CONFIG'
] 
 
 