"""
用户资料管理模块
实现用户资料的存储、更新和查询功能
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

class ProfileManager:
    """用户资料管理器"""
    
    def __init__(self):
        """初始化资料管理器"""
        self.profiles_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "profiles.json")
        self._ensure_profiles_file()
        
    def _ensure_profiles_file(self):
        """确保资料文件存在"""
        os.makedirs(os.path.dirname(self.profiles_file), exist_ok=True)
        if not os.path.exists(self.profiles_file):
            with open(self.profiles_file, "w", encoding="utf-8") as f:
                json.dump({"profiles": {}}, f, ensure_ascii=False, indent=2)
    
    def _load_profiles(self) -> Dict[str, Any]:
        """加载用户资料"""
        with open(self.profiles_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save_profiles(self, data: Dict[str, Any]):
        """保存用户资料"""
        with open(self.profiles_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_profile(self, username: str, email: str = "", phone: str = "", role: str = "user") -> bool:
        """
        创建用户资料
        
        Args:
            username: 用户名
            email: 电子邮件
            phone: 电话号码
            role: 用户角色
            
        Returns:
            bool: 是否创建成功
        """
        data = self._load_profiles()
        
        if username in data["profiles"]:
            return False
            
        data["profiles"][username] = {
            "email": email,
            "phone": phone,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        self._save_profiles(data)
        return True
    
    def get_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        获取用户资料
        
        Args:
            username: 用户名
            
        Returns:
            Optional[Dict[str, Any]]: 用户资料，如果不存在则返回None
        """
        data = self._load_profiles()
        return data["profiles"].get(username)
    
    def update_profile(self, username: str, **kwargs) -> bool:
        """
        更新用户资料
        
        Args:
            username: 用户名
            **kwargs: 要更新的字段
            
        Returns:
            bool: 是否更新成功
        """
        data = self._load_profiles()
        
        if username not in data["profiles"]:
            return False
            
        profile = data["profiles"][username]
        for key, value in kwargs.items():
            if key in profile:
                profile[key] = value
                
        profile["last_updated"] = datetime.now().isoformat()
        self._save_profiles(data)
        return True
    
    def delete_profile(self, username: str) -> bool:
        """
        删除用户资料
        
        Args:
            username: 用户名
            
        Returns:
            bool: 是否删除成功
        """
        data = self._load_profiles()
        
        if username not in data["profiles"]:
            return False
            
        del data["profiles"][username]
        self._save_profiles(data)
        return True 