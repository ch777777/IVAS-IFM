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

class LoginFrame(tk.Frame):
    """登录界面组件"""
    
    def __init__(self, master, on_login=None, **kwargs):
        """
        创建登录界面
        
        Args:
            master: 父组件
            on_login: 登录回调函数，接收(username, password)参数
            **kwargs: 其他Frame参数
        """
        # 设置默认样式
        frame_config = {
            "bg": COLORS["background"],
            "padx": 20,
            "pady": 20,
            "relief": tk.GROOVE,
            "borderwidth": 1
        }
        frame_config.update(kwargs)
        
        # 初始化框架
        super().__init__(master, **frame_config)
        
        # 存储回调函数
        self.on_login = on_login
        
        # 创建标题
        self.title_label = tk.Label(
            self,
            text="IVAS-IFM 登录",
            font=(DEFAULT_FONT[0], DEFAULT_FONT[1] + 4, "bold"),
            bg=COLORS["background"],
            fg=COLORS["primary"]
        )
        self.title_label.pack(pady=(0, 20))
        
        # 创建用户名输入框
        self.username_frame = tk.Frame(self, bg=COLORS["background"])
        self.username_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.username_label = tk.Label(
            self.username_frame,
            text="用户名:",
            font=DEFAULT_FONT,
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        self.username_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.username_entry = tk.Entry(
            self.username_frame,
            font=DEFAULT_FONT,
            width=20
        )
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 创建密码输入框
        self.password_frame = tk.Frame(self, bg=COLORS["background"])
        self.password_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.password_label = tk.Label(
            self.password_frame,
            text="密码:",
            font=DEFAULT_FONT,
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        self.password_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.password_entry = tk.Entry(
            self.password_frame,
            font=DEFAULT_FONT,
            width=20,
            show="*"  # 密码显示为星号
        )
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 创建按钮框架
        self.button_frame = tk.Frame(self, bg=COLORS["background"])
        self.button_frame.pack(fill=tk.X)
        
        # 创建登录按钮
        self.login_button = StyledButton(
            self.button_frame,
            text="登录",
            command=self._handle_login,
            primary=True
        )
        self.login_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 创建注册按钮
        self.register_button = StyledButton(
            self.button_frame,
            text="注册",
            command=self._handle_register,
            primary=False
        )
        self.register_button.pack(side=tk.LEFT)
        
        # 绑定回车键
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self._handle_login())
        
        # 设置初始焦点
        self.username_entry.focus()
    
    def _handle_login(self):
        """处理登录事件"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self._show_error("用户名和密码不能为空")
            return
            
        if self.on_login:
            self.on_login(username, password)
    
    def _handle_register(self):
        """处理注册事件"""
        # TODO: 实现注册功能
        pass
    
    def _show_error(self, message):
        """显示错误消息"""
        # 创建错误标签
        if hasattr(self, 'error_label'):
            self.error_label.destroy()
            
        self.error_label = tk.Label(
            self,
            text=message,
            font=DEFAULT_FONT,
            bg=COLORS["background"],
            fg=COLORS["error"]
        )
        self.error_label.pack(pady=(10, 0))
        
        # 3秒后自动清除错误消息
        self.after(3000, lambda: self.error_label.destroy() if hasattr(self, 'error_label') else None)
    
    def clear(self):
        """清空输入框"""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        if hasattr(self, 'error_label'):
            self.error_label.destroy()
 
 