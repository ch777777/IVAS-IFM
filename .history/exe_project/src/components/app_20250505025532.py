"""
主应用程序类模块
实现应用程序的核心功能和界面
"""
import tkinter as tk
from tkinter import messagebox
import platform
import os

from ..config.settings import APP_TITLE, DEFAULT_WINDOW_SIZE, COLORS, MESSAGES
from ..utils.helpers import center_window, get_os_info
from .ui_components import StyledButton, InfoFrame

class Application:
    """主应用程序类"""
    
    def __init__(self, root):
        """
        初始化应用程序
        
        Args:
            root: Tk根窗口
        """
        self.root = root
        self.setup_window()
        self.create_menu()
        self.create_widgets()
        self.setup_layout()
        
    def setup_window(self):
        """设置窗口属性"""
        self.root.title(APP_TITLE)
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.root.configure(bg=COLORS["background"])
        
        # 设置窗口图标（如果存在）
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
            
        # 窗口居中显示
        self.root.update_idletasks()
        center_window(self.root)
        
    def create_menu(self):
        """创建菜单栏"""
        self.menu_bar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="设置", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        self.menu_bar.add_cascade(label="文件", menu=file_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        self.menu_bar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=self.menu_bar)
        
    def create_widgets(self):
        """创建界面组件"""
        # 标题标签
        self.title_label = tk.Label(
            self.root,
            text=MESSAGES["welcome"],
            font=("Arial", 18, "bold"),
            bg=COLORS["background"],
            fg=COLORS["primary"]
        )
        
        # 系统信息框
        os_info = get_os_info()
        os_info_text = f"系统: {os_info['system']}\n版本: {os_info['version']}\n架构: {os_info['architecture']}"
        self.system_info = InfoFrame(
            self.root,
            "系统信息",
            os_info_text
        )
        
        # 按钮区域
        self.button_frame = tk.Frame(
            self.root,
            bg=COLORS["background"],
            pady=10
        )
        
        # 主按钮
        self.main_button = StyledButton(
            self.button_frame,
            MESSAGES["button_text"],
            command=self.show_message,
            primary=True
        )
        
        # 次要按钮
        self.secondary_button = StyledButton(
            self.button_frame,
            "查看系统信息",
            command=self.show_system_info,
            primary=False
        )
        
    def setup_layout(self):
        """设置组件布局"""
        # 标题标签
        self.title_label.pack(pady=(20, 30))
        
        # 系统信息框
        self.system_info.pack(padx=20, pady=10, fill=tk.X)
        
        # 按钮区域
        self.button_frame.pack(pady=20)
        self.main_button.pack(side=tk.LEFT, padx=10)
        self.secondary_button.pack(side=tk.LEFT, padx=10)
        
    def show_message(self):
        """显示消息对话框"""
        messagebox.showinfo(MESSAGES["message_title"], MESSAGES["button_click"])
        
    def show_system_info(self):
        """显示系统信息对话框"""
        os_info = get_os_info()
        info_text = f"系统: {os_info['system']}\n版本: {os_info['version']}\n架构: {os_info['architecture']}"
        messagebox.showinfo("系统信息", info_text)
        
    def show_settings(self):
        """显示设置对话框"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("300x200")
        settings_window.configure(bg=COLORS["background"])
        
        # 居中显示
        settings_window.update_idletasks()
        center_window(settings_window)
        
        # 设置为模态窗口
        settings_window.grab_set()
        settings_window.transient(self.root)
        
        # 添加设置选项
        tk.Label(
            settings_window,
            text="应用程序设置",
            font=("Arial", 14, "bold"),
            bg=COLORS["background"],
            fg=COLORS["primary"]
        ).pack(pady=10)
        
        tk.Label(
            settings_window,
            text="这里将来可添加实际设置选项",
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).pack(pady=20)
        
        # 确定按钮
        StyledButton(
            settings_window,
            "确定",
            command=settings_window.destroy
        ).pack(pady=10)
        
    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于",
            f"{APP_TITLE}\n\n版本: 1.0.0\n\n这是一个使用Python和Tkinter创建的演示应用程序，\n可以被打包为Windows可执行文件。"
        ) 