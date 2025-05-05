#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
环境变量加载模块
用于加载和管理环境变量
"""

import os
import sys
from pathlib import Path
from typing import Optional

def load_env(env_file: Optional[str] = None) -> None:
    """
    加载环境变量
    
    Args:
        env_file: 环境变量文件路径，如果为None则自动查找
    """
    if env_file is None:
        # 获取项目根目录
        root_dir = Path(__file__).parent.parent.parent
        
        # 根据环境确定配置文件
        env = os.getenv('ENV', 'development')
        env_files = {
            'development': root_dir / '.env.development',
            'production': root_dir / '.env.production',
            'test': root_dir / '.env.test'
        }
        
        # 首先尝试加载特定环境的配置文件
        env_file = env_files.get(env)
        if not env_file or not env_file.exists():
            # 如果特定环境的配置文件不存在，尝试加载默认配置文件
            env_file = root_dir / '.env'
            
    if not env_file or not os.path.exists(env_file):
        return
        
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip("'").strip('"')
                    
                    if key and value:
                        os.environ[key] = value
                        
    except Exception as e:
        print(f"加载环境变量失败: {str(e)}", file=sys.stderr)

def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    获取环境变量
    
    Args:
        key: 环境变量名
        default: 默认值
        
    Returns:
        Optional[str]: 环境变量值
    """
    return os.getenv(key, default)

def set_env(key: str, value: str) -> None:
    """
    设置环境变量
    
    Args:
        key: 环境变量名
        value: 环境变量值
    """
    os.environ[key] = value

def get_bool_env(key: str, default: bool = False) -> bool:
    """
    获取布尔类型的环境变量
    
    Args:
        key: 环境变量名
        default: 默认值
        
    Returns:
        bool: 环境变量值
    """
    value = get_env(key)
    if value is None:
        return default
        
    return value.lower() in ('true', '1', 'yes', 'on') 