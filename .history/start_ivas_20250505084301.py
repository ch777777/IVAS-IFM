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
logger = logging.getLogger("ivas-starter")

def start_tikhub_api(background=True):
    """启动TikHub API服务"""
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
                    start_new_session=True  # 在新的会话中运行
                )
            
            logger.info(f"TikHub API服务已在后台启动，进程ID: {process.pid}")
            return process
        except Exception as e:
            logger.error(f"启动TikHub API服务失败: {e}")
            return None
    else:
        # 在前台运行
        try:
            subprocess.run(cmd)
            return None
        except KeyboardInterrupt:
            logger.info("TikHub API服务已停止")
            return None
        except Exception as e:
            logger.error(f"启动TikHub API服务失败: {e}")
            return None

def start_ivas_api(background=True):
    """启动IVAS API服务"""
    logger.info("启动IVAS API服务...")
    
    cmd = [sys.executable, "ivas_api.py"]
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
                    start_new_session=True  # 在新的会话中运行
                )
            
            logger.info(f"IVAS API服务已在后台启动，进程ID: {process.pid}")
            return process
        except Exception as e:
            logger.error(f"启动IVAS API服务失败: {e}")
            return None
    else:
        # 在前台运行
        try:
            subprocess.run(cmd)
            return None
        except KeyboardInterrupt:
            logger.info("IVAS API服务已停止")
            return None
        except Exception as e:
            logger.error(f"启动IVAS API服务失败: {e}")
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
                    start_new_session=True  # 在新的会话中运行
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

def show_menu():
    """显示菜单"""
    print("\n" + "="*50)
    print("IVAS-IFM 视频平台API集成服务启动菜单")
    print("="*50)
    print("1. 启动TikHub API服务 (基础解析服务)")
    print("2. 启动IVAS API服务 (集成服务)")
    print("3. 启动TikHub Web应用 (Web界面)")
    print("4. 启动所有服务")
    print("5. 退出")
    print("="*50)
    choice = input("请输入选项 [1-5]: ")
    return choice

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="IVAS-IFM 启动器")
    parser.add_argument("--menu", action="store_true", help="显示交互式菜单")
    parser.add_argument("--tikhub", action="store_true", help="启动TikHub API服务")
    parser.add_argument("--ivas", action="store_true", help="启动IVAS API服务")
    parser.add_argument("--web", action="store_true", help="启动TikHub Web应用")
    parser.add_argument("--all", action="store_true", help="启动所有服务")
    parser.add_argument("--foreground", action="store_true", help="在前台运行服务")
    
    args = parser.parse_args()
    
    # 如果没有参数，默认显示菜单
    if not any([args.menu, args.tikhub, args.ivas, args.web, args.all]):
        args.menu = True
    
    processes = []
    
    try:
        # 交互式菜单
        if args.menu:
            while True:
                choice = show_menu()
                
                if choice == "1":
                    process = start_tikhub_api(background=True)
                    if process:
                        processes.append(("TikHub API", process))
                
                elif choice == "2":
                    process = start_ivas_api(background=True)
                    if process:
                        processes.append(("IVAS API", process))
                
                elif choice == "3":
                    process = start_web_app(background=True)
                    if process:
                        processes.append(("TikHub Web", process))
                
                elif choice == "4":
                    logger.info("启动所有服务...")
                    
                    # 启动TikHub API服务
                    process = start_tikhub_api(background=True)
                    if process:
                        processes.append(("TikHub API", process))
                        time.sleep(3)  # 等待TikHub API启动
                    
                    # 启动IVAS API服务
                    process = start_ivas_api(background=True)
                    if process:
                        processes.append(("IVAS API", process))
                    
                    # 启动Web应用
                    process = start_web_app(background=True)
                    if process:
                        processes.append(("TikHub Web", process))
                
                elif choice == "5":
                    # 停止所有服务并退出
                    break
                
                else:
                    print("无效的选项，请重新输入")
                    continue
                
                # 显示当前运行的服务
                if processes:
                    print("\n当前运行的服务:")
                    for name, proc in processes:
                        if proc.poll() is None:  # 检查进程是否还在运行
                            print(f"- {name} (PID: {proc.pid})")
                        else:
                            print(f"- {name} (已停止)")
                
                print("\n按Enter键返回菜单，或按Ctrl+C退出...", end="")
                try:
                    input()
                except KeyboardInterrupt:
                    break
            
            # 停止所有服务
            stop_processes(processes)
        
        # 命令行参数启动
        else:
            # 启动TikHub API服务
            if args.tikhub or args.all:
                process = start_tikhub_api(background=not args.foreground)
                if process:
                    processes.append(("TikHub API", process))
                    if args.all:
                        time.sleep(3)  # 等待TikHub API启动
            
            # 启动IVAS API服务
            if args.ivas or args.all:
                process = start_ivas_api(background=not args.foreground)
                if process:
                    processes.append(("IVAS API", process))
            
            # 启动Web应用
            if args.web or args.all:
                process = start_web_app(background=not args.foreground)
                if process:
                    processes.append(("TikHub Web", process))
            
            # 如果后台运行多个服务，等待用户中断
            if processes and not args.foreground:
                logger.info("所有服务已启动!")
                logger.info("TikHub API服务地址: http://localhost:8002")
                logger.info("IVAS API服务地址: http://localhost:8000")
                logger.info("TikHub Web应用地址: http://localhost:8000")
                logger.info("按Ctrl+C退出...")
                
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("正在停止所有服务...")
                    stop_processes(processes)
    
    except KeyboardInterrupt:
        logger.info("启动被用户中断")
        stop_processes(processes)
    except Exception as e:
        logger.error(f"启动失败: {e}")
        stop_processes(processes)

def stop_processes(processes):
    """停止所有进程"""
    for name, process in processes:
        if process and process.poll() is None:  # 检查进程是否还在运行
            try:
                process.terminate()
                logger.info(f"{name}服务已停止")
            except Exception as e:
                logger.error(f"停止{name}服务失败: {e}")

if __name__ == "__main__":
    main() 