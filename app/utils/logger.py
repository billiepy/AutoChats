from loguru import logger
import sys
import os
from pathlib import Path

# Setup loguru
def setup_logger():
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        log_dir / "userbot.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{extra}",
        serialize=True
    )
    
    return logger

logger = setup_logger()
