"""
爬虫管理器
负责协调多个爬虫实例，管理视频采集任务
"""
import logging
import concurrent.futures
import importlib
import os
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)

class CrawlerManager:
    """爬虫管理器，用于协调多个平台爬虫实例"""
    
    def __init__(self, max_workers: int = 3, timeout: int = 300):
        """
        初始化爬虫管理器
        
        Args:
            max_workers: 最大并发爬虫数量
            timeout: 爬虫任务超时时间(秒)
        """
        self.max_workers = max_workers
        self.timeout = timeout
        self.platform_adapters = {}  # 平台适配器字典
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.running_tasks = {}  # 正在运行的任务
        
    def register_platform(self, platform_name: str, adapter_class: Any) -> bool:
        """
        注册平台适配器
        
        Args:
            platform_name: 平台名称
            adapter_class: 适配器类
            
        Returns:
            注册是否成功
        """
        if platform_name in self.platform_adapters:
            logger.warning(f"平台 {platform_name} 适配器已存在，将被覆盖")
            
        self.platform_adapters[platform_name] = adapter_class
        logger.info(f"已注册平台适配器: {platform_name}")
        return True
        
    def load_platform_adapters(self, adapter_dir: str = None) -> int:
        """
        从指定目录动态加载平台适配器
        
        Args:
            adapter_dir: 适配器目录路径，默认为当前模块下的platform_adapters
            
        Returns:
            加载的适配器数量
        """
        if adapter_dir is None:
            # 默认使用当前模块目录下的platform_adapters
            current_dir = os.path.dirname(os.path.abspath(__file__))
            adapter_dir = os.path.join(current_dir, 'platform_adapters')
            
        if not os.path.exists(adapter_dir) or not os.path.isdir(adapter_dir):
            logger.error(f"适配器目录不存在: {adapter_dir}")
            return 0
            
        count = 0
        # 遍历目录加载所有平台适配器
        for filename in os.listdir(adapter_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]  # 去掉.py后缀
                try:
                    # 动态导入模块
                    module_path = f"src.modules.vca.platform_adapters.{module_name}"
                    module = importlib.import_module(module_path)
                    
                    # 获取适配器类，约定每个适配器模块都有一个与文件名相同的类
                    adapter_class = getattr(module, module_name.capitalize() + 'Adapter')
                    platform_name = getattr(module, 'PLATFORM_NAME', module_name)
                    
                    self.register_platform(platform_name, adapter_class)
                    count += 1
                except (ImportError, AttributeError) as e:
                    logger.error(f"加载平台适配器 {module_name} 失败: {str(e)}")
        
        logger.info(f"共加载了 {count} 个平台适配器")
        return count
        
    def crawl(self, 
              platform: str, 
              search_query: str, 
              limit: int = 10, 
              filters: Dict = None) -> Tuple[str, List[Dict]]:
        """
        执行视频爬取任务
        
        Args:
            platform: 平台名称
            search_query: 搜索关键词
            limit: 限制结果数量
            filters: 过滤条件字典
            
        Returns:
            任务ID和结果列表
        """
        if platform not in self.platform_adapters:
            raise ValueError(f"不支持的平台: {platform}，请先注册平台适配器")
            
        # 创建平台适配器实例
        adapter_class = self.platform_adapters[platform]
        adapter = adapter_class()
        
        # 创建任务并提交到线程池
        task_id = f"{platform}_{search_query}_{limit}"
        future = self.executor.submit(
            adapter.search_videos,
            search_query=search_query,
            limit=limit,
            filters=filters or {}
        )
        self.running_tasks[task_id] = future
        
        # 等待任务完成或超时
        try:
            results = future.result(timeout=self.timeout)
            logger.info(f"任务 {task_id} 完成，获取到 {len(results)} 个结果")
            return task_id, results
        except concurrent.futures.TimeoutError:
            logger.error(f"任务 {task_id} 超时")
            future.cancel()
            return task_id, []
        except Exception as e:
            logger.error(f"任务 {task_id} 执行失败: {str(e)}")
            return task_id, []
            
    def crawl_multi_platform(self, 
                            search_query: str, 
                            platforms: List[str] = None, 
                            limit_per_platform: int = 5,
                            filters: Dict = None) -> Dict[str, List[Dict]]:
        """
        从多个平台爬取视频
        
        Args:
            search_query: 搜索关键词
            platforms: 平台列表，默认为所有已注册平台
            limit_per_platform: 每个平台的结果限制
            filters: 过滤条件字典
            
        Returns:
            各平台的结果字典
        """
        if not platforms:
            platforms = list(self.platform_adapters.keys())
            
        futures = {}
        results = {}
        
        # 提交所有平台的爬取任务
        for platform in platforms:
            if platform not in self.platform_adapters:
                logger.warning(f"不支持的平台: {platform}，已跳过")
                continue
                
            task_id, _ = self.crawl(
                platform=platform,
                search_query=search_query,
                limit=limit_per_platform,
                filters=filters
            )
            futures[platform] = self.running_tasks[task_id]
            
        # 收集所有平台的结果
        for platform, future in futures.items():
            try:
                platform_results = future.result(timeout=self.timeout)
                results[platform] = platform_results
            except Exception as e:
                logger.error(f"获取平台 {platform} 结果失败: {str(e)}")
                results[platform] = []
                
        return results
        
    def cancel_task(self, task_id: str) -> bool:
        """
        取消正在运行的任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        if task_id not in self.running_tasks:
            logger.warning(f"任务 {task_id} 不存在或已完成")
            return False
            
        future = self.running_tasks[task_id]
        cancelled = future.cancel()
        if cancelled:
            logger.info(f"已取消任务: {task_id}")
        else:
            logger.warning(f"无法取消任务: {task_id}，可能已经完成或正在运行")
            
        return cancelled
        
    def shutdown(self, wait: bool = True):
        """
        关闭爬虫管理器
        
        Args:
            wait: 是否等待所有任务完成
        """
        self.executor.shutdown(wait=wait)
        logger.info("爬虫管理器已关闭")
        
    def get_supported_platforms(self) -> List[str]:
        """
        获取所有支持的平台列表
        
        Returns:
            平台名称列表
        """
        return list(self.platform_adapters.keys())


# 示例用法
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建爬虫管理器
    manager = CrawlerManager(max_workers=3)
    
    # 加载平台适配器
    adapter_count = manager.load_platform_adapters()
    print(f"加载了 {adapter_count} 个平台适配器")
    
    # 输出支持的平台
    platforms = manager.get_supported_platforms()
    print(f"支持的平台: {platforms}")
    
    # 关闭管理器
    manager.shutdown() 