#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
IVAS-IFM GUI应用程序

简单的GUI应用程序，用于测试系统功能。
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

# 设置基本路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# 创建日志目录
logs_dir = BASE_DIR / "logs"
logs_dir.mkdir(exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(str(logs_dir / "gui.log"), encoding="utf-8")
    ]
)

logger = logging.getLogger(__name__)

try:
    from src.config.settings import APP_CONFIG, PLATFORM_CONFIGS, MESSAGES
except ImportError:
    logger.warning("无法导入配置，使用默认值")
    
    # 默认配置
    APP_CONFIG = {
        "app_name": "IVAS-IFM",
        "app_version": "1.1.0",
        "ui": {
            "theme": "default",
            "width": 800,
            "height": 600,
            "title": "IVAS-IFM - 智能视频分析系统"
        }
    }
    
    PLATFORM_CONFIGS = {
        "youtube": {"max_results": 10, "use_mock_data": True},
        "bilibili": {"max_results": 10, "use_mock_data": True},
        "tiktok": {"max_results": 10, "use_mock_data": True},
        "weibo": {"max_results": 10, "use_mock_data": True},
        "facebook": {"max_results": 10, "use_mock_data": True}
    }
    
    MESSAGES = {
        "welcome": "欢迎使用 IVAS-IFM 智能视频分析系统",
        "search_prompt": "输入关键词搜索多平台视频",
        "no_results": "未找到匹配的结果，请尝试不同的关键词。",
        "download_success": "视频已成功下载到 {path}",
        "download_error": "下载视频时出错: {error}"
    }

# 尝试导入爬虫管理器
try:
    from src.modules.vca.crawler_manager import CrawlerManager
    HAS_CRAWLER = True
except ImportError:
    logger.warning("无法导入爬虫管理器，使用模拟数据")
    HAS_CRAWLER = False


