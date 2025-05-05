"""
角色管理界面模块
实现角色的查看、创建、编辑和删除功能
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ..utils.role_manager import RoleManager
from .ui_components import StyledButton, InfoFrame
from ..config.settings import COLORS, DEFAULT_FONT

class RoleManagementFrame(tk.Frame):
    """角色管理界面"""
    
    def __init__(self, master, on_save=None, **kwargs):
        """
        创建角色管理界面
        
        Args:
            master: 父组件
            on_save: 保存回调函数
            **kwargs: 其他Frame参数
        """
        super().__init__(master, bg=COLORS["background"], **kwargs)
        
        self.on_save = on_save
        self.role_manager = RoleManager()
        
        self._create_widgets()
        self._load_roles()
        
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        self.title_label = tk.Label(
            self,
            text="角色管理",
            font=(DEFAULT_FONT[0], DEFAULT_FONT[1] + 4, "bold"),
            bg=COLORS["background"],
            fg=COLORS["primary"]
        )
        self.title_label.pack(pady=(0, 20))
        
        # 角色列表
        self.list_frame = tk.Frame(self, bg=COLORS["background"])
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # 创建Treeview
        self.tree = ttk.Treeview(
            self.list_frame,
            columns=("name", "permissions", "description"),
            show="headings",
            selectmode="browse"
        )
        
        # 设置列
        self.tree.heading("name", text="角色名称")
        self.tree.heading("permissions", text="权限")
        self.tree.heading("description", text="描述")
        
        self.tree.column("name", width=100)
        self.tree.column("permissions", width=200)
        self.tree.column("description", width=300)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self._handle_select)
        
        # 按钮区域
        self.button_frame = tk.Frame(self, bg=COLORS["background"])
        self.button_frame.pack(pady=20)
        
        # 新建按钮
        self.new_button = StyledButton(
            self.button_frame,
            "新建角色",
            command=self._handle_new,
            primary=True
        )
        self.new_button.pack(side=tk.LEFT, padx=10)
        
        # 编辑按钮
        self.edit_button = StyledButton(
            self.button_frame,
            "编辑角色",
            command=self._handle_edit,
            primary=True
        )
        self.edit_button.pack(side=tk.LEFT, padx=10)
        
        # 删除按钮
        self.delete_button = StyledButton(
            self.button_frame,
            "删除角色",
            command=self._handle_delete,
            primary=False
        )
        self.delete_button.pack(side=tk.LEFT, padx=10)
        
        # 保存按钮
        self.save_button = StyledButton(
            self.button_frame,
            "保存更改",
            command=self._handle_save,
            primary=True
        )
        self.save_button.pack(side=tk.LEFT, padx=10)
        
    def _load_roles(self):
        """加载角色列表"""
        # 清空现有项
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 加载角色
        roles = self.role_manager.get_all_roles()
        for role_id, role in roles.items():
            permissions = ", ".join(role["permissions"])
            self.tree.insert("", "end", values=(
                role["name"],
                permissions,
                role["description"]
            ), tags=(role_id,))
            
    def _handle_select(self, event):
        """处理选择事件"""
        selection = self.tree.selection()
        if selection:
            self.edit_button.config(state="normal")
            self.delete_button.config(state="normal")
        else:
            self.edit_button.config(state="disabled")
            self.delete_button.config(state="disabled")
            
    def _handle_new(self):
        """处理新建角色事件"""
        dialog = RoleDialog(self, "新建角色")
        if dialog.result:
            role_id, name, permissions, description = dialog.result
            if self.role_manager.create_role(role_id, name, permissions, description):
                self._load_roles()
                messagebox.showinfo("成功", "角色创建成功")
            else:
                messagebox.showerror("错误", "角色创建失败")
                
    def _handle_edit(self):
        """处理编辑角色事件"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        role_id = self.tree.item(item, "tags")[0]
        role = self.role_manager.get_role(role_id)
        
        dialog = RoleDialog(self, "编辑角色", role)
        if dialog.result:
            _, name, permissions, description = dialog.result
            if self.role_manager.update_role(
                role_id,
                name=name,
                permissions=permissions,
                description=description
            ):
                self._load_roles()
                messagebox.showinfo("成功", "角色更新成功")
            else:
                messagebox.showerror("错误", "角色更新失败")
                
    def _handle_delete(self):
        """处理删除角色事件"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        role_id = self.tree.item(item, "tags")[0]
        
        if messagebox.askyesno("确认", "确定要删除这个角色吗？"):
            if self.role_manager.delete_role(role_id):
                self._load_roles()
                messagebox.showinfo("成功", "角色删除成功")
            else:
                messagebox.showerror("错误", "角色删除失败")
                
    def _handle_save(self):
        """处理保存事件"""
        if self.on_save:
            self.on_save()

class RoleDialog(tk.Toplevel):
    """角色编辑对话框"""
    
    def __init__(self, parent, title, role=None):
        """
        创建角色编辑对话框
        
        Args:
            parent: 父组件
            title: 对话框标题
            role: 要编辑的角色（如果有）
        """
        super().__init__(parent)
        
        self.title(title)
        self.result = None
        
        # 设置模态
        self.transient(parent)
        self.grab_set()
        
        # 创建界面
        self._create_widgets(role)
        
        # 居中显示
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # 等待窗口关闭
        self.wait_window()
        
    def _create_widgets(self, role):
        """创建界面组件"""
        # 表单框架
        form_frame = tk.Frame(self, bg=COLORS["background"], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 角色ID
        tk.Label(
            form_frame,
            text="角色ID:",
            font=DEFAULT_FONT,
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).grid(row=0, column=0, sticky="e", pady=5)
        
        self.role_id_var = tk.StringVar()
        self.role_id_entry = tk.Entry(
            form_frame,
            textvariable=self.role_id_var,
            font=DEFAULT_FONT,
            width=30
        )
        self.role_id_entry.grid(row=0, column=1, sticky="w", pady=5)
        
        # 角色名称
        tk.Label(
            form_frame,
            text="角色名称:",
            font=DEFAULT_FONT,
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).grid(row=1, column=0, sticky="e", pady=5)
        
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(
            form_frame,
            textvariable=self.name_var,
            font=DEFAULT_FONT,
            width=30
        )
        self.name_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # 权限列表
        tk.Label(
            form_frame,
            text="权限:",
            font=DEFAULT_FONT,
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).grid(row=2, column=0, sticky="ne", pady=5)
        
        self.permissions_text = tk.Text(
            form_frame,
            font=DEFAULT_FONT,
            width=30,
            height=5
        )
        self.permissions_text.grid(row=2, column=1, sticky="w", pady=5)
        
        # 描述
        tk.Label(
            form_frame,
            text="描述:",
            font=DEFAULT_FONT,
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).grid(row=3, column=0, sticky="ne", pady=5)
        
        self.description_text = tk.Text(
            form_frame,
            font=DEFAULT_FONT,
            width=30,
            height=3
        )
        self.description_text.grid(row=3, column=1, sticky="w", pady=5)
        
        # 按钮区域
        button_frame = tk.Frame(form_frame, bg=COLORS["background"])
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # 确定按钮
        StyledButton(
            button_frame,
            "确定",
            command=self._handle_ok,
            primary=True
        ).pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        StyledButton(
            button_frame,
            "取消",
            command=self._handle_cancel,
            primary=False
        ).pack(side=tk.LEFT, padx=10)
        
        # 如果是编辑模式，填充现有数据
        if role:
            self.role_id_var.set(role.get("id", ""))
            self.role_id_entry.config(state="readonly")
            self.name_var.set(role.get("name", ""))
            self.permissions_text.insert("1.0", "\n".join(role.get("permissions", [])))
            self.description_text.insert("1.0", role.get("description", ""))
            
    def _handle_ok(self):
        """处理确定事件"""
        role_id = self.role_id_var.get().strip()
        name = self.name_var.get().strip()
        permissions = [p.strip() for p in self.permissions_text.get("1.0", "end-1c").split("\n") if p.strip()]
        description = self.description_text.get("1.0", "end-1c").strip()
        
        if not role_id:
            messagebox.showerror("错误", "请输入角色ID")
            return
            
        if not name:
            messagebox.showerror("错误", "请输入角色名称")
            return
            
        if not permissions:
            messagebox.showerror("错误", "请输入至少一个权限")
            return
            
        self.result = (role_id, name, permissions, description)
        self.destroy()
        
    def _handle_cancel(self):
        """处理取消事件"""
        self.destroy() 