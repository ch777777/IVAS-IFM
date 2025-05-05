"""
用户认证模块
实现用户登录、注册和认证功能
"""
import os
import json
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from ..config.settings import SECURITY

class AuthManager:
    """用户认证管理器"""
    
    def __init__(self):
        """初始化认证管理器"""
        self.users_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "users.json")
        self._ensure_users_file()
        
    def _ensure_users_file(self):
        """确保用户数据文件存在"""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        if not os.path.exists(self.users_file):
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump({"users": []}, f, ensure_ascii=False, indent=2)
    
    def _load_users(self) -> Dict[str, Any]:
        """加载用户数据"""
        with open(self.users_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save_users(self, data: Dict[str, Any]):
        """保存用户数据"""
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
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
    
    def _verify_password(self, stored_password: str, provided_password: str) -> bool:
        """验证密码"""
        salt = bytes.fromhex(stored_password[:64])
        stored_key = stored_password[64:]
        key = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt,
            SECURITY["password_salt_rounds"]
        )
        return stored_key == key.hex()
    
    def register(self, username: str, password: str) -> Tuple[bool, str]:
        """
        注册新用户
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Tuple[bool, str]: (是否成功, 结果信息)
        """
        data = self._load_users()
        
        # 检查用户名是否已存在
        if any(user["username"] == username for user in data["users"]):
            return False, "用户名已存在"
        
        # 创建新用户
        new_user = {
            "username": username,
            "password": self._hash_password(password),
            "created_at": datetime.now().isoformat()
        }
        
        data["users"].append(new_user)
        self._save_users(data)
        return True, "注册成功"
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Tuple[bool, str]: (是否成功, 结果信息)
        """
        data = self._load_users()
        
        # 查找用户
        user = next((u for u in data["users"] if u["username"] == username), None)
        if not user:
            return False, "用户名或密码错误"
        
        # 验证密码
        if not self._verify_password(user["password"], password):
            return False, "用户名或密码错误"
        
        # 生成JWT令牌
        token = jwt.encode(
            {
                "username": username,
                "exp": datetime.utcnow() + timedelta(minutes=SECURITY["token_expire_minutes"])
            },
            SECURITY["jwt_secret"],
            algorithm="HS256"
        )
        
        return True, token
    
    def verify_token(self, token: str) -> Tuple[bool, Any]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            Tuple[bool, Any]: (是否有效, 用户信息或错误信息)
        """
        try:
            payload = jwt.decode(token, SECURITY["jwt_secret"], algorithms=["HS256"])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, "令牌已过期"
        except jwt.InvalidTokenError:
            return False, "无效的令牌"
            
    def update_password(self, username: str, new_password: str) -> Tuple[bool, str]:
        """
        更新用户密码
        
        Args:
            username: 用户名
            new_password: 新密码
            
        Returns:
            Tuple[bool, str]: (是否成功, 结果信息)
        """
        if len(new_password) < 6:
            return False, "密码长度必须至少为6个字符"
            
        data = self._load_users()
        
        # 查找用户
        user = next((u for u in data["users"] if u["username"] == username), None)
        if not user:
            return False, "用户不存在"
        
        # 更新密码
        user["password"] = self._hash_password(new_password)
        self._save_users(data)
        return True, "密码更新成功" 