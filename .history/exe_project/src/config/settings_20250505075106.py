#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Application configuration settings.

This module contains all the configuration settings for the application.
"""

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Logs directory
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Application configuration
APP_CONFIG = {
    "app_name": "IVAS-IFM",
    "app_version": "1.1.0",
    "app_release_date": "2025-05-05",
    "app_author": "xiangye72",
    "app_description": "Intelligent Video Acquisition System - Intelligent File Management",
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": str(LOGS_DIR / "ivas-ifm.log")
    },
    "ui": {
        "theme": "default",
        "width": 1200,
        "height": 800,
        "title": "IVAS-IFM - Intelligent Video Analysis System",
        "icon": str(BASE_DIR / "assets" / "icon.ico")
    }
}

# Platform configurations
PLATFORM_CONFIGS = {
    "youtube": {
        "api_key": os.environ.get("YOUTUBE_API_KEY", ""),
        "max_results": 50,
        "default_region": "US",
        "request_timeout": 30
    },
    "tiktok": {
        "api_url": "https://api.douyin.wtf/api",
        "max_results": 30,
        "request_timeout": 40
    },
    "bilibili": {
        "max_results": 50,
        "cookie_file": str(BASE_DIR / "config" / "cookies" / "bilibili.txt"),
        "request_timeout": 30
    },
    "weibo": {
        "max_results": 30,
        "cookie_file": str(BASE_DIR / "config" / "cookies" / "weibo.txt"),
        "request_timeout": 30
    },
    "facebook": {
        "max_results": 30,
        "use_selenium": True,
        "request_timeout": 45
    }
}

# Proxy configuration
PROXY_CONFIG = {
    "enabled": False,
    "proxy_list_file": str(BASE_DIR / "config" / "proxies.txt"),
    "rotation_interval": 5,  # Minutes
    "timeout": 10,
    "retry_count": 3
}

# Download settings
DOWNLOAD_CONFIG = {
    "default_output_dir": str(BASE_DIR / "downloads"),
    "max_concurrent_downloads": 3,
    "timeout": 600,  # 10 minutes
    "retry_count": 3,
    "chunk_size": 8192,  # 8 KB
    "file_formats": {
        "video": ["mp4", "webm", "mkv", "avi"],
        "audio": ["mp3", "wav", "m4a", "aac"]
    }
}

# AI model settings
MODEL_CONFIG = {
    "vision": {
        "object_detection": {
            "model": "yolov8",
            "weights": str(BASE_DIR / "models" / "vision" / "yolov8n.pt"),
            "confidence": 0.5,
            "device": "cuda" if os.environ.get("USE_CUDA", "1") == "1" else "cpu"
        },
        "image_classification": {
            "model": "clip",
            "weights": "openai/clip-vit-base-patch32",
            "device": "cuda" if os.environ.get("USE_CUDA", "1") == "1" else "cpu"
        }
    },
    "speech": {
        "asr": {
            "model": "whisper",
            "weights": "base",
            "device": "cuda" if os.environ.get("USE_CUDA", "1") == "1" else "cpu",
            "language": "auto"
        }
    },
    "text": {
        "ocr": {
            "model": "pp-ocrv3",
            "weights": str(BASE_DIR / "models" / "ocr" / "ppocr_v3"),
            "device": "cuda" if os.environ.get("USE_CUDA", "1") == "1" else "cpu"
        },
        "embedding": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "device": "cuda" if os.environ.get("USE_CUDA", "1") == "1" else "cpu"
        }
    }
}

# Message templates
MESSAGES = {
    "welcome": "Welcome to IVAS-IFM - Intelligent Video Analysis System",
    "search_prompt": "Enter search keywords to find videos across multiple platforms",
    "no_results": "No results found for your search. Please try different keywords.",
    "download_success": "Video downloaded successfully to {path}",
    "download_error": "Error downloading video: {error}",
    "processing_start": "Processing video: {title}",
    "processing_complete": "Processing complete for video: {title}"
}

# Get environment variable helper
def get_env(name, default=None):
    """Get an environment variable or return a default value."""
    return os.environ.get(name, default) 
 
 