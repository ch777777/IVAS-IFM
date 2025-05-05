"""
应用程序主类
"""
import tkinter as tk
from tkinter import ttk
from src.components.login_frame import LoginFrame
from src.components.profile_frame import ProfileFrame
from src.components.role_management_frame import RoleManagementFrame
from src.components.password_reset_frame import PasswordResetFrame

class Application:
    """应用程序主类"""
    
    def __init__(self, root, auth_manager, profile_manager, role_manager, password_reset_manager, logger):
        """初始化应用程序
        
        Args:
            root: Tkinter根窗口
            auth_manager: 认证管理器
            profile_manager: 用户资料管理器
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
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建各个功能页面
        self.login_frame = LoginFrame(self.notebook, self.auth_manager, self.logger)
        self.profile_frame = ProfileFrame(self.notebook, self.profile_manager, self.logger)
        self.role_frame = RoleManagementFrame(self.notebook, self.role_manager, self.logger)
        self.password_reset_frame = PasswordResetFrame(self.notebook, self.password_reset_manager, self.logger)
        
        # 添加标签页
        self.notebook.add(self.login_frame, text="登录")
        self.notebook.add(self.profile_frame, text="个人资料")
        self.notebook.add(self.role_frame, text="角色管理")
        self.notebook.add(self.password_reset_frame, text="密码重置")
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
    
    def start(self):
        """启动应用程序"""
        self.logger.info("应用程序已启动")
        self.root.mainloop() 