"""
角色管理界面组件
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from src.utils.logger import Logger
from src.managers.role_manager import RoleManager

class RoleManagementFrame(ttk.Frame):
    """角色管理界面组件"""
    
    def __init__(
        self,
        parent: ttk.Notebook,
        role_manager: RoleManager,
        logger: Logger
    ):
        """初始化角色管理界面
        
        Args:
            parent: 父组件
            role_manager: 角色管理器
            logger: 日志记录器
        """
        super().__init__(parent)
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
            text="角色管理",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # 角色列表
        roles_frame = ttk.LabelFrame(self, text="角色列表", padding="10")
        roles_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # 创建树形视图
        columns = ("角色ID", "角色名称", "权限")
        self.roles_tree = ttk.Treeview(
            roles_frame,
            columns=columns,
            show="headings",
            height=10
        )
        
        # 设置列标题
        for col in columns:
            self.roles_tree.heading(col, text=col)
            self.roles_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            roles_frame,
            orient=tk.VERTICAL,
            command=self.roles_tree.yview
        )
        self.roles_tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置树形视图和滚动条
        self.roles_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置角色列表框架的网格权重
        roles_frame.columnconfigure(0, weight=1)
        roles_frame.rowconfigure(0, weight=1)
        
        # 创建角色按钮
        create_button = ttk.Button(
            self,
            text="创建角色",
            command=self._on_create_role
        )
        create_button.grid(row=2, column=0, pady=10)
        
        # 删除角色按钮
        delete_button = ttk.Button(
            self,
            text="删除角色",
            command=self._on_delete_role
        )
        delete_button.grid(row=2, column=1, pady=10)
        
        # 用户角色列表
        user_roles_frame = ttk.LabelFrame(self, text="用户角色", padding="10")
        user_roles_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # 创建树形视图
        columns = ("用户名", "角色")
        self.user_roles_tree = ttk.Treeview(
            user_roles_frame,
            columns=columns,
            show="headings",
            height=10
        )
        
        # 设置列标题
        for col in columns:
            self.user_roles_tree.heading(col, text=col)
            self.user_roles_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            user_roles_frame,
            orient=tk.VERTICAL,
            command=self.user_roles_tree.yview
        )
        self.user_roles_tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置树形视图和滚动条
        self.user_roles_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置用户角色列表框架的网格权重
        user_roles_frame.columnconfigure(0, weight=1)
        user_roles_frame.rowconfigure(0, weight=1)
        
        # 分配角色按钮
        assign_button = ttk.Button(
            self,
            text="分配角色",
            command=self._on_assign_role
        )
        assign_button.grid(row=4, column=0, pady=10)
        
        # 移除角色按钮
        remove_button = ttk.Button(
            self,
            text="移除角色",
            command=self._on_remove_role
        )
        remove_button.grid(row=4, column=1, pady=10)
    
    def set_current_user(self, username: str):
        """设置当前用户
        
        Args:
            username: 用户名
        """
        self.current_user = username
        self._refresh_roles()
        self._refresh_user_roles()
    
    def _refresh_roles(self):
        """刷新角色列表"""
        # 清空现有数据
        for item in self.roles_tree.get_children():
            self.roles_tree.delete(item)
        
        # 获取角色数据
        success, message, roles = self.role_manager.get_roles()
        if success and roles:
            for role_id, role_data in roles.items():
                self.roles_tree.insert(
                    "",
                    tk.END,
                    values=(
                        role_id,
                        role_data["name"],
                        ", ".join(role_data["permissions"])
                    )
                )
    
    def _refresh_user_roles(self):
        """刷新用户角色列表"""
        # 清空现有数据
        for item in self.user_roles_tree.get_children():
            self.user_roles_tree.delete(item)
        
        # 获取角色数据
        success, message, roles = self.role_manager.get_roles()
        if not success or not roles:
            return
        
        # 获取用户角色
        success, message, user_roles = self.role_manager.get_user_roles(self.current_user)
        if success and user_roles:
            for role_id in user_roles:
                if role_id in roles:
                    self.user_roles_tree.insert(
                        "",
                        tk.END,
                        values=(
                            self.current_user,
                            roles[role_id]["name"]
                        )
                    )
    
    def _on_create_role(self):
        """处理创建角色事件"""
        # 创建角色窗口
        create_window = tk.Toplevel(self)
        create_window.title("创建角色")
        create_window.geometry("400x300")
        
        # 创建表单
        form_frame = ttk.Frame(create_window, padding="20")
        form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 角色ID
        role_id_label = ttk.Label(form_frame, text="角色ID:")
        role_id_label.grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        
        role_id_var = tk.StringVar()
        role_id_entry = ttk.Entry(
            form_frame,
            textvariable=role_id_var,
            width=30
        )
        role_id_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 角色名称
        name_label = ttk.Label(form_frame, text="角色名称:")
        name_label.grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        
        name_var = tk.StringVar()
        name_entry = ttk.Entry(
            form_frame,
            textvariable=name_var,
            width=30
        )
        name_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 权限列表
        permissions_label = ttk.Label(form_frame, text="权限:")
        permissions_label.grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        
        permissions_var = tk.StringVar()
        permissions_entry = ttk.Entry(
            form_frame,
            textvariable=permissions_var,
            width=30
        )
        permissions_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 创建按钮
        create_button = ttk.Button(
            form_frame,
            text="创建",
            command=lambda: self._on_create_role_submit(
                create_window,
                role_id_var.get().strip(),
                name_var.get().strip(),
                [p.strip() for p in permissions_var.get().split(",")]
            )
        )
        create_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # 配置网格权重
        form_frame.columnconfigure(1, weight=1)
        create_window.columnconfigure(0, weight=1)
        create_window.rowconfigure(0, weight=1)
    
    def _on_create_role_submit(
        self,
        window: tk.Toplevel,
        role_id: str,
        name: str,
        permissions: List[str]
    ):
        """处理创建角色提交事件
        
        Args:
            window: 创建角色窗口
            role_id: 角色ID
            name: 角色名称
            permissions: 权限列表
        """
        if not role_id or not name or not permissions:
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        success, message = self.role_manager.create_role(role_id, name, permissions)
        
        if success:
            self.logger.info(f"角色 {role_id} 创建成功")
            messagebox.showinfo("成功", "角色创建成功")
            window.destroy()
            self._refresh_roles()
        else:
            self.logger.warning(f"角色 {role_id} 创建失败: {message}")
            messagebox.showerror("创建失败", message)
    
    def _on_delete_role(self):
        """处理删除角色事件"""
        # 获取选中的角色
        selected = self.roles_tree.selection()
        if not selected:
            messagebox.showerror("错误", "请选择要删除的角色")
            return
        
        # 获取角色ID
        role_id = self.roles_tree.item(selected[0])["values"][0]
        
        # 确认删除
        if not messagebox.askyesno("确认", f"确定要删除角色 {role_id} 吗？"):
            return
        
        success, message = self.role_manager.delete_role(role_id)
        
        if success:
            self.logger.info(f"角色 {role_id} 删除成功")
            messagebox.showinfo("成功", "角色删除成功")
            self._refresh_roles()
            self._refresh_user_roles()
        else:
            self.logger.warning(f"角色 {role_id} 删除失败: {message}")
            messagebox.showerror("删除失败", message)
    
    def _on_assign_role(self):
        """处理分配角色事件"""
        # 获取选中的角色
        selected = self.roles_tree.selection()
        if not selected:
            messagebox.showerror("错误", "请选择要分配的角色")
            return
        
        # 获取角色ID
        role_id = self.roles_tree.item(selected[0])["values"][0]
        
        success, message = self.role_manager.assign_role(self.current_user, role_id)
        
        if success:
            self.logger.info(f"为用户 {self.current_user} 分配角色 {role_id} 成功")
            messagebox.showinfo("成功", "角色分配成功")
            self._refresh_user_roles()
        else:
            self.logger.warning(f"为用户 {self.current_user} 分配角色 {role_id} 失败: {message}")
            messagebox.showerror("分配失败", message)
    
    def _on_remove_role(self):
        """处理移除角色事件"""
        # 获取选中的用户角色
        selected = self.user_roles_tree.selection()
        if not selected:
            messagebox.showerror("错误", "请选择要移除的角色")
            return
        
        # 获取角色名称
        role_name = self.user_roles_tree.item(selected[0])["values"][1]
        
        # 获取角色ID
        success, message, roles = self.role_manager.get_roles()
        if not success or not roles:
            messagebox.showerror("错误", "获取角色数据失败")
            return
        
        role_id = None
        for rid, data in roles.items():
            if data["name"] == role_name:
                role_id = rid
                break
        
        if not role_id:
            messagebox.showerror("错误", "找不到对应的角色ID")
            return
        
        success, message = self.role_manager.remove_role(self.current_user, role_id)
        
        if success:
            self.logger.info(f"为用户 {self.current_user} 移除角色 {role_id} 成功")
            messagebox.showinfo("成功", "角色移除成功")
            self._refresh_user_roles()
        else:
            self.logger.warning(f"为用户 {self.current_user} 移除角色 {role_id} 失败: {message}")
            messagebox.showerror("移除失败", message) 