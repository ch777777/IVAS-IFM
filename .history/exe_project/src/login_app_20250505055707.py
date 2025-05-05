"""
多平台视频爬虫测试工具 - 登录界面
"""
import customtkinter as ctk
from PIL import Image, ImageTk
import os
from .components.custom_ctk_widgets import (
    StyledButton, StyledEntry, StyledLabel, FormFrame
)
from .config.custom_theme import COLORS

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 配置窗口
        self.title("IFMCM - 多平台视频爬虫测试工具")
        self.geometry("1280x720")
        self.configure(fg_color="#1A1A2E")
        
        # 创建主容器
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        
        # 创建左侧Logo区域
        self.left_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.left_frame.pack(side="left", fill="both", expand=True)
        
        # Logo标题
        self.logo_label = StyledLabel(
            self.left_frame,
            text="IFMCM",
            font=("Orbitron", 64, "bold"),
            text_color="#FFE082"
        )
        self.logo_label.pack(pady=(100, 20))
        
        # 副标题
        self.subtitle_label = StyledLabel(
            self.left_frame,
            text="多平台视频爬虫测试工具",
            font=("Rajdhani", 32, "bold"),
            text_color="#9C4DFF"
        )
        self.subtitle_label.pack()
        
        # 支持平台列表
        self.platforms_label = StyledLabel(
            self.left_frame,
            text="支持平台: YouTube | TikTok | Bilibili | 微博 | Facebook",
            font=("Rajdhani", 16),
            text_color=COLORS["text_secondary"]
        )
        self.platforms_label.pack(pady=(20, 0))
        
        # 创建右侧登录区域
        self.login_frame = FormFrame(self.main_frame)
        self.login_frame.pack(side="right", padx=50, pady=50)
        
        # 登录标题
        self.login_title = StyledLabel(
            self.login_frame,
            text="登录",
            style="heading"
        )
        self.login_title.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # 登录选项卡
        self.tab_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        self.tab_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        self.cookie_btn = StyledButton(
            self.tab_frame,
            text="Cookie登录",
            style="secondary",
            command=self.cookie_login
        )
        self.cookie_btn.pack(side="left", padx=5)
        
        self.account_btn = StyledButton(
            self.tab_frame,
            text="账号登录",
            style="primary",
            command=self.account_login
        )
        self.account_btn.pack(side="left", padx=5)
        
        # 添加登录表单
        self.username_entry = self.login_frame.add_field(
            "账号:",
            placeholder_text="请输入账号"
        )
        self.password_entry = self.login_frame.add_field(
            "密码:",
            placeholder_text="请输入密码",
            show="*"  # 密码显示为星号
        )
        
        # 添加代理设置
        self.proxy_entry = self.login_frame.add_field(
            "代理:",
            placeholder_text="可选: http://127.0.0.1:7890"
        )
        
        # 添加登录按钮
        self.button_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        self.button_frame.grid(row=5, column=0, columnspan=2, pady=30)
        
        self.login_button = StyledButton(
            self.button_frame,
            text="登录系统",
            command=self.login
        )
        self.login_button.pack(pady=10)
        
        # 添加其他选项
        self.options_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        self.options_frame.grid(row=6, column=0, columnspan=2)
        
        self.selenium_var = ctk.BooleanVar(value=False)
        self.selenium_check = ctk.CTkCheckBox(
            self.options_frame,
            text="使用Selenium",
            variable=self.selenium_var,
            text_color=COLORS["text_secondary"]
        )
        self.selenium_check.pack(pady=5)
        
        # 添加底部链接
        self.bottom_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        self.bottom_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        self.docs_link = StyledLabel(
            self.bottom_frame,
            text="使用文档",
            text_color=COLORS["accent"],
            cursor="hand2"
        )
        self.docs_link.pack(side="left", padx=10)
        
        self.help_link = StyledLabel(
            self.bottom_frame,
            text="问题排查",
            text_color=COLORS["text_secondary"],
            cursor="hand2"
        )
        self.help_link.pack(side="left", padx=10)
    
    def cookie_login(self):
        print("Cookie登录被点击")
    
    def account_login(self):
        print("账号登录被点击")
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        proxy = self.proxy_entry.get()
        use_selenium = self.selenium_var.get()
        print(f"登录信息:")
        print(f"- 账号: {username}")
        print(f"- 密码: {'*' * len(password)}")
        print(f"- 代理: {proxy if proxy else '未设置'}")
        print(f"- Selenium: {'启用' if use_selenium else '禁用'}")

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop() 