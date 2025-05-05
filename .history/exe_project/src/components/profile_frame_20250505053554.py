"""
用户资料管理界面模块
实现用户资料的查看和编辑功能
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ..utils.profile import ProfileManager
from ..utils.role_manager import RoleManager
from .ui_components import StyledButton, InfoFrame
from ..config.settings import COLORS, DEFAULT_FONT

class ProfileFrame(tk.Frame):
    """用户资料管理界面"""
    
    def __init__(self, master, username: str, on_save=None, **kwargs):
        """
        创建用户资料管理界面
        
        Args:
            master: 父组件
            username: 用户名
            on_save: 保存回调函数
            **kwargs: 其他Frame参数
        """
        super().__init__(master, bg=COLORS["background"], **kwargs)
        
        self.username = username
        self.on_save = on_save
        self.profile_manager = ProfileManager()
        self.role_manager = RoleManager()
        
        self._create_widgets()
        self._load_profile()
        
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        self.title_label = tk.Label(
            self,
            text="用户资料",
            font=(DEFAULT_FONT[0], DEFAULT_FONT[1] + 4, "bold"),
            bg=COLORS["background"],
            fg=COLORS["primary"]
        )
        self.title_label.pack(pady=(0, 20))
        
        # 资料表单
        self.form_frame = tk.Frame(self, bg=COLORS["background"])
        self.form_frame.pack(fill=tk.X, padx=20)
        
        # 用户名
        self._create_form_row("用户名:", self.username, readonly=True)
        
        # 电子邮件
        self.email_var = tk.StringVar()
        self._create_form_row("电子邮件:", self.email_var)
        
        # 电话号码
        self.phone_var = tk.StringVar()
        self._create_form_row("电话号码:", self.phone_var)
        
        # 角色
        self.role_var = tk.StringVar()
        self._create_role_selector()
        
        # 按钮区域
        self.button_frame = tk.Frame(self, bg=COLORS["background"])
        self.button_frame.pack(pady=20)
        
        # 保存按钮
        self.save_button = StyledButton(
            self.button_frame,
            "保存修改",
            command=self._handle_save,
            primary=True
        )
        self.save_button.pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        self.cancel_button = StyledButton(
            self.button_frame,
            "取消",
            command=self._handle_cancel,
            primary=False
        )
        self.cancel_button.pack(side=tk.LEFT, padx=10)
        
    def _create_form_row(self, label: str, variable: tk.StringVar, readonly: bool = False):
        """
        创建表单行
        
        Args:
            label: 标签文本
            variable: 输入变量
            readonly: 是否只读
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
            state="readonly" if readonly else "normal"
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    def _create_role_selector(self):
        """创建角色选择器"""
        frame = tk.Frame(self.form_frame, bg=COLORS["background"])
        frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            frame,
            text="角色:",
            font=DEFAULT_FONT,
            bg=COLORS["background"],
            fg=COLORS["text"],
            width=10,
            anchor="e"
        )
        label.pack(side=tk.LEFT, padx=(0, 10))
        
        # 获取所有角色
        roles = self.role_manager.get_all_roles()
        role_names = [role["name"] for role in roles.values()]
        
        self.role_combo = ttk.Combobox(
            frame,
            textvariable=self.role_var,
            values=role_names,
            state="readonly",
            width=28
        )
        self.role_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    def _load_profile(self):
        """加载用户资料"""
        profile = self.profile_manager.get_profile(self.username)
        if profile:
            self.email_var.set(profile.get("email", ""))
            self.phone_var.set(profile.get("phone", ""))
            
            # 设置角色
            role_id = profile.get("role", "user")
            role = self.role_manager.get_role(role_id)
            if role:
                self.role_var.set(role["name"])
                
    def _handle_save(self):
        """处理保存事件"""
        # 获取角色ID
        role_name = self.role_var.get()
        role_id = None
        for rid, role in self.role_manager.get_all_roles().items():
            if role["name"] == role_name:
                role_id = rid
                break
                
        if not role_id:
            messagebox.showerror("错误", "无效的角色选择")
            return
            
        # 更新资料
        success = self.profile_manager.update_profile(
            self.username,
            email=self.email_var.get(),
            phone=self.phone_var.get(),
            role=role_id
        )
        
        if success:
            messagebox.showinfo("成功", "资料更新成功")
            if self.on_save:
                self.on_save()
        else:
            messagebox.showerror("错误", "资料更新失败")
            
    def _handle_cancel(self):
        """处理取消事件"""
        if self.on_save:
            self.on_save() 