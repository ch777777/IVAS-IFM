"""
启动脚本
"""
import os
import sys
import logging
import traceback

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)

def setup_environment():
    """设置运行环境"""
    try:
        # 添加项目根目录到Python路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.append(current_dir)
        logging.info(f"Python路径: {sys.path}")
        
        # 创建必要的目录
        dirs = ['src/config', 'logs', 'data']
        for d in dirs:
            os.makedirs(os.path.join(current_dir, d), exist_ok=True)
            logging.info(f"确保目录存在: {d}")
            
        return True
    except Exception as e:
        logging.error(f"环境设置失败: {str(e)}")
        return False

def main():
    """启动登录界面"""
    try:
        # 设置环境
        if not setup_environment():
            sys.exit(1)
            
        logging.info("正在导入必要的模块...")
        import customtkinter as ctk
        from src.login_app import LoginApp
        
        logging.info("正在初始化登录界面...")
        app = LoginApp()
        
        logging.info("登录界面初始化完成，开始主循环")
        app.mainloop()
        
    except ImportError as e:
        logging.error(f"模块导入失败: {str(e)}")
        logging.debug(f"详细错误信息: {traceback.format_exc()}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"程序运行出错: {str(e)}")
        logging.debug(f"详细错误信息: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 