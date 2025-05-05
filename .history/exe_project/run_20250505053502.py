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
    """设置应用程序环境"""
    # 创建必要的目录
    directories = ["data", "data/users", "data/profiles", "data/roles", "data/reset_tokens", "logs"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """主函数"""
    try:
        # 设置环境
        setup_environment()
        
        # 初始化日志记录器
        logger = Logger()
        logger.info("应用程序启动")
        
        # 初始化管理器
        auth_manager = AuthManager()
        profile_manager = ProfileManager()
        role_manager = RoleManager()
        password_reset_manager = PasswordResetManager()
        
        # 创建主窗口
        root = tk.Tk()
        root.title("用户认证系统")
        root.geometry("800x600")
        
        # 创建应用程序实例
        app = Application(
            root,
            auth_manager=auth_manager,
            profile_manager=profile_manager,
            role_manager=role_manager,
            password_reset_manager=password_reset_manager,
            logger=logger
        )
        
        # 启动应用程序
        app.start()
        
        # 运行主循环
        root.mainloop()
        
    except Exception as e:
        logger.error(f"应用程序启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 