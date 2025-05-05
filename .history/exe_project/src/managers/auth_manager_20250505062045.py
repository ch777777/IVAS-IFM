"""
认证管理器类
"""
import os
import json
import bcrypt
import jwt
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

class AuthManager:
    """认证管理器类"""
    
    def __init__(self):
        """初始化认证管理器"""
        self.users_file = os.path.join("data", "users", "users.json")
        self.secret_key = "your-secret-key"  # 在实际应用中应该使用环境变量
        
        # 确保用户数据目录存在
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        
        # 如果用户文件不存在，创建空文件
        if not os.path.exists(self.users_file):
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
    
    def register(self, username: str, password: str, email: str) -> Tuple[bool, str]:
        """注册新用户
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 读取用户数据
            with open(self.users_file, "r", encoding="utf-8") as f:
                users = json.load(f)
            
            # 检查用户名是否已存在
            if username in users:
                return False, "用户名已存在"
            
            # 检查邮箱是否已存在
            for user in users.values():
                if user.get("email") == email:
                    return False, "邮箱已被注册"
            
            # 加密密码
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode(), salt)
            
            # 创建新用户
            users[username] = {
                "password": hashed_password.decode(),
                "email": email,
                "created_at": datetime.now().isoformat(),
                "last_login": None
            }
            
            # 保存用户数据
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            
            return True, "注册成功"
            
        except Exception as e:
            return False, f"注册失败: {str(e)}"
    
    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Tuple[bool, str, Optional[str]]: (是否成功, 消息, JWT令牌)
        """
        try:
            # 读取用户数据
            with open(self.users_file, "r", encoding="utf-8") as f:
                users = json.load(f)
            
            # 检查用户是否存在
            if username not in users:
                return False, "用户名或密码错误", None
            
            user = users[username]
            
            # 验证密码
            if not bcrypt.checkpw(password.encode(), user["password"].encode()):
                return False, "用户名或密码错误", None
            
            # 更新最后登录时间
            user["last_login"] = datetime.now().isoformat()
            
            # 保存用户数据
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            
            # 生成JWT令牌
            token = jwt.encode(
                {
                    "username": username,
                    "exp": datetime.utcnow() + timedelta(days=1)
                },
                self.secret_key,
                algorithm="HS256"
            )
            
            return True, "登录成功", token
            
        except Exception as e:
            return False, f"登录失败: {str(e)}", None
    
    def verify_token(self, token: str) -> Tuple[bool, str, Optional[str]]:
        """验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            Tuple[bool, str, Optional[str]]: (是否有效, 消息, 用户名)
        """
        try:
            # 解码令牌
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            username = payload.get("username")
            
            # 检查用户是否存在
            with open(self.users_file, "r", encoding="utf-8") as f:
                users = json.load(f)
            
            if username not in users:
                return False, "无效的令牌", None
            
            return True, "令牌有效", username
            
        except jwt.ExpiredSignatureError:
            return False, "令牌已过期", None
        except jwt.InvalidTokenError:
            return False, "无效的令牌", None
        except Exception as e:
            return False, f"验证令牌失败: {str(e)}", None
    
    def change_password(self, username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """修改密码
        
        Args:
            username: 用户名
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 读取用户数据
            with open(self.users_file, "r", encoding="utf-8") as f:
                users = json.load(f)
            
            # 检查用户是否存在
            if username not in users:
                return False, "用户不存在"
            
            user = users[username]
            
            # 验证旧密码
            if not bcrypt.checkpw(old_password.encode(), user["password"].encode()):
                return False, "旧密码错误"
            
            # 加密新密码
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode(), salt)
            
            # 更新密码
            user["password"] = hashed_password.decode()
            
            # 保存用户数据
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            
            return True, "密码修改成功"
            
        except Exception as e:
            return False, f"修改密码失败: {str(e)}" 