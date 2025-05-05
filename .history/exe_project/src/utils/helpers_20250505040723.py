"""
工具函数模块
提供应用程序中重复使用的通用工具函数
"""
import tkinter as tk
import platform
import os
import sys

def center_window(window):
    """
    将窗口居中显示在屏幕上
    
    Args:
        window: Tkinter窗口实例
    """
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")

def apply_theme(widget, bg_color, fg_color=None):
    """
    应用主题颜色到控件
    
    Args:
        widget: Tkinter控件
        bg_color: 背景颜色
        fg_color: 前景颜色（可选）
    """
    widget.configure(bg=bg_color)
    if fg_color:
        if hasattr(widget, 'configure') and 'fg' in widget.config():
            widget.configure(fg=fg_color)

def get_os_info():
    """
    获取操作系统信息
    
    Returns:
        dict: 包含操作系统名称和版本的字典
    """
    return {
        "system": platform.system(),
        "version": platform.version(),
        "architecture": platform.architecture()[0]
    }

def get_resource_path(relative_path):
    """
    获取资源的绝对路径，适用于PyInstaller打包后的环境
    
    Args:
        relative_path: 资源的相对路径
        
    Returns:
        str: 资源的绝对路径
    """
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    except Exception:
        # 不是PyInstaller环境，使用当前目录
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path) 