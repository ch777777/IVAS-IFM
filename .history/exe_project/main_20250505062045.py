"""
主程序入口
用于启动和测试系统
"""
import tkinter as tk
from src.components.app import Application
from src.utils.logger import Logger
from src.utils.auth import AuthManager
from src.utils.profile import ProfileManager
from src.utils.role_manager import RoleManager
from src.utils.password_reset import PasswordResetManager

def main():
    """主函数"""
    # 初始化日志
    logger = Logger()
    logger.log_action("系统启动", "系统初始化")
    
    try:
        # 初始化认证管理器
        auth_manager = AuthManager()
        
        # 初始化其他管理器
        profile_manager = ProfileManager()
        role_manager = RoleManager()
        password_reset_manager = PasswordResetManager()
        
        # 创建主窗口
        root = tk.Tk()
        root.title("用户认证系统")
        
        # 设置窗口大小和位置
        window_width = 800
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建应用程序实例
        app = Application(root)
        
        # 启动主循环
        root.mainloop()
        
    except Exception as e:
        logger.log_error(str(e), "系统启动失败")
        raise
    finally:
        logger.log_action("系统关闭", "系统正常退出")

if __name__ == "__main__":
    main() 