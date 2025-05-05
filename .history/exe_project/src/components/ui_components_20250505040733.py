"""
UI组件模块
包含应用程序中使用的自定义UI组件
"""
import tkinter as tk
from tkinter import ttk
from ..config.settings import COLORS, DEFAULT_FONT

class StyledButton(tk.Button):
    """自定义风格的按钮组件"""
    
    def __init__(self, master, text, command=None, primary=True, **kwargs):
        """
        创建一个自定义风格的按钮
        
        Args:
            master: 父组件
            text: 按钮文本
            command: 点击事件回调函数
            primary: 是否为主要按钮 (True=主要, False=次要)
            **kwargs: 其他Button参数
        """
        # 设置默认样式
        bg_color = COLORS["primary"] if primary else COLORS["secondary"]
        fg_color = "white"
        
        # 合并自定义样式和用户提供的参数
        button_config = {
            "bg": bg_color,
            "fg": fg_color,
            "font": DEFAULT_FONT,
            "relief": tk.RAISED,
            "borderwidth": 1,
            "padx": 10,
            "pady": 5,
            "cursor": "hand2"
        }
        button_config.update(kwargs)
        
        # 初始化按钮
        super().__init__(master, text=text, command=command, **button_config)
        
        # 绑定鼠标悬停事件
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        
    def _on_hover(self, event):
        """鼠标悬停时改变按钮颜色"""
        current_bg = self.cget("bg")
        # 使按钮颜色变亮
        self.config(bg=self._lighten_color(current_bg))
        
    def _on_leave(self, event):
        """鼠标离开时恢复按钮颜色"""
        if self.cget("bg") != COLORS["primary"] and self.cget("bg") != COLORS["secondary"]:
            primary = self.cget("bg") == self._lighten_color(COLORS["primary"])
            self.config(bg=COLORS["primary"] if primary else COLORS["secondary"])
    
    @staticmethod
    def _lighten_color(hex_color):
        """使颜色变亮"""
        # 转换十六进制颜色为RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # 增加亮度 (限制最大值为255)
        r = min(r + 20, 255)
        g = min(g + 20, 255)
        b = min(b + 20, 255)
        
        # 转回十六进制格式
        return f"#{r:02x}{g:02x}{b:02x}"

class InfoFrame(tk.Frame):
    """显示信息的框架组件"""
    
    def __init__(self, master, title, content, **kwargs):
        """
        创建一个信息显示框架
        
        Args:
            master: 父组件
            title: 标题文本
            content: 内容文本
            **kwargs: 其他Frame参数
        """
        # 设置默认样式
        frame_config = {
            "bg": COLORS["background"],
            "padx": 10,
            "pady": 10,
            "relief": tk.GROOVE,
            "borderwidth": 1
        }
        frame_config.update(kwargs)
        
        # 初始化框架
        super().__init__(master, **frame_config)
        
        # 创建标题和内容标签
        self.title_label = tk.Label(
            self, 
            text=title,
            font=(DEFAULT_FONT[0], DEFAULT_FONT[1] + 2, "bold"),
            bg=COLORS["background"],
            fg=COLORS["primary"]
        )
        self.title_label.pack(anchor="w", pady=(0, 5))
        
        self.content_label = tk.Label(
            self,
            text=content,
            font=DEFAULT_FONT,
            bg=COLORS["background"],
            fg=COLORS["text"],
            justify=tk.LEFT,
            wraplength=300
        )
        self.content_label.pack(anchor="w")
    
    def update_content(self, new_content):
        """更新内容文本"""
        self.content_label.config(text=new_content) 