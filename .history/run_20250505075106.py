#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
IVAS-IFM 启动脚本

这个脚本用于启动IVAS-IFM系统。
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# 配置基本路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# 创建日志目录
logs_dir = BASE_DIR / "logs"
logs_dir.mkdir(exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(str(logs_dir / "startup.log"), encoding="utf-8")
    ]
)

logger = logging.getLogger("run")

def main():
    """主入口函数"""
    logger.info("启动 IVAS-IFM 系统...")
    
    # 尝试运行fixed_main.py
    try:
        fixed_main_path = BASE_DIR / "fixed_main.py"
        if fixed_main_path.exists():
            logger.info("使用 fixed_main.py 启动系统")
            
            # 使用Python解释器运行脚本
            result = subprocess.run([sys.executable, str(fixed_main_path)], check=True)
            return result.returncode
        else:
            fixed_main_path = BASE_DIR / "exe_project" / "fixed_main.py"
            if fixed_main_path.exists():
                logger.info("使用 exe_project/fixed_main.py 启动系统")
                
                # 使用Python解释器运行脚本
                result = subprocess.run([sys.executable, str(fixed_main_path)], check=True)
                return result.returncode
            else:
                logger.error("找不到 fixed_main.py 文件")
                logger.info("尝试使用备选方法启动系统...")
                
                # 备选：导入gui_app并运行
                try:
                    from src.gui_app import App
                    app = App()
                    app.run()
                    return 0
                except ImportError:
                    logger.error("无法导入 gui_app 模块")
                    return 1
    except Exception as e:
        logger.exception(f"启动系统时出错: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 