"""
个人资料界面组件
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from src.utils.logger import Logger
from src.managers.profile_manager import ProfileManager
from src.managers.role_manager import RoleManager

class ProfileFrame(ttk.Frame):
    """个人资料界面组件"""
    
    def __init__(
        self,
        parent: ttk.Notebook,
        profile_manager: ProfileManager,
        role_manager: RoleManager,
        logger: Logger
    ):
        """初始化个人资料界面
        
        Args:
            parent: 父组件
            profile_manager: 资料管理器
            role_manager: 角色管理器
            logger: 日志记录器
        """
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.role_manager = role_manager
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
            text="个人资料",
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
        
        # 昵称
        nickname_label = ttk.Label(self, text="昵称:")
        nickname_label.grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.nickname_var = tk.StringVar()
        nickname_entry = ttk.Entry(
            self,
            textvariable=self.nickname_var,
            width=30
        )
        nickname_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 邮箱
        email_label = ttk.Label(self, text="邮箱:")
        email_label.grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(
            self,
            textvariable=self.email_var,
            width=30
        )
        email_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 电话
        phone_label = ttk.Label(self, text="电话:")
        phone_label.grid(row=4, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.phone_var = tk.StringVar()
        phone_entry = ttk.Entry(
            self,
            textvariable=self.phone_var,
            width=30
        )
        phone_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 角色
        roles_label = ttk.Label(self, text="角色:")
        roles_label.grid(row=5, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.roles_var = tk.StringVar()
        roles_entry = ttk.Entry(
            self,
            textvariable=self.roles_var,
            state="readonly",
            width=30
        )
        roles_entry.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 保存按钮
        save_button = ttk.Button(
            self,
            text="保存",
            command=self._on_save
        )
        save_button.grid(row=6, column=0, columnspan=2, pady=20)
    
    def set_current_user(self, username: str):
        """设置当前用户
        
        Args:
            username: 用户名
        """
        self.current_user = username
        self.username_var.set(username)
        
        # 加载用户资料
        success, message, profile = self.profile_manager.get_profile(username)
        if success and profile:
            self.nickname_var.set(profile.get("nickname", ""))
            self.email_var.set(profile.get("email", ""))
            self.phone_var.set(profile.get("phone", ""))
        
        # 加载用户角色
        success, message, roles = self.role_manager.get_user_roles(username)
        if success and roles:
            # 获取角色数据
            success, message, role_data = self.role_manager.get_roles()
            if success and role_data:
                role_names = []
                for role_id in roles:
                    if role_id in role_data:
                        role_names.append(role_data[role_id]["name"])
                self.roles_var.set(", ".join(role_names))
    
    def _on_save(self):
        """处理保存事件"""
        if not self.current_user:
            messagebox.showerror("错误", "请先登录")
            return
        
        # 收集资料数据
        profile_data = {
            "nickname": self.nickname_var.get().strip(),
            "email": self.email_var.get().strip(),
            "phone": self.phone_var.get().strip()
        }
        
        success, message = self.profile_manager.update_profile(self.current_user, profile_data)
        
        if success:
            self.logger.info(f"用户 {self.current_user} 更新资料成功")
            messagebox.showinfo("成功", "资料更新成功")
        else:
            self.logger.warning(f"用户 {self.current_user} 更新资料失败: {message}")
            messagebox.showerror("更新失败", message) 