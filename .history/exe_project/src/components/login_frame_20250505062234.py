"""
登录界面组件
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
from src.utils.logger import Logger
from src.managers.auth_manager import AuthManager

class LoginFrame(ttk.Frame):
    """登录界面组件"""
    
    def __init__(
        self,
        parent: ttk.Notebook,
        auth_manager: AuthManager,
        logger: Logger,
        on_login_success: Callable[[str], None]
    ):
        """初始化登录界面
        
        Args:
            parent: 父组件
            auth_manager: 认证管理器
            logger: 日志记录器
            on_login_success: 登录成功回调函数
        """
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.logger = logger
        self.on_login_success = on_login_success
        
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
            text="用户登录",
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
            width=30
        )
        username_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 密码
        password_label = ttk.Label(self, text="密码:")
        password_label.grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(
            self,
            textvariable=self.password_var,
            show="*",
            width=30
        )
        password_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 登录按钮
        login_button = ttk.Button(
            self,
            text="登录",
            command=self._on_login
        )
        login_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # 注册链接
        register_link = ttk.Label(
            self,
            text="没有账号？点击注册",
            cursor="hand2",
            foreground="blue"
        )
        register_link.grid(row=4, column=0, columnspan=2, pady=10)
        register_link.bind("<Button-1>", self._on_register_click)
    
    def _on_login(self):
        """处理登录事件"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码")
            return
        
        success, message, token = self.auth_manager.login(username, password)
        
        if success:
            self.logger.info(f"用户 {username} 登录成功")
            self.on_login_success(username)
        else:
            self.logger.warning(f"用户 {username} 登录失败: {message}")
            messagebox.showerror("登录失败", message)
    
    def _on_register_click(self, event):
        """处理注册链接点击事件"""
        # 创建注册窗口
        register_window = tk.Toplevel(self)
        register_window.title("用户注册")
        register_window.geometry("400x300")
        
        # 创建注册表单
        register_frame = ttk.Frame(register_window, padding="20")
        register_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 用户名
        username_label = ttk.Label(register_frame, text="用户名:")
        username_label.grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        
        username_var = tk.StringVar()
        username_entry = ttk.Entry(
            register_frame,
            textvariable=username_var,
            width=30
        )
        username_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 密码
        password_label = ttk.Label(register_frame, text="密码:")
        password_label.grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        
        password_var = tk.StringVar()
        password_entry = ttk.Entry(
            register_frame,
            textvariable=password_var,
            show="*",
            width=30
        )
        password_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 确认密码
        confirm_label = ttk.Label(register_frame, text="确认密码:")
        confirm_label.grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        
        confirm_var = tk.StringVar()
        confirm_entry = ttk.Entry(
            register_frame,
            textvariable=confirm_var,
            show="*",
            width=30
        )
        confirm_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 邮箱
        email_label = ttk.Label(register_frame, text="邮箱:")
        email_label.grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)
        
        email_var = tk.StringVar()
        email_entry = ttk.Entry(
            register_frame,
            textvariable=email_var,
            width=30
        )
        email_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 注册按钮
        register_button = ttk.Button(
            register_frame,
            text="注册",
            command=lambda: self._on_register(
                register_window,
                username_var.get().strip(),
                password_var.get(),
                confirm_var.get(),
                email_var.get().strip()
            )
        )
        register_button.grid(row=4, column=0, columnspan=2, pady=20)
        
        # 配置网格权重
        register_frame.columnconfigure(1, weight=1)
        register_window.columnconfigure(0, weight=1)
        register_window.rowconfigure(0, weight=1)
    
    def _on_register(
        self,
        window: tk.Toplevel,
        username: str,
        password: str,
        confirm: str,
        email: str
    ):
        """处理注册事件
        
        Args:
            window: 注册窗口
            username: 用户名
            password: 密码
            confirm: 确认密码
            email: 邮箱
        """
        if not username or not password or not confirm or not email:
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        if password != confirm:
            messagebox.showerror("错误", "两次输入的密码不一致")
            return
        
        success, message = self.auth_manager.register(username, password, email)
        
        if success:
            self.logger.info(f"用户 {username} 注册成功")
            messagebox.showinfo("成功", "注册成功，请登录")
            window.destroy()
        else:
            self.logger.warning(f"用户 {username} 注册失败: {message}")
            messagebox.showerror("注册失败", message) 