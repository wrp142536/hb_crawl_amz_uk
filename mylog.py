import logging.config

logging.config.fileConfig("log.conf")


class My_log:
    """
    单例模式日志
    """

    def __init__(self, name):
        self.name = logging.getLogger(name)

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_logger'):
            cls._logger = object.__new__(cls)
        return cls._logger

    def get_logger(self):
        return self.name
