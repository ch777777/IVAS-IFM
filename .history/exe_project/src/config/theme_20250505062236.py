"""
UI主题配置
"""

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
    "heading": ("Helvetica", 24, "bold"),
    "subheading": ("Helvetica", 18, "bold"),
    "body": ("Helvetica", 12),
    "body_bold": ("Helvetica", 12, "bold"),
    "small": ("Helvetica", 10)
}

# 样式配置
STYLES = {
    "button": {
        "font": ("Helvetica", 12),
        "background": COLORS["primary"],
        "foreground": "white",
        "activebackground": COLORS["primary_dark"],
        "activeforeground": "white",
        "borderwidth": 0,
        "padx": 20,
        "pady": 10,
        "cursor": "hand2"
    },
    "button_secondary": {
        "font": ("Helvetica", 12),
        "background": COLORS["background_light"],
        "foreground": COLORS["text"],
        "activebackground": COLORS["border"],
        "activeforeground": COLORS["text"],
        "borderwidth": 1,
        "padx": 20,
        "pady": 10,
        "cursor": "hand2"
    },
    "entry": {
        "font": ("Helvetica", 12),
        "background": "white",
        "foreground": COLORS["text"],
        "borderwidth": 1,
        "relief": "solid"
    },
    "label": {
        "font": ("Helvetica", 12),
        "background": COLORS["background"],
        "foreground": COLORS["text"]
    }
}

# 布局配置
LAYOUT = {
    "padding": 20,
    "spacing": 10,
    "border_radius": 5
} 