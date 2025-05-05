import os
import sys
import time
import subprocess
import logging
import argparse
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("tikhub-starter")

def start_api_service(background=True):
    """启动API服务"""
    logger.info("启动TikHub API服务...")
    
    cmd = [sys.executable, "run_tikhub_api_updated.py"]
    if background:
        # 在后台运行
        try:
            if os.name == 'nt':  # Windows
                process = subprocess.Popen(
                    cmd, 
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:  # Unix/Linux/Mac
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setpgrp  # 在新的进程组中运行
                )
            
            logger.info(f"API服务已在后台启动，进程ID: {process.pid}")
            return process
        except Exception as e:
            logger.error(f"启动API服务失败: {e}")
            return None
    else:
        # 在前台运行
        try:
            subprocess.run(cmd)
            return None
        except KeyboardInterrupt:
            logger.info("API服务已停止")
            return None
        except Exception as e:
            logger.error(f"启动API服务失败: {e}")
            return None

def start_web_app(background=True):
    """启动Web应用"""
    logger.info("启动TikHub Web应用...")
    
    cmd = [sys.executable, "web_app.py"]
    if background:
        # 在后台运行
        try:
            if os.name == 'nt':  # Windows
                process = subprocess.Popen(
                    cmd, 
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:  # Unix/Linux/Mac
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setpgrp  # 在新的进程组中运行
                )
            
            logger.info(f"Web应用已在后台启动，进程ID: {process.pid}")
            return process
        except Exception as e:
            logger.error(f"启动Web应用失败: {e}")
            return None
    else:
        # 在前台运行
        try:
            subprocess.run(cmd)
            return None
        except KeyboardInterrupt:
            logger.info("Web应用已停止")
            return None
        except Exception as e:
            logger.error(f"启动Web应用失败: {e}")
            return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="TikHub 启动器")
    parser.add_argument("--api-only", action="store_true", help="只启动API服务")
    parser.add_argument("--web-only", action="store_true", help="只启动Web应用")
    parser.add_argument("--foreground", action="store_true", help="在前台运行服务")
    
    args = parser.parse_args()
    
    api_process = None
    web_process = None
    
    try:
        # 启动API服务
        if not args.web_only:
            api_process = start_api_service(not args.foreground)
            # 等待API服务启动
            if api_process:
                logger.info("等待API服务启动...")
                time.sleep(3)
        
        # 启动Web应用
        if not args.api_only:
            web_process = start_web_app(not args.foreground)
        
        # 如果两个服务都在后台运行，显示访问信息
        if (api_process or args.web_only) and (web_process or args.api_only) and not args.foreground:
            logger.info("所有服务已成功启动!")
            logger.info("API服务地址: http://localhost:8002")
            logger.info("Web应用地址: http://localhost:8000")
            logger.info("按Ctrl+C退出...")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("正在停止服务...")
                
                # 停止服务
                if api_process:
                    api_process.terminate()
                    logger.info("API服务已停止")
                
                if web_process:
                    web_process.terminate()
                    logger.info("Web应用已停止")
    except KeyboardInterrupt:
        logger.info("启动被用户中断")
    except Exception as e:
        logger.error(f"启动失败: {e}")
    
if __name__ == "__main__":
    main() 