"""
密码重置模块
实现密码重置和验证功能
"""
import os
import json
import random
import string
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from ..config.settings import SECURITY

class PasswordResetManager:
    """密码重置管理器"""
    
    def __init__(self):
        """初始化密码重置管理器"""
        self.reset_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "password_resets.json")
        self._ensure_reset_file()
        
    def _ensure_reset_file(self):
        """确保重置文件存在"""
        os.makedirs(os.path.dirname(self.reset_file), exist_ok=True)
        if not os.path.exists(self.reset_file):
            with open(self.reset_file, "w", encoding="utf-8") as f:
                json.dump({"resets": {}}, f, ensure_ascii=False, indent=2)
    
    def _load_resets(self) -> Dict[str, Any]:
        """加载重置记录"""
        with open(self.reset_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save_resets(self, data: Dict[str, Any]):
        """保存重置记录"""
        with open(self.reset_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _generate_reset_code(self) -> str:
        """生成重置验证码"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def _hash_password(self, password: str) -> str:
        """对密码进行哈希处理"""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            SECURITY["password_salt_rounds"]
        )
        return salt.hex() + key.hex()
    
    def request_reset(self, username: str, email: str) -> Tuple[bool, str]:
        """
        请求密码重置
        
        Args:
            username: 用户名
            email: 电子邮件
            
        Returns:
            Tuple[bool, str]: (是否成功, 重置码或错误信息)
        """
        data = self._load_resets()
        
        # 检查是否已有未过期的重置请求
        if username in data["resets"]:
            reset_info = data["resets"][username]
            if datetime.fromisoformat(reset_info["expires_at"]) > datetime.now():
                return False, "已有未过期的重置请求"
        
        # 生成新的重置码
        reset_code = self._generate_reset_code()
        expires_at = datetime.now() + timedelta(minutes=30)
        
        data["resets"][username] = {
            "code": reset_code,
            "email": email,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat()
        }
        
        self._save_resets(data)
        return True, reset_code
    
    def verify_reset_code(self, username: str, code: str) -> bool:
        """
        验证重置码
        
        Args:
            username: 用户名
            code: 重置码
            
        Returns:
            bool: 是否验证成功
        """
        data = self._load_resets()
        
        if username not in data["resets"]:
            return False
            
        reset_info = data["resets"][username]
        if datetime.fromisoformat(reset_info["expires_at"]) <= datetime.now():
            return False
            
        return reset_info["code"] == code
    
    def reset_password(self, username: str, code: str, new_password: str) -> Tuple[bool, str]:
        """
        重置密码
        
        Args:
            username: 用户名
            code: 重置码
            new_password: 新密码
            
        Returns:
            Tuple[bool, str]: (是否成功, 结果信息)
        """
        if not self.verify_reset_code(username, code):
            return False, "无效或已过期的重置码"
            
        if len(new_password) < 6:
            return False, "密码长度必须至少为6个字符"
            
        # 更新密码
        from .auth import AuthManager
        auth_manager = AuthManager()
        success, message = auth_manager.update_password(username, new_password)
        
        if success:
            # 删除重置记录
            data = self._load_resets()
            del data["resets"][username]
            self._save_resets(data)
            
        return success, message 