"""
工具函数测试模块
测试src/utils/helpers.py中的函数
"""
import unittest
import os
import sys
import tkinter as tk

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from src.utils.helpers import get_os_info, get_resource_path

class TestHelperFunctions(unittest.TestCase):
    """测试辅助函数"""
    
    def test_get_os_info(self):
        """测试获取操作系统信息函数"""
        # 执行函数
        os_info = get_os_info()
        
        # 验证返回值
        self.assertIsInstance(os_info, dict)
        self.assertIn('system', os_info)
        self.assertIn('version', os_info)
        self.assertIn('architecture', os_info)
        
        # 验证值类型
        self.assertIsInstance(os_info['system'], str)
        self.assertIsInstance(os_info['version'], str)
        self.assertIsInstance(os_info['architecture'], str)
        
    def test_get_resource_path(self):
        """测试获取资源路径函数"""
        # 测试相对路径
        test_path = "test_file.txt"
        resource_path = get_resource_path(test_path)
        
        # 验证返回值是字符串
        self.assertIsInstance(resource_path, str)
        
        # 验证路径末尾包含测试文件名
        self.assertTrue(resource_path.endswith(test_path))
        
if __name__ == "__main__":
    unittest.main() 