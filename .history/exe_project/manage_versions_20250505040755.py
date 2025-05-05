#!/usr/bin/env python
"""
版本管理工具
用于管理项目文档版本和清理带时间戳的文件

用法:
    # 更新版本号
    python manage_versions.py --version 1.0.1
    
    # 更新版本号和指定构建日期
    python manage_versions.py --version 1.0.1 --date 2024-05-10
    
    # 清理带时间戳的文件
    python manage_versions.py --clean
    
    # 迁移带时间戳的文件到单文件系统
    python manage_versions.py --migrate
    
    # 组合操作
    python manage_versions.py --version 1.0.1 --clean --migrate
"""
import os
import sys
from pathlib import Path

# 添加当前目录到路径，确保模块可以被正确导入
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from src.utils.update_version import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"错误: 导入模块失败 - {e}")
    print("确保您在项目根目录运行此脚本")
    sys.exit(1) 