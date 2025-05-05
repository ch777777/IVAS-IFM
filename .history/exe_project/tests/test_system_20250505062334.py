"""
系统测试脚本
用于测试系统的各项功能
"""
import unittest
import os
import json
from src.utils.auth import AuthManager
from src.utils.profile import ProfileManager
from src.utils.role_manager import RoleManager
from src.utils.password_reset import PasswordResetManager
from src.utils.logger import Logger

class TestSystem(unittest.TestCase):
    """系统测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试数据目录
        self.test_dir = "test_data"
        os.makedirs(self.test_dir, exist_ok=True)
        
        # 初始化管理器
        self.auth_manager = AuthManager()
        self.profile_manager = ProfileManager()
        self.role_manager = RoleManager()
        self.password_reset_manager = PasswordResetManager()
        self.logger = Logger()
        
    def tearDown(self):
        """测试后清理"""
        # 删除测试数据
        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)
            
    def test_user_registration(self):
        """测试用户注册"""
        # 注册新用户
        success, message = self.auth_manager.register("testuser", "password123")
        self.assertTrue(success)
        self.assertEqual(message, "注册成功")
        
        # 测试重复注册
        success, message = self.auth_manager.register("testuser", "password123")
        self.assertFalse(success)
        self.assertEqual(message, "用户名已存在")
        
    def test_user_login(self):
        """测试用户登录"""
        # 先注册用户
        self.auth_manager.register("testuser", "password123")
        
        # 测试登录
        success, token = self.auth_manager.login("testuser", "password123")
        self.assertTrue(success)
        self.assertIsNotNone(token)
        
        # 测试错误密码
        success, message = self.auth_manager.login("testuser", "wrongpassword")
        self.assertFalse(success)
        self.assertEqual(message, "密码错误")
        
    def test_profile_management(self):
        """测试用户资料管理"""
        # 创建用户资料
        success = self.profile_manager.create_profile(
            "testuser",
            email="test@example.com",
            phone="1234567890",
            role="user"
        )
        self.assertTrue(success)
        
        # 获取用户资料
        profile = self.profile_manager.get_profile("testuser")
        self.assertIsNotNone(profile)
        self.assertEqual(profile["email"], "test@example.com")
        
        # 更新用户资料
        success = self.profile_manager.update_profile(
            "testuser",
            email="new@example.com",
            phone="0987654321"
        )
        self.assertTrue(success)
        
        # 验证更新
        profile = self.profile_manager.get_profile("testuser")
        self.assertEqual(profile["email"], "new@example.com")
        
    def test_role_management(self):
        """测试角色管理"""
        # 创建角色
        success = self.role_manager.create_role(
            "admin",
            "管理员",
            ["read", "write", "delete"],
            "系统管理员"
        )
        self.assertTrue(success)
        
        # 获取角色
        role = self.role_manager.get_role("admin")
        self.assertIsNotNone(role)
        self.assertEqual(role["name"], "管理员")
        
        # 更新角色
        success = self.role_manager.update_role(
            "admin",
            name="超级管理员",
            permissions=["read", "write", "delete", "admin"]
        )
        self.assertTrue(success)
        
        # 验证更新
        role = self.role_manager.get_role("admin")
        self.assertEqual(role["name"], "超级管理员")
        self.assertIn("admin", role["permissions"])
        
    def test_password_reset(self):
        """测试密码重置"""
        # 注册用户
        self.auth_manager.register("testuser", "password123")
        
        # 请求重置码
        success, code = self.password_reset_manager.request_reset("testuser", "test@example.com")
        self.assertTrue(success)
        self.assertIsNotNone(code)
        
        # 验证重置码
        success = self.password_reset_manager.verify_reset_code("testuser", code)
        self.assertTrue(success)
        
        # 重置密码
        success, message = self.password_reset_manager.reset_password(
            "testuser",
            code,
            "newpassword123"
        )
        self.assertTrue(success)
        
        # 验证新密码
        success, token = self.auth_manager.login("testuser", "newpassword123")
        self.assertTrue(success)
        self.assertIsNotNone(token)
        
    def test_logging(self):
        """测试日志记录"""
        # 记录登录
        self.logger.log_login("testuser", True, "127.0.0.1", "Test Browser")
        
        # 记录操作
        self.logger.log_action("testuser", "测试操作", "测试详情")
        
        # 记录错误
        self.logger.log_error("测试错误", "testuser")
        
        # 获取登录历史
        history = self.logger.get_login_history("testuser")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["username"], "testuser")
        self.assertTrue(history[0]["success"])

if __name__ == "__main__":
    unittest.main() 