import logging
from datetime import datetime
import os
from pathlib import Path

def setup_logger():
    """
    配置日志系统，创建两个日志文件：
    - info_日期.log: 只记录INFO级别的日志
    - error_日期.log: 只记录ERROR级别的日志
    同时在控制台显示所有日志
    """
    # 确保logs目录存在
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # 配置日志文件名
    date_str = datetime.now().strftime("%Y-%m-%d")
    info_log_file = logs_dir / f'info_{date_str}.log'
    error_log_file = logs_dir / f'error_{date_str}.log'

    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 清理现有的handlers
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    # 创建INFO级别的handler
    info_handler = logging.FileHandler(info_log_file, encoding='utf-8')
    info_handler.setFormatter(formatter)
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(lambda record: record.levelno == logging.INFO)

    # 创建ERROR级别的handler
    error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # 创建控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # 配置根日志记录器
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(info_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    logging.info("日志配置完成")
