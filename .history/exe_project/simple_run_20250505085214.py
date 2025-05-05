#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单的IVAS-IFM启动脚本
用于演示应用的功能
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

class DemoApp:
    """演示应用，展示IVAS-IFM的基本界面"""
    
    def __init__(self):
        """初始化演示应用"""
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.layout_widgets()
        
    def setup_window(self):
        """设置窗口属性"""
        self.root.title("IVAS-IFM - 智能视频分析系统")
        self.root.geometry("800x600")
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        self.main_frame = ttk.Frame(self.root, padding=10)
        
        # 标题标签
        self.title_label = ttk.Label(
            self.main_frame,
            text="欢迎使用 IVAS-IFM 智能视频分析系统",
            font=("Microsoft YaHei UI", 16, "bold")
        )
        
        # 搜索区域
        self.search_frame = ttk.LabelFrame(self.main_frame, text="视频搜索", padding=10)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, width=40, textvariable=self.search_var)
        self.search_button = ttk.Button(self.search_frame, text="搜索", command=self.search)
        
        # 平台选择区域
        self.platform_frame = ttk.LabelFrame(self.search_frame, text="平台选择", padding=5)
        
        # 平台复选框
        self.platform_vars = {
            "youtube": tk.BooleanVar(value=True),
            "bilibili": tk.BooleanVar(value=True),
            "tiktok": tk.BooleanVar(value=True),
            "weibo": tk.BooleanVar(value=True),
            "facebook": tk.BooleanVar(value=True)
        }
        
        self.platform_checkbuttons = {}
        for platform, var in self.platform_vars.items():
            self.platform_checkbuttons[platform] = ttk.Checkbutton(
                self.platform_frame,
                text=platform.capitalize(),
                variable=var
            )
        
        # 结果区域
        self.results_frame = ttk.LabelFrame(self.main_frame, text="搜索结果", padding=10)
        self.results_text = tk.Text(self.results_frame, width=70, height=20)
        self.results_scrollbar = ttk.Scrollbar(
            self.results_frame, 
            orient=tk.VERTICAL, 
            command=self.results_text.yview
        )
        self.results_text.config(yscrollcommand=self.results_scrollbar.set)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        
    def layout_widgets(self):
        """布局界面组件"""
        # 主框架
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        self.title_label.pack(fill=tk.X, pady=(0, 10))
        
        # 搜索区域
        self.search_frame.pack(fill=tk.X, pady=10)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # 平台选择
        self.platform_frame.pack(side=tk.LEFT, padx=(0, 10))
        for platform, checkbutton in self.platform_checkbuttons.items():
            checkbutton.pack(anchor=tk.W)
            
        self.search_button.pack(side=tk.LEFT)
        
        # 结果区域
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def search(self):
        """执行搜索操作"""
        query = self.search_var.get().strip()
        if not query:
            messagebox.showinfo("提示", "请输入搜索关键词")
            return
            
        # 获取选择的平台
        platforms = [
            platform for platform, var in self.platform_vars.items() if var.get()
        ]
        
        if not platforms:
            messagebox.showinfo("提示", "请至少选择一个平台")
            return
            
        # 更新状态
        self.status_var.set(f"正在搜索: {query}")
        
        # 清空结果
        self.results_text.delete(1.0, tk.END)
        
        # 模拟搜索结果
        self.results_text.insert(tk.END, f"搜索关键词: {query}\n")
        self.results_text.insert(tk.END, f"选择的平台: {', '.join(platforms)}\n\n")
        
        # 为每个平台生成模拟结果
        for platform in platforms:
            self.results_text.insert(tk.END, f"--- {platform.upper()} 搜索结果 ---\n\n")
            
            for i in range(1, 6):
                self.results_text.insert(tk.END, f"标题: {query} - 视频 {i} (来自 {platform})\n")
                self.results_text.insert(tk.END, f"作者: 用户{platform}{i}\n")
                self.results_text.insert(tk.END, f"时长: {i}:00\n")
                self.results_text.insert(tk.END, f"观看次数: {i * 1000}\n")
                self.results_text.insert(tk.END, f"发布日期: 2023-05-0{i}\n")
                self.results_text.insert(
                    tk.END, 
                    f"简介: 这是一个关于 {query} 的示例视频，由 {platform} 平台的用户发布。\n\n"
                )
        
        # 更新状态
        self.status_var.set(f"找到 {len(platforms) * 5} 个结果")
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()


def main():
    """主程序入口"""
    app = DemoApp()
    app.run()
    

if __name__ == "__main__":
    main() 