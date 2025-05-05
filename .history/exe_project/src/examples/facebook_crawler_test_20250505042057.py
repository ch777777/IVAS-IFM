#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Facebook视频爬虫测试脚本
"""
import os
import sys
import logging
import time
from pathlib import Path

# 添加项目根目录到系统路径
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from src.modules.vca.platform_adapters.facebook import FacebookAdapter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_search_videos():
    """测试搜索视频功能"""
    adapter = FacebookAdapter(use_selenium=True)
    
    try:
        # 搜索视频
        search_query = "climate change"
        limit = 5
        
        logger.info(f"开始搜索视频: {search_query}, 限制: {limit}")
        results = adapter.search_videos(search_query=search_query, limit=limit)
        
        logger.info(f"找到 {len(results)} 个视频")
        
        # 打印搜索结果
        for i, video in enumerate(results):
            logger.info(f"视频 {i+1}:")
            logger.info(f"  标题: {video.get('title')}")
            logger.info(f"  URL: {video.get('url')}")
            logger.info(f"  作者: {video.get('author')}")
            logger.info("  ------------------------")
            
    except Exception as e:
        logger.error(f"搜索视频失败: {str(e)}")
    finally:
        adapter.close()
        
def test_video_info():
    """测试获取视频信息功能"""
    adapter = FacebookAdapter(use_selenium=True)
    
    try:
        # 测试视频地址
        video_url = "https://www.facebook.com/watch?v=860089585525258"
        
        logger.info(f"获取视频信息: {video_url}")
        video_info = adapter.get_video_info(video_url)
        
        if video_info:
            logger.info("视频信息:")
            logger.info(f"  标题: {video_info.get('title')}")
            logger.info(f"  平台: {video_info.get('platform')}")
            logger.info(f"  作者: {video_info.get('author')}")
            logger.info(f"  时长: {video_info.get('duration')} 秒")
            logger.info(f"  上传日期: {video_info.get('upload_date')}")
            logger.info(f"  缩略图: {video_info.get('thumbnail')}")
            logger.info(f"  标清源: {video_info.get('sd_src')}")
            logger.info(f"  高清源: {video_info.get('hd_src')}")
        else:
            logger.error("未能获取视频信息")
            
    except Exception as e:
        logger.error(f"获取视频信息失败: {str(e)}")
    finally:
        adapter.close()
        
def test_download_video():
    """测试下载视频功能"""
    adapter = FacebookAdapter(use_selenium=True)
    
    try:
        # 测试视频地址
        video_url = "https://www.facebook.com/watch?v=860089585525258"
        
        # 创建输出目录
        output_dir = os.path.join(ROOT_DIR, "downloads", "facebook")
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"下载视频: {video_url}")
        filepath = adapter.download_video(
            video_url=video_url,
            output_path=output_dir
        )
        
        if filepath:
            logger.info(f"视频已下载到: {filepath}")
        else:
            logger.error("视频下载失败")
            
    except Exception as e:
        logger.error(f"下载视频失败: {str(e)}")
    finally:
        adapter.close()

if __name__ == "__main__":
    # 测试搜索功能
    test_search_videos()
    
    # 等待几秒
    time.sleep(2)
    
    # 测试获取视频信息
    test_video_info()
    
    # 等待几秒
    time.sleep(2)
    
    # 测试下载视频
    test_download_video() 