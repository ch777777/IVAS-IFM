"""
角色管理器类
"""
import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class RoleManager:
    """角色管理器类"""
    
    def __init__(self):
        """初始化角色管理器"""
        self.roles_file = os.path.join("data", "roles", "roles.json")
        self.user_roles_file = os.path.join("data", "roles", "user_roles.json")
        
        # 确保角色数据目录存在
        os.makedirs(os.path.dirname(self.roles_file), exist_ok=True)
        
        # 如果角色文件不存在，创建默认角色
        if not os.path.exists(self.roles_file):
            default_roles = {
                "admin": {
                    "name": "管理员",
                    "permissions": ["all"],
                    "created_at": datetime.now().isoformat()
                },
                "user": {
                    "name": "普通用户",
                    "permissions": ["read", "write"],
                    "created_at": datetime.now().isoformat()
                }
            }
            with open(self.roles_file, "w", encoding="utf-8") as f:
                json.dump(default_roles, f, ensure_ascii=False, indent=2)
        
        # 如果用户角色文件不存在，创建空文件
        if not os.path.exists(self.user_roles_file):
            with open(self.user_roles_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
    
    def get_roles(self) -> Tuple[bool, str, Optional[Dict]]:
        """获取所有角色
        
        Returns:
            Tuple[bool, str, Optional[Dict]]: (是否成功, 消息, 角色数据)
        """
        try:
            with open(self.roles_file, "r", encoding="utf-8") as f:
                roles = json.load(f)
            return True, "获取成功", roles
        except Exception as e:
            return False, f"获取角色失败: {str(e)}", None
    
    def create_role(self, role_id: str, name: str, permissions: List[str]) -> Tuple[bool, str]:
        """创建新角色
        
        Args:
            role_id: 角色ID
            name: 角色名称
            permissions: 权限列表
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 读取现有角色
            with open(self.roles_file, "r", encoding="utf-8") as f:
                roles = json.load(f)
            
            # 检查角色ID是否已存在
            if role_id in roles:
                return False, "角色ID已存在"
            
            # 创建新角色
            roles[role_id] = {
                "name": name,
                "permissions": permissions,
                "created_at": datetime.now().isoformat()
            }
            
            # 保存角色数据
            with open(self.roles_file, "w", encoding="utf-8") as f:
                json.dump(roles, f, ensure_ascii=False, indent=2)
            
            return True, "角色创建成功"
            
        except Exception as e:
            return False, f"创建角色失败: {str(e)}"
    
    def update_role(self, role_id: str, name: str, permissions: List[str]) -> Tuple[bool, str]:
        """更新角色
        
        Args:
            role_id: 角色ID
            name: 角色名称
            permissions: 权限列表
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 读取现有角色
            with open(self.roles_file, "r", encoding="utf-8") as f:
                roles = json.load(f)
            
            # 检查角色是否存在
            if role_id not in roles:
                return False, "角色不存在"
            
            # 更新角色
            roles[role_id].update({
                "name": name,
                "permissions": permissions
            })
            
            # 保存角色数据
            with open(self.roles_file, "w", encoding="utf-8") as f:
                json.dump(roles, f, ensure_ascii=False, indent=2)
            
            return True, "角色更新成功"
            
        except Exception as e:
            return False, f"更新角色失败: {str(e)}"
    
    def delete_role(self, role_id: str) -> Tuple[bool, str]:
        """删除角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 读取现有角色
            with open(self.roles_file, "r", encoding="utf-8") as f:
                roles = json.load(f)
            
            # 检查角色是否存在
            if role_id not in roles:
                return False, "角色不存在"
            
            # 删除角色
            del roles[role_id]
            
            # 保存角色数据
            with open(self.roles_file, "w", encoding="utf-8") as f:
                json.dump(roles, f, ensure_ascii=False, indent=2)
            
            # 从用户角色中移除该角色
            with open(self.user_roles_file, "r", encoding="utf-8") as f:
                user_roles = json.load(f)
            
            for username in user_roles:
                if role_id in user_roles[username]:
                    user_roles[username].remove(role_id)
            
            with open(self.user_roles_file, "w", encoding="utf-8") as f:
                json.dump(user_roles, f, ensure_ascii=False, indent=2)
            
            return True, "角色删除成功"
            
        except Exception as e:
            return False, f"删除角色失败: {str(e)}"
    
    def assign_role(self, username: str, role_id: str) -> Tuple[bool, str]:
        """为用户分配角色
        
        Args:
            username: 用户名
            role_id: 角色ID
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 检查角色是否存在
            with open(self.roles_file, "r", encoding="utf-8") as f:
                roles = json.load(f)
            
            if role_id not in roles:
                return False, "角色不存在"
            
            # 读取用户角色
            with open(self.user_roles_file, "r", encoding="utf-8") as f:
                user_roles = json.load(f)
            
            # 为用户添加角色
            if username not in user_roles:
                user_roles[username] = []
            
            if role_id not in user_roles[username]:
                user_roles[username].append(role_id)
            
            # 保存用户角色数据
            with open(self.user_roles_file, "w", encoding="utf-8") as f:
                json.dump(user_roles, f, ensure_ascii=False, indent=2)
            
            return True, "角色分配成功"
            
        except Exception as e:
            return False, f"分配角色失败: {str(e)}"
    
    def remove_role(self, username: str, role_id: str) -> Tuple[bool, str]:
        """移除用户的角色
        
        Args:
            username: 用户名
            role_id: 角色ID
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 读取用户角色
            with open(self.user_roles_file, "r", encoding="utf-8") as f:
                user_roles = json.load(f)
            
            # 检查用户是否有该角色
            if username not in user_roles or role_id not in user_roles[username]:
                return False, "用户没有该角色"
            
            # 移除角色
            user_roles[username].remove(role_id)
            
            # 保存用户角色数据
            with open(self.user_roles_file, "w", encoding="utf-8") as f:
                json.dump(user_roles, f, ensure_ascii=False, indent=2)
            
            return True, "角色移除成功"
            
        except Exception as e:
            return False, f"移除角色失败: {str(e)}"
    
    def get_user_roles(self, username: str) -> Tuple[bool, str, Optional[List[str]]]:
        """获取用户的角色列表
        
        Args:
            username: 用户名
            
        Returns:
            Tuple[bool, str, Optional[List[str]]]: (是否成功, 消息, 角色列表)
        """
        try:
            # 读取用户角色
            with open(self.user_roles_file, "r", encoding="utf-8") as f:
                user_roles = json.load(f)
            
            # 获取用户角色
            roles = user_roles.get(username, [])
            
            return True, "获取成功", roles
            
        except Exception as e:
            return False, f"获取用户角色失败: {str(e)}", None
    
    def check_permission(self, username: str, permission: str) -> Tuple[bool, str]:
        """检查用户是否有指定权限
        
        Args:
            username: 用户名
            permission: 权限名称
            
        Returns:
            Tuple[bool, str]: (是否有权限, 消息)
        """
        try:
            # 获取用户角色
            success, message, roles = self.get_user_roles(username)
            if not success:
                return False, message
            
            # 读取角色数据
            with open(self.roles_file, "r", encoding="utf-8") as f:
                role_data = json.load(f)
            
            # 检查每个角色的权限
            for role_id in roles:
                if role_id in role_data:
                    role = role_data[role_id]
                    if "all" in role["permissions"] or permission in role["permissions"]:
                        return True, "有权限"
            
            return False, "没有权限"
            
        except Exception as e:
            return False, f"检查权限失败: {str(e)}" 