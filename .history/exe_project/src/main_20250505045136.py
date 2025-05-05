"""
主程序入口
启动应用程序的入口点
"""
import tkinter as tk
import sys
import os

# 确保能够找到应用程序模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from src.components.app import Application

def main():
    """程序入口函数"""
    # 创建Tk根窗口
    root = tk.Tk()
    
    # 创建应用程序实例
    app = Application(root)
    
    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    main() 
 