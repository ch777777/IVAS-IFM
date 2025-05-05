"""
应用程序启动脚本
"""
import os
import sys
import tkinter as tk
from src.utils.logger import Logger
from src.managers.auth_manager import AuthManager
from src.managers.profile_manager import ProfileManager
from src.managers.role_manager import RoleManager
from src.managers.password_reset_manager import PasswordResetManager
from src.application import Application

def setup_environment():
    """设置运行环境"""
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # 创建必要的目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/users", exist_ok=True)
    os.makedirs("data/profiles", exist_ok=True)
    os.makedirs("data/roles", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

def main():
    """主函数"""
    try:
        # 设置环境
        setup_environment()
        
        # 初始化日志
        logger = Logger()
        logger.info("正在启动应用程序...")
        
        # 初始化管理器
        auth_manager = AuthManager()
        profile_manager = ProfileManager()
        role_manager = RoleManager()
        password_reset_manager = PasswordResetManager()
        
        # 创建主窗口
        root = tk.Tk()
        root.title("用户认证系统")
        root.geometry("800x600")
        
        # 创建应用实例
        app = Application(
            root,
            auth_manager,
            profile_manager,
            role_manager,
            password_reset_manager,
            logger
        )
        
        # 启动应用
        app.start()
        
    except Exception as e:
        print(f"启动失败: {str(e)}")
        if 'logger' in locals():
            logger.error(f"启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 