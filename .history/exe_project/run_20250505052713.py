"""
应用程序启动脚本
"""
import os
import sys
import tkinter as tk

def setup_environment():
    """设置运行环境"""
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # 创建必要的数据目录
    data_dirs = [
        "data",
        "data/users",
        "data/profiles",
        "data/roles",
        "logs"
    ]
    for dir_path in data_dirs:
        os.makedirs(os.path.join(project_root, dir_path), exist_ok=True)

def main():
    """主函数"""
    # 设置环境
    setup_environment()
    
    try:
        # 导入应用程序
        from src.components.app import Application
        from src.utils.logger import Logger
        
        # 初始化日志
        logger = Logger()
        logger.log_action("系统启动", "系统初始化")
        
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
        print(f"启动失败: {str(e)}")
        sys.exit(1)
    finally:
        if 'logger' in locals():
            logger.log_action("系统关闭", "系统正常退出")

if __name__ == "__main__":
    main() 