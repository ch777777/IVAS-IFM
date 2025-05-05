#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
IVAS-IFM (Intelligent Video Acquisition System - Intelligent File Management)
主入口模块

这个模块初始化应用程序并管理执行上下文。
"""

import os
import sys
import logging
import importlib.util
from pathlib import Path

# 首先确定路径并修复导入问题
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


def import_settings():
    """导入设置模块"""
    settings_path = BASE_DIR / "src" / "config" / "settings.py"
    if not settings_path.exists():
        raise ImportError(f"找不到设置文件: {settings_path}")
        
    spec = importlib.util.spec_from_file_location("settings", settings_path)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)
    return settings


# 导入设置
settings = import_settings()
APP_CONFIG = settings.APP_CONFIG

# 初始化日志目录
logs_dir = BASE_DIR / "logs"
logs_dir.mkdir(exist_ok=True)


def setup_logging():
    """配置日志系统"""
    log_level = getattr(logging, APP_CONFIG['logging']['level'])
    log_format = APP_CONFIG['logging']['format']
    
    log_file = Path(APP_CONFIG['logging']['file'])
    if not log_file.is_absolute():
        log_file = logs_dir / log_file.name
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(str(log_file), encoding='utf-8')
        ]
    )
    
    return logging.getLogger(__name__)


def import_app():
    """导入应用类"""
    app_path = BASE_DIR / "src" / "gui_app.py"
    if not app_path.exists():
        # 如果主应用不存在，使用简单的示例应用
        app_path = BASE_DIR / "simple_run.py"
        if not app_path.exists():
            raise ImportError("找不到应用程序文件")
    
    spec = importlib.util.spec_from_file_location("app_module", app_path)
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)
    
    # 从模块中获取app类
    App = getattr(app_module, "DemoApp", None)
    if App is None:
        App = getattr(app_module, "App", None)
    
    if App is None:
        raise ImportError("找不到应用程序类")
    
    return App


def main():
    """应用程序主入口"""
    logger = setup_logging()
    logger.info("正在启动 IVAS-IFM 应用程序...")
    
    try:
        App = import_app()
        app = App()
        app.run()
    except Exception as e:
        logger.exception(f"应用程序执行过程中发生错误: {e}")
        return 1
    
    logger.info("应用程序已成功关闭。")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 