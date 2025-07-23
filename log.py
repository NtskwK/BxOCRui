from datetime import datetime
import sys
from loguru import logger as log
from config import self_dir, is_debug


def log_init():
    log.remove()
    if is_debug():
        std_out_level = "DEBUG"
    else:
        std_out_level = "INFO"

    log_dir = self_dir.joinpath("logs")
    log_dir.mkdir(exist_ok=True)
    log.add(
        log_dir.joinpath(f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        rotation="1 MB",
        level="WARNING",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <6}</level> | "
        "<cyan>{file}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    log.add(
        sys.stdout,
        level=std_out_level,
        format="<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <6}</level> | "
        "<cyan>{file}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    log.info("Starting BxOCR application...")
