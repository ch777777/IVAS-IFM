"""
Video Crawling & Aggregation (VCA) module.

This module handles video crawling and aggregation from multiple platforms.
"""

from .crawler_manager import CrawlerManager
from .download_manager import DownloadManager

__all__ = ["CrawlerManager", "DownloadManager"] 
 
 