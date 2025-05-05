"""
主应用程序类
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional
from src.utils.logger import Logger
from src.managers.auth_manager import AuthManager
from src.managers.profile_manager import ProfileManager
from src.managers.role_manager import RoleManager
from src.managers.password_reset_manager import PasswordResetManager
from src.components.login_frame import LoginFrame
from src.components.profile_frame import ProfileFrame
from src.components.role_management_frame import RoleManagementFrame
from src.components.password_reset_frame import PasswordResetFrame

class Application:
    """主应用程序类"""
    
    def __init__(
        self,
        root: tk.Tk,
        auth_manager: AuthManager,
        profile_manager: ProfileManager,
        role_manager: RoleManager,
        password_reset_manager: PasswordResetManager,
        logger: Logger
    ):
        """初始化应用程序
        
        Args:
            root: 主窗口
            auth_manager: 认证管理器
            profile_manager: 资料管理器
            role_manager: 角色管理器
            password_reset_manager: 密码重置管理器
            logger: 日志记录器
        """
        self.root = root
        self.auth_manager = auth_manager
        self.profile_manager = profile_manager
        self.role_manager = role_manager
        self.password_reset_manager = password_reset_manager
        self.logger = logger
        
        # 当前登录用户
        self.current_user: Optional[str] = None
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建选项卡控件
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建各个选项卡
        self.login_frame = LoginFrame(
            self.notebook,
            self.auth_manager,
            self.logger,
            self.on_login_success
        )
        self.profile_frame = ProfileFrame(
            self.notebook,
            self.profile_manager,
            self.role_manager,
            self.logger
        )
        self.role_management_frame = RoleManagementFrame(
            self.notebook,
            self.role_manager,
            self.logger
        )
        self.password_reset_frame = PasswordResetFrame(
            self.notebook,
            self.password_reset_manager,
            self.logger
        )
        
        # 添加选项卡
        self.notebook.add(self.login_frame, text="登录")
        self.notebook.add(self.profile_frame, text="个人资料")
        self.notebook.add(self.role_management_frame, text="角色管理")
        self.notebook.add(self.password_reset_frame, text="密码重置")
        
        # 初始时禁用其他选项卡
        self.notebook.tab(1, state="disabled")
        self.notebook.tab(2, state="disabled")
        self.notebook.tab(3, state="disabled")
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
    
    def on_login_success(self, username: str):
        """登录成功回调
        
        Args:
            username: 用户名
        """
        self.current_user = username
        self.logger.info(f"用户 {username} 登录成功")
        
        # 启用其他选项卡
        self.notebook.tab(1, state="normal")
        self.notebook.tab(2, state="normal")
        self.notebook.tab(3, state="normal")
        
        # 切换到个人资料选项卡
        self.notebook.select(1)
        
        # 更新各个选项卡的用户信息
        self.profile_frame.set_current_user(username)
        self.role_management_frame.set_current_user(username)
        self.password_reset_frame.set_current_user(username)
    
    def start(self):
        """启动应用程序"""
        self.logger.info("应用程序启动")
        self.root.mainloop() 