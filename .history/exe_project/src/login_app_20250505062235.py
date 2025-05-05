"""
多功能登录界面
"""
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import sys
import socket
import threading
import json
import shutil
from pathlib import Path
import requests
from .components.custom_ctk_widgets import (
    StyledButton, StyledEntry, StyledLabel, FormFrame
)
from .config.custom_theme import COLORS

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 初始化状态变量
        self.is_ready = False
        self.error_messages = []
        
        # 启动自检
        self.show_loading_screen()
        threading.Thread(target=self.system_check, daemon=True).start()
        
    def show_loading_screen(self):
        """显示加载界面"""
        self.loading_window = ctk.CTkToplevel(self)
        self.loading_window.title("系统初始化")
        self.loading_window.geometry("400x300")
        self.loading_window.configure(fg_color="#151823")
        
        # 使加载窗口居中
        self.loading_window.withdraw()
        self.loading_window.update()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 300) // 2
        self.loading_window.geometry(f"400x300+{x}+{y}")
        self.loading_window.deiconify()
        
        # 加载动画和状态显示
        self.loading_label = StyledLabel(
            self.loading_window,
            text="系统初始化中...",
            font=("Orbitron", 18, "bold"),
            text_color="#7B2BF9"
        )
        self.loading_label.pack(pady=20)
        
        self.status_label = StyledLabel(
            self.loading_window,
            text="正在检查系统环境...",
            font=("Rajdhani", 12),
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(pady=10)
        
        # 进度条
        self.progress_bar = ctk.CTkProgressBar(
            self.loading_window,
            width=300,
            height=15,
            corner_radius=10,
            fg_color="#1A1E2D",
            progress_color="#7B2BF9"
        )
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0)
        
    def system_check(self):
        """系统自检流程"""
        checks = [
            (self.check_python_version, "检查Python版本"),
            (self.check_dependencies, "检查依赖包"),
            (self.check_network, "检查网络连接"),
            (self.check_config, "检查配置文件"),
            (self.check_storage, "检查存储空间")
        ]
        
        total_checks = len(checks)
        for i, (check_func, message) in enumerate(checks):
            self.status_label.configure(text=message)
            self.progress_bar.set((i + 1) / total_checks)
            
            try:
                check_func()
            except Exception as e:
                self.error_messages.append(f"{message}失败: {str(e)}")
            
            self.loading_window.update()
            
        if self.error_messages:
            self.show_error_dialog()
        else:
            self.is_ready = True
            self.loading_window.destroy()
            self.initialize_ui()
            
    def check_python_version(self):
        """检查Python版本"""
        if sys.version_info < (3, 7):
            raise Exception("需要Python 3.7或更高版本")
            
    def check_dependencies(self):
        """检查依赖包"""
        required_packages = ['customtkinter', 'pillow', 'requests']
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                raise Exception(f"缺少必要的依赖包: {package}")
                
    def check_network(self):
        """检查网络连接"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
        except OSError:
            raise Exception("网络连接不可用")
            
    def check_config(self):
        """检查配置文件"""
        config_path = Path("config/app_config.json")
        if not config_path.exists():
            self.create_default_config(config_path)
            
    def check_storage(self):
        """检查存储空间"""
        min_space = 100 * 1024 * 1024  # 100MB
        try:
            # 获取当前目录所在磁盘的可用空间
            current_dir = Path.cwd()
            free_space = shutil.disk_usage(current_dir).free
            if free_space < min_space:
                raise Exception("存储空间不足")
        except Exception as e:
            raise Exception(f"存储空间检查失败: {str(e)}")
            
    def create_default_config(self, config_path):
        """创建默认配置文件"""
        default_config = {
            "theme": "dark",
            "language": "zh_CN",
            "auto_login": False,
            "remember_account": False
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
            
    def show_error_dialog(self):
        """显示错误对话框"""
        self.loading_window.destroy()
        
        error_window = ctk.CTkToplevel(self)
        error_window.title("初始化错误")
        error_window.geometry("500x400")
        error_window.configure(fg_color="#151823")
        
        error_label = StyledLabel(
            error_window,
            text="系统初始化过程中发现以下问题：",
            font=("Rajdhani", 14, "bold"),
            text_color=COLORS["error"]
        )
        error_label.pack(pady=20)
        
        error_text = ctk.CTkTextbox(
            error_window,
            width=400,
            height=250,
            fg_color="#1A1E2D",
            text_color=COLORS["text"]
        )
        error_text.pack(pady=10)
        error_text.insert("1.0", "\n".join(self.error_messages))
        error_text.configure(state="disabled")
        
        retry_button = StyledButton(
            error_window,
            text="重试",
            command=self.retry_initialization
        )
        retry_button.pack(pady=20)
        
    def retry_initialization(self):
        """重试初始化"""
        self.error_messages = []
        self.show_loading_screen()
        threading.Thread(target=self.system_check, daemon=True).start()
        
    def initialize_ui(self):
        """初始化主界面"""
        # 配置窗口
        self.title("登录")
        self.geometry("800x600")
        self.configure(fg_color="#151823")
        
        # 创建主容器
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=40
        )
        
        # Logo和标题
        self.title_label = StyledLabel(
            self.main_frame,
            text="IFMCM",
            font=("Orbitron", 36, "bold"),
            text_color="#7B2BF9"
        )
        self.title_label.pack(pady=(0, 20))

        # 创建选项卡视图
        self.tabview = ctk.CTkTabview(
            self.main_frame,
            fg_color="#1A1E2D",
            corner_radius=15,
            segmented_button_fg_color="#1A1E2D",
            segmented_button_selected_color="#7B2BF9",
            segmented_button_unselected_color="#1A1E2D"
        )
        self.tabview.pack(fill="both", expand=True, pady=20)

        # 添加登录选项卡
        self.tab_account = self.tabview.add("账号登录")
        self.tab_phone = self.tabview.add("手机登录")
        self.tab_wechat = self.tabview.add("微信登录")

        # 设置各个登录方式的界面
        self.setup_account_login()
        self.setup_phone_login()
        self.setup_wechat_login()

        # 底部链接
        self.setup_bottom_links()
        
    def setup_bottom_links(self):
        """设置底部链接"""
        self.bottom_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.bottom_frame.pack(fill="x", pady=10)
        
        self.register_link = StyledLabel(
            self.bottom_frame,
            text="还没有账号？立即注册",
            font=("Rajdhani", 12),
            text_color=COLORS["text_secondary"],
            cursor="hand2"
        )
        self.register_link.pack(side="right", padx=10)

        self.help_link = StyledLabel(
            self.bottom_frame,
            text="遇到问题？",
            font=("Rajdhani", 12),
            text_color=COLORS["text_secondary"],
            cursor="hand2"
        )
        self.help_link.pack(side="left", padx=10)

    def setup_account_login(self):
        """设置账号密码登录表单"""
        self.account_frame = FormFrame(
            self.tab_account,
            fg_color="transparent"
        )
        self.account_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.username_entry = self.account_frame.add_field(
            "",
            placeholder_text="账号",
            height=45,
            corner_radius=8
        )
        
        self.password_entry = self.account_frame.add_field(
            "",
            placeholder_text="密码",
            show="●",
            height=45,
            corner_radius=8
        )

        # 记住密码选项
        self.remember_var = ctk.BooleanVar(value=False)
        self.remember_check = ctk.CTkCheckBox(
            self.account_frame,
            text="记住密码",
            variable=self.remember_var,
            text_color=COLORS["text_secondary"],
            font=("Rajdhani", 12),
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            fg_color="#7B2BF9",
            hover_color="#5A1DB8"
        )
        self.remember_check.grid(row=self.account_frame.current_row, column=0, pady=10)
        self.account_frame.current_row += 1

        self.login_button = StyledButton(
            self.account_frame,
            text="登录",
            height=45,
            corner_radius=8
        )
        self.login_button.grid(
            row=self.account_frame.current_row,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=20
        )

    def setup_phone_login(self):
        """设置手机验证码登录表单"""
        self.phone_frame = FormFrame(
            self.tab_phone,
            fg_color="transparent"
        )
        self.phone_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 手机号输入框
        self.phone_entry = self.phone_frame.add_field(
            "",
            placeholder_text="请输入手机号",
            height=45,
            corner_radius=8
        )

        # 验证码输入框和获取验证码按钮
        self.code_frame = ctk.CTkFrame(
            self.phone_frame,
            fg_color="transparent"
        )
        self.code_frame.grid(row=self.phone_frame.current_row, column=0, columnspan=2, sticky="ew", pady=10)
        
        self.code_entry = ctk.CTkEntry(
            self.code_frame,
            placeholder_text="验证码",
            height=45,
            corner_radius=8,
            width=200
        )
        self.code_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.get_code_button = StyledButton(
            self.code_frame,
            text="获取验证码",
            height=45,
            corner_radius=8,
            width=120
        )
        self.get_code_button.pack(side="right")

        self.phone_frame.current_row += 1

        # 登录按钮
        self.phone_login_button = StyledButton(
            self.phone_frame,
            text="登录",
            height=45,
            corner_radius=8
        )
        self.phone_login_button.grid(
            row=self.phone_frame.current_row,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=20
        )

    def setup_wechat_login(self):
        """设置微信扫码登录界面"""
        self.wechat_frame = ctk.CTkFrame(
            self.tab_wechat,
            fg_color="transparent"
        )
        self.wechat_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 二维码显示区域（示例）
        self.qr_frame = ctk.CTkFrame(
            self.wechat_frame,
            width=200,
            height=200,
            fg_color="#1A1E2D",
            corner_radius=15
        )
        self.qr_frame.pack(pady=20)
        
        # 提示文本
        self.qr_label = StyledLabel(
            self.wechat_frame,
            text="请使用微信扫码登录",
            font=("Rajdhani", 14),
            text_color=COLORS["text_secondary"]
        )
        self.qr_label.pack(pady=10)

        # 刷新按钮
        self.refresh_button = StyledButton(
            self.wechat_frame,
            text="刷新二维码",
            height=35,
            corner_radius=8,
            width=120
        )
        self.refresh_button.pack(pady=10)

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop() 