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

# 创建必要的目录
logs_dir = BASE_DIR / "logs"
downloads_dir = BASE_DIR / "downloads"
cache_dir = BASE_DIR / "cache"
data_dir = BASE_DIR / "data"

# 创建目录
for directory in [logs_dir, downloads_dir, cache_dir, data_dir]:
    directory.mkdir(exist_ok=True)


def setup_logging(log_file="ivas-ifm.log", level="INFO"):
    """配置日志系统"""
    log_level = getattr(logging, level)
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    log_path = logs_dir / log_file
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(str(log_path), encoding='utf-8')
        ]
    )
    
    return logging.getLogger(__name__)


def import_settings():
    """导入设置模块"""
    try:
        # 尝试从src.config导入
        from src.config.settings import APP_CONFIG, PLATFORM_CONFIGS, MESSAGES
        return {
            "APP_CONFIG": APP_CONFIG,
            "PLATFORM_CONFIGS": PLATFORM_CONFIGS,
            "MESSAGES": MESSAGES
        }
    except ImportError:
        # 尝试直接导入settings.py文件
        settings_path = BASE_DIR / "src" / "config" / "settings.py"
        if not settings_path.exists():
            # 如果设置文件不存在，使用默认设置
            return create_default_settings()
            
        try:
            spec = importlib.util.spec_from_file_location("settings", settings_path)
            settings = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(settings)
            return {
                "APP_CONFIG": getattr(settings, "APP_CONFIG", {}),
                "PLATFORM_CONFIGS": getattr(settings, "PLATFORM_CONFIGS", {}),
                "MESSAGES": getattr(settings, "MESSAGES", {})
            }
        except Exception as e:
            logging.error(f"导入设置时出错: {e}")
            return create_default_settings()


def create_default_settings():
    """创建默认设置"""
    APP_CONFIG = {
        "app_name": "IVAS-IFM",
        "app_version": "1.1.0",
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": str(logs_dir / "ivas-ifm.log")
        },
        "ui": {
            "theme": "default",
            "width": 1200,
            "height": 800,
            "title": "IVAS-IFM - Intelligent Video Analysis System"
        }
    }
    
    PLATFORM_CONFIGS = {
        "youtube": {"max_results": 10},
        "bilibili": {"max_results": 10},
        "tiktok": {"max_results": 10},
        "weibo": {"max_results": 10},
        "facebook": {"max_results": 10}
    }
    
    MESSAGES = {
        "welcome": "欢迎使用 IVAS-IFM 智能视频分析系统",
        "search_prompt": "输入关键词搜索多平台视频",
        "no_results": "未找到匹配的结果，请尝试不同的关键词。",
        "download_success": "视频已成功下载到 {path}",
        "download_error": "下载视频时出错: {error}",
        "processing_start": "正在处理视频: {title}",
        "processing_complete": "处理完成: {title}"
    }
    
    return {
        "APP_CONFIG": APP_CONFIG,
        "PLATFORM_CONFIGS": PLATFORM_CONFIGS,
        "MESSAGES": MESSAGES
    }


def import_app():
    """导入应用类"""
    # 首先尝试导入gui_app.py
    try:
        from src.gui_app import App
        return App
    except ImportError:
        pass
    
    # 如果直接导入失败，尝试使用importlib
    app_path = BASE_DIR / "src" / "gui_app.py"
    if app_path.exists():
        try:
            spec = importlib.util.spec_from_file_location("app_module", app_path)
            app_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(app_module)
            
            # 从模块中获取App类
            if hasattr(app_module, "App"):
                return getattr(app_module, "App")
        except Exception as e:
            logging.error(f"导入App类时出错: {e}")
    
    # 尝试导入simple_run.py
    simple_app_path = BASE_DIR / "simple_run.py"
    if simple_app_path.exists():
        try:
            spec = importlib.util.spec_from_file_location("simple_app", simple_app_path)
            simple_app = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(simple_app)
            
            # 尝试获取DemoApp类
            if hasattr(simple_app, "DemoApp"):
                return getattr(simple_app, "DemoApp")
        except Exception as e:
            logging.error(f"导入DemoApp类时出错: {e}")
    
    raise ImportError("找不到应用程序类")


def main():
    """应用程序主入口"""
    # 设置日志
    logger = setup_logging()
    logger.info("正在启动 IVAS-IFM 应用程序...")
    
    # 导入设置
    settings = import_settings()
    app_config = settings.get("APP_CONFIG", {})
    
    try:
        # 导入应用类
        App = import_app()
        app = App()
        app.run()
        logger.info("应用程序已正常关闭")
        return 0
    except Exception as e:
        logger.exception(f"应用程序执行过程中发生错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 