#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多平台视频爬虫批量测试脚本
一键测试所有支持的平台
"""
import os
import sys
import logging
import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime

# 添加项目根目录到系统路径
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('all_platforms_test.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 支持的平台列表
SUPPORTED_PLATFORMS = ['youtube', 'tiktok', 'bilibili', 'weibo', 'facebook']

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="多平台视频爬虫批量测试脚本")
    
    # 基本参数
    parser.add_argument('--query', '-q', type=str, default="Python tutorial",
                      help='搜索关键词')
    parser.add_argument('--limit', '-l', type=int, default=3,
                      help='每个平台搜索结果数量限制')
    parser.add_argument('--platforms', '-p', type=str, nargs='+',
                      default=SUPPORTED_PLATFORMS,
                      help=f'要测试的平台，可选: {", ".join(SUPPORTED_PLATFORMS)}')
    
    # 功能选择
    parser.add_argument('--download', '-d', action='store_true',
                      help='是否测试下载功能')
    parser.add_argument('--no-search', action='store_true',
                      help='跳过搜索测试')
    
    # 其他配置
    parser.add_argument('--output-dir', '-o', type=str, default='./downloads',
                      help='视频下载目录')
    parser.add_argument('--cookie', '-c', type=str,
                      help='Cookie字符串，用于某些平台的认证')
    parser.add_argument('--proxy', type=str,
                      help='代理服务器地址')
    parser.add_argument('--selenium', '-s', action='store_true',
                      help='使用Selenium进行爬取')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='显示详细日志')
    parser.add_argument('--output-json', type=str, default='test_results.json',
                      help='将测试结果保存为JSON文件')
    parser.add_argument('--test-script', type=str, 
                      default=str(Path(__file__).parent / "multi_platform_test.py"),
                      help='测试脚本路径')
    
    return parser.parse_args()

def test_platform(platform, args):
    """测试单个平台"""
    logger.info(f"=== 开始测试平台: {platform} ===")
    
    # 构建命令行参数
    cmd = [sys.executable, args.test_script, "--platform", platform]
    
    # 添加查询参数
    if args.query:
        cmd.extend(["--query", args.query])
    
    # 限制结果数量
    cmd.extend(["--limit", str(args.limit)])
    
    # 下载选项
    if args.download:
        cmd.append("--download")
        cmd.extend(["--output-dir", args.output_dir])
    
    # 其他选项
    if args.cookie:
        cmd.extend(["--cookie", args.cookie])
    if args.proxy:
        cmd.extend(["--proxy", args.proxy])
    if args.selenium:
        cmd.append("--selenium")
    if args.verbose:
        cmd.append("--verbose")
    
    # 生成特定于平台的JSON输出文件
    platform_json = f"results_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    cmd.extend(["--output-json", platform_json])
    
    # 运行测试
    logger.info(f"执行命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 输出日志
        if result.stdout:
            logger.info(f"{platform} 测试输出:")
            for line in result.stdout.splitlines():
                logger.info(f"  {line}")
        
        if result.stderr:
            logger.error(f"{platform} 测试错误:")
            for line in result.stderr.splitlines():
                logger.error(f"  {line}")
                
        # 加载测试结果
        if os.path.exists(platform_json):
            with open(platform_json, 'r', encoding='utf-8') as f:
                try:
                    test_result = json.load(f)
                    logger.info(f"{platform} 测试结果摘要:")
                    
                    # 搜索结果
                    if test_result.get('search'):
                        status = "成功" if test_result['search']['success'] else "失败"
                        logger.info(f"  搜索: {status}, 找到 {test_result['search'].get('count', 0)} 个结果")
                    
                    # 视频信息结果
                    if test_result.get('video_info'):
                        status = "成功" if test_result['video_info']['success'] else "失败"
                        logger.info(f"  获取视频信息: {status}")
                    
                    # 下载结果
                    if test_result.get('download'):
                        status = "成功" if test_result['download']['success'] else "失败"
                        logger.info(f"  下载视频: {status}")
                    
                    return test_result
                except json.JSONDecodeError:
                    logger.error(f"无法解析 {platform} 测试结果文件")
    except Exception as e:
        logger.error(f"测试 {platform} 时发生错误: {str(e)}")
    
    return {
        "platform": platform,
        "error": "测试执行失败"
    }

def main():
    """主函数"""
    args = parse_arguments()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 验证平台
    for platform in args.platforms:
        if platform not in SUPPORTED_PLATFORMS:
            logger.warning(f"不支持的平台: {platform}，将被跳过")
    
    # 仅使用支持的平台
    platforms = [p for p in args.platforms if p in SUPPORTED_PLATFORMS]
    if not platforms:
        logger.error("没有指定有效的平台进行测试")
        sys.exit(1)
    
    logger.info(f"开始测试以下平台: {', '.join(platforms)}")
    
    # 依次测试每个平台
    all_results = {}
    for platform in platforms:
        result = test_platform(platform, args)
        all_results[platform] = result
    
    # 汇总结果
    logger.info("\n=== 所有平台测试结果摘要 ===")
    for platform, result in all_results.items():
        logger.info(f"平台: {platform}")
        
        if "error" in result:
            logger.info(f"  状态: 失败 ({result['error']})")
            continue
        
        # 搜索结果
        if result.get('search'):
            status = "成功" if result['search']['success'] else "失败"
            logger.info(f"  搜索: {status}, 找到 {result['search'].get('count', 0)} 个结果")
        
        # 视频信息结果
        if result.get('video_info'):
            status = "成功" if result['video_info']['success'] else "失败"
            logger.info(f"  获取视频信息: {status}")
        
        # 下载结果
        if result.get('download'):
            status = "成功" if result['download']['success'] else "失败"
            logger.info(f"  下载视频: {status}")
    
    # 保存整体测试结果
    if args.output_json:
        try:
            with open(args.output_json, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
            logger.info(f"所有测试结果已保存到: {args.output_json}")
        except Exception as e:
            logger.error(f"保存结果到JSON失败: {str(e)}")
    
    logger.info("所有平台测试完成")

if __name__ == "__main__":
    main() 