"""
密码重置管理器类
"""
import os
import json
import random
import string
import bcrypt
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

class PasswordResetManager:
    """密码重置管理器类"""
    
    def __init__(self):
        """初始化密码重置管理器"""
        self.reset_tokens_file = os.path.join("data", "reset_tokens", "tokens.json")
        
        # 确保重置令牌数据目录存在
        os.makedirs(os.path.dirname(self.reset_tokens_file), exist_ok=True)
        
        # 如果重置令牌文件不存在，创建空文件
        if not os.path.exists(self.reset_tokens_file):
            with open(self.reset_tokens_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
    
    def generate_reset_token(self, username: str) -> Tuple[bool, str, Optional[str]]:
        """生成密码重置令牌
        
        Args:
            username: 用户名
            
        Returns:
            Tuple[bool, str, Optional[str]]: (是否成功, 消息, 重置令牌)
        """
        try:
            # 生成随机令牌
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            
            # 读取现有令牌
            with open(self.reset_tokens_file, "r", encoding="utf-8") as f:
                tokens = json.load(f)
            
            # 保存新令牌
            tokens[token] = {
                "username": username,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
            # 保存令牌数据
            with open(self.reset_tokens_file, "w", encoding="utf-8") as f:
                json.dump(tokens, f, ensure_ascii=False, indent=2)
            
            return True, "令牌生成成功", token
            
        except Exception as e:
            return False, f"生成令牌失败: {str(e)}", None
    
    def verify_reset_token(self, token: str) -> Tuple[bool, str, Optional[str]]:
        """验证密码重置令牌
        
        Args:
            token: 重置令牌
            
        Returns:
            Tuple[bool, str, Optional[str]]: (是否有效, 消息, 用户名)
        """
        try:
            # 读取令牌数据
            with open(self.reset_tokens_file, "r", encoding="utf-8") as f:
                tokens = json.load(f)
            
            # 检查令牌是否存在
            if token not in tokens:
                return False, "无效的令牌", None
            
            token_data = tokens[token]
            
            # 检查令牌是否过期
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            if datetime.now() > expires_at:
                # 删除过期令牌
                del tokens[token]
                with open(self.reset_tokens_file, "w", encoding="utf-8") as f:
                    json.dump(tokens, f, ensure_ascii=False, indent=2)
                return False, "令牌已过期", None
            
            return True, "令牌有效", token_data["username"]
            
        except Exception as e:
            return False, f"验证令牌失败: {str(e)}", None
    
    def reset_password(self, token: str, new_password: str) -> Tuple[bool, str]:
        """重置密码
        
        Args:
            token: 重置令牌
            new_password: 新密码
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 验证令牌
            success, message, username = self.verify_reset_token(token)
            if not success:
                return False, message
            
            # 读取用户数据
            users_file = os.path.join("data", "users", "users.json")
            with open(users_file, "r", encoding="utf-8") as f:
                users = json.load(f)
            
            # 检查用户是否存在
            if username not in users:
                return False, "用户不存在"
            
            # 加密新密码
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(new_password.encode(), salt)
            
            # 更新密码
            users[username]["password"] = hashed_password.decode()
            
            # 保存用户数据
            with open(users_file, "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            
            # 删除已使用的令牌
            with open(self.reset_tokens_file, "r", encoding="utf-8") as f:
                tokens = json.load(f)
            
            del tokens[token]
            
            with open(self.reset_tokens_file, "w", encoding="utf-8") as f:
                json.dump(tokens, f, ensure_ascii=False, indent=2)
            
            return True, "密码重置成功"
            
        except Exception as e:
            return False, f"重置密码失败: {str(e)}"
    
    def cleanup_expired_tokens(self) -> Tuple[bool, str]:
        """清理过期的重置令牌
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 读取令牌数据
            with open(self.reset_tokens_file, "r", encoding="utf-8") as f:
                tokens = json.load(f)
            
            # 删除过期令牌
            expired_tokens = []
            for token, data in tokens.items():
                expires_at = datetime.fromisoformat(data["expires_at"])
                if datetime.now() > expires_at:
                    expired_tokens.append(token)
            
            for token in expired_tokens:
                del tokens[token]
            
            # 保存令牌数据
            with open(self.reset_tokens_file, "w", encoding="utf-8") as f:
                json.dump(tokens, f, ensure_ascii=False, indent=2)
            
            return True, f"已清理 {len(expired_tokens)} 个过期令牌"
            
        except Exception as e:
            return False, f"清理过期令牌失败: {str(e)}" 