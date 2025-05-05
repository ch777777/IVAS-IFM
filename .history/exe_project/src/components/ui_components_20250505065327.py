"""
UI组件模块
包含应用程序中使用的自定义UI组件
"""
import os
import logging
import tkinter as tk
from tkinter import ttk
from ..config.settings import COLORS, DEFAULT_FONT
from typing import Dict, List, Any, Callable, Optional

logger = logging.getLogger(__name__)

class StyledButton(ttk.Button):
    """自定义风格的按钮组件"""
    
    def __init__(self, parent, text, command=None, **kwargs):
        """
        创建一个自定义风格的按钮
        
        Args:
            parent: 父组件
            text: 按钮文本
            command: 点击事件回调函数
            **kwargs: 其他Button参数
        """
        super().__init__(
            parent,
            text=text,
            command=command,
            style="StyledButton.TButton",
            **kwargs
        )
        # Configure the style if not already configured
        style = ttk.Style()
        if "StyledButton.TButton" not in style.layout():
            style.configure(
                "StyledButton.TButton",
                background="#4a86e8",
                foreground="white",
                padding=(10, 5),
                font=("Arial", 10, "bold")
            )
            style.map(
                "StyledButton.TButton",
                background=[("active", "#3a76d8")],
                foreground=[("active", "white")]
            )
        
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
    
    def __init__(self, master, on_login=None, on_register=None, **kwargs):
        """
        创建登录界面
        
        Args:
            master: 父组件
            on_login: 登录回调函数，接收(username, password)参数
            on_register: 注册回调函数，接收(username, password)参数
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
        self.on_register = on_register
        
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
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self._show_error("用户名和密码不能为空")
            return
            
        if len(password) < 6:
            self._show_error("密码长度不能少于6个字符")
            return
            
        if self.on_register:
            self.on_register(username, password)
    
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

class SearchBar(ttk.Entry):
    """A search bar with placeholder text."""
    
    def __init__(self, parent, variable, placeholder="Search...", **kwargs):
        """Initialize a search bar with placeholder text."""
        self.placeholder = placeholder
        self.variable = variable
        self.showing_placeholder = True
        
        super().__init__(
            parent,
            textvariable=self.variable,
            style="SearchBar.TEntry",
            **kwargs
        )
        
        # Configure the style
        style = ttk.Style()
        style.configure("SearchBar.TEntry", padding=(5, 5))
        
        # Add placeholder behavior
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        
        # Initialize with placeholder
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Show the placeholder text."""
        self.variable.set(self.placeholder)
        self.showing_placeholder = True
        # Apply "placeholder" styling (gray text)
        self.configure(foreground="gray")
    
    def _on_focus_in(self, event):
        """Handle focus in event to clear placeholder."""
        if self.showing_placeholder:
            self.variable.set("")
            self.showing_placeholder = False
            # Apply normal styling
            self.configure(foreground="black")
    
    def _on_focus_out(self, event):
        """Handle focus out event to show placeholder if empty."""
        if not self.variable.get():
            self._show_placeholder()

class StatusBar(ttk.Frame):
    """A status bar for displaying application status messages."""
    
    def __init__(self, parent, textvariable=None, **kwargs):
        """Initialize a status bar."""
        super().__init__(parent, style="StatusBar.TFrame", **kwargs)
        
        # Configure style
        style = ttk.Style()
        style.configure("StatusBar.TFrame", background="#f3f3f3")
        
        # Create status label
        self.status_var = textvariable or tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            style="StatusBar.TLabel",
            padding=(5, 2)
        )
        
        style.configure("StatusBar.TLabel", background="#f3f3f3", foreground="#333333")
        
        # Layout
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

