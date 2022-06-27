try:
    from config import CMD_START, CMD_SEP
except ImportError:
    from .logger import logger
    logger.error('config load failed, use default setting')
    # 命令前缀
    CMD_START = {'/', ''}
    # 命令连接符
    CMD_SEP = '.'