class App:
    """IVAS-IFM主应用程序类"""
    
    def __init__(self):
        """初始化应用程序"""
        self.root = tk.Tk()
        self.setup_window()
        self.create_variables()
        self.create_widgets()
        self.layout_widgets()
        
        # 初始化爬虫管理器
        if HAS_CRAWLER:
            try:
                self.crawler = CrawlerManager()
                logger.info("爬虫管理器已初始化")
            except Exception as e:
                logger.error(f"初始化爬虫管理器失败: {e}")
                self.crawler = None
                messagebox.showwarning("初始化警告", f"爬虫管理器初始化失败: {e}\n系统将使用模拟数据。")
        else:
            self.crawler = None
            logger.warning("爬虫管理器不可用，使用模拟数据")
    
    def setup_window(self):
        """设置窗口"""
        # 获取UI配置
        ui_config = APP_CONFIG.get("ui", {})
        width = ui_config.get("width", 800)
        height = ui_config.get("height", 600)
        title = ui_config.get("title", "IVAS-IFM")
        
        # 配置窗口
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(640, 480)
        
        # 设置窗口图标
        icon_path = BASE_DIR / "assets" / "icon.ico"
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))
    
    def create_variables(self):
        """创建变量"""
        self.search_query = tk.StringVar()
        self.search_results = {}
        self.selected_platforms = {
            platform: tk.BooleanVar(value=True)
            for platform in PLATFORM_CONFIGS.keys()
        }
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding=10)
        
        # 创建搜索框
        self.search_frame = ttk.LabelFrame(self.main_frame, text="搜索", padding=5)
        self.search_entry = ttk.Entry(
            self.search_frame,
            textvariable=self.search_query,
            width=40
        )
        self.search_button = ttk.Button(
            self.search_frame,
            text="搜索",
            command=self.search
        )
        
        # 创建平台选择
        self.platform_frame = ttk.LabelFrame(self.main_frame, text="平台", padding=5)
        self.platform_checkbuttons = {}
        for platform in PLATFORM_CONFIGS:
            self.platform_checkbuttons[platform] = ttk.Checkbutton(
                self.platform_frame,
                text=platform.capitalize(),
                variable=self.selected_platforms[platform]
            )
        
        # 创建结果显示区域
        self.results_frame = ttk.LabelFrame(self.main_frame, text="搜索结果", padding=5)
        self.results_text = tk.Text(self.results_frame, height=15, width=80)
        self.results_scrollbar = ttk.Scrollbar(
            self.results_frame,
            orient="vertical",
            command=self.results_text.yview
        )
        self.results_text.configure(yscrollcommand=self.results_scrollbar.set)
        
        # 创建下载区域
        self.download_frame = ttk.LabelFrame(self.main_frame, text="下载", padding=5)
        self.download_entry = ttk.Entry(self.download_frame, width=50)
        self.download_button = ttk.Button(
            self.download_frame,
            text="下载",
            command=self.download
        )
        
        # 创建状态栏
        self.status_var = tk.StringVar(value=MESSAGES.get("welcome", "欢迎使用"))
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
    
    def layout_widgets(self):
        """布局界面组件"""
        # 布局主框架
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 布局搜索框
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.search_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 布局平台选择
        self.platform_frame.pack(fill=tk.X, padx=5, pady=5)
        for platform, checkbutton in self.platform_checkbuttons.items():
            checkbutton.pack(side=tk.LEFT, padx=10)
        
        # 布局结果显示区域
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 布局下载区域
        self.download_frame.pack(fill=tk.X, padx=5, pady=5)
        self.download_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.download_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 布局状态栏
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def search(self):
        """执行搜索"""
        # 获取搜索关键词
        query = self.search_query.get().strip()
        if not query:
            messagebox.showwarning("搜索提示", "请输入搜索关键词")
            return
        
        # 获取选中的平台
        platforms = [
            platform for platform, var in self.selected_platforms.items()
            if var.get()
        ]
        
        if not platforms:
            messagebox.showwarning("搜索提示", "请至少选择一个平台")
            return
        
        # 清空结果显示
        self.results_text.delete(1.0, tk.END)
        self.status_var.set(f"正在搜索: {query}")
        self.root.update()
        
        try:
            # 使用爬虫管理器搜索
            if self.crawler:
                results = self.crawler.search_videos(query, platforms)
                self.search_results = results
            else:
                # 使用模拟数据
                self.search_results = self._get_mock_results(query, platforms)
            
            # 显示结果
            self._display_results()
            
        except Exception as e:
            logger.error(f"搜索出错: {e}")
            messagebox.showerror("搜索错误", f"搜索过程中出错: {e}")
            self.status_var.set("搜索失败")
    
    def _get_mock_results(self, query, platforms):
        """获取模拟搜索结果"""
        results = {}
        for platform in platforms:
            results[platform] = []
            # 为每个平台生成几个模拟结果
            for i in range(3):
                results[platform].append({
                    "platform": platform,
                    "video_id": f"mock_{platform}_{i}",
                    "title": f"【模拟】{platform.capitalize()} - {query} 视频 {i+1}",
                    "url": f"https://www.{platform}.com/video/mock_{i}",
                    "thumbnail": f"https://via.placeholder.com/320x180.png?text={platform}+Demo",
                    "channel": f"{platform.capitalize()} 演示频道",
                    "publish_date": "2025-05-05",
                    "duration": 60 * (i+1),
                    "views": 1000 * (i+1),
                    "description": f"这是一个模拟的 {platform} 视频，关键词: {query}"
                })
        return results
    
    def _display_results(self):
        """显示搜索结果"""
        if not self.search_results:
            self.results_text.insert(tk.END, MESSAGES.get("no_results", "未找到结果"))
            self.status_var.set("搜索完成: 未找到结果")
            return
        
        total_count = sum(len(videos) for videos in self.search_results.values())
        self.status_var.set(f"搜索完成: 找到 {total_count} 个结果")
        
        # 显示每个平台的结果
        for platform, videos in self.search_results.items():
            self.results_text.insert(tk.END, f"\n===== {platform.upper()} ({len(videos)}) =====\n\n")
            
            for i, video in enumerate(videos):
                self.results_text.insert(tk.END, f"{i+1}. {video['title']}\n")
                self.results_text.insert(tk.END, f"   频道: {video.get('channel', 'N/A')}\n")
                self.results_text.insert(tk.END, f"   时长: {video.get('duration', 0)} 秒\n")
                self.results_text.insert(tk.END, f"   URL: {video['url']}\n\n")
    
    def download(self):
        """下载视频"""
        url = self.download_entry.get().strip()
        if not url:
            messagebox.showwarning("下载提示", "请输入视频URL")
            return
        
        # 选择下载目录
        output_dir = filedialog.askdirectory(
            title="选择下载目录",
            initialdir=str(BASE_DIR / "downloads")
        )
        
        if not output_dir:
            return
        
        self.status_var.set(f"正在下载: {url}")
        self.root.update()
        
        try:
            # 使用爬虫管理器下载
            if self.crawler:
                file_path = self.crawler.download_video(url, output_dir)
            else:
                # 模拟下载
                file_path = self._mock_download(url, output_dir)
            
            if file_path:
                self.status_var.set(MESSAGES.get("download_success", "下载成功").format(path=file_path))
                messagebox.showinfo("下载完成", f"视频已下载到:\n{file_path}")
            else:
                self.status_var.set(MESSAGES.get("download_error", "下载失败").format(error="未知错误"))
                messagebox.showerror("下载失败", "下载过程中出现未知错误")
                
        except Exception as e:
            logger.error(f"下载出错: {e}")
            self.status_var.set(MESSAGES.get("download_error", "下载失败").format(error=str(e)))
            messagebox.showerror("下载错误", f"下载过程中出错: {e}")
    
    def _mock_download(self, url, output_dir):
        """模拟下载"""
        import time
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        file_name = f"mock_video_{int(time.time())}.mp4"
        file_path = os.path.join(output_dir, file_name)
        
        # 创建模拟文件
        with open(file_path, "w") as f:
            f.write(f"这是一个模拟的视频文件，URL: {url}")
        
        return file_path
    
    def run(self):
        """运行应用程序"""
        logger.info("应用程序开始运行")
        self.root.mainloop()
        logger.info("应用程序已关闭")


def main():
    """主函数"""
    app = App()
    app.run()


if __name__ == "__main__":
    main() 