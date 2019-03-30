import logging.config
from tools import Singleton


class My_log(Singleton):
    """
    单例模式日志
    """

    def __init__(self, conf_file='log.conf'):
        logging.config.fileConfig(conf_file)
        pass

    def get_logger(self, logger):
        logger = logging.getLogger(logger)
        return logger

