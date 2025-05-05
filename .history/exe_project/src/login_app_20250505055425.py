"""
电竞风格登录界面
"""
import customtkinter as ctk
from PIL import Image, ImageTk
import os
from .components.custom_ctk_widgets import (
    StyledButton, StyledEntry, StyledLabel, FormFrame
)

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 配置窗口
        self.title("5ENL - 登录")
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
            text="5ENL",
            font=("Orbitron", 64, "bold"),
            text_color="#FFE082"
        )
        self.logo_label.pack(pady=(100, 20))
        
        # 副标题
        self.subtitle_label = StyledLabel(
            self.left_frame,
            text="全民联赛",
            font=("Rajdhani", 32, "bold"),
            text_color="#9C4DFF"
        )
        self.subtitle_label.pack()
        
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
        
        self.steam_btn = StyledButton(
            self.tab_frame,
            text="Steam登录",
            style="secondary",
            command=self.steam_login
        )
        self.steam_btn.pack(side="left", padx=5)
        
        self.account_btn = StyledButton(
            self.tab_frame,
            text="账号登录",
            style="primary",
            command=self.account_login
        )
        self.account_btn.pack(side="left", padx=5)
        
        # 添加登录表单
        self.username_entry = self.login_frame.add_field(
            "手机号:",
            placeholder_text="请输入手机号"
        )
        self.password_entry = self.login_frame.add_field(
            "验证码:",
            placeholder_text="请输入验证码"
        )
        
        # 添加登录按钮
        self.button_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        self.button_frame.grid(row=4, column=0, columnspan=2, pady=30)
        
        self.login_button = StyledButton(
            self.button_frame,
            text="立即登录",
            command=self.login
        )
        self.login_button.pack(pady=10)
        
        # 添加其他登录方式
        self.other_login_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        self.other_login_frame.grid(row=5, column=0, columnspan=2)
        
        self.wechat_label = StyledLabel(
            self.other_login_frame,
            text="微信扫码登录",
            style="small"
        )
        self.wechat_label.pack()
        
        # 添加底部链接
        self.bottom_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        self.bottom_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        self.register_link = StyledLabel(
            self.bottom_frame,
            text="立即注册",
            text_color=COLORS["accent"],
            cursor="hand2"
        )
        self.register_link.pack(side="left", padx=10)
        
        self.help_link = StyledLabel(
            self.bottom_frame,
            text="帮助",
            text_color=COLORS["text_secondary"],
            cursor="hand2"
        )
        self.help_link.pack(side="left", padx=10)
    
    def steam_login(self):
        print("Steam登录被点击")
    
    def account_login(self):
        print("账号登录被点击")
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        print(f"登录: {username}, {password}")

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop() 