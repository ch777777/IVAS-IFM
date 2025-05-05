"""
启动脚本
"""
import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from src.login_app import LoginApp

def main():
    """启动登录界面"""
    app = LoginApp()
    app.mainloop()

if __name__ == "__main__":
    main() 