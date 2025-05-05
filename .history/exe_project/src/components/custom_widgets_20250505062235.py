"""
自定义UI组件
"""
import tkinter as tk
from tkinter import ttk
from ..config.theme import COLORS, FONTS, STYLES, LAYOUT

class StyledButton(tk.Button):
    """自定义样式按钮"""
    
    def __init__(self, master, text, command=None, style="primary", **kwargs):
        """初始化按钮
        
        Args:
            master: 父组件
            text: 按钮文本
            command: 点击回调函数
            style: 按钮样式 ("primary" 或 "secondary")
        """
        button_style = STYLES["button"] if style == "primary" else STYLES["button_secondary"]
        super().__init__(
            master,
            text=text,
            command=command,
            **button_style,
            **kwargs
        )
        
        # 绑定鼠标事件
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_enter(self, e):
        """鼠标进入事件"""
        self.config(background=COLORS["primary_dark"])
        
    def _on_leave(self, e):
        """鼠标离开事件"""
        self.config(background=COLORS["primary"])

class StyledEntry(ttk.Entry):
    """自定义样式输入框"""
    
    def __init__(self, master, **kwargs):
        """初始化输入框
        
        Args:
            master: 父组件
        """
        super().__init__(
            master,
            style="Custom.TEntry",
            **kwargs
        )
        
        # 创建自定义样式
        style = ttk.Style()
        style.configure(
            "Custom.TEntry",
            fieldbackground=STYLES["entry"]["background"],
            foreground=STYLES["entry"]["foreground"],
            font=STYLES["entry"]["font"]
        )

class StyledLabel(ttk.Label):
    """自定义样式标签"""
    
    def __init__(self, master, text, style="normal", **kwargs):
        """初始化标签
        
        Args:
            master: 父组件
            text: 标签文本
            style: 标签样式 ("normal", "heading", "subheading")
        """
        font = FONTS["body"]
        if style == "heading":
            font = FONTS["heading"]
        elif style == "subheading":
            font = FONTS["subheading"]
            
        super().__init__(
            master,
            text=text,
            font=font,
            foreground=COLORS["text"],
            background=COLORS["background"],
            **kwargs
        )

class FormFrame(ttk.Frame):
    """表单框架"""
    
    def __init__(self, master, padding=LAYOUT["padding"], **kwargs):
        """初始化表单框架
        
        Args:
            master: 父组件
            padding: 内边距
        """
        super().__init__(master, padding=padding, **kwargs)
        
        # 配置网格权重
        self.columnconfigure(1, weight=1)
        
        self.current_row = 0
    
    def add_field(self, label_text, widget_class=StyledEntry, readonly=False, **widget_kwargs):
        """添加表单字段
        
        Args:
            label_text: 标签文本
            widget_class: 组件类
            readonly: 是否只读
            **widget_kwargs: 组件参数
        
        Returns:
            创建的组件
        """
        # 创建标签
        label = StyledLabel(self, text=label_text)
        label.grid(row=self.current_row, column=0, sticky="e", padx=(0, 10), pady=5)
        
        # 创建组件
        if readonly and widget_class == StyledEntry:
            widget_kwargs["state"] = "readonly"
        widget = widget_class(self, **widget_kwargs)
        widget.grid(row=self.current_row, column=1, sticky="ew", pady=5)
        
        self.current_row += 1
        return widget 