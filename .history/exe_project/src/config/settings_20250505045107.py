"""
应用程序配置常量
包含所有配置参数和版本信息
"""

# 版本信息
VERSION = "1.1.0"
BUILD_DATE = "2025-05-05"
PREVIOUS_VERSION = "1.0.0"

# 应用程序信息
APP_NAME = "IFMCM - 信息流素材集中管理系统"
APP_NAME_EN = "Information Flow Material Centralized Management"
APP_DESCRIPTION = "用于集中管理和处理信息流素材的模块化应用程序"
AUTHOR = "xiangye72"
GITHUB_USER = "ch777777"
GITHUB_URL = "https://github.com/ch777777"
DEVELOPER_TYPE = "个人开发者"

# UI配置
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
WINDOW_TITLE = f"{APP_NAME} v{VERSION}"
THEME_COLOR_PRIMARY = "#4a6baf"
THEME_COLOR_SECONDARY = "#6c757d"
THEME_COLOR_SUCCESS = "#28a745"
THEME_COLOR_DANGER = "#dc3545"
THEME_COLOR_WARNING = "#ffc107"
THEME_COLOR_INFO = "#17a2b8"
THEME_COLOR_LIGHT = "#f8f9fa"
THEME_COLOR_DARK = "#343a40"
FONT_FAMILY = "Segoe UI"
FONT_SIZE_NORMAL = 10
FONT_SIZE_SMALL = 8
FONT_SIZE_LARGE = 12
FONT_SIZE_HEADER = 14

# 路径配置
ASSETS_DIR = "assets"
ICON_PATH = f"{ASSETS_DIR}/icon.ico"
TEMP_DIR = "temp"
LOG_DIR = "logs"

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = f"{LOG_DIR}/app.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 3

# 功能标志
ENABLE_LOGGING = True
ENABLE_DARK_MODE = True
ENABLE_AUTO_UPDATE = False
ENABLE_ANIMATIONS = True
DEBUG_MODE = False

# 构建状态
BUILD_STATUS = "计划阶段"  # 可选值: 计划阶段, 开发中, 测试中, 已发布

# 项目计划信息
PLANNED_START_DATE = "2025-06-01"
PLANNED_RELEASE_DATE = "2025-07-31"

# 应用程序基本设置
APP_TITLE = "我的高级EXE应用程序"
DEFAULT_WINDOW_SIZE = "500x400"
DEFAULT_FONT = ("Arial", 14)
DEFAULT_PADDING = 20

# 主题颜色
COLORS = {
    "primary": "#4a86e8",
    "secondary": "#6aa84f",
    "background": "#f3f3f3",
    "text": "#333333",
    "warning": "#e69138",
    "error": "#cc0000"
}

# 消息配置
MESSAGES = {
    "welcome": "欢迎使用我的应用程序!",
    "button_click": "您点击了按钮！",
    "button_text": "点击我",
    "message_title": "消息"
} 
 