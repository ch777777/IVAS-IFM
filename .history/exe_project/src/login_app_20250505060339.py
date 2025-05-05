"""
多功能登录界面
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
        self.title("登录")
        self.geometry("800x600")
        self.configure(fg_color="#151823")  # 深色背景
        
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
            text_color="#7B2BF9"  # 主紫色
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

        # 账号密码登录表单
        self.setup_account_login()
        
        # 手机验证码登录表单
        self.setup_phone_login()
        
        # 微信扫码登录界面
        self.setup_wechat_login()

        # 底部注册链接
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