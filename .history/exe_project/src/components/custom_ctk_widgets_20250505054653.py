"""
自定义CustomTkinter组件
"""
import customtkinter as ctk
from ..config.custom_theme import (
    COLORS, FONTS, BUTTON_STYLES, 
    ENTRY_STYLE, FRAME_STYLE, LAYOUT
)

class StyledButton(ctk.CTkButton):
    """自定义样式按钮"""
    
    def __init__(self, master, text, command=None, style="primary", **kwargs):
        """初始化按钮
        
        Args:
            master: 父组件
            text: 按钮文本
            command: 点击回调函数
            style: 按钮样式 ("primary" 或 "secondary")
        """
        button_style = BUTTON_STYLES[style].copy()
        button_style.update(kwargs)
        
        super().__init__(
            master,
            text=text,
            command=command,
            **button_style
        )

class StyledEntry(ctk.CTkEntry):
    """自定义样式输入框"""
    
    def __init__(self, master, **kwargs):
        """初始化输入框
        
        Args:
            master: 父组件
        """
        entry_style = ENTRY_STYLE.copy()
        entry_style.update(kwargs)
        
        super().__init__(
            master,
            **entry_style
        )

class StyledLabel(ctk.CTkLabel):
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
            text_color=COLORS["text"],
            **kwargs
        )

class FormFrame(ctk.CTkFrame):
    """表单框架"""
    
    def __init__(self, master, **kwargs):
        """初始化表单框架
        
        Args:
            master: 父组件
        """
        frame_style = FRAME_STYLE.copy()
        frame_style.update(kwargs)
        
        super().__init__(master, **frame_style)
        
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
        label.grid(row=self.current_row, column=0, sticky="e", 
                  padx=(0, LAYOUT["spacing"]), pady=LAYOUT["spacing"])
        
        # 创建组件
        if readonly and widget_class == StyledEntry:
            widget_kwargs["state"] = "readonly"
        widget = widget_class(self, **widget_kwargs)
        widget.grid(row=self.current_row, column=1, sticky="ew", 
                   pady=LAYOUT["spacing"])
        
        self.current_row += 1
        return widget 