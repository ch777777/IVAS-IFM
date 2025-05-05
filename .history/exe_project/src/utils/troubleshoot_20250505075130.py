#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
IVAS-IFM 故障排查工具

这个模块提供了帮助用户诊断和解决常见问题的工具。
"""

import os
import sys
import logging
import requests
import socket
import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import importlib.util

# 设置基本路径
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# 设置日志
logger = logging.getLogger("troubleshoot")

class SystemDiagnostic:
    """系统诊断类"""
    
    def __init__(self):
        """初始化诊断工具"""
        self.problems = []
        self.solutions = []
        self.platform_status = {}
    
    def check_network(self):
        """检查网络连接"""
        try:
            # 尝试连接到常用网站
            response = requests.get("https://www.baidu.com", timeout=5)
            if response.status_code == 200:
                return True
            return False
        except Exception as e:
            self.problems.append(f"网络连接问题: {e}")
            self.solutions.append("请检查您的互联网连接")
            return False
    
    def check_platform_access(self):
        """检查各平台访问状态"""
        platforms = {
            "YouTube": "https://www.youtube.com",
            "Bilibili": "https://www.bilibili.com",
            "TikTok": "https://www.tiktok.com",
            "Weibo": "https://weibo.com",
            "Facebook": "https://www.facebook.com"
        }
        
        for platform, url in platforms.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.platform_status[platform] = "可访问"
                else:
                    self.platform_status[platform] = f"响应异常 (状态码: {response.status_code})"
                    self.problems.append(f"{platform} 访问异常")
                    self.solutions.append(f"检查 {platform} 是否在您的地区可访问，可能需要配置代理")
            except Exception as e:
                self.platform_status[platform] = f"无法访问 ({e})"
                self.problems.append(f"{platform} 无法访问")
                self.solutions.append(f"检查 {platform} 是否在您的地区可访问，可能需要配置代理")
    
    def check_api_keys(self):
        """检查API密钥配置"""
        config_path = BASE_DIR / "src" / "config" / "settings.py"
        
        if not config_path.exists():
            self.problems.append("找不到配置文件")
            self.solutions.append("请确保配置文件存在: src/config/settings.py")
            return
            
        try:
            # 尝试导入配置
            spec = importlib.util.spec_from_file_location("settings", config_path)
            settings = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(settings)
            
            # 检查平台配置
            if hasattr(settings, "PLATFORM_CONFIGS"):
                platform_configs = settings.PLATFORM_CONFIGS
                
                # 检查YouTube API密钥
                if "youtube" in platform_configs:
                    youtube_config = platform_configs["youtube"]
                    api_key = youtube_config.get("api_key", "")
                    if not api_key:
                        self.problems.append("YouTube API密钥未配置")
                        self.solutions.append("配置YouTube API密钥以获取更好的搜索结果")
                
                # 检查其他平台的配置
                for platform in ["bilibili", "tiktok", "weibo", "facebook"]:
                    if platform in platform_configs:
                        if platform in ["bilibili", "weibo"] and not platform_configs[platform].get("cookie_file"):
                            self.problems.append(f"{platform.capitalize()} cookie文件未配置")
                            self.solutions.append(f"配置{platform.capitalize()} cookie文件以获取更好的搜索结果")
        except Exception as e:
            self.problems.append(f"读取配置文件出错: {e}")
            self.solutions.append("请确保配置文件格式正确")
    
    def check_search_keywords(self, keywords):
        """检查搜索关键词"""
        if not keywords:
            self.problems.append("搜索关键词为空")
            self.solutions.append("请输入搜索关键词")
            return False
            
        if len(keywords) < 2:
            self.problems.append("搜索关键词过短")
            self.solutions.append("请使用更具体的搜索关键词")
            
        if len(keywords) > 50:
            self.problems.append("搜索关键词过长")
            self.solutions.append("请缩短搜索关键词")
            
        # 检查关键词是否包含特殊字符
        special_chars = "!@#$%^&*()+=[]{}|\\:;\"'<>,?/"
        if any(c in special_chars for c in keywords):
            self.problems.append("搜索关键词包含特殊字符")
            self.solutions.append("尝试移除特殊字符")
            
        return True
    
    def check_log_files(self):
        """分析日志文件中的错误"""
        log_dir = BASE_DIR / "logs"
        if not log_dir.exists():
            self.problems.append("日志目录不存在")
            self.solutions.append("请确保logs目录存在并可写入")
            return
            
        # 查找最新的日志文件
        log_files = list(log_dir.glob("*.log"))
        if not log_files:
            self.problems.append("未找到日志文件")
            self.solutions.append("请确保应用程序已运行并生成日志")
            return
            
        # 按修改时间排序，获取最新的日志文件
        latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
        
        try:
            with open(latest_log, "r", encoding="utf-8") as f:
                log_content = f.read()
                
            # 检查常见错误模式
            if "API rate limit exceeded" in log_content:
                self.problems.append("API请求频率超出限制")
                self.solutions.append("等待一段时间后再次尝试，或者获取更高配额的API密钥")
                
            if "No results found" in log_content:
                self.problems.append("未找到匹配的搜索结果")
                self.solutions.append("尝试使用不同的搜索关键词或选择不同的平台")
                
            if "Error establishing connection" in log_content or "Connection refused" in log_content:
                self.problems.append("网络连接错误")
                self.solutions.append("检查网络连接和代理设置")
                
            if "HTTPError: 403" in log_content:
                self.problems.append("访问被拒绝 (HTTP 403)")
                self.solutions.append("检查API密钥或Cookie是否有效，或者是否被平台封禁")
                
            if "HTTPError: 404" in log_content:
                self.problems.append("资源不存在 (HTTP 404)")
                self.solutions.append("检查URL是否正确")
                
            if "Network is unreachable" in log_content:
                self.problems.append("网络不可达")
                self.solutions.append("检查网络连接和防火墙设置")
                
            # 提取最后10个错误
            error_lines = [line for line in log_content.split("\n") if "ERROR" in line][-10:]
            for error in error_lines:
                self.problems.append(f"日志中的错误: {error}")
                
        except Exception as e:
            self.problems.append(f"读取日志文件出错: {e}")
            self.solutions.append("请确保日志文件可读")
    
    def check_system(self):
        """运行所有检查"""
        self.check_network()
        self.check_platform_access()
        self.check_api_keys()
        self.check_log_files()
        
        return {
            "problems": self.problems,
            "solutions": self.solutions,
            "platform_status": self.platform_status
        }
    
    def generate_report(self):
        """生成诊断报告"""
        report = {
            "timestamp": import_time.time(),
            "system_info": {
                "platform": sys.platform,
                "python_version": sys.version
            },
            "network_check": self.check_network(),
            "platform_status": self.platform_status,
            "problems": self.problems,
            "solutions": self.solutions
        }
        
        # 保存报告到文件
        report_path = BASE_DIR / "logs" / f"diagnostic_{int(import_time.time())}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
        return report_path


class DiagnosticGUI:
    """诊断工具的图形界面"""
    
    def __init__(self):
        """初始化诊断工具界面"""
        self.root = tk.Tk()
        self.root.title("IVAS-IFM 故障排查工具")
        self.root.geometry("800x600")
        
        self.diagnostic = SystemDiagnostic()
        self.create_widgets()
        self.layout_widgets()
        
    def create_widgets(self):
        """创建界面组件"""
        # 标题
        self.title_label = ttk.Label(
            self.root,
            text="IVAS-IFM 系统诊断工具",
            font=("Microsoft YaHei UI", 16, "bold")
        )
        
        # 检查按钮
        self.check_button = ttk.Button(
            self.root,
            text="开始诊断",
            command=self.run_diagnostics
        )
        
        # 关键词检查部分
        self.keyword_frame = ttk.LabelFrame(self.root, text="搜索关键词检查")
        self.keyword_var = tk.StringVar()
        self.keyword_entry = ttk.Entry(
            self.keyword_frame,
            textvariable=self.keyword_var,
            width=40
        )
        self.keyword_check_button = ttk.Button(
            self.keyword_frame,
            text="检查关键词",
            command=self.check_keyword
        )
        
        # 结果区域
        self.result_frame = ttk.LabelFrame(self.root, text="诊断结果")
        self.result_text = tk.Text(
            self.result_frame,
            width=80,
            height=20
        )
        self.result_scrollbar = ttk.Scrollbar(
            self.result_frame,
            orient=tk.VERTICAL,
            command=self.result_text.yview
        )
        self.result_text.config(yscrollcommand=self.result_scrollbar.set)
        
        # 操作按钮
        self.action_frame = ttk.Frame(self.root)
        self.save_button = ttk.Button(
            self.action_frame,
            text="保存报告",
            command=self.save_report
        )
        self.close_button = ttk.Button(
            self.action_frame,
            text="关闭",
            command=self.root.destroy
        )
        
    def layout_widgets(self):
        """布局界面组件"""
        # 标题
        self.title_label.pack(pady=10)
        
        # 检查按钮
        self.check_button.pack(pady=10)
        
        # 关键词检查部分
        self.keyword_frame.pack(fill=tk.X, padx=10, pady=5)
        self.keyword_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.keyword_check_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 结果区域
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 操作按钮
        self.action_frame.pack(fill=tk.X, pady=10)
        self.save_button.pack(side=tk.LEFT, padx=10)
        self.close_button.pack(side=tk.RIGHT, padx=10)
        
    def run_diagnostics(self):
        """运行系统诊断"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "正在进行系统诊断，请稍候...\n\n")
        self.root.update()
        
        # 运行诊断
        results = self.diagnostic.check_system()
        
        # 显示结果
        self.result_text.delete(1.0, tk.END)
        
        # 显示平台状态
        self.result_text.insert(tk.END, "=== 平台访问状态 ===\n")
        for platform, status in results["platform_status"].items():
            self.result_text.insert(tk.END, f"{platform}: {status}\n")
        self.result_text.insert(tk.END, "\n")
        
        # 显示问题
        if results["problems"]:
            self.result_text.insert(tk.END, "=== 检测到的问题 ===\n")
            for problem in results["problems"]:
                self.result_text.insert(tk.END, f"- {problem}\n")
            self.result_text.insert(tk.END, "\n")
        else:
            self.result_text.insert(tk.END, "未检测到系统问题。\n\n")
            
        # 显示解决方案
        if results["solutions"]:
            self.result_text.insert(tk.END, "=== 建议的解决方案 ===\n")
            for solution in results["solutions"]:
                self.result_text.insert(tk.END, f"- {solution}\n")
        
    def check_keyword(self):
        """检查搜索关键词"""
        keyword = self.keyword_var.get().strip()
        
        # 重置诊断对象
        self.diagnostic = SystemDiagnostic()
        
        # 检查关键词
        self.diagnostic.check_search_keywords(keyword)
        
        # 显示结果
        self.result_text.delete(1.0, tk.END)
        
        # 显示问题
        if self.diagnostic.problems:
            self.result_text.insert(tk.END, "=== 关键词问题 ===\n")
            for problem in self.diagnostic.problems:
                self.result_text.insert(tk.END, f"- {problem}\n")
            self.result_text.insert(tk.END, "\n")
        else:
            self.result_text.insert(tk.END, "关键词检查通过，未发现问题。\n\n")
            
        # 显示解决方案
        if self.diagnostic.solutions:
            self.result_text.insert(tk.END, "=== 建议的解决方案 ===\n")
            for solution in self.diagnostic.solutions:
                self.result_text.insert(tk.END, f"- {solution}\n")
        
    def save_report(self):
        """保存诊断报告"""
        try:
            report_path = self.diagnostic.generate_report()
            messagebox.showinfo("保存成功", f"诊断报告已保存到:\n{report_path}")
        except Exception as e:
            messagebox.showerror("保存失败", f"保存诊断报告失败: {e}")
    
    def run(self):
        """运行诊断工具"""
        self.root.mainloop()


# 导入时间模块 (避免循环导入)
import time as import_time

def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(str(BASE_DIR / "logs" / "troubleshoot.log"), encoding="utf-8")
        ]
    )
    
    # 创建并运行GUI
    app = DiagnosticGUI()
    app.run()

if __name__ == "__main__":
    main() 