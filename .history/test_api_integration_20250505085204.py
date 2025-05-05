#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IVAS-IFM外部API集成测试工具
用于测试与BibiGPT和KrillinAI的API集成
"""

import os
import json
import logging
import argparse
from pathlib import Path
from ivas_integration import IVASVideoProcessor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ivas-api-test")

def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}
    else:
        logger.warning("配置文件不存在，使用环境变量")
        return {}

def test_bibigpt_integration(processor, text=None):
    """测试BibiGPT API集成"""
    logger.info("=== 测试BibiGPT摘要API集成 ===")
    
    # 准备测试数据
    video_info = {
        "title": text or "这是一个测试视频，展示了如何使用BibiGPT进行视频摘要生成",
        "description": "视频内容包括：BibiGPT介绍、功能演示、API使用方法、集成案例等。希望对大家有帮助！",
        "platform": "douyin",
        "author": {"nickname": "测试账号"},
        "share_url": "https://example.com/test-video"
    }
    
    # 调用摘要生成
    summary_result = processor._generate_summary(video_info)
    
    # 检查结果
    logger.info(f"摘要生成结果:")
    logger.info(f"- 摘要: {summary_result.get('summary', '无')}")
    logger.info(f"- 关键词: {', '.join(summary_result.get('keywords', []))}")
    logger.info(f"- 情感: {summary_result.get('sentiment', '无')}")
    
    # 检查是否使用了模拟功能
    if summary_result.get("is_mocked", False):
        logger.warning("注意: 使用了模拟摘要功能，未成功调用BibiGPT API")
    else:
        logger.info("成功调用BibiGPT API！")
    
    return not summary_result.get("is_mocked", False)

def test_krillinai_integration(processor, text=None):
    """测试KrillinAI API集成"""
    logger.info("=== 测试KrillinAI翻译API集成 ===")
    
    # 准备测试数据
    test_text = text or "这是一个测试文本，用于验证KrillinAI翻译API的集成是否成功"
    
    # 调用翻译
    translation_result = processor.translate_text(test_text, "zh", "en")
    
    # 检查结果
    logger.info(f"翻译结果:")
    logger.info(f"- 原文: {translation_result.get('original_text', '无')}")
    logger.info(f"- 译文: {translation_result.get('translated_text', '无')}")
    logger.info(f"- 源语言: {translation_result.get('source_language', '无')}")
    logger.info(f"- 目标语言: {translation_result.get('target_language', '无')}")
    
    # 检查是否使用了模拟功能
    if translation_result.get("is_mocked", False):
        logger.warning("注意: 使用了模拟翻译功能，未成功调用KrillinAI API")
    else:
        logger.info("成功调用KrillinAI API！")
    
    return not translation_result.get("is_mocked", False)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="IVAS-IFM API集成测试工具")
    parser.add_argument("--bibigpt", action="store_true", help="测试BibiGPT API集成")
    parser.add_argument("--krillinai", action="store_true", help="测试KrillinAI API集成")
    parser.add_argument("--text", help="指定测试文本")
    parser.add_argument("--all", action="store_true", help="测试所有API集成")
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config()
    tikhub_api_key = config.get("tikhub_api_key", os.environ.get("TIKHUB_API_KEY", ""))
    
    # 初始化处理器
    processor = IVASVideoProcessor(tikhub_api_key=tikhub_api_key)
    
    # 如果未指定具体测试，则默认测试所有
    if not any([args.bibigpt, args.krillinai, args.all]):
        args.all = True
    
    results = {}
    
    # 测试BibiGPT集成
    if args.bibigpt or args.all:
        results["bibigpt"] = test_bibigpt_integration(processor, args.text)
    
    # 测试KrillinAI集成
    if args.krillinai or args.all:
        results["krillinai"] = test_krillinai_integration(processor, args.text)
    
    # 总结测试结果
    logger.info("\n=== 测试结果汇总 ===")
    for api, success in results.items():
        status = "成功" if success else "失败 (使用了模拟功能)"
        logger.info(f"{api.upper()} API集成测试: {status}")
    
    # 给出改进建议
    if not all(results.values()):
        logger.info("\n=== 改进建议 ===")
        if "bibigpt" in results and not results["bibigpt"]:
            logger.info("1. 检查BibiGPT API密钥是否正确配置在config.json或环境变量中")
            logger.info("2. 确认BibiGPT API服务是否可用")
        
        if "krillinai" in results and not results["krillinai"]:
            logger.info("1. 检查KrillinAI API密钥是否正确配置在config.json或环境变量中")
            logger.info("2. 确认KrillinAI API服务是否可用")

if __name__ == "__main__":
    main() 