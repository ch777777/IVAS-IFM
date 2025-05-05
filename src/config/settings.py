
# -*- coding: utf-8 -*-

"""
IVAS-IFM系统配置
"""

# 应用程序配置
APP_CONFIG = {
    "app_name": "IVAS-IFM",
    "app_version": "1.1.0",
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/ivas-ifm.log"
    },
    "ui": {
        "theme": "default",
        "width": 1200,
        "height": 800,
        "title": "IVAS-IFM - 智能视频分析系统"
    }
}

# 平台配置
PLATFORM_CONFIGS = {
    "youtube": {
        "max_results": 10,
        "api_key": "",  # 这里填入您的YouTube API密钥
        "use_mock_data": True  # 使用模拟数据
    },
    "bilibili": {
        "max_results": 10,
        "cookie_file": "cookies/bilibili.json",
        "use_mock_data": True
    },
    "tiktok": {
        "max_results": 10,
        "use_mock_data": True
    },
    "weibo": {
        "max_results": 10,
        "cookie_file": "cookies/weibo.json",
        "use_mock_data": True
    },
    "facebook": {
        "max_results": 10,
        "use_mock_data": True
    }
}

# 下载配置
DOWNLOAD_CONFIG = {
    "default_output_dir": "downloads",
    "max_concurrent_downloads": 3,
    "default_video_quality": "720p"
}

# 界面提示信息
MESSAGES = {
    "welcome": "欢迎使用 IVAS-IFM 智能视频分析系统",
    "search_prompt": "输入关键词搜索多平台视频",
    "no_results": "未找到匹配的结果，请尝试不同的关键词。",
    "download_success": "视频已成功下载到 {path}",
    "download_error": "下载视频时出错: {error}",
    "processing_start": "正在处理视频: {title}",
    "processing_complete": "处理完成: {title}"
}

# 模拟数据(用于演示)
MOCK_DATA = {
    "youtube": [
        {
            "platform": "youtube",
            "video_id": "demo_yt_1",
            "title": "【演示】YouTube视频 - 猫咪合集",
            "url": "https://www.youtube.com/watch?v=demo_yt_1",
            "thumbnail": "https://via.placeholder.com/320x180.png?text=YouTube+Demo",
            "channel": "Demo Channel",
            "publish_date": "2025-04-01",
            "duration": 360,
            "views": 15000,
            "description": "这是一个演示YouTube视频"
        },
        {
            "platform": "youtube",
            "video_id": "demo_yt_2",
            "title": "【演示】YouTube视频 - 旅行风景",
            "url": "https://www.youtube.com/watch?v=demo_yt_2",
            "thumbnail": "https://via.placeholder.com/320x180.png?text=Travel+Demo",
            "channel": "Travel Channel",
            "publish_date": "2025-04-15",
            "duration": 480,
            "views": 25000,
            "description": "这是另一个演示YouTube视频"
        }
    ],
    "bilibili": [
        {
            "platform": "bilibili",
            "video_id": "demo_bili_1",
            "title": "【演示】B站视频 - 编程教程",
            "url": "https://www.bilibili.com/video/demo_bili_1",
            "thumbnail": "https://via.placeholder.com/320x180.png?text=Bilibili+Demo",
            "channel": "编程学习",
            "publish_date": "2025-05-01",
            "duration": 1200,
            "views": 50000,
            "description": "这是一个演示B站视频"
        }
    ],
    "tiktok": [
        {
            "platform": "tiktok",
            "video_id": "demo_tt_1",
            "title": "【演示】TikTok视频 - 舞蹈",
            "url": "https://www.tiktok.com/@user/video/demo_tt_1",
            "thumbnail": "https://via.placeholder.com/320x180.png?text=TikTok+Demo",
            "channel": "舞蹈达人",
            "publish_date": "2025-05-03",
            "duration": 60,
            "views": 100000,
            "description": "这是一个演示TikTok视频"
        }
    ]
}
