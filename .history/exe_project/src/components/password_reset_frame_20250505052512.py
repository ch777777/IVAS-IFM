"""
密码重置界面模块
实现密码重置功能
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ..utils.password_reset import PasswordResetManager
from ..utils.profile import ProfileManager
from .ui_components import StyledButton
from ..config.settings import COLORS, DEFAULT_FONT

class PasswordResetFrame(tk.Frame):
    """密码重置界面"""
    
    def __init__(self, master, username: str, on_complete=None, **kwargs):
        """
        创建密码重置界面
        
        Args:
            master: 父组件
            username: 用户名
            on_complete: 完成回调函数
            **kwargs: 其他Frame参数
        """
        super().__init__(master, bg=COLORS["background"], **kwargs)
        
        self.username = username
        self.on_complete = on_complete
        self.reset_manager = PasswordResetManager()
        self.profile_manager = ProfileManager()
        
        self._create_widgets()
        
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        self.title_label = tk.Label(
            self,
            text="密码重置",
            font=(DEFAULT_FONT[0], DEFAULT_FONT[1] + 4, "bold"),
            bg=COLORS["background"],
            fg=COLORS["primary"]
        )
        self.title_label.pack(pady=(0, 20))
        
        # 步骤说明
        self.step_label = tk.Label(
            self,
            text="步骤1: 验证身份",
            font=(DEFAULT_FONT[0], DEFAULT_FONT[1] + 2),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        self.step_label.pack(pady=(0, 10))
        
        # 表单框架
        self.form_frame = tk.Frame(self, bg=COLORS["background"])
        self.form_frame.pack(fill=tk.X, padx=20)
        
        # 电子邮件
        self.email_var = tk.StringVar()
        self._create_form_row("电子邮件:", self.email_var)
        
        # 验证码
        self.code_var = tk.StringVar()
        self._create_form_row("验证码:", self.code_var)
        
        # 新密码
        self.password_var = tk.StringVar()
        self._create_form_row("新密码:", self.password_var, show="*")
        
        # 确认密码
        self.confirm_var = tk.StringVar()
        self._create_form_row("确认密码:", self.confirm_var, show="*")
        
        # 按钮区域
        self.button_frame = tk.Frame(self, bg=COLORS["background"])
        self.button_frame.pack(pady=20)
        
        # 获取验证码按钮
        self.get_code_button = StyledButton(
            self.button_frame,
            "获取验证码",
            command=self._handle_get_code,
            primary=True
        )
        self.get_code_button.pack(side=tk.LEFT, padx=10)
        
        # 重置按钮
        self.reset_button = StyledButton(
            self.button_frame,
            "重置密码",
            command=self._handle_reset,
            primary=True
        )
        self.reset_button.pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        self.cancel_button = StyledButton(
            self.button_frame,
            "取消",
            command=self._handle_cancel,
            primary=False
        )
        self.cancel_button.pack(side=tk.LEFT, padx=10)
        
    def _create_form_row(self, label: str, variable: tk.StringVar, show: str = None):
        """
        创建表单行
        
        Args:
            label: 标签文本
            variable: 输入变量
            show: 密码显示字符
        """
        frame = tk.Frame(self.form_frame, bg=COLORS["background"])
        frame.pack(fill=tk.X, pady=5)
        
        label_widget = tk.Label(
            frame,
            text=label,
            font=DEFAULT_FONT,
            bg=COLORS["background"],
            fg=COLORS["text"],
            width=10,
            anchor="e"
        )
        label_widget.pack(side=tk.LEFT, padx=(0, 10))
        
        entry = tk.Entry(
            frame,
            textvariable=variable,
            font=DEFAULT_FONT,
            width=30,
            show=show
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    def _handle_get_code(self):
        """处理获取验证码事件"""
        email = self.email_var.get().strip()
        if not email:
            messagebox.showerror("错误", "请输入电子邮件地址")
            return
            
        # 验证电子邮件是否匹配
        profile = self.profile_manager.get_profile(self.username)
        if not profile or profile.get("email") != email:
            messagebox.showerror("错误", "电子邮件地址与账号不匹配")
            return
            
        # 请求重置码
        success, result = self.reset_manager.request_reset(self.username, email)
        if success:
            messagebox.showinfo("成功", f"验证码已发送到您的邮箱: {result}")
            self.step_label.config(text="步骤2: 输入验证码和新密码")
        else:
            messagebox.showerror("错误", result)
            
    def _handle_reset(self):
        """处理重置密码事件"""
        code = self.code_var.get().strip()
        password = self.password_var.get()
        confirm = self.confirm_var.get()
        
        if not code:
            messagebox.showerror("错误", "请输入验证码")
            return
            
        if not password:
            messagebox.showerror("错误", "请输入新密码")
            return
            
        if password != confirm:
            messagebox.showerror("错误", "两次输入的密码不一致")
            return
            
        if len(password) < 6:
            messagebox.showerror("错误", "密码长度必须至少为6个字符")
            return
            
        # 重置密码
        success, message = self.reset_manager.reset_password(
            self.username,
            code,
            password
        )
        
        if success:
            messagebox.showinfo("成功", message)
            if self.on_complete:
                self.on_complete()
        else:
            messagebox.showerror("错误", message)
            
    def _handle_cancel(self):
        """处理取消事件"""
        if self.on_complete:
            self.on_complete() 