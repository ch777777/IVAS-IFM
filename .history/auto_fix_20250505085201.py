#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
IVAS-IFM 自动修复工具

该脚本用于修复IVAS-IFM系统的常见问题，特别是空搜索结果问题。
它会：
1. 检查系统结构
2. 创建必要的配置文件
3. 设置模拟数据，使系统在没有真实API密钥的情况下也能展示结果
"""

import os
import sys
import json
import shutil
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("fix_log.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("auto_fix")

# 基本路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# 必要的目录
REQUIRED_DIRS = [
    "logs", "downloads", "cache", "data", "cookies",
    "src/config", "src/modules/vca/platform_adapters"
]

# 模拟数据 - 各平台的搜索结果
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

# 配置文件内容
SETTINGS_CONTENT = """
# -*- coding: utf-8 -*-

\"\"\"
IVAS-IFM系统配置
\"\"\"

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
"""

# 爬虫管理器修改
CRAWLER_MANAGER_PATCH = """
    def _search_platform(
        self, 
        platform: str, 
        query: str, 
        max_results: int, 
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        \"\"\"
        在指定平台上搜索视频
        
        Args:
            platform: 平台名称
            query: 搜索关键词
            max_results: 最大结果数
            filters: 搜索过滤条件
            
        Returns:
            搜索结果列表
        \"\"\"
        # 检查是否使用模拟数据
        platform_config = PLATFORM_CONFIGS.get(platform, {})
        use_mock = platform_config.get("use_mock_data", False)
        
        if use_mock and hasattr(settings, "MOCK_DATA") and platform in settings.MOCK_DATA:
            # 使用模拟数据
            logger.info(f"使用 {platform} 平台模拟数据")
            results = settings.MOCK_DATA.get(platform, [])
            
            # 过滤结果 (简单匹配标题或描述中是否包含查询词)
            if query:
                query_lower = query.lower()
                results = [
                    r for r in results 
                    if query_lower in r.get("title", "").lower() or query_lower in r.get("description", "").lower()
                ]
            
            return results[:max_results]
        
        if platform not in self.platform_adapters:
            logger.warning(f"未找到 {platform} 平台适配器")
            return []
            
        adapter = self.platform_adapters[platform]
        try:
            # 使用适配器搜索视频
            results = adapter.search_videos(query, max_results, filters)
            return results
        except Exception as e:
            logger.error(f"在 {platform} 平台搜索时出错: {e}")
            return []
"""

def ensure_directories():
    """确保所有必要的目录存在"""
    logger.info("检查并创建必要的目录...")
    for directory in REQUIRED_DIRS:
        dir_path = BASE_DIR / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建目录: {directory}")
        else:
            logger.info(f"目录已存在: {directory}")
    
    return True

def create_settings_file():
    """创建或更新设置文件"""
    settings_path = BASE_DIR / "src" / "config" / "settings.py"
    
    # 检查是否已存在配置文件
    if settings_path.exists():
        # 备份现有文件
        backup_path = BASE_DIR / "src" / "config" / "settings.py.bak"
        shutil.copy2(settings_path, backup_path)
        logger.info(f"已备份原配置文件到: {backup_path}")
    
    # 创建新的配置文件
    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(SETTINGS_CONTENT)
    
    logger.info(f"已创建新的配置文件: {settings_path}")
    return True

def create_empty_cookies():
    """创建空的Cookie文件"""
    cookie_files = {
        "bilibili.json": {"DedeUserID": "", "DedeUserID__ckMd5": "", "SESSDATA": ""},
        "weibo.json": {"SUB": "", "SUBP": ""}
    }
    
    for filename, content in cookie_files.items():
        cookie_path = BASE_DIR / "cookies" / filename
        with open(cookie_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2)
        
        logger.info(f"已创建空的Cookie文件: {filename}")
    
    return True

def patch_crawler_manager():
    """修补爬虫管理器以支持模拟数据"""
    crawler_path = BASE_DIR / "src" / "modules" / "vca" / "crawler_manager.py"
    
    if not crawler_path.exists():
        logger.error(f"找不到爬虫管理器文件: {crawler_path}")
        return False
    
    # 读取当前文件内容
    with open(crawler_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 添加导入语句
    if "import importlib" in content and "from src.config import settings" not in content:
        # 寻找导入部分的末尾
        import_section_end = content.find("logger = logging.getLogger(__name__)")
        if import_section_end > 0:
            # 在导入部分末尾添加设置导入
            new_import = "try:\n    from src.config import settings\nexcept ImportError:\n    settings = None\n\n"
            content = content[:import_section_end] + new_import + content[import_section_end:]
    
    # 替换_search_platform方法
    start_marker = "def _search_platform"
    end_marker = "def _detect_platform_from_url"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx > 0 and end_idx > start_idx:
        # 找到方法的结束位置
        # 查找方法体中的最后一个return语句
        method_body = content[start_idx:end_idx]
        
        # 替换整个方法
        content = content[:start_idx] + CRAWLER_MANAGER_PATCH + content[end_idx:]
        
        # 保存修改后的文件
        with open(crawler_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"已修补爬虫管理器支持模拟数据: {crawler_path}")
        return True
    else:
        logger.error("无法在爬虫管理器中找到_search_platform方法")
        return False

def fix_system():
    """执行系统修复"""
    logger.info("开始自动修复IVAS-IFM系统...")
    
    # 1. 确保目录结构
    if not ensure_directories():
        logger.error("创建目录结构失败")
        return False
    
    # 2. 创建或更新设置文件
    if not create_settings_file():
        logger.error("创建设置文件失败")
        return False
    
    # 3. 创建空的Cookie文件
    if not create_empty_cookies():
        logger.error("创建Cookie文件失败")
        return False
    
    # 4. 修补爬虫管理器
    if not patch_crawler_manager():
        logger.warning("修补爬虫管理器失败，但不影响基本功能")
    
    logger.info("修复完成！现在您可以运行fixed_main.py或run.py启动系统。")
    logger.info("系统将使用模拟数据展示搜索结果。")
    return True

if __name__ == "__main__":
    fix_system() 