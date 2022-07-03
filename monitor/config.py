try:
    from config import CMD_START, CMD_SEP, TULING_API_KEY, TULING_URL, BOT_NAME
except ImportError:
    from .logger import logger

    logger.error('config load failed, use default setting')
    # 命令前缀
    CMD_START = {'/', ''}
    # 命令连接符
    CMD_SEP = '.'
    # TULING_API_KEY
    TULING_API_KEY = ''
    # TULING_URL
    TULING_URL = ''
    # bot name
    BOT_NAME = ''
