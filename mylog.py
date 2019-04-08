import logging
import logging.handlers
from tools import Singleton


class My_log(Singleton):
    """
    日志系统，error和info分别记录
    """

    def __init__(self, logger_name='lyl', info_name='amz_info.log', error_name='amz_error.log',
                 warning_name='amz_warning.log'):
        self.info_name = info_name
        self.logger_name = logger_name
        self.error_name = error_name
        self.warning_name = warning_name

    def get_logger(self):
        logger = logging.getLogger(self.logger_name)
        # 添加此行，防止日志重复记录
        if not logger.handlers:
            # 默认日志等级
            logger.setLevel(logging.INFO)

            # 格式化输出
            formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(message)s", "%Y%m%d %H:%M:%S")
            formatter01 = logging.Formatter("%(asctime)s - %(message)s", "%Y%m%d %H:%M:%S")

            # 创建两个handler
            info_handler = logging.handlers.TimedRotatingFileHandler(self.info_name, when='midnight', interval=7,
                                                                     backupCount=7, encoding='utf-8')
            error_handler = logging.handlers.TimedRotatingFileHandler(self.error_name, when='midnight', interval=7,
                                                                      backupCount=7, encoding='utf-8')
            warning_handler = logging.handlers.TimedRotatingFileHandler(self.warning_name, when='midnight', interval=7,
                                                                      backupCount=7, encoding='utf-8')

            # 设置日志切割后的名字后缀
            info_handler.suffix = "%Y%m%d-%H%M.log"
            error_handler.suffix = "%Y%m%d-%H%M.log"
            warning_handler.suffix = "%Y%m%d-%H%M.log"

            # 设置日志等级
            error_handler.setLevel(logging.ERROR)
            warning_handler.setLevel(logging.WARNING)
            info_handler.setLevel(logging.INFO)

            # 格式化输出应用给handlers
            info_handler.setFormatter(formatter)
            error_handler.setFormatter(formatter)
            warning_handler.setFormatter(formatter01)

            # 添加过滤器，过滤掉info中等级小于warning的
            info_filter = logging.Filter()
            info_filter.filter = lambda record: record.levelno == logging.INFO

            warning_filter = logging.Filter()
            warning_filter.filter = lambda record: record.levelno == logging.WARNING

            info_handler.addFilter(info_filter)
            warning_handler.addFilter(warning_filter)

            # handler添加给对象
            logger.addHandler(info_handler)
            logger.addHandler(error_handler)
            logger.addHandler(warning_handler)
            return logger


logger = My_log().get_logger()
