"""
用户资料管理器类
"""
import os
import json
from typing import Dict, Optional, Tuple
from datetime import datetime

class ProfileManager:
    """用户资料管理器类"""
    
    def __init__(self):
        """初始化资料管理器"""
        self.profiles_file = os.path.join("data", "profiles", "profiles.json")
        
        # 确保资料数据目录存在
        os.makedirs(os.path.dirname(self.profiles_file), exist_ok=True)
        
        # 如果资料文件不存在，创建空文件
        if not os.path.exists(self.profiles_file):
            with open(self.profiles_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
    
    def get_profile(self, username: str) -> Tuple[bool, str, Optional[Dict]]:
        """获取用户资料
        
        Args:
            username: 用户名
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (是否成功, 消息, 资料数据)
        """
        try:
            # 读取资料数据
            with open(self.profiles_file, "r", encoding="utf-8") as f:
                profiles = json.load(f)
            
            # 检查用户资料是否存在
            if username not in profiles:
                return False, "用户资料不存在", None
            
            return True, "获取成功", profiles[username]
            
        except Exception as e:
            return False, f"获取资料失败: {str(e)}", None
    
    def update_profile(self, username: str, profile_data: Dict) -> Tuple[bool, str]:
        """更新用户资料
        
        Args:
            username: 用户名
            profile_data: 资料数据
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 读取现有资料
            with open(self.profiles_file, "r", encoding="utf-8") as f:
                profiles = json.load(f)
            
            # 更新资料
            profiles[username] = {
                **profiles.get(username, {}),
                **profile_data,
                "updated_at": datetime.now().isoformat()
            }
            
            # 保存资料数据
            with open(self.profiles_file, "w", encoding="utf-8") as f:
                json.dump(profiles, f, ensure_ascii=False, indent=2)
            
            return True, "资料更新成功"
            
        except Exception as e:
            return False, f"更新资料失败: {str(e)}"
    
    def delete_profile(self, username: str) -> Tuple[bool, str]:
        """删除用户资料
        
        Args:
            username: 用户名
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 读取现有资料
            with open(self.profiles_file, "r", encoding="utf-8") as f:
                profiles = json.load(f)
            
            # 检查用户资料是否存在
            if username not in profiles:
                return False, "用户资料不存在"
            
            # 删除资料
            del profiles[username]
            
            # 保存资料数据
            with open(self.profiles_file, "w", encoding="utf-8") as f:
                json.dump(profiles, f, ensure_ascii=False, indent=2)
            
            return True, "资料删除成功"
            
        except Exception as e:
            return False, f"删除资料失败: {str(e)}" 