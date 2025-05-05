"""
CustomTkinter主题配置
"""
import customtkinter as ctk

# 设置默认外观模式和主题
ctk.set_appearance_mode("light")  # 模式: light, dark, system
ctk.set_default_color_theme("blue")  # 主题: blue, dark-blue, green

# 颜色配置
COLORS = {
    "primary": "#2196F3",      # 主色调（蓝色）
    "primary_dark": "#1976D2",  # 深色主色调
    "secondary": "#FFC107",    # 次要色调（琥珀色）
    "success": "#4CAF50",      # 成功色（绿色）
    "error": "#F44336",        # 错误色（红色）
    "warning": "#FF9800",      # 警告色（橙色）
    "text": "#212121",         # 主文本色
    "text_secondary": "#757575", # 次要文本色
    "background": "#FFFFFF",    # 背景色
    "background_light": "#F5F5F5", # 浅色背景
    "border": "#E0E0E0"        # 边框色
}

# 字体配置
FONTS = {
    "heading": ("Helvetica", 24),
    "subheading": ("Helvetica", 18),
    "body": ("Helvetica", 12),
    "small": ("Helvetica", 10)
}

# 组件样式配置
BUTTON_STYLES = {
    "primary": {
        "corner_radius": 8,
        "border_width": 0,
        "fg_color": COLORS["primary"],
        "hover_color": COLORS["primary_dark"],
        "text_color": "white",
        "font": FONTS["body"]
    },
    "secondary": {
        "corner_radius": 8,
        "border_width": 1,
        "fg_color": "transparent",
        "hover_color": COLORS["background_light"],
        "text_color": COLORS["text"],
        "font": FONTS["body"]
    }
}

ENTRY_STYLE = {
    "corner_radius": 8,
    "border_width": 2,
    "fg_color": "transparent",
    "border_color": COLORS["border"],
    "text_color": COLORS["text"],
    "font": FONTS["body"]
}

FRAME_STYLE = {
    "corner_radius": 10,
    "fg_color": "transparent",
    "border_width": 1,
    "border_color": COLORS["border"]
}

# 布局配置
LAYOUT = {
    "padding": 20,
    "spacing": 10
} 