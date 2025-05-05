"""
密码重置界面组件
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from src.utils.logger import Logger
from src.managers.password_reset_manager import PasswordResetManager

class PasswordResetFrame(ttk.Frame):
    """密码重置界面组件"""
    
    def __init__(
        self,
        parent: ttk.Notebook,
        password_reset_manager: PasswordResetManager,
        logger: Logger
    ):
        """初始化密码重置界面
        
        Args:
            parent: 父组件
            password_reset_manager: 密码重置管理器
            logger: 日志记录器
        """
        super().__init__(parent)
        self.password_reset_manager = password_reset_manager
        self.logger = logger
        
        # 当前用户
        self.current_user: Optional[str] = None
        
        # 创建界面元素
        self._create_widgets()
        
        # 配置网格权重
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
    
    def _create_widgets(self):
        """创建界面元素"""
        # 标题
        title_label = ttk.Label(
            self,
            text="密码重置",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # 用户名
        username_label = ttk.Label(self, text="用户名:")
        username_label.grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(
            self,
            textvariable=self.username_var,
            state="readonly",
            width=30
        )
        username_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 重置令牌
        token_label = ttk.Label(self, text="重置令牌:")
        token_label.grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.token_var = tk.StringVar()
        token_entry = ttk.Entry(
            self,
            textvariable=self.token_var,
            width=30
        )
        token_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 新密码
        new_password_label = ttk.Label(self, text="新密码:")
        new_password_label.grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.new_password_var = tk.StringVar()
        new_password_entry = ttk.Entry(
            self,
            textvariable=self.new_password_var,
            show="*",
            width=30
        )
        new_password_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 确认新密码
        confirm_password_label = ttk.Label(self, text="确认新密码:")
        confirm_password_label.grid(row=4, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.confirm_password_var = tk.StringVar()
        confirm_password_entry = ttk.Entry(
            self,
            textvariable=self.confirm_password_var,
            show="*",
            width=30
        )
        confirm_password_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 生成令牌按钮
        generate_token_button = ttk.Button(
            self,
            text="生成重置令牌",
            command=self._on_generate_token
        )
        generate_token_button.grid(row=5, column=0, pady=20)
        
        # 重置密码按钮
        reset_password_button = ttk.Button(
            self,
            text="重置密码",
            command=self._on_reset_password
        )
        reset_password_button.grid(row=5, column=1, pady=20)
    
    def set_current_user(self, username: str):
        """设置当前用户
        
        Args:
            username: 用户名
        """
        self.current_user = username
        self.username_var.set(username)
    
    def _on_generate_token(self):
        """处理生成令牌事件"""
        if not self.current_user:
            messagebox.showerror("错误", "请先登录")
            return
        
        success, message, token = self.password_reset_manager.generate_reset_token(self.current_user)
        
        if success:
            self.logger.info(f"为用户 {self.current_user} 生成重置令牌成功")
            self.token_var.set(token)
            messagebox.showinfo("成功", "重置令牌生成成功")
        else:
            self.logger.warning(f"为用户 {self.current_user} 生成重置令牌失败: {message}")
            messagebox.showerror("生成失败", message)
    
    def _on_reset_password(self):
        """处理重置密码事件"""
        if not self.current_user:
            messagebox.showerror("错误", "请先登录")
            return
        
        token = self.token_var.get().strip()
        new_password = self.new_password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        if not token:
            messagebox.showerror("错误", "请输入重置令牌")
            return
        
        if not new_password:
            messagebox.showerror("错误", "请输入新密码")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("错误", "两次输入的密码不一致")
            return
        
        success, message = self.password_reset_manager.reset_password(token, new_password)
        
        if success:
            self.logger.info(f"用户 {self.current_user} 重置密码成功")
            messagebox.showinfo("成功", "密码重置成功")
            # 清空表单
            self.token_var.set("")
            self.new_password_var.set("")
            self.confirm_password_var.set("")
        else:
            self.logger.warning(f"用户 {self.current_user} 重置密码失败: {message}")
            messagebox.showerror("重置失败", message) 