"""
简洁优雅的登录界面
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
        self.geometry("400x600")
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
        self.title_label.pack(pady=(0, 10))
        
        # 登录表单区域
        self.form_frame = FormFrame(
            self.main_frame,
            fg_color="#1A1E2D",  # 稍亮的背景色
            corner_radius=15
        )
        self.form_frame.pack(
            fill="both",
            expand=True,
            pady=20
        )
        
        # 账号输入框
        self.username_entry = self.form_frame.add_field(
            "",  # 不显示标签文本
            placeholder_text="账号",
            height=45,
            corner_radius=8
        )
        
        # 密码输入框
        self.password_entry = self.form_frame.add_field(
            "",  # 不显示标签文本
            placeholder_text="密码",
            show="●",  # 使用点替代星号
            height=45,
            corner_radius=8
        )
        
        # 代理设置
        self.proxy_entry = self.form_frame.add_field(
            "",  # 不显示标签文本
            placeholder_text="代理服务器 (可选)",
            height=45,
            corner_radius=8
        )
        
        # Selenium选项
        self.selenium_frame = ctk.CTkFrame(
            self.form_frame,
            fg_color="transparent"
        )
        self.selenium_frame.grid(
            row=self.form_frame.current_row,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=10
        )
        
        self.selenium_var = ctk.BooleanVar(value=False)
        self.selenium_check = ctk.CTkCheckBox(
            self.selenium_frame,
            text="使用 Selenium",
            variable=self.selenium_var,
            text_color=COLORS["text_secondary"],
            font=("Rajdhani", 12),
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            fg_color="#7B2BF9",
            hover_color="#5A1DB8"
        )
        self.selenium_check.pack(pady=5)
        
        self.form_frame.current_row += 1
        
        # 登录按钮
        self.login_button = StyledButton(
            self.form_frame,
            text="登录系统",
            height=45,
            corner_radius=8
        )
        self.login_button.grid(
            row=self.form_frame.current_row,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=20
        )
        
        self.form_frame.current_row += 1
        
        # 底部链接
        self.bottom_frame = ctk.CTkFrame(
            self.form_frame,
            fg_color="transparent"
        )
        self.bottom_frame.grid(
            row=self.form_frame.current_row,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=10
        )
        
        self.docs_link = StyledLabel(
            self.bottom_frame,
            text="使用文档",
            font=("Rajdhani", 12),
            text_color=COLORS["text_secondary"],
            cursor="hand2"
        )
        self.docs_link.pack(side="left", padx=10)
        
        self.help_link = StyledLabel(
            self.bottom_frame,
            text="问题排查",
            font=("Rajdhani", 12),
            text_color=COLORS["text_secondary"],
            cursor="hand2"
        )
        self.help_link.pack(side="right", padx=10)

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop() 