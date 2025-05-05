"""
角色权限管理模块
实现基于角色的访问控制功能
"""
import os
import json
from typing import Dict, Any, List, Set
from datetime import datetime

class RoleManager:
    """角色权限管理器"""
    
    def __init__(self):
        """初始化角色管理器"""
        self.roles_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "roles.json")
        self._ensure_roles_file()
        
    def _ensure_roles_file(self):
        """确保角色文件存在"""
        os.makedirs(os.path.dirname(self.roles_file), exist_ok=True)
        if not os.path.exists(self.roles_file):
            default_roles = {
                "roles": {
                    "admin": {
                        "name": "管理员",
                        "permissions": ["*"],
                        "description": "系统管理员，拥有所有权限"
                    },
                    "user": {
                        "name": "普通用户",
                        "permissions": [
                            "view_videos",
                            "search_videos",
                            "download_videos",
                            "view_profile",
                            "edit_profile"
                        ],
                        "description": "普通用户，拥有基本操作权限"
                    },
                    "guest": {
                        "name": "访客",
                        "permissions": [
                            "view_videos",
                            "search_videos"
                        ],
                        "description": "访客用户，仅拥有查看权限"
                    }
                }
            }
            with open(self.roles_file, "w", encoding="utf-8") as f:
                json.dump(default_roles, f, ensure_ascii=False, indent=2)
    
    def _load_roles(self) -> Dict[str, Any]:
        """加载角色数据"""
        with open(self.roles_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save_roles(self, data: Dict[str, Any]):
        """保存角色数据"""
        with open(self.roles_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_role(self, role_id: str) -> Dict[str, Any]:
        """
        获取角色信息
        
        Args:
            role_id: 角色ID
            
        Returns:
            Dict[str, Any]: 角色信息
        """
        data = self._load_roles()
        return data["roles"].get(role_id, {})
    
    def get_all_roles(self) -> Dict[str, Any]:
        """
        获取所有角色信息
        
        Returns:
            Dict[str, Any]: 所有角色信息
        """
        data = self._load_roles()
        return data["roles"]
    
    def create_role(self, role_id: str, name: str, permissions: List[str], description: str = "") -> bool:
        """
        创建新角色
        
        Args:
            role_id: 角色ID
            name: 角色名称
            permissions: 权限列表
            description: 角色描述
            
        Returns:
            bool: 是否创建成功
        """
        data = self._load_roles()
        
        if role_id in data["roles"]:
            return False
            
        data["roles"][role_id] = {
            "name": name,
            "permissions": permissions,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        self._save_roles(data)
        return True
    
    def update_role(self, role_id: str, **kwargs) -> bool:
        """
        更新角色信息
        
        Args:
            role_id: 角色ID
            **kwargs: 要更新的字段
            
        Returns:
            bool: 是否更新成功
        """
        data = self._load_roles()
        
        if role_id not in data["roles"]:
            return False
            
        role = data["roles"][role_id]
        for key, value in kwargs.items():
            if key in role:
                role[key] = value
                
        role["updated_at"] = datetime.now().isoformat()
        self._save_roles(data)
        return True
    
    def delete_role(self, role_id: str) -> bool:
        """
        删除角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            bool: 是否删除成功
        """
        data = self._load_roles()
        
        if role_id not in data["roles"]:
            return False
            
        del data["roles"][role_id]
        self._save_roles(data)
        return True
    
    def check_permission(self, role_id: str, permission: str) -> bool:
        """
        检查角色是否拥有指定权限
        
        Args:
            role_id: 角色ID
            permission: 权限名称
            
        Returns:
            bool: 是否拥有权限
        """
        role = self.get_role(role_id)
        if not role:
            return False
            
        permissions = role.get("permissions", [])
        return "*" in permissions or permission in permissions
    
    def get_role_permissions(self, role_id: str) -> Set[str]:
        """
        获取角色的所有权限
        
        Args:
            role_id: 角色ID
            
        Returns:
            Set[str]: 权限集合
        """
        role = self.get_role(role_id)
        if not role:
            return set()
            
        permissions = role.get("permissions", [])
        return set(permissions) 