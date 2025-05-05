"""
启动脚本
"""
import os
import sys
import logging

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from src.login_app import LoginApp
    logging.info("成功导入LoginApp模块")
except ImportError as e:
    logging.error(f"导入LoginApp失败: {str(e)}")
    sys.exit(1)

def main():
    """启动登录界面"""
    try:
        logging.info("正在初始化登录界面...")
        app = LoginApp()
        logging.info("登录界面初始化完成，开始主循环")
        app.mainloop()
    except Exception as e:
        logging.error(f"程序运行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 