class VideoResultFrame(ttk.Frame):
    """A frame for displaying video search results."""
    
    def __init__(self, parent, video_data, platform, download_callback=None, **kwargs):
        """Initialize a video result frame."""
        super().__init__(parent, style="VideoResult.TFrame", **kwargs)
        
        # Store data
        self.video_data = video_data
        self.platform = platform
        self.download_callback = download_callback
        
        # Configure style
        style = ttk.Style()
        style.configure("VideoResult.TFrame", padding=10)
        
        # Create widgets
        self._create_widgets()
        self._layout_widgets()
    
    def _create_widgets(self):
        """Create the widgets for the video result frame."""
        # Title
        self.title_label = ttk.Label(
            self,
            text=self.video_data.get('title', 'Unknown Title'),
            font=("Arial", 11, "bold"),
            wraplength=500
        )
        
        # Platform label
        self.platform_label = ttk.Label(
            self,
            text=f"Platform: {self.platform.capitalize()}",
            font=("Arial", 9)
        )
        
        # Video info
        info_text = (
            f"Author: {self.video_data.get('author', 'Unknown')}\n"
            f"Duration: {self.video_data.get('duration', 'Unknown')}\n"
            f"Views: {self.video_data.get('views', 'Unknown')}\n"
            f"Published: {self.video_data.get('published', 'Unknown')}"
        )
        self.info_label = ttk.Label(
            self,
            text=info_text,
            font=("Arial", 9),
            wraplength=500
        )
        
        # Description
        description = self.video_data.get('description', '')
        if description:
            self.description_label = ttk.Label(
                self,
                text=description[:150] + ("..." if len(description) > 150 else ""),
                font=("Arial", 9),
                wraplength=500
            )
        else:
            self.description_label = None
        
        # Download button
        self.download_button = StyledButton(
            self,
            text="Download",
            command=self._on_download
        )
    
    def _layout_widgets(self):
        """Layout the widgets in the frame."""
        # Use grid for better control
        self.title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.platform_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.info_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        if self.description_label:
            self.description_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
            self.download_button.grid(row=4, column=0, sticky=tk.W)
        else:
            self.download_button.grid(row=3, column=0, sticky=tk.W)
    
    def _on_download(self):
        """Handle download button click."""
        if self.download_callback:
            self.download_callback()

class PlatformSelector(ttk.LabelFrame):
    """A frame for selecting video platforms to search."""
    
    def __init__(self, parent, platforms, variables, **kwargs):
        """Initialize a platform selector."""
        super().__init__(
            parent,
            text="Platforms",
            style="PlatformSelector.TLabelFrame",
            **kwargs
        )
        
        # Store data
        self.platforms = platforms
        self.variables = variables
        
        # Configure style
        style = ttk.Style()
        style.configure("PlatformSelector.TLabelFrame", padding=5)
        
        # Create checkbuttons
        self.checkbuttons = {}
        for platform in self.platforms:
            self.checkbuttons[platform] = ttk.Checkbutton(
                self,
                text=platform.capitalize(),
                variable=self.variables[platform],
                style="Platform.TCheckbutton"
            )
            self.checkbuttons[platform].pack(anchor=tk.W, padx=5, pady=2)

class ProgressIndicator(ttk.Frame):
    """A progress indicator for long-running operations."""
    
    def __init__(self, parent, **kwargs):
        """Initialize a progress indicator."""
        super().__init__(parent, **kwargs)
        
        # Create progress bar
        self.progress_bar = ttk.Progressbar(
            self,
            mode='indeterminate',
            length=200
        )
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        # Create status label
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            anchor=tk.CENTER
        )
        self.status_label.pack(fill=tk.X, padx=5)
        
        # Hide by default
        self.pack_forget()
    
    def start(self, status_text="Processing..."):
        """Start the progress indicator."""
        self.status_var.set(status_text)
        self.progress_bar.start()
        self.pack(fill=tk.X, padx=10, pady=5)
    
    def stop(self):
        """Stop the progress indicator."""
        self.progress_bar.stop()
        self.pack_forget()
        self.status_var.set("")
 
 