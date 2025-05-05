#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
平台配置模块，用于管理各平台的代理、Cookie和反爬策略配置
"""

import os
import json
from typing import Dict, List, Any, Optional

# 代理配置
PROXY_CONFIG = {
    # 全局代理设置
    "global": {
        "enabled": False,                           # 是否启用代理
        "rotation_interval": 10,                    # 代理轮换间隔(秒)
        "proxy_file": "config/proxies.txt",         # 代理文件路径
        "proxy_api_url": "",                        # 代理API地址(如果有)
        "proxy_api_key": "",                        # 代理API密钥(如果有)
    },
    
    # 平台特定代理设置
    "platforms": {
        "youtube": {
            "enabled": True,                        # 是否启用代理
            "country": "us",                        # 国家/地区代码
            "rotation_interval": 30,                # 代理轮换间隔(秒)
        },
        "facebook": {
            "enabled": True,                        # 是否启用代理
            "country": "us",                        # 国家/地区代码
            "rotation_interval": 20,                # 代理轮换间隔(秒)
        },
        "tiktok": {
            "enabled": True,                        # 是否启用代理
            "country": "us",                        # 国家/地区代码
            "rotation_interval": 15,                # 代理轮换间隔(秒)
        },
        "bilibili": {
            "enabled": False,                       # 默认不启用代理
            "country": "cn",                        # 国家/地区代码
            "rotation_interval": 30,                # 代理轮换间隔(秒)
        },
        "twitter": {
            "enabled": True,                        # 是否启用代理
            "country": "us",                        # 国家/地区代码
            "rotation_interval": 25,                # 代理轮换间隔(秒)
        },
    }
}

# Cookie 配置
COOKIE_CONFIG = {
    # 全局Cookie设置
    "global": {
        "enabled": True,                            # 是否启用Cookie
        "cookie_dir": "cookies",                    # Cookie保存目录
    },
    
    # 平台特定Cookie设置
    "platforms": {
        "youtube": {
            "enabled": True,                        # 是否启用Cookie
            "required": False,                      # 是否必需(未登录仍可使用部分功能)
        },
        "facebook": {
            "enabled": True,                        # 是否启用Cookie
            "required": True,                       # 是否必需(未登录无法使用大部分功能)
        },
        "tiktok": {
            "enabled": True,                        # 是否启用Cookie
            "required": False,                      # 是否必需(未登录仍可使用部分功能)
        },
        "bilibili": {
            "enabled": True,                        # 是否启用Cookie
            "required": False,                      # 是否必需(未登录仍可使用部分功能)
        },
        "twitter": {
            "enabled": True,                        # 是否启用Cookie
            "required": True,                       # 是否必需(未登录无法使用部分功能)
        },
    }
}

# 反爬配置
ANTI_CRAWLER_CONFIG = {
    # 全局反爬设置
    "global": {
        "random_delay": {
            "enabled": True,                        # 是否启用随机延迟
            "min_delay": 1,                         # 最小延迟(秒)
            "max_delay": 3,                         # 最大延迟(秒)
        },
        "rate_limit": {
            "enabled": True,                        # 是否启用速率限制
            "max_requests_per_minute": 20,          # 每分钟最大请求数
        },
        "user_agent_rotation": {
            "enabled": True,                        # 是否启用User-Agent轮换
        },
        "referer_spoofing": {
            "enabled": True,                        # 是否启用Referer伪造
        },
        "header_randomization": {
            "enabled": True,                        # 是否启用请求头随机化
        },
    },
    
    # 平台特定反爬设置
    "platforms": {
        "youtube": {
            "random_delay": {
                "min_delay": 2,                     # 平台特定最小延迟(秒)
                "max_delay": 5,                     # 平台特定最大延迟(秒)
            },
            "rate_limit": {
                "max_requests_per_minute": 15,      # 平台特定每分钟最大请求数
            },
        },
        "facebook": {
            "random_delay": {
                "min_delay": 3,                     # 平台特定最小延迟(秒)
                "max_delay": 6,                     # 平台特定最大延迟(秒)
            },
            "rate_limit": {
                "max_requests_per_minute": 10,      # 平台特定每分钟最大请求数
            },
        },
        "tiktok": {
            "random_delay": {
                "min_delay": 2,                     # 平台特定最小延迟(秒)
                "max_delay": 4,                     # 平台特定最大延迟(秒)
            },
            "rate_limit": {
                "max_requests_per_minute": 12,      # 平台特定每分钟最大请求数
            },
        },
        "bilibili": {
            "random_delay": {
                "min_delay": 1,                     # 平台特定最小延迟(秒)
                "max_delay": 3,                     # 平台特定最大延迟(秒)
            },
            "rate_limit": {
                "max_requests_per_minute": 20,      # 平台特定每分钟最大请求数
            },
        },
        "twitter": {
            "random_delay": {
                "min_delay": 2,                     # 平台特定最小延迟(秒)
                "max_delay": 5,                     # 平台特定最大延迟(秒)
            },
            "rate_limit": {
                "max_requests_per_minute": 15,      # 平台特定每分钟最大请求数
            },
        },
    }
}

# 网络请求配置
REQUEST_CONFIG = {
    # 全局网络请求设置
    "global": {
        "timeout": 30,                              # 请求超时时间(秒)
        "retry_times": 3,                           # 请求失败重试次数
        "retry_delay": 2,                           # 请求失败重试延迟(秒)
    },
    
    # 平台特定网络请求设置
    "platforms": {
        "youtube": {
            "timeout": 40,                          # 平台特定超时时间(秒)
            "retry_times": 4,                       # 平台特定重试次数
        },
        "facebook": {
            "timeout": 45,                          # 平台特定超时时间(秒)
            "retry_times": 5,                       # 平台特定重试次数
        },
        "tiktok": {
            "timeout": 35,                          # 平台特定超时时间(秒)
            "retry_times": 4,                       # 平台特定重试次数
        },
        "bilibili": {
            "timeout": 30,                          # 平台特定超时时间(秒)
            "retry_times": 3,                       # 平台特定重试次数
        },
        "twitter": {
            "timeout": 40,                          # 平台特定超时时间(秒)
            "retry_times": 4,                       # 平台特定重试次数
        },
    }
}

class PlatformConfig:
    """平台配置管理类"""
    
    def __init__(self, platform_name: str):
        """
        初始化平台配置
        
        Args:
            platform_name: 平台名称，如'youtube', 'facebook'等
        """
        self.platform_name = platform_name.lower()
        
        # 加载配置
        self.proxy_config = self._merge_config(PROXY_CONFIG, self.platform_name)
        self.cookie_config = self._merge_config(COOKIE_CONFIG, self.platform_name)
        self.anti_crawler_config = self._merge_config(ANTI_CRAWLER_CONFIG, self.platform_name)
        self.request_config = self._merge_config(REQUEST_CONFIG, self.platform_name)
    
    def _merge_config(self, config: Dict[str, Any], platform_name: str) -> Dict[str, Any]:
        """
        合并全局配置和平台特定配置
        
        Args:
            config: 配置字典
            platform_name: 平台名称
            
        Returns:
            合并后的配置
        """
        result = config["global"].copy()
        
        # 如果平台存在特定配置，则合并
        if "platforms" in config and platform_name in config["platforms"]:
            platform_config = config["platforms"][platform_name]
            
            for key, value in platform_config.items():
                # 如果是字典类型，进行深度合并
                if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                    result[key] = {**result[key], **value}
                else:
                    result[key] = value
        
        return result
    
    def load_proxies_from_file(self) -> List[str]:
        """
        从文件加载代理列表
        
        Returns:
            代理列表
        """
        proxy_file = self.proxy_config.get("proxy_file")
        proxies = []
        
        if proxy_file and os.path.exists(proxy_file):
            with open(proxy_file, 'r', encoding='utf-8') as f:
                proxies = [line.strip() for line in f.readlines() if line.strip()]
        
        return proxies
    
    def get_proxy_settings(self) -> Dict[str, Any]:
        """
        获取代理设置
        
        Returns:
            代理设置字典
        """
        return {
            "enabled": self.proxy_config.get("enabled", False),
            "rotation_interval": self.proxy_config.get("rotation_interval", 10),
            "country": self.proxy_config.get("country", "us"),
        }
    
    def get_cookie_settings(self) -> Dict[str, Any]:
        """
        获取Cookie设置
        
        Returns:
            Cookie设置字典
        """
        return {
            "enabled": self.cookie_config.get("enabled", True),
            "required": self.cookie_config.get("required", False),
            "cookie_dir": self.cookie_config.get("cookie_dir", "cookies"),
        }
    
    def get_anti_crawler_settings(self) -> Dict[str, Any]:
        """
        获取反爬设置
        
        Returns:
            反爬设置字典
        """
        return self.anti_crawler_config
    
    def get_request_settings(self) -> Dict[str, Any]:
        """
        获取请求设置
        
        Returns:
            请求设置字典
        """
        return {
            "timeout": self.request_config.get("timeout", 30),
            "retry_times": self.request_config.get("retry_times", 3),
            "retry_delay": self.request_config.get("retry_delay", 2),
        } 