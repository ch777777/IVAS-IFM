"""
电竞风格UI主题配置
"""
import customtkinter as ctk

# 设置默认外观模式和主题
ctk.set_appearance_mode("dark")  # 深色模式
ctk.set_default_color_theme("dark-blue")

# 颜色配置
COLORS = {
    "primary": "#7B2BF9",      # 主紫色
    "primary_dark": "#5A1DB8",  # 深紫色
    "secondary": "#FFE082",    # 金色
    "accent": "#9C4DFF",      # 亮紫色
    "text": "#FFFFFF",        # 主文本色(白色)
    "text_secondary": "#B39DDB", # 次要文本色(浅紫色)
    "background": "#1A1A2E",   # 深色背景
    "background_gradient": ["#2A1B3D", "#1A1A2E"], # 渐变背景
    "border": "#4527A0",      # 边框色(深紫色)
    "success": "#64DD17",     # 成功色(亮绿色)
    "error": "#FF1744",       # 错误色(亮红色)
}

# 字体配置
FONTS = {
    "heading": ("Orbitron", 32, "bold"),     # 电竞风格标题字体
    "subheading": ("Orbitron", 24, "bold"),
    "body": ("Rajdhani", 14),                # 现代科技感正文字体
    "button": ("Rajdhani", 16, "bold"),
    "small": ("Rajdhani", 12)
}

# 组件样式配置
BUTTON_STYLES = {
    "primary": {
        "corner_radius": 5,
        "border_width": 2,
        "border_color": COLORS["accent"],
        "fg_color": COLORS["primary"],
        "hover_color": COLORS["primary_dark"],
        "text_color": COLORS["text"],
        "font": FONTS["button"],
        "height": 40
    },
    "secondary": {
        "corner_radius": 5,
        "border_width": 2,
        "border_color": COLORS["accent"],
        "fg_color": "transparent",
        "hover_color": COLORS["primary"],
        "text_color": COLORS["text"],
        "font": FONTS["button"],
        "height": 40
    }
}

ENTRY_STYLE = {
    "corner_radius": 5,
    "border_width": 2,
    "border_color": COLORS["border"],
    "fg_color": "transparent",
    "text_color": COLORS["text"],
    "font": FONTS["body"],
    "height": 40
}

FRAME_STYLE = {
    "corner_radius": 10,
    "fg_color": "transparent",
    "border_width": 2,
    "border_color": COLORS["border"]
}

# 布局配置
LAYOUT = {
    "padding": 30,
    "spacing": 20,
    "widget_spacing": 15
} 