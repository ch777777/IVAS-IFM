import os
import sys
import logging
import uvicorn
from pathlib import Path

# 配置基本路径
BASE_DIR = Path(__file__).resolve().parent
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
        logging.FileHandler(str(logs_dir / "tikhub_api.log"), encoding="utf-8")
    ]
)

logger = logging.getLogger("run_tikhub_api")

def main():
    """启动TikHub API服务 (更新版)"""
    logger.info("启动 TikHub API V2服务...")
    
    try:
        # 确保API密钥已配置
        config_path = BASE_DIR / "config.json"
        if config_path.exists():
            logger.info("已检测到配置文件")
        else:
            logger.warning("未检测到配置文件，如需使用远程API功能请确保提供API密钥")
        
        # 启动FastAPI应用
        uvicorn.run(
            "tikhub_api_updated:app", 
            host="0.0.0.0", 
            port=8002, 
            reload=True,
            log_level="info"
        )
        return 0
    except Exception as e:
        logger.exception(f"启动TikHub API服务时出错: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 