#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
IVAS-IFM GUI应用程序

实现视频搜索和下载功能的图形界面
"""

import os
import sys
import time
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import importlib.util
from typing import Dict, List, Any, Optional, Tuple

# 设置基本路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# 设置日志
logger = logging.getLogger(__name__)

# 尝试导入设置
try:
    from src.config.settings import APP_CONFIG, MESSAGES, PLATFORM_CONFIGS
except ImportError:
    # 如果无法导入，使用默认值
    logger.warning("无法导入设置，使用默认值")
    
    # 默认配置
    APP_CONFIG = {
        "app_name": "IVAS-IFM",
        "app_version": "1.1.0",
        "ui": {
            "theme": "default",
            "width": 1000,
            "height": 700,
            "title": "IVAS-IFM - 智能视频分析系统"
        }
    }
    
    MESSAGES = {
        "welcome": "欢迎使用 IVAS-IFM 智能视频分析系统",
        "search_prompt": "输入关键词搜索多平台视频",
        "no_results": "未找到匹配的结果，请尝试不同的关键词。",
        "download_success": "视频已成功下载到 {path}",
        "download_error": "下载视频时出错: {error}",
        "processing_start": "正在处理视频: {title}",
        "processing_complete": "处理完成: {title}"
    }
    
    PLATFORM_CONFIGS = {
        "youtube": {"max_results": 10},
        "bilibili": {"max_results": 10},
        "tiktok": {"max_results": 10},
        "weibo": {"max_results": 10},
        "facebook": {"max_results": 10}
    }

# 尝试导入VCA模块
try:
    from src.modules.vca.crawler_manager import CrawlerManager
except ImportError:
    logger.warning("无法导入爬虫管理器，使用模拟数据")
    CrawlerManager = None


class App:
    """IVAS-IFM主应用程序类"""
    
    def __init__(self):
        """初始化应用程序"""
        self.root = tk.Tk()
        self.setup_window()
        self.create_variables()
        self.create_widgets()
        self.layout_widgets()
        self.bind_events()
        
        # 初始化爬虫管理器(如果可用)
        if CrawlerManager is not None:
            self.crawler_manager = CrawlerManager()
        else:
            self.crawler_manager = None
            
        logger.info("应用程序已初始化")
        
    def setup_window(self):
        """配置主窗口属性"""
        self.root.title(APP_CONFIG['ui']['title'])
        self.root.geometry(f"{APP_CONFIG['ui']['width']}x{APP_CONFIG['ui']['height']}")
        
        # 尝试设置图标
        icon_path = BASE_DIR / "assets" / "icon.ico"
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))
            
        # 配置样式
        self.style = ttk.Style()
        self.style.theme_use(APP_CONFIG['ui']['theme'])
        
        # 配置高DPI支持
        try:
            self.root.tk.call('tk', 'scaling', 1.5)
        except:
            logger.warning("无法设置高DPI缩放")
        
    def create_variables(self):
        """创建Tkinter变量"""
        self.search_query = tk.StringVar()
        self.status_message = tk.StringVar(value=MESSAGES.get('welcome', "欢迎使用"))
        self.selected_platforms = {
            platform: tk.BooleanVar(value=True) 
            for platform in PLATFORM_CONFIGS.keys()
        }
        self.is_searching = tk.BooleanVar(value=False)
        self.is_downloading = tk.BooleanVar(value=False)
        self.search_results = {}
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        self.main_frame = ttk.Frame(self.root, padding=10)
        
        # 菜单栏
        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="退出", command=self.on_close)
        self.menu_bar.add_cascade(label="文件", menu=self.file_menu)
        
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="关于", command=self.show_about)
        self.menu_bar.add_cascade(label="帮助", menu=self.help_menu)
        
        self.root.config(menu=self.menu_bar)
        
        # 顶部面板
        self.top_panel = ttk.Frame(self.main_frame)
        
        # 搜索框
        search_placeholder = MESSAGES.get('search_prompt', "输入关键词搜索")
        self.search_frame = ttk.LabelFrame(self.top_panel, text="搜索", padding=5)
        self.search_entry = ttk.Entry(
            self.search_frame,
            textvariable=self.search_query,
            width=40,
            font=("Microsoft YaHei UI", 10)
        )
        
        # 平台选择区域
        self.platform_selector = ttk.LabelFrame(self.top_panel, text="选择平台", padding=5)
        
        # 平台复选框
        self.platform_checkbuttons = {}
        for platform in PLATFORM_CONFIGS.keys():
            self.platform_checkbuttons[platform] = ttk.Checkbutton(
                self.platform_selector,
                text=platform.capitalize(),
                variable=self.selected_platforms[platform]
            )
        
        # 搜索按钮
        self.search_button = ttk.Button(
            self.top_panel,
            text="搜索",
            command=self.perform_search,
            style="Accent.TButton"
        )
        
        # 创建自定义按钮样式
        self.style.configure(
            "Accent.TButton",
            background="#4a86e8",
            foreground="white",
            font=("Microsoft YaHei UI", 10)
        )
        
        # 结果区域
        self.results_frame = ttk.Frame(self.main_frame)
        self.results_notebook = ttk.Notebook(self.results_frame)
        
        # 所有结果标签页
        self.all_results_tab = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.all_results_tab, text="所有结果")
        
        # 平台特定标签页
        self.platform_tabs = {}
        for platform in PLATFORM_CONFIGS.keys():
            tab = ttk.Frame(self.results_notebook)
            self.platform_tabs[platform] = tab
            self.results_notebook.add(tab, text=platform.capitalize())
        
        # 进度指示器
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='indeterminate',
            length=200
        )
        self.progress_label = ttk.Label(
            self.progress_frame,
            text="",
            anchor=tk.CENTER
        )
        
        # 状态栏
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_message,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        
    def layout_widgets(self):
        """布局界面组件"""
        # 主框架
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部面板
        self.top_panel.pack(fill=tk.X, pady=(0, 10))
        
        # 搜索框
        self.search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.search_entry.pack(fill=tk.X, padx=5, pady=5, expand=True)
        
        # 平台选择
        self.platform_selector.pack(side=tk.LEFT, padx=(0, 10))
        for platform, checkbutton in self.platform_checkbuttons.items():
            checkbutton.pack(anchor=tk.W, padx=5, pady=2)
        
        # 搜索按钮
        self.search_button.pack(side=tk.LEFT, pady=5)
        
        # 结果区域
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 进度指示器
        self.progress_frame.pack(fill=tk.X, pady=5)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=2)
        self.progress_label.pack(fill=tk.X, padx=5)
        self.progress_frame.pack_forget()  # 初始隐藏
        
        # 状态栏
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def bind_events(self):
        """绑定事件回调"""
        self.search_entry.bind("<Return>", lambda event: self.perform_search())
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def perform_search(self):
        """执行搜索操作"""
        query = self.search_query.get().strip()
        if not query:
            messagebox.showinfo("提示", "请输入搜索关键词")
            return
            
        # 获取选择的平台
        selected_platforms = [
            platform for platform, var in self.selected_platforms.items() 
            if var.get()
        ]
        
        if not selected_platforms:
            messagebox.showinfo("提示", "请至少选择一个平台")
            return
            
        # 更新UI状态
        self.status_message.set(f"正在搜索: {query}")
        self.is_searching.set(True)
        self.show_progress("搜索中，请稍候...")
        self.root.update()
        
        # 在新线程中执行搜索
        threading.Thread(
            target=self._search_thread,
            args=(query, selected_platforms),
            daemon=True
        ).start()
        
    def _search_thread(self, query, platforms):
        """搜索线程函数"""
        try:
            if self.crawler_manager:
                # 使用实际爬虫
                self.search_results = self.crawler_manager.search_videos(
                    query=query,
                    platforms=platforms,
                    max_results=5
                )
            else:
                # 使用模拟数据
                self.search_results = self._simulate_search_results(query, platforms)
                
            # 切换回主线程更新UI
            self.root.after(0, self._update_results_ui)
        except Exception as e:
            logger.exception(f"搜索过程中出错: {e}")
            self.root.after(0, lambda: self._show_error(f"搜索出错: {str(e)}"))
        finally:
            self.root.after(0, self._finalize_search)
            
    def _update_results_ui(self):
        """更新搜索结果UI"""
        total_count = sum(len(results) for results in self.search_results.values())
        self.status_message.set(f"找到 {total_count} 个结果")
        
        # 清空现有结果
        for widget in self.all_results_tab.winfo_children():
            widget.destroy()
            
        for platform, tab in self.platform_tabs.items():
            for widget in tab.winfo_children():
                widget.destroy()
        
        if total_count == 0:
            # 无结果提示
            no_results_label = ttk.Label(
                self.all_results_tab,
                text=MESSAGES.get('no_results', "未找到结果"),
                font=("Microsoft YaHei UI", 12),
                anchor=tk.CENTER
            )
            no_results_label.pack(pady=50)
            return
            
        # 创建滚动画布 - 所有结果
        self._create_results_canvas(self.all_results_tab, all_platforms=True)
        
        # 创建平台特定滚动画布
        for platform, results in self.search_results.items():
            if results:
                self._create_results_canvas(
                    self.platform_tabs[platform], 
                    platform=platform
                )
                
    def _create_results_canvas(self, parent, platform=None, all_platforms=False):
        """创建滚动结果画布"""
        # 创建画布和滚动条
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            parent, 
            orient=tk.VERTICAL, 
            command=canvas.yview
        )
        
        # 创建帧来包含结果
        results_frame = ttk.Frame(canvas)
        
        # 配置滚动
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 在画布中创建窗口
        canvas.create_window(
            (0, 0), 
            window=results_frame, 
            anchor=tk.NW, 
            tags="results_frame"
        )
        
        row = 0
        # 填充结果
        if all_platforms:
            # 所有平台的结果
            for platform_name, results in self.search_results.items():
                if results:
                    for result in results:
                        self._create_result_item(
                            results_frame, 
                            result, 
                            platform_name, 
                            row
                        )
                        row += 1
        elif platform and platform in self.search_results:
            # 特定平台的结果
            for result in self.search_results[platform]:
                self._create_result_item(
                    results_frame, 
                    result, 
                    platform, 
                    row
                )
                row += 1
                
        # 更新滚动范围
        results_frame.update_idletasks()
        canvas.config(
            scrollregion=canvas.bbox("all"),
            width=APP_CONFIG['ui']['width'] - 50
        )
        
        # 绑定鼠标滚轮
        canvas.bind_all(
            "<MouseWheel>", 
            lambda event, canvas=canvas: self._on_mousewheel(event, canvas)
        )
                
    def _create_result_item(self, parent, item, platform, row):
        """创建一个结果项"""
        frame = ttk.Frame(parent, padding=10, style="ResultItem.TFrame")
        
        # 设置结果项样式
        self.style.configure("ResultItem.TFrame", relief=tk.GROOVE)
        
        # 标题
        title_label = ttk.Label(
            frame,
            text=item.get('title', '未知标题'),
            font=("Microsoft YaHei UI", 11, "bold"),
            wraplength=800
        )
        
        # 平台标签
        platform_label = ttk.Label(
            frame,
            text=f"平台: {platform.capitalize()}",
            font=("Microsoft YaHei UI", 9)
        )
        
        # 视频信息
        info_text = (
            f"作者: {item.get('author', '未知')}\n"
            f"时长: {item.get('duration', '未知')}\n"
            f"观看次数: {item.get('views', '未知')}\n"
            f"发布日期: {item.get('published', '未知')}"
        )
        
        info_label = ttk.Label(
            frame,
            text=info_text,
            font=("Microsoft YaHei UI", 9),
            wraplength=800
        )
        
        # 描述
        description = item.get('description', '')
        if description:
            desc_label = ttk.Label(
                frame,
                text=description[:200] + ("..." if len(description) > 200 else ""),
                font=("Microsoft YaHei UI", 9),
                wraplength=800
            )
        else:
            desc_label = None
        
        # 下载按钮
        download_button = ttk.Button(
            frame,
            text="下载",
            command=lambda url=item['url']: self.download_video(url, item)
        )
        
        # 布局
        title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5), columnspan=2)
        platform_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        info_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        if desc_label:
            desc_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 5), columnspan=2)
            download_button.grid(row=4, column=0, sticky=tk.W)
        else:
            download_button.grid(row=3, column=0, sticky=tk.W)
        
        frame.grid(row=row, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        
    def _on_mousewheel(self, event, canvas):
        """处理鼠标滚轮滚动"""
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
    def _finalize_search(self):
        """完成搜索，更新UI状态"""
        self.is_searching.set(False)
        self.hide_progress()
        
    def download_video(self, url, video_data):
        """下载视频"""
        if self.is_downloading.get():
            messagebox.showinfo("提示", "已有下载任务正在进行，请等待完成")
            return
            
        # 询问保存位置
        output_dir = filedialog.askdirectory(title="选择保存位置")
        if not output_dir:
            return
            
        # 更新UI状态
        self.is_downloading.set(True)
        self.status_message.set(f"正在下载视频: {video_data.get('title', url)}")
        self.show_progress("下载中，请稍候...")
        
        # 在新线程中执行下载
        threading.Thread(
            target=self._download_thread,
            args=(url, output_dir, video_data),
            daemon=True
        ).start()
        
    def _download_thread(self, url, output_dir, video_data):
        """下载线程函数"""
        try:
            title = video_data.get('title', '')
            # 使用视频标题作为文件名（去除无效字符）
            filename = ''.join(c for c in title if c.isalnum() or c in ' ._-')
            
            if self.crawler_manager:
                # 使用实际下载
                file_path = self.crawler_manager.download_video(
                    url, output_dir, filename
                )
            else:
                # 模拟下载
                file_path = self._simulate_download(url, output_dir, filename)
                
            # 切换回主线程更新UI
            success_msg = MESSAGES.get('download_success', "下载成功: {path}").format(path=file_path)
            self.root.after(0, lambda: messagebox.showinfo("下载完成", success_msg))
            self.root.after(0, lambda: self.status_message.set(success_msg))
        except Exception as e:
            logger.exception(f"下载过程中出错: {e}")
            error_msg = MESSAGES.get('download_error', "下载错误: {error}").format(error=str(e))
            self.root.after(0, lambda: self._show_error(error_msg))
        finally:
            self.root.after(0, self._finalize_download)
            
    def _finalize_download(self):
        """完成下载，更新UI状态"""
        self.is_downloading.set(False)
        self.hide_progress()
        
    def _simulate_download(self, url, output_dir, filename):
        """模拟下载过程"""
        # 模拟下载延迟
        time.sleep(3)
        
        # 创建一个空文件
        filename = filename or f"video_{int(time.time())}"
        if not filename.endswith('.mp4'):
            filename += '.mp4'
            
        file_path = os.path.join(output_dir, filename)
        with open(file_path, 'w') as f:
            f.write(f"模拟下载的视频文件 - 来自URL: {url}")
            
        return file_path
        
    def _simulate_search_results(self, query, platforms):
        """生成模拟搜索结果"""
        time.sleep(2)  # 模拟搜索延迟
        
        results = {}
        for platform in platforms:
            platform_results = []
            for i in range(1, 6):
                platform_results.append({
                    'title': f"{query} - 结果 {i} (来自 {platform})",
                    'url': f"https://{platform}.com/video/{i}",
                    'author': f"用户{platform}{i}",
                    'views': i * 1000,
                    'duration': f"{i}:00",
                    'published': f"2023-05-0{i}",
                    'description': f"这是一个关于 {query} 的示例视频，由 {platform} 平台的用户发布。"
                })
            results[platform] = platform_results
            
        return results
        
    def show_progress(self, message=None):
        """显示进度指示器"""
        if message:
            self.progress_label.config(text=message)
        self.progress_frame.pack(fill=tk.X, pady=5)
        self.progress_bar.start()
        
    def hide_progress(self):
        """隐藏进度指示器"""
        self.progress_bar.stop()
        self.progress_frame.pack_forget()
        
    def _show_error(self, message):
        """显示错误信息"""
        messagebox.showerror("错误", message)
        self.status_message.set(f"错误: {message}")
        
    def show_about(self):
        """显示关于对话框"""
        about_text = (
            f"{APP_CONFIG.get('app_name', 'IVAS-IFM')}\n\n"
            f"版本: {APP_CONFIG.get('app_version', '1.1.0')}\n\n"
            f"这是一个智能视频采集和分析系统，支持从多个平台搜索、下载和管理视频内容。\n\n"
            f"作者: {APP_CONFIG.get('app_author', 'xiangye72')}"
        )
        messagebox.showinfo("关于", about_text)
        
    def on_close(self):
        """处理窗口关闭事件"""
        if self.is_searching.get() or self.is_downloading.get():
            if not messagebox.askyesno("确认退出", "有正在进行的任务，确定要退出吗？"):
                return
                
        self.root.destroy()
        
    def run(self):
        """运行应用程序"""
        self.root.mainloop()


def main():
    """程序入口"""
    app = App()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main()) 