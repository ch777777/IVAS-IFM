#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
IVAS-IFM (Intelligent Video Acquisition System - Intelligent File Management)
入口脚本

此脚本简单地调用fixed_main.py中的主函数来启动应用程序。
使用此脚本可以避免处理Python模块导入的复杂性。
"""

import os
import sys
from pathlib import Path

def main():
    """主函数，启动应用程序"""
    # 获取当前脚本所在的目录
    current_dir = Path(__file__).resolve().parent
    
    # 将当前目录添加到Python路径中
    sys.path.insert(0, str(current_dir))
    
    # 导入并运行fixed_main.py中的main函数
    try:
        sys.stdout.write("正在启动IVAS-IFM智能视频采集系统...\n")
        
        # 尝试导入fixed_main.py
        import fixed_main
        
        # 调用main函数
        return fixed_main.main()
    except ImportError as e:
        sys.stderr.write(f"错误: 无法导入fixed_main模块: {e}\n")
        return 1
    except Exception as e:
        sys.stderr.write(f"启动过程中发生错误: {e}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 