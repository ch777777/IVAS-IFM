#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Download Manager for the VCA module.

This module manages the download process of videos from multiple platforms.
"""

import os
import logging
import time
import threading
import queue
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor

try:
    from src.config.settings import DOWNLOAD_CONFIG
except ImportError:
    # Default download configuration
    DOWNLOAD_CONFIG = {
        "default_output_dir": "downloads",
        "max_concurrent_downloads": 3,
        "timeout": 600,  # 10 minutes
        "retry_count": 3,
        "chunk_size": 8192,  # 8 KB
        "file_formats": {
            "video": ["mp4", "webm", "mkv", "avi"],
            "audio": ["mp3", "wav", "m4a", "aac"]
        }
    }

logger = logging.getLogger(__name__)

class DownloadTask:
    """Represents a download task for a video"""
    
    def __init__(self, url: str, output_path: str, platform: str, 
                 video_info: Dict[str, Any] = None,
                 progress_callback: Callable[[str, float], None] = None):
        """
        Initialize a download task
        
        Args:
            url: URL of the video to download
            output_path: Path where the video will be saved
            platform: Platform identifier (youtube, bilibili, etc.)
            video_info: Additional video metadata
            progress_callback: Callback function to report progress updates
        """
        self.url = url
        self.output_path = output_path
        self.platform = platform
        self.video_info = video_info or {}
        self.progress_callback = progress_callback
        self.status = "pending"  # pending, downloading, completed, failed, cancelled
        self.progress = 0.0  # 0.0 to 1.0
        self.error = None
        self.start_time = None
        self.end_time = None
        self.id = f"{platform}_{int(time.time() * 1000)}"
        
    def update_progress(self, progress: float, status: str = None):
        """Update the download progress"""
        self.progress = max(0.0, min(1.0, progress))
        if status:
            self.status = status
            
        if self.progress_callback:
            self.progress_callback(self.id, self.progress)
            
    def get_info(self) -> Dict[str, Any]:
        """Get task information as a dictionary"""
        return {
            "id": self.id,
            "url": self.url,
            "output_path": self.output_path,
            "platform": self.platform,
            "status": self.status,
            "progress": self.progress,
            "error": str(self.error) if self.error else None,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "title": self.video_info.get("title", "Unknown"),
            "author": self.video_info.get("author", "Unknown"),
            "duration": self.video_info.get("duration", "Unknown"),
        }


class DownloadManager:
    """
    Manages the video download process across multiple platforms.
    
    This class coordinates the download process, dispatching download tasks
    to platform-specific adapters and managing concurrent downloads.
    """
    
    def __init__(self, platform_adapters: Dict[str, Any] = None):
        """
        Initialize the download manager
        
        Args:
            platform_adapters: Dictionary mapping platform names to adapter instances
        """
        self.platform_adapters = platform_adapters or {}
        self.tasks = {}  # Dictionary of download tasks by ID
        self.active_tasks = set()  # Set of IDs for currently active tasks
        self.task_queue = queue.Queue()  # Queue for pending download tasks
        self.download_thread = None
        self.is_running = False
        self.output_dir = DOWNLOAD_CONFIG.get("default_output_dir", "downloads")
        self.max_concurrent = DOWNLOAD_CONFIG.get("max_concurrent_downloads", 3)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("DownloadManager initialized")
        
    def start(self):
        """Start the download manager"""
        if not self.is_running:
            self.is_running = True
            self.download_thread = threading.Thread(
                target=self._process_queue,
                daemon=True
            )
            self.download_thread.start()
            logger.info("DownloadManager started")
            
    def stop(self):
        """Stop the download manager"""
        self.is_running = False
        if self.download_thread and self.download_thread.is_alive():
            self.download_thread.join(timeout=5)
        logger.info("DownloadManager stopped")
        
    def download(self, url: str, platform: str, output_dir: Optional[str] = None, 
                 filename: Optional[str] = None, video_info: Dict[str, Any] = None,
                 progress_callback: Optional[Callable] = None) -> str:
        """
        Queue a video for download
        
        Args:
            url: URL of the video to download
            platform: Platform identifier
            output_dir: Directory to save the video
            filename: Filename to use (default: auto-generated)
            video_info: Additional video metadata
            progress_callback: Callback for progress updates
            
        Returns:
            ID of the created download task
        """
        if not url:
            raise ValueError("URL cannot be empty")
            
        if not platform:
            platform = self._detect_platform_from_url(url)
            
        if not platform:
            raise ValueError(f"Couldn't determine platform for URL: {url}")
            
        # Set output directory
        if not output_dir:
            output_dir = self.output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename if not provided
        if not filename:
            title = video_info.get("title", "") if video_info else ""
            if title:
                # Clean up title for use as filename
                filename = ''.join(c for c in title if c.isalnum() or c in ' ._-')
                filename = filename.strip()
            
            if not filename:
                filename = f"video_{platform}_{int(time.time())}"
                
        # Add extension if missing
        if not any(filename.endswith(f".{ext}") for ext in 
                  DOWNLOAD_CONFIG.get("file_formats", {}).get("video", ["mp4"])):
            filename += ".mp4"
            
        output_path = os.path.join(output_dir, filename)
        
        # Create download task
        task = DownloadTask(
            url=url,
            output_path=output_path,
            platform=platform,
            video_info=video_info,
            progress_callback=progress_callback
        )
        
        # Store and queue the task
        self.tasks[task.id] = task
        self.task_queue.put(task)
        
        # Ensure manager is running
        self.start()
        
        logger.info(f"Queued download task {task.id} for URL: {url}")
        return task.id
    
    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get information for all tasks"""
        return [task.get_info() for task in self.tasks.values()]
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a download task"""
        task = self.tasks.get(task_id)
        if not task:
            return False
            
        if task.status == "pending":
            # Task is in queue, mark as cancelled
            task.status = "cancelled"
            return True
        elif task.status == "downloading":
            # Task is active, more complex to cancel
            # For simplicity, we'll just mark it but won't interrupt the actual download
            task.status = "cancelling"
            return True
        else:
            # Task already completed or failed
            return False
    
    def _process_queue(self):
        """Process the download queue"""
        while self.is_running:
            try:
                # Process up to max_concurrent downloads
                while len(self.active_tasks) < self.max_concurrent and not self.task_queue.empty():
                    task = self.task_queue.get(block=False)
                    
                    # Skip if cancelled
                    if task.status == "cancelled":
                        self.task_queue.task_done()
                        continue
                        
                    # Start download in a new thread
                    threading.Thread(
                        target=self._download_task,
                        args=(task,),
                        daemon=True
                    ).start()
                    
                    self.active_tasks.add(task.id)
                    
                time.sleep(0.5)  # Short sleep to prevent CPU overuse
                    
            except queue.Empty:
                time.sleep(1)  # Wait for new tasks
            except Exception as e:
                logger.exception(f"Error in download queue processing: {e}")
                time.sleep(5)  # Longer sleep on error
                
    def _download_task(self, task: DownloadTask):
        """Download a single task"""
        try:
            task.start_time = time.time()
            task.status = "downloading"
            task.update_progress(0.0, "downloading")
            logger.info(f"Starting download for task {task.id}: {task.url}")
            
            # Use platform adapter if available
            adapter = self.platform_adapters.get(task.platform)
            if adapter:
                # Call platform-specific download method
                result = adapter.download_video(
                    task.url, 
                    os.path.dirname(task.output_path),
                    os.path.basename(task.output_path),
                    progress_callback=task.update_progress
                )
                success = bool(result)
            else:
                # Simulate download if no adapter is available
                success = self._simulate_download(task)
                
            task.end_time = time.time()
            
            if success and task.status != "cancelled":
                task.update_progress(1.0, "completed")
                logger.info(f"Download completed for task {task.id}")
            else:
                task.update_progress(task.progress, "failed")
                logger.warning(f"Download failed for task {task.id}")
                
        except Exception as e:
            task.error = e
            task.status = "failed"
            task.end_time = time.time()
            logger.exception(f"Error downloading task {task.id}: {e}")
        finally:
            # Remove from active tasks
            self.active_tasks.discard(task.id)
            self.task_queue.task_done()
    
    def _simulate_download(self, task: DownloadTask) -> bool:
        """Simulate a download (for testing or when no adapter is available)"""
        total_steps = 10
        for i in range(total_steps):
            if task.status == "cancelled":
                return False
                
            # Simulate download progress
            progress = (i + 1) / total_steps
            task.update_progress(progress)
            time.sleep(0.5)  # Simulate download time
            
        # Create an empty file
        try:
            with open(task.output_path, 'w') as f:
                f.write(f"Simulated download from {task.url}")
            return True
        except Exception as e:
            logger.error(f"Error creating simulated download file: {e}")
            return False
            
    def _detect_platform_from_url(self, url: str) -> Optional[str]:
        """Detect which platform a URL belongs to"""
        url = url.lower()
        
        platform_domains = {
            "youtube": ["youtube.com", "youtu.be"],
            "bilibili": ["bilibili.com"],
            "tiktok": ["tiktok.com", "douyin.com"],
            "weibo": ["weibo.com"],
            "facebook": ["facebook.com", "fb.com"]
        }
        
        for platform, domains in platform_domains.items():
            if any(domain in url for domain in domains):
                return platform
                
        return None 