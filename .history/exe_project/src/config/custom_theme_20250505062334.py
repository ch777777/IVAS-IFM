"""
简洁优雅的UI主题配置
"""
import customtkinter as ctk

# 设置默认外观模式和主题
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# 颜色配置
COLORS = {
    "primary": "#7B2BF9",      # 主紫色
    "primary_dark": "#5A1DB8",  # 深紫色
    "accent": "#9C4DFF",      # 强调紫色
    "text": "#FFFFFF",        # 主文本色
    "text_secondary": "#A0A3BD", # 次要文本色
    "background": "#151823",   # 主背景色
    "surface": "#1A1E2D",     # 表面背景色
    "border": "#2A2F42",      # 边框色
    "success": "#00D1B2",     # 成功色
    "error": "#FF3860",       # 错误色
}

# 字体配置
FONTS = {
    "heading": ("Orbitron", 36, "bold"),
    "subheading": ("Orbitron", 24, "bold"),
    "body": ("Rajdhani", 14),
    "button": ("Rajdhani", 14, "bold"),
    "small": ("Rajdhani", 12)
}

# 组件样式配置
BUTTON_STYLES = {
    "primary": {
        "corner_radius": 8,
        "border_width": 0,
        "fg_color": COLORS["primary"],
        "hover_color": COLORS["primary_dark"],
        "text_color": COLORS["text"],
        "font": FONTS["button"],
        "height": 45
    },
    "secondary": {
        "corner_radius": 8,
        "border_width": 1,
        "border_color": COLORS["border"],
        "fg_color": "transparent",
        "hover_color": COLORS["surface"],
        "text_color": COLORS["text"],
        "font": FONTS["button"],
        "height": 45
    }
}

ENTRY_STYLE = {
    "corner_radius": 8,
    "border_width": 1,
    "border_color": COLORS["border"],
    "fg_color": COLORS["surface"],
    "text_color": COLORS["text"],
    "font": FONTS["body"],
    "height": 45,
    "placeholder_text_color": COLORS["text_secondary"]
}

FRAME_STYLE = {
    "corner_radius": 15,
    "fg_color": COLORS["surface"],
    "border_width": 0
}

# 布局配置
LAYOUT = {
    "padding": 40,
    "spacing": 20,
    "widget_spacing": 15
} 